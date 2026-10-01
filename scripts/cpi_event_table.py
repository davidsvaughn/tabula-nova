"""Join archived CPI prints, dated nowcasts and vendor outcomes without filling targets.

Offline coverage audit, not a certified point-in-time model benchmark. The federal
calendar is a reproducible convention, not an exchange/exceptional-closure calendar.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, time, timedelta, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar

ET = ZoneInfo("America/New_York")


def jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines()]


def previous_cutoff(release: str, holidays: set) -> datetime:
    day = datetime.fromisoformat(release).astimezone(ET).date() - timedelta(days=1)
    while day.weekday() >= 5 or day in holidays:
        day -= timedelta(days=1)
    return datetime.combine(day, time(16), ET).astimezone(timezone.utc)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("data/research/cpi"))
    parser.add_argument("--output", type=Path, default=Path("data/research/cpi/events"))
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"Refusing to overwrite {args.output}; choose a fresh --output")
    base = jsonl(args.root / "bls/labels.jsonl")
    alternate = {row["reference_month"]: row for row in jsonl(args.root / "fraser/labels.jsonl")}
    labels = {}
    for row in base:
        other = alternate.get(row["reference_month"])
        if row["parse_status"] == "parsed" and other and other["parse_status"] == "parsed":
            assert Decimal(row["target_value_initial"]) == Decimal(other["target_value_initial"])
        selected = other if row["parse_status"] != "parsed" and other and other["parse_status"] == "parsed" else row
        labels[row["reference_month"]] = dict(selected, bls_acquisition_status=row["parse_status"], archive_snapshot_certified=False)
    assert len(labels) == len(base)
    vintage = json.loads((args.root / "rtdsm/vintage_audit.json").read_text())
    vintage_rows = {row["reference_month"]: row for row in vintage["rows"]}
    vendors = {row["reference_month"]: row for row in jsonl(args.root / "forecasts/candidate_labels.jsonl")}
    forecasts = pd.read_csv(args.root / "forecasts/cleveland/forecasts.csv", dtype={"reference_month": str, "forecast_date": str})
    assert not forecasts.duplicated(["reference_month", "forecast_date"]).any()
    holidays = set(USFederalHolidayCalendar().holidays(start="1999-01-01", end="2027-12-31").date)
    events = []
    for month, label in sorted(labels.items()):
        row = dict(label)
        release = row["release_at_utc"]
        cutoff = previous_cutoff(release, holidays) if release else None
        row["cutoff_at_utc"] = cutoff.isoformat() if cutoff else None
        row["cutoff_calendar"] = f"pandas {pd.__version__} USFederalHolidayCalendar, previous federal business day 16:00 America/New_York"
        row["schedule_known_at_cutoff_certified"] = False
        row["strict_pit_eligible"] = False
        row["lags"] = {}
        for lag in (1, 2, 3, 12):
            previous_month = str(pd.Period(month, freq="M") - lag)
            prior = labels.get(previous_month)
            available = prior and prior.get("label_available_at_utc")
            usable = bool(cutoff and available and datetime.fromisoformat(available) < cutoff and prior["parse_status"] == "parsed")
            row["lags"][str(lag)] = {"reference_month": previous_month, "value": prior["target_value_initial"] if usable else None, "available_at_utc": available, "source_sha256": prior.get("source_sha256") if prior else None, "usable_under_stated_release_clock": usable}
        row["complete_lag_context"] = all(value["usable_under_stated_release_clock"] for value in row["lags"].values())
        proxy = vintage_rows.get(month, {}).get("headline_first_rounded_mom_proxy")
        row["rtdsm_first_rounded_proxy"] = proxy
        row["rtdsm_proxy_matches_print"] = None if proxy is None or row["target_value_initial"] is None else Decimal(str(proxy)) == Decimal(row["target_value_initial"])
        vendor = vendors.get(month)
        row["kalshi_vendor_value"] = vendor["expiration_value"] if vendor else None
        row["kalshi_vendor_matches_print"] = None if not vendor or row["target_value_initial"] is None else Decimal(vendor["expiration_value"]) == Decimal(row["target_value_initial"])
        row["kalshi_candidate_eligible_as_official_label"] = False
        row["cleveland_candidate"] = None
        if cutoff:
            local_date = cutoff.astimezone(ET).date().isoformat()
            eligible = forecasts[(forecasts.reference_month == month) & (forecasts.forecast_date <= local_date)]
            if not eligible.empty:
                candidate = eligible.sort_values("forecast_date").iloc[-1]
                row["cleveland_candidate"] = {"forecast_date": candidate.forecast_date, "value_pct": float(candidate.forecast_cpi_mom_pct), "source_sha256": candidate.source_sha256, "publication_time_assumption": "FAQ around10am ET; actual timestamp unknown", "immutable_vintage_certified": False, "eligible_under_nominal_clock_only": True}
        events.append(row)
    exact = [row for row in events if row["parse_status"] == "parsed"]
    comparisons = [row for row in exact if row["rtdsm_proxy_matches_print"] is not None]
    market_comparisons = [row for row in exact if row["kalshi_vendor_matches_print"] is not None]
    summary = {
        "calendar_rows": len(events), "status_counts": dict(Counter(row["parse_status"] for row in events)),
        "exact_prints": len(exact), "complete_lag_context_exact_targets": sum(row["complete_lag_context"] for row in exact),
        "dated_cleveland_exact_target_overlap": sum(row["cleveland_candidate"] is not None for row in exact),
        "rtdsm_print_comparisons": len(comparisons), "rtdsm_proxy_mismatches": sum(not row["rtdsm_proxy_matches_print"] for row in comparisons),
        "rtdsm_strict_above_0_3_mismatches": sum((Decimal(str(row["rtdsm_first_rounded_proxy"])) > Decimal("0.3")) != (Decimal(row["target_value_initial"]) > Decimal("0.3")) for row in comparisons),
        "kalshi_print_comparisons": len(market_comparisons), "kalshi_vendor_mismatches": sum(not row["kalshi_vendor_matches_print"] for row in market_comparisons),
        "strict_pit_certified_events": 0, "strict_quote_age_certified_events": 0,
        "missing_or_future_months": [{"reference_month": row["reference_month"], "status": row["parse_status"], "vendor_value": row["kalshi_vendor_value"]} for row in events if row["parse_status"] != "parsed"],
        "limitations": ["Archived release text, not independently timestamped first-release snapshots", "Actual release dates known retrospectively; prior announced schedules not certified", "Cleveland dated history lacks immutable-vintage and actual posting-time assurance", "Federal calendar omits exceptional closures and historical-calendar verification", "No monthly survey consensus; no strict quote-age cohort; no model or scoring run"]
    }
    args.output.mkdir(parents=True)
    (args.output / "events.jsonl").write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in events))
    inputs = [args.root / name for name in ("bls/labels.jsonl", "fraser/labels.jsonl", "rtdsm/vintage_audit.json", "forecasts/candidate_labels.jsonl", "forecasts/cleveland/forecasts.csv")]
    summary["input_sha256"] = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs}
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
