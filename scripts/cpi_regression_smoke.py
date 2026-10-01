"""Exercise native regression without scoring or exposing a confirmation outcome."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from threadpoolctl import threadpool_limits

from cpi_model_runtime import ROOT, context, create_model, load_events, predict, resources, sha256


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=("tabpfn", "limix"), required=True)
    parser.add_argument("--model-path", type=Path)
    parser.add_argument("--events", type=Path, default=ROOT / "data/research/cpi/events/events.jsonl")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error(f"Refusing to overwrite {args.output}")
    rows = load_events(args.events)
    query = next(row for row in rows if row["reference_month"] == "2005-01")
    train, x, y, query_x = context(rows, query)
    with threadpool_limits(limits=4):
        model, metadata = create_model(args.model, args.model_path)
        value, timing = predict(args.model, model, x, y, query_x)
    result = {"purpose": "Actual warmup CPI single-query regression API/resource smoke; no model score or confirmation outcome", "protocol": "LOG-009; official native ensembles; single contemporaneous query", "event_table_sha256": sha256(args.events), "query_reference_month": query["reference_month"], "cutoff_at_utc": query["cutoff_at_utc"], "train_n": len(train), "train_reference_month_min": train[0]["reference_month"], "train_reference_month_max": train[-1]["reference_month"], "training_label_available_max": max(row["label_available_at_utc"] for row in train), "prediction_mom_pct": value, "model_metadata": metadata, "prediction_runtime": timing, "resources": resources(True)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps({key: result[key] for key in ("query_reference_month", "train_n", "prediction_mom_pct", "prediction_runtime", "resources")}, indent=2))


if __name__ == "__main__":
    main()
