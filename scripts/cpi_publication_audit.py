"""Audit CPI correction and prior-announced schedule evidence without network access.

Archived official text plus independent RTDSM First corroboration permits a bounded
statistical experiment, not independent first-byte or immutable-snapshot certification.
No missing calendar month is skipped when looking for the announcing release.
"""
from __future__ import annotations

import argparse
import calendar
from collections import Counter
from datetime import datetime, time, timedelta, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
from zoneinfo import ZoneInfo

import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar

from cpi_bls_archive import text_of

ET = ZoneInfo("America/New_York")
MONTHS = {name.lower(): n for n, name in enumerate(calendar.month_name) if name}
MONTH_PATTERN = "|".join(calendar.month_name[1:])
WEEK_PATTERN = "|".join(calendar.day_name)
SCHEDULE = re.compile(
    r"Consumer Price Index(?:\s+(?:data|news release))?\s+for\s+"
    r"(?P<reference>" + MONTH_PATTERN + r")(?:\s+(?P<reference_year>\d{4}))?\s+"
    r"(?:is|are)\s+scheduled\s+(?:for release|to be released|to be published)\s+on\s+"
    r"(?:(?P<weekday>" + WEEK_PATTERN + r"),?\s+)?"
    r"(?P<month>" + MONTH_PATTERN + r")\s+(?P<day>\d{1,2}),?\s+"
    r"(?:(?P<year>\d{4}),?\s+)?at\s+(?P<hour>\d{1,2}):(?P<minute>\d{2})\s*"
    r"(?P<meridiem>[ap]\.?m\.?)\s*\((?P<tz>ET|EST|EDT)\)", re.I,
)
REISSUE = re.compile(
    r"reissued on\s+(?:(?P<weekday>" + WEEK_PATTERN + r"),?\s+)?"
    r"(?P<month>" + MONTH_PATTERN + r")\s+(?P<day>\d{1,2}),?\s+(?P<year>\d{4})", re.I,
)
ASSUMPTIONS = [
    "Archived official headline quotations and next-release announcements are retained original prose unless evidence says otherwise; acquisition in 2026 is not historical availability.",
    "Stated embargo clocks proxy label and announcing-release availability; actual first HTTP byte and immutable first snapshots are not certified.",
    "RTDSM First one-decimal derived MoM agreement independently corroborates a quotation, but is neither a literal BLS print nor a timestamped feature vintage.",
    "Correction notices explicitly preserving release text support the headline quotation, not unchanged tables; All-items 2016 errors require First corroboration, not corrected database substitution.",
    "ET denotes America/New_York; explicit EST/EDT must agree with the zone on the stated date. An omitted announcement year is derived only from its explicit reference year and release-month rollover.",
    "Cutoff uses previous federal business day 16:00 ET plus four documented national-mourning closures. This is a bounded calendar convention, not exhaustive historical or exchange-calendar certification.",
    "For two shutdown-delayed queries, dated Reuters/Dow Jones reports of official rescheduling are secondary corroboration, not primary official notices. Assume selected passages were present on the stated publication dates despite later page modifications; bound unknown publication time by publication-date plus two days UTC. Revised release time is inherited from the prior official announcement unless independently stated.",
    "Bind the next-release announcement through the immediately prior calendar-month release, preserving its literal reference-month wording even if inconsistent. When wording disagrees, a unique explicitly announced date/time matching the actual embargo supports bounded schedule knowledge; this does not correct or certify the erroneous prose.",
]
LIMITATIONS = [
    "No independent first-byte or immutable first-release snapshot certification; strict PIT certification remains false.",
    "Federal holiday implementation plus four mourning orders does not prove absence of every exceptional closure; government shutdown rescheduling is checked separately.",
    "Two required shutdown-rescheduled queries rely on secondary dated articles, whose original publication bytes and actual posting clocks are uncertified; excerpts are hashed selected reader responses, not original HTML.",
    "No survey/forecast/market clock certification and no model inference or scores in this audit.",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def normalized(text: str) -> str:
    # Remove extraction markup, never repair words or OCR prose.
    return re.sub(r"\s+", " ", text.replace("**", "").replace("__", "").replace("#", ""))


def previous_month(month: str) -> str:
    year, number = map(int, month.split("-"))
    return f"{year - (number == 1):04d}-{12 if number == 1 else number - 1:02d}"


def cutoff(release: str, closed: set) -> str:
    day = datetime.fromisoformat(release).astimezone(ET).date() - timedelta(days=1)
    while day.weekday() >= 5 or day in closed:
        day -= timedelta(days=1)
    return datetime.combine(day, time(16), ET).astimezone(timezone.utc).isoformat()


def evidence(row: dict, archive: str) -> dict:
    return {"archive": archive, **{key: row.get(key) for key in (
        "source_url", "source_sha256", "retrieved_at_utc", "cache_path", "representation",
        "raw_pdf_sha256", "raw_pdf_cache_path", "extraction_tool",
    )}}


def announcements(text: str, month: str, row: dict, archive: str) -> list[dict]:
    result = []
    for match in SCHEDULE.finditer(normalized(text)):
        parts = match.groupdict()
        assumed = []
        reference_year = parts["reference_year"]
        if reference_year is None:
            expected = str(pd.Period(month, freq="M") + 1)
            if MONTHS[parts["reference"].lower()] == int(expected[5:]):
                reference_year = expected[:4]
                assumed.append("Reference year omitted; announcing release's next calendar-month year used.")
            elif parts["year"] is not None:
                reference_year = int(parts["year"]) - (MONTHS[parts["reference"].lower()] > MONTHS[parts["month"].lower()])
                assumed.append("Reference year omitted and reference-month wording differs from next calendar month; year attached from explicitly announced release year with month rollover, wording retained.")
            else:
                # No independent date-year basis for conflicting month wording.
                continue
        announced_reference = f"{int(reference_year):04d}-{MONTHS[parts['reference'].lower()]:02d}"
        year = parts["year"]
        if year is None:
            year = int(reference_year) + (MONTHS[parts["month"].lower()] < MONTHS[parts["reference"].lower()])
            assumed.append("Release year omitted; explicit announced reference year plus release-month rollover used.")
        hour = int(parts["hour"])
        if not 1 <= hour <= 12:
            raise ValueError(f"Invalid announced hour in {match[0]}")
        hour = hour % 12 + (12 if parts["meridiem"].lower().startswith("p") else 0)
        local = datetime(int(year), MONTHS[parts["month"].lower()], int(parts["day"]), hour, int(parts["minute"]), tzinfo=ET)
        weekday_valid = parts["weekday"] is None or parts["weekday"].lower() == calendar.day_name[local.weekday()].lower()
        timezone_valid = parts["tz"].upper() == "ET" or parts["tz"].upper() == local.tzname()
        result.append({
            "announcing_reference_month": month, "announced_reference_month": announced_reference,
            "announced_reference_month_name_literal": parts["reference"],
            "announced_at_utc": local.astimezone(timezone.utc).isoformat(),
            "announced_at_local": local.isoformat(), "stated_timezone": parts["tz"],
            "stated_weekday": parts["weekday"], "weekday_valid": weekday_valid,
            "timezone_valid": timezone_valid, "excerpt": match[0],
            "excerpt_representation": "Exact quotation after whitespace and extraction-markup normalization; no prose repair",
            "assumptions": assumed, "evidence": evidence(row, archive),
        })
    return result


def correction(row: dict, event: dict, archive: str, vintage: dict) -> dict | None:
    notice = row.get("correction_notice")
    if not notice:
        return None
    lower = notice.lower()
    unchanged = "no changes made to the text" in lower
    affects_all = "affected the u.s. all items index" in lower
    table_all = "all items" in lower and not affects_all
    parsed = REISSUE.search(notice)
    reissued = None
    weekday_valid = None
    if parsed:
        p = parsed.groupdict()
        dt = datetime(int(p["year"]), MONTHS[p["month"].lower()], int(p["day"]))
        reissued = dt.date().isoformat()
        weekday_valid = p["weekday"] is None or p["weekday"].lower() == calendar.day_name[dt.weekday()].lower()
    proxy = vintage.get("headline_first_rounded_mom_proxy")
    value = event.get("target_value_initial")
    agreement = None if proxy is None or value is None else Decimal(str(proxy)) == Decimal(str(value))
    if affects_all:
        classification = "all_items_index_error_original_headline_corroborated" if agreement else "all_items_error_unresolved"
        assessment = "Notice identifies erroneous original prescription-drug indexes affecting All items. Retain archived headline, corroborated by RTDSM First; corrected database data are not replacements. Actual first snapshot and append time uncertified."
    elif unchanged:
        classification = "tables_corrected_release_prose_explicitly_unchanged"
        assessment = "Notice expressly says release text was unchanged; table corrections do not authorize replacing the headline quotation."
    elif "inpatient hospital services" in lower:
        classification = "inpatient_hospital_series_removed_not_headline"
        assessment = "Reissue removes inpatient hospital services data in tables2/6/7; it does not state a headline All-items prose correction. RTDSM First corroborates headline; intra-day reissue clock is unknown."
    else:
        classification = "unresolved_notice"
        assessment = "Correction scope not adjudicated by supported source text; label excluded under bounded assumptions."
    return {
        "reference_month": row["reference_month"], "exact_correction_notice": notice,
        "reissued_on": reissued, "reissue_weekday_valid": weekday_valid,
        "notice_posted_on": None, "errata_url_date_hint": "2016-10-18" if "cpi-price-corrections-10182016" in lower else None,
        "date_hint_is_certified_notice_clock": False, "prose_explicitly_unchanged": unchanged,
        "affects_all_items_index": affects_all, "mentions_all_items_table": table_all,
        "classification": classification, "assessment": assessment,
        "rtdsm_first_rounded_mom_proxy": proxy, "rtdsm_first_matches_archived_headline": agreement,
        "archival_first_snapshot_uncertified": True, "independent_first_byte_certification": False,
        "label_acceptable_under_bounded_assumptions": classification != "unresolved_notice" and (agreement is True if affects_all else agreement is not False),
        "evidence": evidence(row, archive),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("data/research/cpi"))
    parser.add_argument("--output", type=Path, default=Path("data/research/cpi/publication/audit"))
    args = parser.parse_args()
    if args.output.exists():
        parser.error(f"Refusing to overwrite {args.output}; choose a fresh --output")
    root = args.root
    publication = root / "publication"
    input_paths = [root / name for name in (
        "events/events.jsonl", "bls/manifest.jsonl", "bls/labels.jsonl",
        "fraser/manifest.jsonl", "fraser/labels.jsonl", "rtdsm/vintage_audit.json",
        "publication/sources.jsonl", "publication/closures.json", "publication/acquisition.json",
        "publication/reschedule_gaps.json",
    )]
    secondary_path = publication / "parent_reschedule_corroboration.json"
    secondary = json.loads(secondary_path.read_text()) if secondary_path.exists() else []
    if secondary_path.exists():
        input_paths.append(secondary_path)
    for item in secondary:
        if hashlib.sha256(item["excerpt"].encode()).hexdigest() != item["source_sha256"]:
            raise ValueError(f"Secondary excerpt hash mismatch: {item['source_url']}")
    input_hashes = {str(path): digest(path) for path in input_paths}
    events = jsonl(root / "events/events.jsonl")
    if len(events) != 321 or len({e["reference_month"] for e in events}) != 321:
        raise ValueError("Expected unique frozen321-month calendar")
    vintage = json.loads((root / "rtdsm/vintage_audit.json").read_text())
    vintages = {r["reference_month"]: r for r in vintage["rows"]}
    labels = {name: jsonl(root / name / "labels.jsonl") for name in ("bls", "fraser")}
    labels["publication"] = jsonl(publication / "sources.jsonl")
    by_month = {e["reference_month"]: e for e in events}
    schedules = {}
    corrections = []
    source_hashes = {}
    for archive, rows in labels.items():
        for row in rows:
            if row.get("parse_status") not in (None, "parsed") or row.get("acquisition_status") == "failed":
                continue
            path = root / archive / row["cache_path"]
            actual_hash = digest(path)
            if actual_hash != row["source_sha256"]:
                raise ValueError(f"Source hash mismatch: {path}")
            source_hashes[str(path)] = actual_hash
            if row.get("raw_pdf_cache_path"):
                base = root if row.get("raw_pdf_path_base") == "cpi_root" else root / archive
                raw_path = base / row["raw_pdf_cache_path"]
                raw_hash = digest(raw_path)
                if raw_hash != row["raw_pdf_sha256"]:
                    raise ValueError(f"Raw PDF hash mismatch: {raw_path}")
                source_hashes[str(raw_path)] = raw_hash
            text = text_of(path.read_bytes())
            for announcement in announcements(text, row["reference_month"], row, archive):
                schedules.setdefault(row["reference_month"], []).append(announcement)
            item = correction(row, by_month[row["reference_month"]], archive, vintages.get(row["reference_month"], {}))
            if item and normalized(item["exact_correction_notice"]) not in normalized(text):
                raise ValueError(f"Retained correction notice absent from source: {path}")
            if item and not any(c["reference_month"] == item["reference_month"] and c["exact_correction_notice"] == item["exact_correction_notice"] for c in corrections):
                corrections.append(item)
    closure_document = json.loads((publication / "closures.json").read_text())
    closures = closure_document["sources"]
    for closure in closures:
        path = publication / closure["cache_path"]
        if digest(path) != closure["source_sha256"]:
            raise ValueError(f"Closure source hash mismatch: {path}")
        source_hashes[str(path)] = closure["source_sha256"]
    ordinary = set(USFederalHolidayCalendar().holidays(start="1999-01-01", end="2027-12-31").date)
    closed = ordinary | {datetime.fromisoformat(c["closure_date"]).date() for c in closures}
    correction_by_month = {}
    for item in corrections:
        correction_by_month.setdefault(item["reference_month"], []).append(item)
    output_rows = []
    schedule_conflicts = []
    agreements = []
    gaps = []
    for event in sorted(events, key=lambda e: e["reference_month"]):
        month = event["reference_month"]
        prior_month = previous_month(month)
        prior = by_month.get(prior_month)
        candidates = list(schedules.get(prior_month, []))
        unique_clocks = sorted({a["announced_at_utc"] for a in candidates})
        if len(unique_clocks) > 1:
            schedule_conflicts.append({"reference_month": month, "announced_clocks": unique_clocks, "evidence": candidates})
        chosen = candidates[0] if candidates else None
        release = event.get("release_at_utc")
        nominal_cutoff = event.get("cutoff_at_utc")
        audited_cutoff = cutoff(release, closed) if release else None
        cutoff_changed = bool(nominal_cutoff and audited_cutoff != nominal_cutoff)
        availability = prior.get("release_at_utc") if prior else None
        known = None
        reasons = []
        if chosen:
            chosen = dict(chosen, schedule_available_at_utc=availability,
                          availability_basis="Stated embargo of prior calendar-month announcing release; historical posting/first snapshot uncertified",
                          independent_first_byte_certification=False)
        reference_wording_matches = None if not chosen else chosen["announced_reference_month"] == month
        match = None if not chosen or not release else chosen["announced_at_utc"] == release
        corroboration = []
        effective_announcement = chosen["announced_at_utc"] if chosen else None
        schedule_status = ("prior_calendar_month_announcement" if reference_wording_matches else "prior_calendar_month_date_with_reference_wording_mismatch") if chosen else "missing_prior_calendar_month_announcement"
        if not candidates:
            reasons.append("No complete next-release announcement from immediately prior calendar month; absent months never skipped.")
        elif len(unique_clocks) != 1:
            known = False
            reasons.append("Conflicting archived announced clocks.")
        elif not chosen["weekday_valid"] or not chosen["timezone_valid"]:
            known = False
            reasons.append("Announced weekday/timezone fails calendar validation.")
        elif match is False:
            known = False
            for item in secondary:
                if item["reference_month"] != month:
                    continue
                date_bound = datetime.fromisoformat(item["published_date"]).replace(tzinfo=timezone.utc) + timedelta(days=2)
                original_local = datetime.fromisoformat(chosen["announced_at_local"])
                revised_date = datetime.fromisoformat(item["announced_release_date"]).date()
                revised = datetime.combine(revised_date, original_local.timetz()).astimezone(timezone.utc)
                before = bool(audited_cutoff and date_bound < datetime.fromisoformat(audited_cutoff))
                if revised.isoformat() == release and before:
                    corroboration.append(dict(item, publication_availability_upper_bound_at_utc=date_bound.isoformat(),
                                              availability_bound_is_assumption=True,
                                              effective_announced_at_utc=revised.isoformat(),
                                              release_time_assumption="Prior official announced8:30ET clock retained; revised date stated by secondary report",
                                              known_before_cutoff_under_assumptions=True))
            if corroboration:
                known = True
                effective_announcement = corroboration[0]["effective_announced_at_utc"]
                schedule_status = "secondary_schedule_corroborated"
            else:
                schedule_status = "unresolved_rescheduled_release"
                reasons.append("Prior announced date differs from actual embargo; no acceptable dated before-cutoff rescheduling corroboration.")
        elif not release:
            reasons.append("Target has no actual embargo/released label; announcement alone is not a release.")
        elif not availability or not audited_cutoff:
            reasons.append("Announcing release availability or target cutoff unavailable.")
        else:
            known = datetime.fromisoformat(availability) < datetime.fromisoformat(audited_cutoff)
            if not known:
                reasons.append("Announcing release not available before cutoff under stated clock.")
        notices = correction_by_month.get(month, [])
        label_ok = event["parse_status"] == "parsed" and event.get("rtdsm_proxy_matches_print") is not False and all(c["label_acceptable_under_bounded_assumptions"] for c in notices)
        lag_ok = bool(event.get("complete_lag_context"))
        if not label_ok:
            reasons.append("Target missing/future, proxy disagreement, or unresolved correction scope.")
        if not lag_ok:
            reasons.append("One or more frozen calendar lags1/2/3/12 unavailable before retained cutoff.")
        if cutoff_changed:
            reasons.append("Documented exceptional closure changes frozen cutoff; cohort requires explicit adjudication.")
        lag_notice_ok = all(all(c["label_acceptable_under_bounded_assumptions"] for c in correction_by_month.get(lag["reference_month"], [])) for lag in event.get("lags", {}).values())
        eligible = label_ok and lag_ok and lag_notice_ok and known is True and not cutoff_changed
        query_required = "2005-01" <= month <= "2026-08" and event["parse_status"] == "parsed" and lag_ok
        if match is True:
            agreements.append({"reference_month": month, "announced_at_utc": chosen["announced_at_utc"], "actual_at_utc": release})
        if reasons:
            gaps.append({"reference_month": month, "required_frozen_query": query_required, "reasons": reasons})
        row = {
            "reference_month": month, "parse_status": event["parse_status"], "target_value_initial": event.get("target_value_initial"),
            "actual_embargo_at_utc": release, "retained_cutoff_at_utc": nominal_cutoff, "audited_cutoff_at_utc": audited_cutoff,
            "cutoff_changed_by_documented_closures": cutoff_changed, "announcing_reference_month": prior_month,
            "schedule": chosen, "schedule_evidence_all": candidates, "announced_matches_actual_embargo": match,
            "schedule_known_before_cutoff": known, "schedule_known_at_cutoff_certified": False,
            "schedule_status": schedule_status, "effective_announced_at_utc": effective_announcement,
            "reschedule_corroboration": corroboration,
            "announced_reference_wording_matches_target": reference_wording_matches,
            "corrections": notices, "rtdsm_first_matches_print": event.get("rtdsm_proxy_matches_print"),
            "model_input_eligible": label_ok, "model_query_eligible": eligible,
            "required_frozen_query": query_required, "complete_lag_context": lag_ok,
            "source_clock_certainty": "stated_embargo_and_archived_prose_only" if release else "no_actual_release_clock",
            "archive_snapshot_certified": False, "independent_first_byte_certification": False,
            "strict_pit_eligible": False, "statistical_archive_evidence_acceptable": eligible,
            "label_evidence": {key: event.get(key) for key in ("source_url", "source_sha256", "retrieved_at_utc", "extraction_evidence", "availability_basis")},
            "assumptions": ASSUMPTIONS, "evidence_gaps": reasons,
        }
        output_rows.append(row)
    required = [r for r in output_rows if r["required_frozen_query"]]
    blocked = [r for r in required if not r["model_query_eligible"]]
    period_counts = {}
    for name, first, last, frozen in (("warmup_predictions", "2005-01", "2009-12", 60), ("development", "2010-01", "2019-12", 120), ("confirmation", "2020-01", "2026-08", 75)):
        cohort = [r for r in required if first <= r["reference_month"] <= last]
        period_counts[name] = {"frozen_expected": frozen, "required_queries": len(cohort), "bounded_evidence_eligible": sum(r["model_query_eligible"] for r in cohort), "blocked_months": [r["reference_month"] for r in cohort if not r["model_query_eligible"]]}
    required_months = {r["reference_month"] for r in required}
    required_conflicts = [c for c in schedule_conflicts if c["reference_month"] in required_months]
    permitted = len(required) == 255 and not blocked and not required_conflicts
    summary = {
        "calendar_rows": len(output_rows), "exact_prints": sum(r["parse_status"] == "parsed" for r in output_rows),
        "event_table_sha256": input_hashes[str(root / "events/events.jsonl")],
        "audit_script_sha256": digest(Path(__file__)),
        "model_input_eligible_labels": sum(r["model_input_eligible"] for r in output_rows),
        "rtdsm_first_proxy_comparisons": sum(r["rtdsm_first_matches_print"] is not None for r in output_rows),
        "rtdsm_first_proxy_disagreements": [r["reference_month"] for r in output_rows if r["rtdsm_first_matches_print"] is False],
        "parsed_labels_without_first_proxy": [r["reference_month"] for r in output_rows if r["parse_status"] == "parsed" and r["rtdsm_first_matches_print"] is None],
        "correction_notices": len(corrections), "correction_classification_counts": dict(Counter(c["classification"] for c in corrections)),
        "correction_first_proxy_agreements": sum(c["rtdsm_first_matches_archived_headline"] is True for c in corrections),
        "announcing_months_with_complete_announcements": len(schedules), "announced_actual_agreements": len(agreements),
        "announced_actual_disagreements": [{"reference_month": r["reference_month"], "announced_at_utc": r["schedule"]["announced_at_utc"], "actual_at_utc": r["actual_embargo_at_utc"], "required_frozen_query": r["required_frozen_query"]} for r in output_rows if r["announced_matches_actual_embargo"] is False],
        "schedule_known_before_cutoff_under_assumptions": sum(r["schedule_known_before_cutoff"] is True for r in output_rows),
        "secondary_schedule_corroborated_events": [r["reference_month"] for r in output_rows if r["schedule_status"] == "secondary_schedule_corroborated"],
        "reference_wording_disagreements": [{"reference_month": r["reference_month"], "literal_announced_reference_month": r["schedule"]["announced_reference_month"], "announced_at_utc": r["schedule"]["announced_at_utc"], "actual_at_utc": r["actual_embargo_at_utc"], "assumption": "Prior-calendar-month announcement's validated explicit date/time, not corrected month wording, binds event"} for r in output_rows if r["announced_reference_wording_matches_target"] is False],
        "source_schedule_conflicts": schedule_conflicts, "required_frozen_queries": len(required),
        "bounded_query_eligible": sum(r["model_query_eligible"] for r in output_rows), "period_counts": period_counts,
        "required_query_gaps": [{"reference_month": r["reference_month"], "reasons": r["evidence_gaps"]} for r in blocked],
        "strict_pit_certified_events": 0, "independent_first_byte_certification": False,
        "documented_closure_cutoff_changes": [r["reference_month"] for r in output_rows if r["cutoff_changed_by_documented_closures"]],
        "closures": closure_document, "assumptions": ASSUMPTIONS, "limitations": LIMITATIONS,
        "model_run_gate": {"permitted": permitted, "reason": "Full frozen255-query cohort covered under explicit bounded archival assumptions; not strict PIT certification." if permitted else "Full frozen cohort blocked by listed required-query schedule/correction/calendar gaps; do not silently exclude dates or call narrowed counts120/75.", "limitations": LIMITATIONS, "safe_query_months": [r["reference_month"] for r in required if r["model_query_eligible"]]},
        "input_sha256": input_hashes, "source_sha256": source_hashes,
        "acquisition": json.loads((publication / "acquisition.json").read_text()),
        "reschedule_evidence_search": json.loads((publication / "reschedule_gaps.json").read_text()),
    }
    args.output.mkdir(parents=True)
    for name, rows in (("events", output_rows), ("corrections", corrections), ("agreements", agreements), ("gaps", gaps)):
        (args.output / f"{name}.jsonl").write_text("".join(json.dumps(row, sort_keys=True, allow_nan=False) + "\n" for row in rows))
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({key: summary[key] for key in ("calendar_rows", "correction_notices", "period_counts", "required_query_gaps", "model_run_gate")}, indent=2))


if __name__ == "__main__":
    main()
