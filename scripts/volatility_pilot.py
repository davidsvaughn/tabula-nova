"""Offline, non-commercial feasibility benchmark; never a trading signal.

Run: .venv/bin/python scripts/volatility_pilot.py
Input is the separately captured Schwab SPY history; this script makes no market API calls.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import time

os.environ["TABPFN_DISABLE_TELEMETRY"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from tabpfn import TabPFNRegressor
import torch

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/research/schwab_spy_daily.json"
OUT = ROOT / "data/research/volatility_pilot.json"
LAST_COMPLETED_SESSION = "2026-09-30"
HORIZON = 5
FEATURES = ["rv5", "rv22", "ret1", "ret5", "range", "volume_ratio"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baselines-only", action="store_true", help="Explicitly omit TabPFN; never claim a model comparison")
    args = parser.parse_args()
    payload = json.loads(DATA.read_text())
    bars = pd.DataFrame(payload["candles"]).sort_values("datetime").reset_index(drop=True)
    bars["date"] = pd.to_datetime(bars["datetime"], unit="ms", utc=True).dt.tz_convert("America/New_York").dt.strftime("%Y-%m-%d")
    bars = bars.loc[bars["date"] <= LAST_COMPLETED_SESSION].copy()
    assert bars["date"].is_unique
    assert (bars["close"] > 0).all()
    r = np.log(bars["close"]).diff()
    bars["rv5"] = r.pow(2).rolling(5).mean() * 252
    bars["rv22"] = r.pow(2).rolling(22).mean() * 252
    bars["ret1"] = r
    bars["ret5"] = r.rolling(5).sum()
    bars["range"] = np.log(bars["high"] / bars["low"])
    bars["volume_ratio"] = bars["volume"] / bars["volume"].rolling(22).mean()
    # At close t, target uses returns t+1 through t+5, not the return into t.
    bars["target"] = r.pow(2).rolling(HORIZON).mean().shift(-HORIZON) * 252
    bars["label_end"] = bars["date"].shift(-HORIZON)
    frame = bars.dropna(subset=FEATURES + ["target", "label_end"]).reset_index(drop=True)
    assert np.isfinite(frame[FEATURES + ["target"]].to_numpy()).all()
    assert (frame["target"] > 0).all()
    assert len(frame) >= 850
    if not args.baselines_only and not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable: use the documented compatible Torch build; no silent CPU/model fallback")

    rows = []
    timings = []
    # Three frozen-context blocks; 20 nonoverlapping five-session labels per block.
    # Features update at each decision close, but training is frozen at block start.
    first = len(frame) - 300
    for fold, start in enumerate(range(first, len(frame), 100)):
        test = frame.iloc[start:start + 100:HORIZON]
        decision_date = test.iloc[0]["date"]
        train = frame.loc[frame["label_end"] < decision_date].tail(500)
        assert train["label_end"].max() < decision_date
        assert len(train) == 500
        x, y = train[FEATURES], np.log(train["target"])
        xt = test[FEATURES]
        predictions = {"rv5_persistence": test["rv5"].to_numpy(), "rv22_persistence": test["rv22"].to_numpy()}
        models = {
            "ridge_log_variance": make_pipeline(StandardScaler(), Ridge(alpha=10.0)),
            "hist_gradient_boosting_log_variance": HistGradientBoostingRegressor(max_iter=100, max_leaf_nodes=7, l2_regularization=1.0, early_stopping=False, random_state=17),
        }
        if not args.baselines_only:
            models["tabpfn_3_5_log_variance"] = TabPFNRegressor(device="cuda", n_estimators=2, random_state=17)
        for name, model in models.items():
            t0 = time.perf_counter()
            model.fit(x, y)
            predictions[name] = np.exp(model.predict(xt))
            timings.append({"fold": fold, "model": name, "seconds": time.perf_counter() - t0})
            assert np.isfinite(predictions[name]).all() and (predictions[name] > 0).all()
        for j, (_, event) in enumerate(test.iterrows()):
            rows.append({"fold": fold, "decision_date": event["date"], "label_end": event["label_end"], "training_label_end_max": train["label_end"].max(), "actual_variance": event["target"], "predictions": {name: float(p[j]) for name, p in predictions.items()}})
        print(json.dumps({"fold": fold, "train_n": len(train), "test_n": len(test), "first_decision": decision_date}), flush=True)

    def scores(events):
        actual = np.array([e["actual_variance"] for e in events])
        result = {}
        for name in events[0]["predictions"]:
            pred = np.array([e["predictions"][name] for e in events])
            ratio = actual / pred
            result[name] = {"qlike": float(np.mean(ratio - np.log(ratio) - 1)), "log_variance_mse": float(np.mean((np.log(actual) - np.log(pred)) ** 2))}
        return result

    for prev, current in zip(rows, rows[1:]):
        assert prev["label_end"] <= current["decision_date"]
    result = {
        "purpose": "Exploratory local inference/data feasibility, not evidence of trading edge or a CPI experiment",
        "execution_mode": "baselines_only" if args.baselines_only else "baselines_and_tabpfn",
        "input_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
        "config": {"horizon_sessions": HORIZON, "features": FEATURES, "train_rows": 500, "folds": 3, "test_stride": 5, "last_completed_session": LAST_COMPLETED_SESSION, "seed": 17, "tabpfn_estimators": 2, "target": "252 times mean next-five close-to-close squared log returns", "learned_target_transform": "natural log variance; exponentiated point prediction without mean-bias correction"},
        "versions": {p: importlib.metadata.version(p) for p in ["tabpfn", "torch", "numpy", "pandas", "scikit-learn"]},
        "device": "CPU (baselines only)" if args.baselines_only else torch.cuda.get_device_name(),
        "n_events": len(rows),
        "scores": scores(rows),
        "fold_scores": {str(f): scores([e for e in rows if e["fold"] == f]) for f in range(3)},
        "timings": timings,
        "events": rows,
        "limitations": ["One ETF, 60 nonoverlapping outcomes; no confirmatory significance claim", "Historical bar adjustments/as-of revisions unvalidated", "Closing bars assumed available just after close, not executable at that close", "Reduced two-estimator TabPFN configuration, not leaderboard defaults", "No hyperparameter search, calibration, GARCH benchmark or final untouched holdout", "QLIKE evaluates conditional variance; log-trained predictors need not estimate its optimal conditional mean", "No economic features, market probabilities, LimiX predictions or trading-cost assessment"],
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"n_events": len(rows), "scores": result["scores"], "output": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
