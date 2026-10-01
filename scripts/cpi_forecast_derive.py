"""Reproduce consumed Cleveland forecasts and Kalshi vendor candidates offline.

Verify cached response bytes against the original acquisition provenance before
parsing. Never fetch sources, overwrite inputs, or promote vendor/chart values to
certified original BLS prints. Output must be a fresh directory.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import date
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data/research/cpi/forecasts"
HISTORICAL_PATH = "data/research/kalshi_cpi_probe.json"
CLEVELAND_PATH = "data/research/cpi/forecasts/cleveland/nowcast_month.json"
LIVE_PATH = "data/research/cpi/forecasts/kalshi/live_markets.json"
MONTH_NAMES = ("January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December")
MONTH_CODES = {name[:3].upper(): index for index, name in enumerate(MONTH_NAMES, 1)}
NUMBER = r"[+-]?(?:\d+(?:\.\d+)?|\.\d+)"
RULE_MONTH = re.compile(r"\bin (" + "|".join(MONTH_NAMES) + r")(?:,? (20\d{2}))?\b")
RULE_STRIKE = re.compile(r"\bmore than (" + NUMBER + r")%\s")
FORECAST_FIELDS = ("reference_month", "forecast_date", "raw_forecast_date_label",
                   "forecast_cpi_mom_pct", "source_sha256")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def unique_object(pairs: list[tuple]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise ValueError(f"Nonfinite JSON constant: {value}")


def load_json(content: bytes):
    return json.loads(content, object_pairs_hook=unique_object, parse_constant=reject_constant)


def numeric(value: str, context: str, percent: bool = False) -> Decimal:
    require(isinstance(value, str), f"Non-string numeric value in {context}: {value!r}")
    text = value.removesuffix("%") if percent else value
    require(re.fullmatch(NUMBER, text) is not None, f"Invalid numeric value in {context}: {value!r}")
    result = Decimal(text)
    require(result.is_finite(), f"Nonfinite numeric value in {context}")
    return result


def verified_sources(input_dir: Path, historical_probe: Path) -> tuple[dict, dict, str]:
    provenance_bytes = (input_dir / "provenance.json").read_bytes()
    provenance = load_json(provenance_bytes)
    paths = {CLEVELAND_PATH: input_dir / "cleveland/nowcast_month.json",
             LIVE_PATH: input_dir / "kalshi/live_markets.json",
             HISTORICAL_PATH: historical_probe}
    metadata, raw = {}, {}
    for recorded_path, actual_path in paths.items():
        matches = [row for row in provenance["sources"] if row.get("path") == recorded_path]
        require(len(matches) == 1, f"Expected one provenance record for {recorded_path}")
        record = matches[0]
        require(record.get("status") == 200, f"Unsuccessful recorded acquisition: {recorded_path}")
        content = actual_path.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        require(digest == record.get("sha256"), f"Source SHA256 mismatch: {actual_path}")
        require(len(content) == record.get("bytes"), f"Source byte-count mismatch: {actual_path}")
        require(bool(record.get("retrieved_at_utc")), f"Missing source retrieval clock: {recorded_path}")
        raw[recorded_path] = content
        metadata[recorded_path] = {key: record[key] for key in (
            "path", "sha256", "bytes", "retrieved_at_utc", "source_url",
            "route_from_prior_log", "route_provenance", "base_url_status", "reused_without_refetch"
        ) if key in record}
    require(metadata[HISTORICAL_PATH].get("source_url") is None,
            "Original historical probe URL was not observed; do not reconstruct it")
    # All three hashes must pass before any source response is parsed.
    return {key: load_json(content) for key, content in raw.items()}, metadata, hashlib.sha256(provenance_bytes).hexdigest()


def nearest_date(label: str, target: date) -> date:
    require(isinstance(label, str) and re.fullmatch(r"\d{2}/\d{2}", label) is not None,
            f"Invalid MM/DD chart category: {label!r}")
    month, day = map(int, label.split("/"))
    candidates = []
    for year in (target.year - 1, target.year, target.year + 1):
        try:
            candidates.append(date(year, month, day))
        except ValueError:
            continue
    require(bool(candidates), f"Invalid calendar date: {label!r}")
    distance = min(abs((candidate - target).days) for candidate in candidates)
    winners = [candidate for candidate in candidates if abs((candidate - target).days) == distance]
    require(len(winners) == 1, f"Ambiguous nearest year for {label!r} relative to {target}")
    return winners[0]


def cleveland_rows(charts: list, source: dict) -> tuple[list[dict], dict]:
    require(isinstance(charts, list) and bool(charts), "Expected nonempty Cleveland chart array")
    rows, coverage, months, keys = [], [], set(), set()
    discarded_markers = 0
    for chart in charts:
        caption = chart["chart"]["subcaption"]
        require(re.fullmatch(r"\d{4}-\d{1,2}", caption) is not None, f"Invalid chart target: {caption!r}")
        year, month = map(int, caption.split("-"))
        target = date(year, month, 1)
        reference = target.strftime("%Y-%m")
        require(reference not in months, f"Duplicate Cleveland target chart: {reference}")
        months.add(reference)
        require(chart["chart"].get("yaxisname") == "Month-over-month percent change",
                f"Wrong Cleveland units for {reference}")
        require(len(chart["categories"]) == 1, f"Ambiguous category axis for {reference}")
        categories = []
        for category in chart["categories"][0]["category"]:
            if "vline" in category:
                require(str(category["vline"]).lower() == "true", f"Unknown event marker for {reference}")
                discarded_markers += 1
            else:
                categories.append(category["label"])
        selected = [series for series in chart["dataset"] if series.get("seriesname") == "CPI Inflation"]
        require(len(selected) == 1, f"Expected exactly one CPI Inflation series for {reference}")
        for series in chart["dataset"]:
            require(len(series["data"]) == len(categories), f"Category/series alignment failure for {reference}: {series.get('seriesname')}")
        dates = [nearest_date(label, target) for label in categories]
        require(dates == sorted(set(dates)), f"Duplicate or nonmonotonic category dates for {reference}")
        month_rows = []
        for label, forecast_date, point in zip(categories, dates, selected[0]["data"]):
            tooltip = point.get("tooltext")
            require(isinstance(tooltip, str) and tooltip.split("{br}")[:2] == ["CPI Inflation", label],
                    f"Tooltip/category alignment failure for {reference}: {label}")
            value = point["value"]
            if value == "":
                continue
            numeric(value, f"Cleveland {reference} {label}")
            key = (reference, forecast_date.isoformat())
            require(key not in keys, f"Duplicate Cleveland forecast key: {key}")
            keys.add(key)
            month_rows.append(dict(zip(FORECAST_FIELDS, (reference, key[1], label, value, source["sha256"]))))
        rows.extend(month_rows)
        coverage.append({"reference_month": reference, "forecast_count": len(month_rows),
                         "first_forecast_date": month_rows[0]["forecast_date"] if month_rows else None,
                         "last_forecast_date": month_rows[-1]["forecast_date"] if month_rows else None})
    rows.sort(key=lambda row: (row["reference_month"], row["forecast_date"]))
    coverage.sort(key=lambda row: row["reference_month"])
    require(bool(rows), "No headline Cleveland forecasts")
    return rows, {"charts": len(charts), "chart_target_month_min": min(months),
                  "chart_target_month_max": max(months), "forecast_target_months": sum(bool(row["forecast_count"]) for row in coverage),
                  "headline_forecast_rows": len(rows), "first_forecast_date": min(row["forecast_date"] for row in rows),
                  "last_forecast_date": max(row["forecast_date"] for row in rows), "monthly_counts": coverage,
                  "discarded_event_marker_categories": discarded_markers, "duplicate_reference_date_rows": 0,
                  "date_alignment_failures": 0, "selected_series": "CPI Inflation",
                  "year_convention": "Calendar year nearest target-month first day; reject ties",
                  "actual_series_used_as_labels": False, "immutable_vintage_certified": False,
                  "actual_posting_time_certified": False, "source": source}


def event_month(ticker: str) -> tuple[str, int, int]:
    match = re.fullmatch(r"(?:KXCPI|CPI)-(\d{2})([A-Z]{3})", ticker)
    require(match is not None and match[2] in MONTH_CODES, f"Unknown CPI event ticker: {ticker!r}")
    year, month = 2000 + int(match[1]), MONTH_CODES[match[2]]
    return f"{year:04d}-{month:02d}", year, month


def kalshi_rows(probe: dict, live: dict, sources: dict) -> tuple[list[dict], dict]:
    require(probe["cpi_history"]["http_status"] == 200, "Historical probe market response was unsuccessful")
    historical = probe["cpi_history"]["data"]
    require(probe["retrieved_at_utc"] == sources[HISTORICAL_PATH]["retrieved_at_utc"], "Historical retrieval clock disagrees with provenance")
    events, tickers, event_sources = defaultdict(list), set(), {}
    tiers = {"historical": historical, "live": live}
    for tier, response in tiers.items():
        require(response.get("cursor") == "", f"Unexhausted or missing {tier} market-list cursor")
        require(isinstance(response["markets"], list), f"Invalid {tier} market list")
        source = sources[HISTORICAL_PATH if tier == "historical" else LIVE_PATH]
        for market in response["markets"]:
            ticker, event = market["ticker"], market["event_ticker"]
            require(ticker not in tickers, f"Duplicate Kalshi market ticker across metadata tiers: {ticker}")
            require(ticker.startswith(event + "-"), f"Market/event ticker mismatch: {ticker}")
            event_month(event)
            tickers.add(ticker)
            require(event not in event_sources or event_sources[event] == source,
                    f"Event spans multiple source snapshots: {event}")
            event_sources[event] = source
            events[event].append(market)
    candidates, audits, reference_keys = [], [], set()
    for event, markets in sorted(events.items(), key=lambda item: event_month(item[0])[0]):
        reference, year, month = event_month(event)
        require(reference not in reference_keys, f"Multiple Kalshi events for reference month: {reference}")
        reference_keys.add(reference)
        raw = sorted({market["expiration_value"] for market in markets if market["expiration_value"] != ""})
        values = {numeric(value, event, percent=True) for value in raw}
        require(len(values) <= 1, f"Conflicting event-level expiration values for {event}: {raw}; no averaging")
        statuses = sorted({market["status"] for market in markets})
        require(set(statuses) <= {"active", "finalized"}, f"Unknown market status for {event}: {statuses}")
        resolved = statuses == ["finalized"]
        require(not any(m["expiration_value"] == "" for m in markets if m["status"] == "finalized"),
                f"Finalized market lacks expiration value: {event}")
        require(not values or resolved, f"Partial/unresolved event has expiration values: {event}")
        audit = {"reference_month": reference, "event_ticker": event, "market_count": len(markets),
                 "expiration_values_raw": raw, "normalized_value_count": len(values),
                 "month_rule_mismatches": [], "explicit_year_rule_count": 0, "year_rule_mismatches": [],
                 "resolution_mismatches": [], "unparsed_rule_strikes": [], "status": statuses}
        for market in markets:
            primary = market["rules_primary"]
            rule_months = list(RULE_MONTH.finditer(primary))
            require(len(rule_months) == 1, f"Ambiguous primary-rule month for {market['ticker']}")
            rule = rule_months[0]
            if MONTH_NAMES.index(rule[1]) + 1 != month:
                audit["month_rule_mismatches"].append(market["ticker"])
            if rule[2]:
                audit["explicit_year_rule_count"] += 1
                if int(rule[2]) != year:
                    audit["year_rule_mismatches"].append(market["ticker"])
            strikes = list(RULE_STRIKE.finditer(primary))
            require(len(strikes) <= 1, f"Ambiguous primary-rule strike for {market['ticker']}")
            if not strikes:
                audit["unparsed_rule_strikes"].append(market["ticker"])
            elif resolved:
                expected = "yes" if next(iter(values)) > numeric(strikes[0][1], market["ticker"]) else "no"
                if market["result"] != expected:
                    audit["resolution_mismatches"].append(market["ticker"])
        audits.append(audit)
        if not resolved:
            continue
        source = event_sources[event]
        missing = reference in {"2025-10", "2025-11"}
        candidates.append({"reference_month": reference, "expiration_value": str(numeric(raw[0], event, percent=True)),
            "expiration_values_raw": raw, "event_ticker": event,
            "label_kind": "market_vendor_expiration_value_NOT_verified_BLS_print", "official_mom_missing": missing,
            "eligible_as_official_first_print": False,
            "exclusion_reason": "Official headline SA monthly CPI unavailable; vendor fallback/resolution is not an official print" if missing else "Requires independent reconciliation against original BLS release",
            "market_tickers": [market["ticker"] for market in markets],
            "settlement_timestamps": sorted({market["settlement_ts"] for market in markets}),
            "rules": [{key: market.get(key) for key in ("ticker", "rules_primary", "rules_secondary", "result", "floor_strike", "strike_type")} for market in markets],
            "source_url": source.get("source_url"),
            "source_route": source.get("source_url") or source["route_from_prior_log"],
            "source_path": source["path"], "source_sha256": source["sha256"], "retrieved_at_utc": source["retrieved_at_utc"],
            "series_definition_url": "https://api.elections.kalshi.com/trade-api/v2/series/KXCPI",
            "current_contract_terms_url": "https://assets.kalshi.com/contract_terms/CPI.pdf",
            "terms_limitation": "Current terms fetched now, not independently archived rule vintage", "consistency_audit": audit})
    require(bool(candidates), "No resolved Kalshi vendor candidates")
    coverage = {"historical_markets": len(historical["markets"]), "historical_events": len({m["event_ticker"] for m in historical["markets"]}),
                "live_markets": len(live["markets"]), "live_events": len({m["event_ticker"] for m in live["markets"]}),
                "unique_market_tickers": len(tickers), "events": len(events), "resolved_candidate_months": len(candidates),
                "resolved_markets": sum(len(row["market_tickers"]) for row in candidates),
                "candidate_month_min": candidates[0]["reference_month"], "candidate_month_max": candidates[-1]["reference_month"],
                "candidate_months_by_year": dict(sorted(Counter(row["reference_month"][:4] for row in candidates).items())),
                "missing_official_mom_months": [row["reference_month"] for row in candidates if row["official_mom_missing"]],
                "eligible_as_official_first_print_count": 0, "event_audits": audits,
                "decimal_agreement": "Require one numeric value per resolved event; retain raw formatting; never average conflicts"}
    return candidates, coverage


def write_json(path: Path, value: dict) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT, help="Original forecasts cache containing provenance.json")
    parser.add_argument("--historical-probe", type=Path, default=ROOT / HISTORICAL_PATH)
    parser.add_argument("--output", type=Path, default=ROOT / "data/research/cpi/forecasts-reproduced")
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        parser.error(f"Refusing to overwrite {args.output}; choose a fresh --output")
    try:
        payloads, sources, provenance_hash = verified_sources(args.input_dir, args.historical_probe)
        forecasts, cleveland = cleveland_rows(payloads[CLEVELAND_PATH], sources[CLEVELAND_PATH])
        candidates, kalshi = kalshi_rows(payloads[HISTORICAL_PATH], payloads[LIVE_PATH], sources)
    except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
        parser.error(f"Cannot derive cached CPI forecast inputs: {error}")
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "cleveland").mkdir()
    with (args.output / "cleveland/forecasts.csv").open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FORECAST_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(forecasts)
    with (args.output / "candidate_labels.jsonl").open("x", encoding="utf-8") as stream:
        for row in candidates:
            stream.write(json.dumps(row, sort_keys=True, allow_nan=False) + "\n")
    write_json(args.output / "cleveland/coverage.json", cleveland)
    summary = {"kind": "offline_reproduction_of_forecast_and_vendor_candidates_not_certified_labels",
               "original_provenance_sha256": provenance_hash, "sources": sources,
               "cleveland": {key: value for key, value in cleveland.items() if key not in {"monthly_counts", "source"}},
               "kalshi": kalshi,
               "limitations": ["Source caches and original provenance are not in git; exact reproduction needs those historical snapshots",
                               "Hash agreement checks recorded bytes, not original-publication or immutable-vintage certification",
                               "Cleveland dates use nearest-year parsing, not observed posting timestamps; actual series are never labels",
                               "Kalshi candidates are vendor-only, never eligible official first prints; October/November 2025 official MoM remains missing",
                               "Historical Kalshi source URL/host was not recorded and is not reconstructed",
                               "This producer does not acquire sources, candles, labels, release schedules, models, or scores"],
               "output_sha256": {name: hashlib.sha256((args.output / name).read_bytes()).hexdigest() for name in
                                  ("cleveland/forecasts.csv", "cleveland/coverage.json", "candidate_labels.jsonl")}}
    write_json(args.output / "coverage_summary.json", summary)
    print(json.dumps({"output": str(args.output), "headline_forecast_rows": len(forecasts),
                      "resolved_vendor_candidates": len(candidates), "source_sha256": {key: value["sha256"] for key, value in sources.items()}}, indent=2))


if __name__ == "__main__":
    main()
