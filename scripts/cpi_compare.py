"""Compare frozen CPI outputs using paired12-calendar-month block resampling.

Preserves excluded calendar months as gaps instead of compressing75 observations
into75 consecutive months. No model fitting, configuration selection or new data.
"""
from __future__ import annotations

import argparse
from itertools import combinations
import json
from pathlib import Path

import numpy as np

from cpi_model_runtime import MODELS, sha256

PERIODS = {"development": ((2010, 1), (2019, 12), 120), "confirmation": ((2020, 1), (2026, 8), 75)}
METRICS = ("crps", "mae", "pinball_0.1", "pinball_0.5", "pinball_0.9", "interval_80_covered", "interval_80_width", "brier_print_strict_above_0_3")
BASELINES = ("mean", "ridge", "hgb")


def month_number(value: str) -> int:
    year, month = map(int, value.split("-"))
    return year * 12 + month - 1


def block_indices(calendar_n: int) -> np.ndarray:
    if calendar_n < 12:
        raise ValueError("At least12 calendar months required")
    rng = np.random.default_rng(17)
    starts = rng.integers(0, calendar_n - 12 + 1, size=(2000, (calendar_n + 11) // 12))
    return (starts[:, :, None] + np.arange(12)[None, None, :]).reshape(2000, -1)[:, :calendar_n]


def paired_difference(left: list[dict], right: list[dict], period: str, metric: str) -> dict:
    start, end, expected = PERIODS[period]
    first = start[0] * 12 + start[1] - 1
    last = end[0] * 12 + end[1] - 1
    differences = np.full(last - first + 1, np.nan)
    for a, b in zip(left, right):
        if a["period"] != period:
            continue
        if a["reference_month"] != b["reference_month"]:
            raise ValueError("Unpaired CPI events")
        differences[month_number(a["reference_month"]) - first] = float(a["scores"][metric]) - float(b["scores"][metric])
    present = np.isfinite(differences)
    if int(present.sum()) != expected:
        raise ValueError("Frozen period cohort changed")
    samples = differences[block_indices(len(differences))]
    estimates = np.nanmean(samples, axis=1)
    if not np.isfinite(estimates).all():
        raise ValueError("A resampled block contains no scored event")
    bounds = np.quantile(estimates, [0.025, 0.975], method="linear")
    return {"mean_difference_left_minus_right": float(differences[present].mean()), "paired_95pct_block_interval": bounds.tolist(), "n_paired_events": expected, "n_calendar_months": len(differences), "missing_calendar_months": [f"{(first + index) // 12:04d}-{(first + index) % 12 + 1:02d}" for index in np.flatnonzero(~present)]}


def validate_results(results: dict) -> None:
    reference = next(iter(results.values()))
    for name, result in results.items():
        if result["model"] != name or result["n_warmup"] != 60 or result["n_scored"] != 195:
            raise ValueError("Not a completed frozen CPI result")
        if result["event_table_sha256"] != reference["event_table_sha256"] or result["publication_audit"] != reference["publication_audit"] or result["distribution_config"] != reference["distribution_config"]:
            raise ValueError("Model results used different data, gate or distribution protocol")
        if len(result["events"]) != 255:
            raise ValueError("Incomplete frozen query cohort")
        months = [row["reference_month"] for row in result["events"]]
        if len(set(months)) != len(months) or months != sorted(months):
            raise ValueError("Duplicate or unordered CPI events")
        for row, other in zip(result["events"], reference["events"]):
            for field in ("reference_month", "period", "cutoff_at_utc", "train_n", "train_reference_month_min", "train_reference_month_max", "training_label_available_max", "calibration_n", "calibration_reference_months", "calibration_label_available_max"):
                if row[field] != other[field]:
                    raise ValueError(f"Models differ on information/cohort: {field}")
            if row["period"] != "warmup":
                if row["actual_print_mom_pct"] != other["actual_print_mom_pct"]:
                    raise ValueError("Models used different targets")
                if not all(np.isfinite(float(row["scores"][metric])) for metric in METRICS):
                    raise ValueError("Nonfinite model scores")
        for period, (_, _, count) in PERIODS.items():
            selected = [row for row in result["events"] if row["period"] == period]
            if len(selected) != count:
                raise ValueError("Frozen evaluation period changed")
            for metric in METRICS:
                if not np.isclose(np.mean([row["scores"][metric] for row in selected]), result["scores"][period][metric], rtol=0, atol=1e-12):
                    raise ValueError("Per-event and aggregate score disagreement")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, nargs="+", required=True)
    parser.add_argument("--require-all", action="store_true", help="Require all five declared models for final comparison")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error(f"Refusing to overwrite {args.output}")
    results, hashes = {}, {}
    for path in args.results:
        data = json.loads(path.read_text())
        name = data["model"]
        if name not in MODELS or name in results:
            parser.error("Unknown or duplicate model result")
        results[name] = data
        hashes[str(path)] = sha256(path)
    if len(results) < 2 or (args.require_all and set(results) != set(MODELS)):
        parser.error("Comparison requires at least two models, or all five with --require-all")
    validate_results(results)
    names = [name for name in MODELS if name in results]
    pairs = []
    for left, right in combinations(names, 2):
        # Prefer interpretable learned-minus-baseline differences in the output.
        if left in BASELINES and (right not in BASELINES or left == "mean"):
            left, right = right, left
        comparisons = {period: {metric: paired_difference(results[left]["events"], results[right]["events"], period, metric) for metric in METRICS} for period in PERIODS}
        pairs.append({"left": left, "right": right, "periods": comparisons})
    criteria = {}
    for model in ("tabpfn", "limix"):
        if model not in results:
            continue
        comparisons = [row for row in pairs if row["left"] == model and row["right"] in BASELINES]
        criteria[model] = {"passes_prespecified_confirmation_crps_criterion": len(comparisons) == 3 and all(row["periods"]["confirmation"]["crps"]["mean_difference_left_minus_right"] < 0 and row["periods"]["confirmation"]["crps"]["paired_95pct_block_interval"][1] < 0 for row in comparisons), "comparisons_against_conventional_baselines": len(comparisons), "criterion_scope": "Individual paired95% block intervals below zero against all three declared baselines; not familywise-adjusted significance or a general forecasting claim"}
    result = {"protocol": "LOG-009; fixed12-month moving calendar blocks,2000replicates,seed17", "models": names, "event_table_sha256": next(iter(results.values()))["event_table_sha256"], "publication_audit": next(iter(results.values()))["publication_audit"], "input_sha256": hashes, "scores": {name: results[name]["scores"] for name in names}, "paired_comparisons": pairs, "confirmation_crps_criterion": criteria, "limitations": ["Historical archival comparison under explicitly bounded source/schedule assumptions, not strict first-byte PIT certification", "Calendar blocks preserve excluded months; no independent-strike or iid-month uncertainty claim", "Few correlated regime episodes; block interval is a sensitivity to sampling, not proof of future performance", "No correction for selection across model families; fixed configurations are preserved", "Coverage and all secondary metrics must accompany any positive CRPS criterion; no market/consensus/trading claim"]}
    for path in args.results:
        if sha256(path) != hashes[str(path)]:
            raise ValueError("Result changed during comparison")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"models": names, "confirmation_crps_criterion": criteria, "confirmation_crps_pairs": [{"left": row["left"], "right": row["right"], **row["periods"]["confirmation"]["crps"]} for row in pairs]}, indent=2))


if __name__ == "__main__":
    main()
