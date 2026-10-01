"""Retrospective SPF forecast-combination feasibility; not an NBER recession model.

Inputs: local public Philadelphia Fed workbooks and release-date file documented
in LOG-004 and data/research/spf/sources.json. Ablations follow LOG-006.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import time

os.environ["TABPFN_DISABLE_TELEMETRY"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss
import torch

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/research/spf"
MEANS = [f"RECESS{i}" for i in range(1, 6)]
FEATURES = MEANS + ["p25", "median", "p75", "std", "respondents"]


def publication_dates(path: Path) -> dict[pd.Period, str]:
    dates = {}
    year = None
    for line in path.read_text().splitlines():
        match = re.match(r"^\s*(?:(\d{4})\s+)?Q([1-4])\s+(.+)$", line)
        if not match:
            continue
        if match[1]:
            year = int(match[1])
        values = re.findall(r"\d{1,2}/\d{1,2}/\d{2,4}", match[3])
        if year is None or len(values) != 2:
            raise ValueError(f"Unrecognized survey date row: {line}")
        dates[pd.Period(f"{year}Q{match[2]}", freq="Q")] = pd.to_datetime(values[1], format="%m/%d/%y").date().isoformat()
    return dates


def load_events() -> tuple[pd.DataFrame, dict]:
    means = pd.read_excel(INPUT / "mean_recess.xlsx")
    individuals = pd.read_excel(INPUT / "individual_recess.xlsx")
    releases = pd.read_excel(INPUT / "first_gdp.xlsx", sheet_name="DATA", header=4)
    releases["quarter"] = pd.PeriodIndex(releases["Date"].str.replace(":", "", regex=False), freq="Q")
    first = releases.set_index("quarter")["First"]
    assert first.index.is_unique
    dates = publication_dates(INPUT / "release_dates.txt")
    means["quarter"] = pd.PeriodIndex(means["YEAR"].astype(str) + "Q" + means["QUARTER"].astype(str), freq="Q")
    assert means["quarter"].is_unique
    individuals["RECESS2"] = pd.to_numeric(individuals["RECESS2"], errors="coerce")
    available = individuals.dropna(subset=["RECESS2"])
    assert available["RECESS2"].between(0, 100).all()
    grouped = available.groupby(["YEAR", "QUARTER"])["RECESS2"]
    dispersion = grouped.agg(median="median", std="std", respondents="count")
    dispersion["p25"] = grouped.quantile(0.25)
    dispersion["p75"] = grouped.quantile(0.75)
    frame = means.merge(dispersion, on=["YEAR", "QUARTER"], validate="one_to_one")
    frame = frame.loc[(frame["quarter"] >= pd.Period("1992Q1")) & (frame["quarter"] <= pd.Period("2024Q4"))].copy()
    frame["target_quarter"] = frame["quarter"] + 1
    frame["first_growth"] = frame["target_quarter"].map(first)
    frame["publication_date"] = frame["quarter"].map(dates)
    excluded = frame.loc[frame[FEATURES + ["first_growth", "publication_date"]].isna().any(axis=1), ["quarter", "target_quarter"]]
    frame = frame.dropna(subset=FEATURES + ["first_growth", "publication_date"]).sort_values("quarter").reset_index(drop=True)
    for column in MEANS + ["p25", "median", "p75", "std"]:
        frame[column] = frame[column] / 100.0
    assert np.isfinite(frame[FEATURES].to_numpy()).all()
    assert frame[MEANS].ge(0).all().all() and frame[MEANS].le(1).all().all()
    assert (frame["respondents"] > 1).all()
    # These dates are publication days, not invented intra-day receipt timestamps.
    assert all(pd.Timestamp(d) < q.start_time for d, q in zip(frame["publication_date"], frame["target_quarter"]))
    frame["outcome"] = (frame["first_growth"] < 0).astype(int)
    return frame, {"eligible_events": len(frame), "excluded": excluded.astype(str).to_dict("records")}


def score(events: list[dict]) -> dict:
    y = [event["outcome"] for event in events]
    result = {}
    for name in events[0]["predictions"]:
        p = np.array([event["predictions"][name] for event in events])
        result[name] = {"brier": float(brier_score_loss(y, p)), "log_loss": float(log_loss(y, np.clip(p, 1e-6, 1 - 1e-6), labels=[0, 1]))}
    return result


def main() -> None:
    from tabpfn import TabPFNClassifier

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--feature-set", choices=["all", "no-count", "means"], default="all")
    parser.add_argument("--estimators", type=int, choices=[2, 8], default=2)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.model_path.is_file():
        parser.error("--model-path must be an existing licensed checkpoint")
    original = args.feature_set == "all" and args.estimators == 2
    output = args.output or INPUT / (
        "macro_spf_pilot.json" if original
        else f"macro_spf_{args.feature_set}_e{args.estimators}.json"
    )
    if output.exists():
        parser.error(f"Refusing to overwrite an existing research artifact: {output}; choose a new --output")
    features = {
        "all": FEATURES,
        "no-count": [column for column in FEATURES if column != "respondents"],
        "means": MEANS,
    }[args.feature_set]
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA required for this pinned local pilot")
    frame, coverage = load_events()
    events, folds, timings = [], [], []
    for fold, (start_year, end_year) in enumerate([(2004, 2010), (2011, 2017), (2018, 2024)]):
        start = pd.Period(f"{start_year}Q1", freq="Q")
        end = pd.Period(f"{end_year}Q4", freq="Q")
        train = frame.loc[frame["target_quarter"] <= start - 4]
        test = frame.loc[(frame["quarter"] >= start) & (frame["quarter"] <= end)]
        assert len(train) >= 40 and len(test) > 0
        assert train["outcome"].nunique() == 2
        assert train["target_quarter"].max() <= start - 4
        y = train["outcome"]
        probabilities = {
            "spf_mean": test["RECESS2"].to_numpy(),
            "training_frequency": np.full(len(test), y.mean()),
        }
        # Simple one-variable logistic recalibration of the public consensus probability.
        def logits(values):
            p = np.clip(values.to_numpy(), 1e-6, 1 - 1e-6)
            return np.log(p / (1 - p)).reshape(-1, 1)

        calibration = LogisticRegression(C=1.0, random_state=17)
        calibration.fit(logits(train["RECESS2"]), y)
        probabilities["logistic_calibration"] = calibration.predict_proba(logits(test["RECESS2"]))[:, 1]
        models = {
            "hist_gradient_boosting": HistGradientBoostingClassifier(max_iter=100, max_leaf_nodes=3, min_samples_leaf=10, l2_regularization=1, early_stopping=False, random_state=17),
            "tabpfn_3_5": TabPFNClassifier(model_path=str(args.model_path), device="cuda", n_estimators=args.estimators, random_state=17),
        }
        for name, model in models.items():
            begin = time.perf_counter()
            model.fit(train[features], y)
            positive = list(model.classes_).index(1)
            probabilities[name] = model.predict_proba(test[features])[:, positive]
            timings.append({"fold": fold, "model": name, "seconds": time.perf_counter() - begin})
        for name, p in probabilities.items():
            assert np.isfinite(p).all() and ((p >= 0) & (p <= 1)).all(), name
        for j, (_, row) in enumerate(test.iterrows()):
            events.append({"fold": fold, "survey_quarter": str(row["quarter"]), "publication_date": row["publication_date"], "target_quarter": str(row["target_quarter"]), "first_release_growth": float(row["first_growth"]), "outcome": int(row["outcome"]), "predictions": {name: float(p[j]) for name, p in probabilities.items()}})
        fold_info = {"fold": fold, "train_n": len(train), "train_positive": int(y.sum()), "train_target_max": str(train["target_quarter"].max()), "test_n": len(test), "test_positive": int(test["outcome"].sum()), "first_publication": test.iloc[0]["publication_date"]}
        folds.append(fold_info)
        print(json.dumps(fold_info), flush=True)
    assert len({row["target_quarter"] for row in events}) == len(events)
    with args.model_path.open("rb") as weights:
        checkpoint_hash = hashlib.file_digest(weights, "sha256").hexdigest()
    inputs = {name: hashlib.sha256((INPUT / name).read_bytes()).hexdigest() for name in ["mean_recess.xlsx", "individual_recess.xlsx", "first_gdp.xlsx", "release_dates.txt"]}
    result = {
        "task": "Probability of negative next-quarter real GDP growth under RTDSM First vintage-derived growth; NOT NBER recession",
        "protocol": "LOG-004" if original else "LOG-006; post-result exploratory ablation; same LOG-004 cohort and folds",
        "features": features, "feature_set": args.feature_set, "seed": 17, "tabpfn_estimators": args.estimators,
        "cpu_threads": {name: os.environ.get(name) for name in ["OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"]},
        "checkpoint_sha256": checkpoint_hash, "input_sha256": inputs,
        "versions": {p: importlib.metadata.version(p) for p in ["tabpfn", "torch", "pandas", "numpy", "scikit-learn", "openpyxl"]},
        "coverage": coverage, "folds": folds, "n_events": len(events), "n_positive": sum(e["outcome"] for e in events),
        "scores": score(events), "fold_scores": {str(f): score([e for e in events if e["fold"] == f]) for f in range(3)},
        "timings": timings, "events": events,
        "limitations": ["SPF predicts contraction but does not prescribe this specific RTDSM outcome vintage", "Latest historical archives may contain subsequent corrections", "Conservative target-period embargo instead of exact release-timestamp audit", "Few contractions and serially correlated quarters; no significance claim", "No untouched confirmation cohort, hyperparameter search or past-only post-hoc calibration", "Three frozen-context models, not continuously retrained production forecasts", "No claim that a marginal probability forecast identifies policy effects"],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"n_events": len(events), "n_positive": result["n_positive"], "scores": result["scores"], "output": str(output)}, indent=2))


if __name__ == "__main__":
    main()
