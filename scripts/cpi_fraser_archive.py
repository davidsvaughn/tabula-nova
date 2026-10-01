"""Parse cached original BLS releases hosted by the St. Louis Fed's FRASER.

Reader acquisition saves bounded PDF-extracted text with its own source hash,
not raw PDF-byte provenance. BLS index linkage verifies filename/date/reference
month; source_url remains the actual FRASER document URL.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import re
from pathlib import Path

from cpi_bls_archive import extract, text_of

DEFAULT_ROOT = Path("data/research/cpi/fraser")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args()
    manifest_path = args.root / "manifest.jsonl"
    records = [json.loads(line) for line in manifest_path.read_text().splitlines()]
    rows = []
    for record in records:
        path = args.root / record["cache_path"]
        body = path.read_bytes()
        assert hashlib.sha256(body).hexdigest() == record["source_sha256"]
        row = {key: record[key] for key in ["reference_month", "source_url", "source_sha256", "retrieved_at_utc", "cache_path", "index_bls_url", "representation"]}
        for key in ("raw_pdf_sha256", "raw_pdf_cache_path", "raw_pdf_http_status", "extraction_tool", "fraser_item_url"):
            if key in record:
                row[key] = record[key]
        if "raw_pdf_cache_path" in record:
            assert hashlib.sha256((args.root / record["raw_pdf_cache_path"]).read_bytes()).hexdigest() == record["raw_pdf_sha256"]
        row.update(target_value_initial=None, release_at_utc=None, label_available_at_utc=None, acquisition_method="fraser_archived_pdf_extract")
        if record["acquisition_status"] != "success":
            row.update(parse_status="acquisition_failed", reason=record["reason"])
        else:
            try:
                text = text_of(body).replace("**", "").replace("__", "")
                correction = re.search(r"\(NOTE:.*?(?:release\.|database\.)\s*\)", re.sub(r"\s+", " ", text), re.I)
                row["correction_notice"] = correction[0] if correction else None
                row["snapshot_certification"] = "Archived publication; no independent first-release capture. Correction notice retained when present."
                row.update(extract(text, row["reference_month"], row["index_bls_url"]))
            except ValueError as error:
                row.update(parse_status="unparsed", reason=str(error))
        rows.append(row)
    assert len({row["reference_month"] for row in rows}) == len(rows)
    (args.root / "labels.jsonl").write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in sorted(rows, key=lambda r: r["reference_month"])))
    summary = {"n_attempts": len(rows), "status_counts": dict(Counter(row["parse_status"] for row in rows)), "parse_failures": [{"reference_month": row["reference_month"], "reason": row["reason"]} for row in rows if row["parse_status"] != "parsed"], "representation_counts": dict(Counter(row["representation"] for row in rows)), "raw_pdfs_hashed": sum("raw_pdf_sha256" in row for row in rows), "archive": "Federal Reserve Bank of St. Louis FRASER original BLS documents"}
    (args.root / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
