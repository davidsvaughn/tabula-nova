"""LOG-009: gate-cleared, single-query CPI walk-forward residual distributions.

Smoke executes60 actual warmup predictions and the first development forecast,
without exposing its outcome or any score. Full inference requires a publication
availability audit matching the exact event-table hash and frozen query cohort.
"""
from __future__ import annotations

import argparse
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import json
from pathlib import Path
import time

import numpy as np
from threadpoolctl import threadpool_limits

from cpi_model_runtime import MODELS, ROOT, context, create_model, load_events, predict, resources, sha256


def round_print(value: float) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def distribution_scores(samples: np.ndarray, actual: float, point: float) -> dict:
    if samples.shape != (60,) or not np.isfinite(samples).all():
        raise ValueError("Exactly60 finite past-error predictive samples required")
    ordered = np.sort(samples)
    n = len(samples)
    half_pairwise = np.dot(2 * np.arange(1, n + 1) - n - 1, ordered) / n**2
    crps = float(np.abs(samples - actual).mean() - half_pairwise)
    if crps < -1e-12:
        raise ValueError("Invalid negative CRPS")
    quantiles = np.quantile(samples, [0.1, 0.5, 0.9], method="linear")
    probability = sum(round_print(float(sample)) > Decimal("0.3") for sample in samples) / n
    truth = Decimal(str(actual)) > Decimal("0.3")
    result = {"crps": crps, "mae": abs(point - actual), "interval_80_covered": bool(quantiles[0] <= actual <= quantiles[2]), "interval_80_width": float(quantiles[2] - quantiles[0]), "probability_print_strict_above_0_3": probability, "brier_print_strict_above_0_3": (probability - int(truth))**2}
    for q, value in zip((0.1, 0.5, 0.9), quantiles):
        error = actual - value
        result[f"quantile_{q}"] = float(value)
        result[f"pinball_{q}"] = float(max(q * error, (q - 1) * error))
    return result


def frozen_queries(rows: list[dict]) -> list[dict]:
    candidates = [row for row in rows if row["parse_status"] == "parsed" and row["complete_lag_context"]]
    if len(candidates) != 303:
        raise ValueError("Frozen303-event candidate cohort changed; adjudicate before running")
    queries = [row for row in candidates if "2005-01" <= row["reference_month"] <= "2026-08"]
    sizes = {"warmup": sum(row["reference_month"] < "2010-01" for row in queries), "development": sum("2010-01" <= row["reference_month"] <= "2019-12" for row in queries), "confirmation": sum(row["reference_month"] >= "2020-01" for row in queries)}
    if sizes != {"warmup": 60, "development": 120, "confirmation": 75}:
        raise ValueError(f"Frozen query partition changed: {sizes}")
    return queries


def require_publication_gate(directory: Path, event_path: Path, rows: list[dict], queries: list[dict]) -> dict:
    summary = json.loads((directory / "summary.json").read_text())
    if summary["event_table_sha256"] != sha256(event_path):
        raise ValueError("Publication audit targets a different event-table snapshot")
    gate = summary["model_run_gate"]
    if gate["permitted"] is not True:
        raise ValueError(f"Full inference blocked by publication audit: {gate['reason']}")
    audit = {row["reference_month"]: row for row in (json.loads(line) for line in (directory / "events.jsonl").read_text().splitlines())}
    required_labels = set()
    for query in queries:
        if not audit[query["reference_month"]]["model_query_eligible"]:
            raise ValueError(f"Frozen query lacks publication evidence: {query['reference_month']}")
        train, _, _, _ = context(rows, query)
        required_labels.update(row["reference_month"] for row in train)
        required_labels.update(lag["reference_month"] for row in train + [query] for lag in row["lags"].values())
        required_labels.add(query["reference_month"])
    for month in required_labels:
        if not audit[month]["model_input_eligible"]:
            raise ValueError(f"Training/lag/target print lacks publication evidence: {month}")
    return {"summary_sha256": sha256(directory / "summary.json"), "events_sha256": sha256(directory / "events.jsonl"), "model_run_gate": gate}


def aggregate(records: list[dict]) -> dict:
    return {name: float(np.mean([row["scores"][name] for row in records])) for name in ("crps", "mae", "pinball_0.1", "pinball_0.5", "pinball_0.9", "interval_80_covered", "interval_80_width", "brier_print_strict_above_0_3")}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=MODELS, required=True)
    parser.add_argument("--model-path", type=Path)
    parser.add_argument("--events", type=Path, default=ROOT / "data/research/cpi/events/events.jsonl")
    parser.add_argument("--publication-audit", type=Path)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error(f"Refusing to overwrite {args.output}")
    if args.smoke and args.model not in ("mean", "ridge", "hgb"):
        parser.error("Runner smoke uses conventional models; native single-query smoke has a separate exercised CLI")
    if not args.smoke and args.publication_audit is None:
        parser.error("Full scored inference requires --publication-audit; no uncertified fallback")
    rows = load_events(args.events)
    queries = frozen_queries(rows)
    gate = None
    if args.smoke:
        queries = [row for row in queries if row["reference_month"] <= "2010-01"]
    else:
        gate = require_publication_gate(args.publication_audit, args.events, rows, queries)
    event_hash = sha256(args.events)
    history = []
    forecasts = []
    timings = []
    started = time.perf_counter()
    with threadpool_limits(limits=4):
        model, metadata = create_model(args.model, args.model_path)
        for index, query in enumerate(queries):
            train, x, y, query_x = context(rows, query)
            point, timing = predict(args.model, model, x, y, query_x)
            timings.append(timing)
            cutoff = datetime.fromisoformat(query["cutoff_at_utc"])
            past = [error for error in history if datetime.fromisoformat(error["label_available_at_utc"]) < cutoff][-60:]
            month = query["reference_month"]
            period = "warmup" if month < "2010-01" else "development" if month <= "2019-12" else "confirmation"
            record = {"reference_month": month, "cutoff_at_utc": query["cutoff_at_utc"], "period": period, "point_prediction_mom_pct": point, "train_n": len(train), "train_reference_month_min": train[0]["reference_month"], "train_reference_month_max": train[-1]["reference_month"], "training_label_available_max": max(row["label_available_at_utc"] for row in train), "calibration_n": len(past), "calibration_reference_months": [error["reference_month"] for error in past], "calibration_label_available_max": max((error["label_available_at_utc"] for error in past), default=None)}
            if period != "warmup":
                if len(past) != 60:
                    raise ValueError(f"Not60 available past prediction errors for {month}")
                samples = point + np.array([error["error"] for error in past])
                record["predictive_samples_mom_pct"] = samples.tolist()
                if not args.smoke:
                    actual = float(query["target_value_initial"])
                    record.update(actual_print_mom_pct=actual, scores=distribution_scores(samples, actual, point))
            forecasts.append(record)
            if not args.smoke or period == "warmup":
                history.append({"reference_month": month, "label_available_at_utc": query["label_available_at_utc"], "error": float(query["target_value_initial"]) - point})
            if (index + 1) % 12 == 0:
                print(json.dumps({"model": args.model, "completed": index + 1, "reference_month": month, "elapsed_seconds": time.perf_counter() - started}), flush=True)
    if sha256(args.events) != event_hash:
        raise ValueError("Event-table snapshot changed during inference")
    result = {"purpose": "Past-only runner smoke without scores/outcome" if args.smoke else "Gate-cleared frozen CPI release-distribution comparison; not a trading or consensus claim", "protocol": "LOG-009", "model": args.model, "event_table_sha256": event_hash, "publication_audit": gate, "model_metadata": metadata, "elapsed_seconds": time.perf_counter() - started, "resources": resources(args.model in ("tabpfn", "limix")), "prediction_headroom_min": {key: min(timing[key] for timing in timings) for key in timings[0] if key.endswith("_bytes")}, "prediction_seconds_total": sum(timing["elapsed_seconds"] for timing in timings), "n_warmup": sum(row["period"] == "warmup" for row in forecasts), "n_scored": 0 if args.smoke else sum(row["period"] != "warmup" for row in forecasts), "distribution_config": {"calibration": "last60 signed strictly available past walk-forward errors", "quantile_interpolation": "numpy linear", "print_rounding": "Decimal HALF_UP to0.1 (half-away-from-zero)", "target_units": "percentage points", "queries_per_call": 1}, "events": forecasts, "limitations": ["Archived print/vintage and dated schedule evidence, not independent first-HTTP snapshots", "Restricted six-feature lag/seasonality information; no nowcast or market combination", "Shared empirical residual method, not native posterior comparison", "Native models have different preprocessing/runtime; not an equal-compute architecture comparison", "Historical confirmation, not proof of prospectively unknown training-corpus outcomes"]}
    if not args.smoke:
        scored = [row for row in forecasts if row["period"] != "warmup"]
        result["scores"] = {period: aggregate([row for row in scored if row["period"] == period]) for period in ("development", "confirmation")}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"model": args.model, "output": str(args.output), "n_warmup": result["n_warmup"], "n_scored": result["n_scored"], "scores": result.get("scores"), "resources": result["resources"]}, indent=2))


if __name__ == "__main__":
    main()
