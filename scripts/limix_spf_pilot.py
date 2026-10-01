"""LOG-007: non-commercial LimiX-2 capability comparison. Built with StableAI LimiX.

Uses one contemporaneous query per call because upstream preprocessing is
transductive. Original TabPFN/consensus artifacts remain immutable.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import resource
import subprocess
import time

import numpy as np
import pandas as pd
import torch

from macro_spf_pilot import FEATURES, INPUT, ROOT, load_events, score

EXPECTED_CHECKPOINT = "ed01f7a0a18d25451bc9d1058b479ba6b68048aa1ebde06156c8fcfaf8b8fe81"
RUNTIME = ROOT / "data/research/limix-runtime"


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def check_headroom() -> dict:
    memory = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        fields = line.split()
        memory[fields[0].rstrip(":")] = int(fields[1])
    free_gpu, _ = torch.cuda.mem_get_info()
    available_ram = memory["MemAvailable"] * 1024
    if available_ram < 4 * 1024**3 or free_gpu < 2 * 1024**3:
        raise RuntimeError("Shared laptop headroom below reserve: stopping this experiment before another prediction")
    return {"available_ram_bytes": available_ram, "free_gpu_bytes": free_gpu}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--inference-config", type=Path, default=RUNTIME / "source/config/cls_default_noretrieval_v2.json")
    parser.add_argument("--output", type=Path, default=INPUT / "macro_spf_limix2_all.json")
    args = parser.parse_args()
    if args.output.exists():
        parser.error(f"Refusing to overwrite an existing research artifact: {args.output}")
    if not args.model_path.is_file() or not args.inference_config.is_file():
        parser.error("Checkpoint and official v2 inference config must exist")
    checkpoint_hash = sha256(args.model_path)
    if checkpoint_hash != EXPECTED_CHECKPOINT:
        raise ValueError("Checkpoint does not match the verified official LimiX-2 SHA256; refusing pickle loading")
    if not torch.cuda.is_available():
        raise RuntimeError("This experiment requires the verified local CUDA environment")
    torch.set_num_threads(4)
    os.environ["LIMIX_CACHE_DIR"] = str(RUNTIME / "cache")
    initial_headroom = check_headroom()
    original_path = INPUT / "macro_spf_pilot.json"
    eight_path = INPUT / "macro_spf_all_e8.json"
    original_hash = sha256(original_path)
    original = json.loads(original_path.read_text())
    eight = json.loads(eight_path.read_text())
    frame, coverage = load_events()
    assert coverage == original["coverage"]
    assert {name: sha256(INPUT / name) for name in original["input_sha256"]} == original["input_sha256"]
    identity = ["fold", "survey_quarter", "publication_date", "target_quarter", "first_release_growth", "outcome"]
    assert len(original["events"]) == len(eight["events"]) == 84
    assert original["input_sha256"] == eight["input_sha256"]
    assert original["folds"] == eight["folds"]
    events = copy.deepcopy(original["events"])
    by_quarter = frame.set_index("quarter")
    for event, e8 in zip(events, eight["events"]):
        assert all(event[key] == e8[key] for key in identity)
        row = by_quarter.loc[pd.Period(event["survey_quarter"], freq="Q")]
        assert event["target_quarter"] == str(row["target_quarter"])
        assert event["publication_date"] == row["publication_date"]
        assert event["outcome"] == int(row["outcome"])
        assert event["first_release_growth"] == float(row["first_growth"])
        event["predictions"]["tabpfn_3_5_e8"] = e8["predictions"]["tabpfn_3_5"]
    inference_config = json.loads(args.inference_config.read_text())
    assert len(inference_config["pipelines"]) == 32
    inference_config["adaptive_svd"]["retry_on_cuda_resource_error"] = False

    import limix
    from limix import LimiXPredictor

    source_root = Path(limix.__file__).resolve().parent.parent
    source_revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source_root, text=True).strip()
    started = time.perf_counter()
    torch.cuda.reset_peak_memory_stats()
    predictor = LimiXPredictor(
        device=torch.device("cuda"), model_path=str(args.model_path),
        inference_config=inference_config, seed=17,
        preprocess_num_jobs=4, use_data_cache=False,
    )
    assert type(predictor).__module__ == "inference.v2_0.predictor"
    constructor_seconds = time.perf_counter() - started
    print(json.dumps({"stage": "model_loaded", "pipelines": predictor.n_estimators, "constructor_seconds": constructor_seconds}), flush=True)
    timings = []
    headroom = [initial_headroom]
    audit_names = ["svd_runtime_retry_audit", "polynomial_interaction_runtime_retry_audit", "cuda_pipeline_fallback_audit"]
    for fold in original["folds"]:
        train = frame.loc[frame["target_quarter"] <= pd.Period(fold["train_target_max"], freq="Q")]
        assert len(train) == fold["train_n"]
        assert int(train["outcome"].sum()) == fold["train_positive"]
        assert str(train["target_quarter"].max()) == fold["train_target_max"]
        x_train = train[FEATURES].to_numpy()
        y_train = train["outcome"].to_numpy()
        fold_events = [event for event in events if event["fold"] == fold["fold"]]
        assert len(fold_events) == fold["test_n"]
        begin = time.perf_counter()
        for index, event in enumerate(fold_events):
            headroom.append(check_headroom())
            query = by_quarter.loc[[pd.Period(event["survey_quarter"], freq="Q")], FEATURES].to_numpy()
            # Never pass the other future quarters or any query outcome to preprocessing.
            with torch.inference_mode():
                probabilities = np.asarray(predictor.predict(x_train, y_train, query, task_type="Classification"))
            assert probabilities.shape == (1, 2)
            assert np.isfinite(probabilities).all()
            assert ((probabilities >= 0) & (probabilities <= 1)).all()
            assert np.allclose(probabilities.sum(axis=1), 1, atol=1e-5)
            assert list(predictor.classes) == [0, 1]
            for name in audit_names:
                if getattr(predictor, name):
                    raise RuntimeError(f"Refusing resource-altered ensemble: {name}")
            event["predictions"]["limix_2"] = float(probabilities[0, 1])
            if index == 0 or (index + 1) % 7 == 0:
                print(json.dumps({"fold": fold["fold"], "completed": index + 1, "survey_quarter": event["survey_quarter"], "probability": event["predictions"]["limix_2"], "elapsed_seconds": time.perf_counter() - begin}), flush=True)
        timings.append({"fold": fold["fold"], "seconds": time.perf_counter() - begin})
    assert all("limix_2" in event["predictions"] for event in events)
    assert sha256(original_path) == original_hash
    result = {
        "task": original["task"], "protocol": "LOG-007; single-query LimiX transductive inference; frozen LOG-004 cohort",
        "attribution": "Built with StableAI LimiX", "features": FEATURES, "seed": 17,
        "baseline_artifact_sha256": original_hash, "tabpfn_e8_artifact_sha256": sha256(eight_path),
        "input_sha256": original["input_sha256"], "checkpoint_sha256": checkpoint_hash,
        "checkpoint_path": str(args.model_path.resolve()), "source_revision": source_revision,
        "patched_predictor_sha256": sha256(source_root / "inference/v2_0/predictor.py"),
        "upstream_config_sha256": sha256(args.inference_config), "effective_inference_config": inference_config,
        "predictor_settings": {"seed": 17, "preprocess_num_jobs": 4, "use_data_cache": False, "queries_per_call": 1, "pipelines": predictor.n_estimators, "softmax_temperature": predictor.softmax_temperature, "mix_precision": predictor.mix_precision},
        "versions": {p: importlib.metadata.version(p) for p in ["limix", "torch", "numpy", "pandas", "scikit-learn", "openpyxl", "kditransform"]},
        "baseline_versions": original["versions"], "coverage": coverage, "folds": original["folds"],
        "n_events": len(events), "n_positive": sum(event["outcome"] for event in events),
        "scores": score(events), "fold_scores": {str(f): score([event for event in events if event["fold"] == f]) for f in range(3)},
        "constructor_seconds": constructor_seconds, "timings": timings, "elapsed_seconds": time.perf_counter() - started,
        "resources": {"peak_cuda_allocated_bytes": torch.cuda.max_memory_allocated(), "peak_cuda_reserved_bytes": torch.cuda.max_memory_reserved(), "peak_process_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024, "min_available_ram_bytes": min(h["available_ram_bytes"] for h in headroom), "min_free_gpu_bytes": min(h["free_gpu_bytes"] for h in headroom)},
        "events": events,
        "limitations": original["limitations"] + ["Exploratory already-seen cohort, not untouched confirmation", "Different native ensemble sizes and preprocessing; not an equal-compute architecture comparison", "LimiX preprocessing uses training and the single contemporaneous query covariates", "Non-commercial capability comparison only; no commercial reuse or competing-model training"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"scores": result["scores"], "resources": result["resources"], "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
