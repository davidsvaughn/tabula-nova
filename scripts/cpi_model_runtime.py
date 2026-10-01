"""Frozen LOG-009 CPI inputs and single-query native model runtime.

Built with StableAI LimiX. Non-commercial research; original weights stay in place.
"""
from __future__ import annotations

from datetime import datetime
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

os.environ["TABPFN_DISABLE_TELEMETRY"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FEATURES = ["cpi_lag1", "cpi_lag2", "cpi_lag3", "cpi_lag12", "month_sin", "month_cos"]
CHECKPOINTS = {
    "tabpfn": (Path("/home/david/Downloads/tabpfn/tabpfn-v3.5-20260909.safetensors"), "ece4d67eadfea42eb0e610df5189bea60cb7f31073d81e9c7a019b76eacf0be3"),
    "limix": (Path("/home/david/Downloads/limix2/LimiX-2.ckpt"), "ed01f7a0a18d25451bc9d1058b479ba6b68048aa1ebde06156c8fcfaf8b8fe81"),
}
RUNTIME = ROOT / "data/research/limix-runtime"
MODELS = ("mean", "ridge", "hgb", "tabpfn", "limix")


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def load_events(path: Path) -> list[dict]:
    summary = json.loads((path.parent / "summary.json").read_text())
    for name, expected in summary["input_sha256"].items():
        source = Path(name)
        if not source.is_absolute():
            source = ROOT / source
        if sha256(source) != expected:
            raise ValueError(f"Input changed since event-table audit: {source}")
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    if len({row["reference_month"] for row in rows}) != len(rows):
        raise ValueError("Duplicate CPI reference months")
    rows.sort(key=lambda row: row["reference_month"])
    for row in rows:
        if row["parse_status"] == "parsed" and row["complete_lag_context"]:
            cutoff = datetime.fromisoformat(row["cutoff_at_utc"])
            for lag in row["lags"].values():
                if lag["value"] is None or datetime.fromisoformat(lag["available_at_utc"]) >= cutoff:
                    raise ValueError("Future or missing CPI lag")
    return rows


def features(row: dict) -> np.ndarray:
    month = int(row["reference_month"][5:])
    return np.array([float(row["lags"][str(lag)]["value"]) for lag in (1, 2, 3, 12)] + [math.sin(2 * math.pi * month / 12), math.cos(2 * math.pi * month / 12)], dtype=np.float64)


def context(rows: list[dict], query: dict) -> tuple[list[dict], np.ndarray, np.ndarray, np.ndarray]:
    cutoff = datetime.fromisoformat(query["cutoff_at_utc"])
    previous = [row for row in rows if row["reference_month"] < query["reference_month"] and row["parse_status"] == "parsed" and row["complete_lag_context"] and datetime.fromisoformat(row["label_available_at_utc"]) < cutoff][-120:]
    if len(previous) < 48:
        raise ValueError(f"Fewer than48 past eligible training rows for {query['reference_month']}")
    return previous, np.stack([features(row) for row in previous]), np.array([float(row["target_value_initial"]) for row in previous]), features(query)[None, :]


def headroom(gpu: bool) -> dict:
    memory = {line.split()[0].rstrip(":"): int(line.split()[1]) * 1024 for line in Path("/proc/meminfo").read_text().splitlines() if len(line.split()) >= 2}
    result = {"available_ram_bytes": memory["MemAvailable"], "swap_free_bytes": memory["SwapFree"]}
    if result["available_ram_bytes"] < 4 * 1024**3:
        raise RuntimeError("Stopping before prediction: shared-laptop RAM reserve below4GiB")
    if gpu:
        import torch
        free, total = torch.cuda.mem_get_info()
        result.update(free_gpu_bytes=free, total_gpu_bytes=total)
        if free < 2 * 1024**3:
            raise RuntimeError("Stopping before prediction: shared-laptop VRAM reserve below2GiB")
    return result


def create_model(name: str, model_path: Path | None = None) -> tuple[object, dict]:
    started = time.perf_counter()
    metadata = {"model": name, "seed": 17, "features": FEATURES, "queries_per_call": 1, "python": sys.version, "versions": {package: importlib.metadata.version(package) for package in ("numpy", "pandas", "scikit-learn")}}
    if name == "mean":
        model = None
    elif name == "ridge":
        from sklearn.linear_model import Ridge
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        model = make_pipeline(StandardScaler(), Ridge(alpha=1))
        metadata["config"] = {"standardized": True, "alpha": 1}
    elif name == "hgb":
        from sklearn.ensemble import HistGradientBoostingRegressor
        config = dict(max_iter=100, max_leaf_nodes=7, learning_rate=0.05, min_samples_leaf=10, l2_regularization=1, early_stopping=False, random_state=17)
        model = HistGradientBoostingRegressor(**config)
        metadata["config"] = config
    else:
        import torch
        if not torch.cuda.is_available():
            raise RuntimeError("Native model smoke requires verified CUDA runtime")
        torch.set_num_threads(4)
        metadata["initial_headroom"] = headroom(True)
        torch.cuda.reset_peak_memory_stats()
        default, expected = CHECKPOINTS[name]
        checkpoint = model_path or default
        digest = sha256(checkpoint)
        if digest != expected:
            raise ValueError("Checkpoint is not the verified official weight; refusing model load")
        metadata.update(checkpoint_path=str(checkpoint), checkpoint_sha256=digest, device=torch.cuda.get_device_name(), torch_version=torch.__version__)
        if name == "tabpfn":
            from tabpfn import TabPFNRegressor
            model = TabPFNRegressor(device="cuda", n_estimators=8, random_state=17, model_path=str(checkpoint))
            metadata.update(native_estimators=8, tabpfn_version=importlib.metadata.version("tabpfn"))
        else:
            os.environ["LIMIX_CACHE_DIR"] = str(RUNTIME / "cache")
            import limix
            from limix import LimiXPredictor
            config_path = RUNTIME / "source/config/reg_default_noretrieval_v2.json"
            config = json.loads(config_path.read_text())
            if len(config["pipelines"]) != 8:
                raise ValueError("Native regression pipeline count changed")
            config["adaptive_svd"]["retry_on_cuda_resource_error"] = False
            model = LimiXPredictor(device=torch.device("cuda"), model_path=str(checkpoint), inference_config=config, seed=17, preprocess_num_jobs=4, use_data_cache=False)
            if model.n_estimators != 8 or type(model).__module__ != "inference.v2_0.predictor":
                raise ValueError("Unexpected LimiX architecture or ensemble")
            source = Path(limix.__file__).resolve().parent.parent
            revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip()
            if revision != "516bf396333feb3198cf7aff8a6c10421f218e24":
                raise ValueError("LimiX source revision changed")
            metadata.update(native_estimators=8, attribution="Built with StableAI LimiX", limix_version=importlib.metadata.version("limix"), source_revision=revision, patched_predictor_sha256=sha256(source / "inference/v2_0/predictor.py"), upstream_config_sha256=sha256(config_path), effective_inference_config=config)
    metadata["constructor_seconds"] = time.perf_counter() - started
    return model, metadata


def predict(name: str, model: object, x: np.ndarray, y: np.ndarray, query: np.ndarray) -> tuple[float, dict]:
    if query.shape != (1, len(FEATURES)):
        raise ValueError("Only one contemporaneous six-feature query is permitted")
    available = headroom(name in ("tabpfn", "limix"))
    started = time.perf_counter()
    if name == "mean":
        raw = np.array([y.mean()])
    elif name == "limix":
        import torch
        with torch.inference_mode():
            raw = np.asarray(model.predict(x, y, query, task_type="Regression"))
        for audit in ("svd_runtime_retry_audit", "polynomial_interaction_runtime_retry_audit", "cuda_pipeline_fallback_audit"):
            if getattr(model, audit):
                raise RuntimeError(f"Refusing resource-altered LimiX ensemble: {audit}")
    else:
        model.fit(x, y)
        raw = np.asarray(model.predict(query))
    if raw.shape != (1,) or not np.isfinite(raw).all():
        raise ValueError(f"Unexpected native regression output: {raw.shape}")
    return float(raw[0]), dict(available, elapsed_seconds=time.perf_counter() - started, output_shape=list(raw.shape))


def resources(gpu: bool) -> dict:
    result = {"peak_process_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024, "final_headroom": headroom(gpu)}
    if gpu:
        import torch
        result.update(peak_cuda_allocated_bytes=torch.cuda.max_memory_allocated(), peak_cuda_reserved_bytes=torch.cuda.max_memory_reserved())
    return result
