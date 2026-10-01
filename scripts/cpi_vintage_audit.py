"""Audit RTDSM CPI workbooks without relabeling derived values as BLS prints.

Input downloads and metadata are frozen under data/research/cpi/rtdsm.
Monthly units are recovered from annualized discrete-compounding growth rates.
"""
from __future__ import annotations

import argparse
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
import math
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data/research/cpi/rtdsm"


def monthly_proxy(value: float) -> float | None:
    if pd.isna(value):
        return None
    if not math.isfinite(value) or value <= -100:
        raise ValueError(f"Invalid annualized CPI growth value: {value}")
    return 100 * math.expm1(math.log1p(value / 100) / 12)


def rounded_proxy(value: float | None) -> float | None:
    if value is None or pd.isna(value):
        return None
    return float(Decimal(str(value)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_INPUT / "vintage_audit.json")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Refusing to overwrite an existing vintage audit; choose a new --output")
    sources = json.loads((args.input_dir / "sources.json").read_text())
    source_by_name = {source["name"]: source for source in sources}
    frames = []
    coverage = {}
    for name in ["headline", "core"]:
        path = args.input_dir / f"{name}.xlsx"
        content_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        assert content_hash == source_by_name[name]["sha256"]
        notes = pd.read_excel(path, sheet_name="NOTES", header=None).iloc[:, 0].dropna().astype(str)
        assert any("M/M Growth (Annual Rate, Percentage Points)" in line for line in notes)
        updated = [line for line in notes if "Last updated on:" in line]
        frame = pd.read_excel(path, sheet_name="DATA", header=4)
        assert {"Date", "First", "Most_Recent"}.issubset(frame.columns)
        frame["reference_month"] = frame["Date"].str.replace(":", "-", regex=False)
        periods = pd.PeriodIndex(frame["reference_month"], freq="M")
        assert periods.is_unique and periods.is_monotonic_increasing
        selected = pd.DataFrame({"reference_month": frame["reference_month"]})
        for column, suffix in [("First", "first"), ("Most_Recent", "recent")]:
            values = pd.to_numeric(frame[column], errors="raise")
            selected[f"{name}_{suffix}_annualized_pct"] = values
            monthly = values.map(monthly_proxy)
            selected[f"{name}_{suffix}_derived_mom_pct"] = monthly
            selected[f"{name}_{suffix}_rounded_mom_proxy"] = monthly.map(rounded_proxy)
        scope = selected.loc[selected["reference_month"] >= "2000-01"]
        first = scope[f"{name}_first_rounded_mom_proxy"]
        recent = scope[f"{name}_recent_rounded_mom_proxy"]
        pairs = first.notna() & recent.notna()
        changed = pairs & (first != recent)
        threshold_changed = pairs & ((first > 0.3) != (recent > 0.3))
        coverage[name] = {
            "source_sha256": content_hash, "source_last_updated_note": updated,
            "reference_month_min": selected["reference_month"].min(),
            "reference_month_max": selected["reference_month"].max(),
            "n_months": len(selected), "n_scope_months_since_2000": len(scope),
            "n_scope_first_values": int(first.notna().sum()),
            "missing_first_months_since_2000": scope.loc[first.isna(), "reference_month"].tolist(),
            "n_first_recent_pairs_since_2000": int(pairs.sum()),
            "n_rounded_proxy_revisions_since_2000": int(changed.sum()),
            "n_strict_above_0_3_proxy_label_revisions_since_2000": int(threshold_changed.sum()),
            "revision_examples": json.loads(scope.loc[changed].iloc[:10].to_json(orient="records")),
        }
        frames.append(selected)
    combined = frames[0].merge(frames[1], on="reference_month", how="outer", validate="one_to_one").sort_values("reference_month")
    result = {
        "kind": "vintage_derived_proxies_not_original_BLS_prints",
        "monthly_conversion": "100 * expm1(log1p(annualized_pct / 100) / 12)",
        "rounding": "Decimal ROUND_HALF_UP to 0.1 percentage point; candidate proxy only",
        "availability": "No exact release timestamps supplied by these workbooks; join independently verified BLS availability before model use",
        "sources": sources, "coverage": coverage,
        "rows": json.loads(combined.to_json(orient="records", double_precision=15)),
        "limitations": ["First values are derived from historical vintage levels, not literal press-release quotations", "Monthly vintages and subsequent archive corrections do not certify an exact real-time feature history", "Most_Recent values are revised outcomes and not permitted replacements for First", "Annualized source rounding and index precision may disagree with BLS published one-decimal prints", "Missing months remain missing; no forward-fill or latest-vintage substitution"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"coverage": coverage, "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
