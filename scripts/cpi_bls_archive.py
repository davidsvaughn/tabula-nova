#!/usr/bin/env python3
"""Acquire/cache original BLS releases and extract headline CPI-U SA monthly prints.

Offline: python scripts/cpi_bls_archive.py parse
HTTP (bounded; stops on access denial): python scripts/cpi_bls_archive.py fetch --limit 3
Reader import: python scripts/cpi_bls_archive.py import-reader --url URL --file FILE
  --retrieved-at UTC_ISO --evidence NOTE [--kind index]

Reader files are extracted text, never represented as raw HTTP HTML. An external
supported reader must supply them; this stdlib CLI does not emulate that service.
Only explicit headline monthly statements in the release's opening section are
accepted; historical \"virtually unchanged\" prose additionally requires the printed
Table A value under matching month AND year headers. Earlier historical columns,
annual changes, core CPI, and multi-month changes are never substituted.

labels.jsonl and coverage.jsonl retain every calendar reference month, including
null targets. exact_labels.jsonl contains only parsed labels; failures.jsonl holds
all other statuses. summary.json reports status counts by reference year.
source_sha256 hashes the exact cached representation, not an unobserved HTTP body.
label_available_at_utc equals the stated embargo time only for an exact label;
release_at_utc may still exist when the release did not publish the target.
"""
from __future__ import annotations

import argparse
import calendar
from collections import Counter
from datetime import date, datetime, timezone
from decimal import Decimal
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import time
import urllib.error
import urllib.request
from urllib.parse import urljoin, urlparse
from zoneinfo import ZoneInfo

INDEX_URL = 'https://www.bls.gov/bls/news-release/cpi.htm'
DEFAULT_ROOT = Path('data/research/cpi/bls')
MONTHS = {name.lower(): n for n, name in enumerate(calendar.month_name) if name}
MONTH_PATTERN = '|'.join(MONTHS)
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def dump_jsonl(path, rows):
    path.write_text(''.join(json.dumps(row, sort_keys=True) + '\n' for row in rows))


def load_manifest(root):
    path = root / 'manifest.jsonl'
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


def cache(root, url, body, method, retrieved_at, kind='release', status=None,
          reason=None, evidence=None, response_headers=None):
    digest = hashlib.sha256(body).hexdigest()
    relative = Path('raw') / (digest + ('.reader.txt' if method == 'reader' else '.body'))
    (root / relative).parent.mkdir(parents=True, exist_ok=True)
    if not (root / relative).exists():
        (root / relative).write_bytes(body)
    record = dict(source_url=url, source_sha256=digest, retrieved_at_utc=retrieved_at,
                  acquisition_method=method, representation='reader_extracted_text' if method == 'reader' else 'http_response_bytes',
                  cache_path=str(relative), kind=kind, http_status=status,
                  acquisition_status='success' if reason is None else 'failed', reason=reason,
                  evidence=evidence, response_headers=response_headers)
    with (root / 'manifest.jsonl').open('a') as f:
        f.write(json.dumps(record, sort_keys=True) + '\n')
    return record


class TextHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.hidden += 1
        if tag in ('li', 'p', 'div', 'br', 'tr', 'pre', 'h1', 'h2', 'h3', 'h4'):
            self.parts.append('\n')
        if tag == 'a':
            href = dict(attrs).get('href', '')
            self.parts.append(' ' + href + ' ')

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.hidden = max(0, self.hidden - 1)
        if tag in ('li', 'p', 'div', 'tr', 'pre'):
            self.parts.append('\n')

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def text_of(body):
    text = body.decode('utf-8-sig', errors='replace')
    if re.search(r'<(?:html|!doctype|pre)\b', text, re.I):
        parser = TextHTML()
        parser.feed(text)
        return ''.join(parser.parts)
    return text


def index_entries(text):
    result = {}
    for line in text.splitlines():
        match = re.search(rf'({MONTH_PATTERN})\s+(\d{{4}})\s+Consumer Price Index', line, re.I)
        if not match:
            continue
        month = f'{int(match[2]):04d}-{MONTHS[match[1].lower()]:02d}'
        urls = re.findall(r'(?:https://www\.bls\.gov)?(/news\.release/(?:archives|history)/cpi_\d+\.(?:htm|txt))', line)
        if urls:
            result[month] = dict(reference_month=month, source_url=urljoin(INDEX_URL, urls[0]), index_status='listed')
        elif 'not published' in line.lower():
            result[month] = dict(reference_month=month, source_url=None, index_status='not_published', reason=line.strip())
    if not result:
        raise ValueError('No release entries found in index representation')
    return result


def historical_table_value(text, reference_month):
    """Read a seven-month historical Table A using its month AND year headers."""
    table = re.search(r'Table A\.\s+Percent changes in CPI for All Urban Consumers \(CPI-U\)(.*?)(?:\n\s*Food and beverages)', text, re.S | re.I)
    if not table or not re.search(r'Changes from preceding month', table[1], re.I):
        raise ValueError('unsupported_historical_table')
    lines = table[1].splitlines()
    abbreviations = {name[:3]: number for name, number in MONTHS.items()}
    for i, line in enumerate(lines[:-1]):
        tokens = line.split()
        if len(tokens) != 9 or tokens[-2:] != ['ended', 'ended']:
            continue
        names = [token.lower().rstrip('.')[:3] for token in tokens[:7]]
        years = lines[i + 1].split()[:7]
        if any(name not in abbreviations for name in names) or len(years) != 7 or not all(re.fullmatch(r'\d{4}', y) for y in years):
            continue
        headers = [f'{y}-{abbreviations[name]:02d}' for name, y in zip(names, years)]
        row = re.search(r'^\s*All items\.+\s+(.+)$', table[1], re.M | re.I)
        values = row[1].split() if row else []
        if len(values) != 9 or headers.count(reference_month) != 1 or not all(re.fullmatch(r'-?\d*\.\d+', value) for value in values):
            continue
        return Decimal(values[headers.index(reference_month)]), row[0].strip()
    raise ValueError('ambiguous_historical_table_month_year_headers')


def extract(text, expected_month, url):
    flat = re.sub(r'\s+', ' ', text).replace('CPI\\-U', 'CPI-U')
    title = re.search(rf'CONSUMER PRICE INDEX\s*[-:–—]\s*({MONTH_PATTERN})\s+(\d{{4}})', flat, re.I)
    if not title:
        raise ValueError('missing_reference_month_title')
    month = f'{int(title[2]):04d}-{MONTHS[title[1].lower()]:02d}'
    if month != expected_month:
        raise ValueError('reference_month_disagrees_with_index')
    # Contact details and correction notes are not part of the embargo header.
    header = re.split(r'Technical information:', flat[:title.start()], flags=re.I)[0]
    # Restrict date/time to the actual embargo header, not the next-release notice.
    times = list(re.finditer(r'(\d{1,2}):(\d{2})\s*([ap])\.?m\.?\s*\((ET|EST|EDT)\)', header, re.I))
    if len(times) != 1 or 'embargoed' not in header.lower():
        raise ValueError('ambiguous_or_missing_embargo_time')
    tm = times[0]
    dates = re.findall(rf'({MONTH_PATTERN})\s+(\d{{1,2}}),\s*(\d{{4}})', header[tm.end():], re.I)
    if len(dates) != 1:
        raise ValueError('ambiguous_or_missing_embargo_date')
    mon, day, year = dates[0]
    hour = int(tm[1]) % 12 + (12 if tm[3].lower() == 'p' else 0)
    local = datetime(int(year), MONTHS[mon.lower()], int(day), hour, int(tm[2]), tzinfo=ZoneInfo('America/New_York'))
    stated_zone = tm[4].upper()
    if stated_zone != 'ET' and stated_zone != local.tzname():
        raise ValueError('stated_timezone_disagrees_with_zoneinfo')
    filename_date = re.search(r'cpi_(\d{8})\.', url)
    if not filename_date or datetime.strptime(filename_date[1], '%m%d%Y').date() != local.date():
        raise ValueError('stated_date_disagrees_with_archive_filename')
    opening = flat[title.end():].split('Table A.')[0]
    subject = r'The Consumer Price Index for All Urban Consumers \(CPI-U\)'
    change = r'(?P<verb>increased|rose|advanced|decreased|declined|fell)\s+(?P<amount>\d+\.\d+|\.\d+)\s+percent'
    movement = rf'(?:{change}|(?P<zero>was unchanged|remained unchanged))'
    ref_name = re.escape(title[1])
    timestamp = local.astimezone(timezone.utc).isoformat()
    metadata = dict(reference_month=month, target_value_initial=None, release_at_utc=timestamp,
                    label_available_at_utc=None, release_at_local=local.isoformat(), release_timezone='America/New_York',
                    stated_timezone=stated_zone, target_units='percent',
                    target_definition='headline CPI-U all items seasonally adjusted month-over-month',
                    availability_basis='stated embargo release time; not observed first HTTP availability')
    # Explicit observed prose orders; nothing selected by numeric column position.
    patterns = [
        rf'{subject}\s+{movement}\s+in\s+{ref_name}\s+on a seasonally adjusted basis',
        rf'{subject}\s+{movement}\s+on a seasonally adjusted basis\s+in\s+{ref_name}\b',
        rf'On a seasonally adjusted basis, the CPI-U(?:, which was unchanged in (?:{MONTH_PATTERN}),)?\s+{movement}\s+in\s+{ref_name}\b',
        rf'On a seasonally adjusted basis, {subject}\s+{movement}\s+in\s+{ref_name}\b',
        rf'On a seasonally adjusted basis, the {ref_name} Consumer Price Index for All Urban Consumers \(CPI-U\)\s+{movement}(?=,|\.)',
        rf'{subject}\s+{movement}\s+on a seasonally adjusted basis(?=,|\.)',
        rf'On a seasonally adjusted basis, the CPI-U (?P<verb>decreased) for the second consecutive month--down (?P<amount>\d+\.\d+) percent in {ref_name}(?P<zero>)',
    ]
    matches = [m for pattern in patterns for m in re.finditer(pattern, opening, re.I)]
    if not matches:
        virtual = re.search(rf'On a seasonally adjusted basis, the CPI-U was virtually unchanged in {ref_name}\b', opening, re.I)
        if virtual:
            try:
                value, evidence = historical_table_value(text, month)
            except ValueError as exc:
                return dict(metadata, parse_status='unparsed', reason=str(exc))
            if value != 0:
                return dict(metadata, parse_status='unparsed', reason='headline_table_disagreement')
            return dict(metadata, target_value_initial=str(value), label_available_at_utc=timestamp,
                        extraction_evidence=virtual[0] + '; Table A: ' + evidence, parse_status='parsed', reason=None)
        headline = re.search(rf'{subject}\s+[^.]+(?:\.\d+[^.]+)?', opening, re.I)
        if headline and re.search(r'over the\s+2\s+months', headline[0], re.I):
            return dict(metadata, parse_status='target_not_published', reason='Opening reports a two-month change, not month-over-month')
        return dict(metadata, parse_status='unparsed', reason='unrecognized_or_missing_explicit_headline_sa_monthly_statement')
    if len(matches) != 1:
        return dict(metadata, parse_status='unparsed', reason='ambiguous_multiple_monthly_statements')
    match = matches[0]
    value = Decimal('0.0') if match['zero'] else Decimal(match['amount'])
    if match['verb'] and match['verb'].lower() in ('decreased', 'declined', 'fell'):
        value = -value
    return dict(metadata, target_value_initial=str(value), label_available_at_utc=timestamp,
                extraction_evidence=match[0], parse_status='parsed', reason=None)


def cached_text(root, record):
    body = (root / record['cache_path']).read_bytes()
    if hashlib.sha256(body).hexdigest() != record['source_sha256']:
        raise ValueError('cache_sha256_mismatch')
    return text_of(body)


def parse(root, start, as_of):
    records = load_manifest(root)
    indices = [r for r in records if r['kind'] == 'index' and r['acquisition_status'] == 'success']
    if not indices:
        raise ValueError('No cached successful index; use fetch or import-reader --kind index')
    index = indices[-1]
    entries = index_entries(cached_text(root, index))
    by_url = {}
    for record in records:
        if record['kind'] == 'release':
            previous = by_url.get(record['source_url'])
            if previous is None or record['acquisition_status'] == 'success' or previous['acquisition_status'] != 'success':
                by_url[record['source_url']] = record
    rows = []
    for month, entry in sorted(entries.items()):
        if month < start or month >= as_of[:7]:
            continue
        row = dict(entry, target_value_initial=None, release_at_utc=None, label_available_at_utc=None,
                   source_sha256=None, retrieved_at_utc=None, parse_status='not_acquired', reason='archive listed; release body not acquired')
        if entry['index_status'] == 'not_published':
            row.update(parse_status='not_published', reason=entry['reason'], source_url=INDEX_URL,
                       source_sha256=index['source_sha256'], retrieved_at_utc=index['retrieved_at_utc'], acquisition_method=index['acquisition_method'])
        elif entry['source_url'] in by_url:
            record = by_url[entry['source_url']]
            row.update({key: record[key] for key in ('source_sha256', 'retrieved_at_utc', 'acquisition_method', 'representation', 'cache_path')})
            if record['acquisition_status'] != 'success':
                row.update(parse_status='acquisition_failed', reason=record['reason'])
                if record['reason'] == 'not_fetched_rate_limited':
                    row.update(parse_status='not_fetched_rate_limited')
                reported = re.search(r'HTTP\s+(\d{3})', cached_text(root, record))
                if reported:
                    row.update(reason=f'reader_reported_HTTP_{reported[1]}', reported_http_status=int(reported[1]))
            else:
                try:
                    row.update(extract(cached_text(root, record), month, entry['source_url']))
                    if row['release_at_local'][:10] > as_of:
                        row.update(parse_status='after_as_of', target_value_initial=None, reason='release date after as-of date')
                except ValueError as exc:
                    row.update(parse_status='target_not_published' if str(exc).startswith('target_not_published:') else 'unparsed', reason=str(exc))
        rows.append(row)
    # Include months absent from the archive, not just listed releases.
    known = {r['reference_month'] for r in rows}
    year, month = map(int, start.split('-'))
    while f'{year:04d}-{month:02d}' < as_of[:7]:
        ref = f'{year:04d}-{month:02d}'
        if ref not in known:
            rows.append(dict(reference_month=ref, source_url=INDEX_URL, source_sha256=index['source_sha256'],
                             retrieved_at_utc=index['retrieved_at_utc'], target_value_initial=None,
                             release_at_utc=None, label_available_at_utc=None, parse_status='not_yet_released' if ref > max(entries) else 'not_in_archive',
                             reason='Reference month is later than latest archived release as of index retrieval' if ref > max(entries) else 'No archive entry as of retrieved index'))
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    rows.sort(key=lambda r: r['reference_month'])
    labels = [r for r in rows if r['parse_status'] == 'parsed']
    dump_jsonl(root / 'labels.jsonl', rows)
    dump_jsonl(root / 'exact_labels.jsonl', labels)
    dump_jsonl(root / 'failures.jsonl', [r for r in rows if r['parse_status'] != 'parsed'])
    dump_jsonl(root / 'coverage.jsonl', rows)
    summary = dict(start_reference_month=start, as_of_date=as_of, expected_reference_months=len(rows),
                   status_counts=dict(Counter(r['parse_status'] for r in rows)),
                   archive_listed_release_count=sum(r.get('index_status') == 'listed' for r in rows),
                   acquired_release_count=sum(r.get('parse_status') in ('parsed', 'unparsed', 'target_not_published') for r in rows),
                   by_reference_year={year: dict(Counter(r['parse_status'] for r in rows if r['reference_month'].startswith(year)))
                                      for year in sorted({r['reference_month'][:4] for r in rows})},
                   parsed_reference_month_min=labels[0]['reference_month'] if labels else None,
                   parsed_reference_month_max=labels[-1]['reference_month'] if labels else None,
                   index_source_sha256=index['source_sha256'], index_retrieved_at_utc=index['retrieved_at_utc'],
                   complete=False, limitation='Coverage is measured explicitly; unparsed/unacquired months are not exact labels. Archive copies are not independently timestamped first-release snapshots.')
    (root / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    return summary


def fetch_one(root, url, kind):
    request = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'text/html,text/plain'})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return cache(root, url, response.read(), 'urllib_browser_user_agent', utc_now(), kind,
                         status=response.status, response_headers=dict(response.headers))
    except urllib.error.HTTPError as exc:
        return cache(root, url, exc.read(), 'urllib_browser_user_agent', utc_now(), kind,
                     status=exc.code, reason=f'HTTP {exc.code}', response_headers=dict(exc.headers))
    except (urllib.error.URLError, TimeoutError) as exc:
        return cache(root, url, b'', 'urllib_browser_user_agent', utc_now(), kind, reason=str(exc))


async def acquire_with_reader(root, read_url, read_artifact, limit=3):
    """Supported-reader adapter, sequential and stopping on the first access denial.

    In the tool host, pass an async read_url(url) returning tool.read's dict and
    read_artifact(uri) returning the COMPLETE artifact string (not default paging).
    Existing attempts, including failures, are retained and never silently retried.
    """
    records = load_manifest(root)
    indices = [r for r in records if r['kind'] == 'index' and r['acquisition_status'] == 'success']
    if not indices:
        raise ValueError('Import the supported-reader index before release acquisition')
    entries = index_entries(cached_text(root, indices[-1]))
    existing = {r['source_url'] for r in records}
    pending = [e for month, e in sorted(entries.items())
               if month >= '2000-01' and e['source_url'] and e['source_url'] not in existing]
    attempted = []
    for i, entry in enumerate(pending[:limit]):
        url = entry['source_url']
        try:
            response = await read_url(url)
            stamp = utc_now()
            text = response.get('text', '')
            artifact = re.search(r'Read (artifact://\d+) for full output', text)
            if artifact:
                text = read_artifact(artifact[1])
            denied = re.search(r'HTTP\s+(401|403|429)\b', text)
            reason = f'reader_reported_HTTP_{denied[1]}' if denied else None
            if reason is None and ('embargoed' not in text.lower() or 'consumer price index' not in text.lower()):
                reason = 'reader_output_missing_release_content'
        except Exception as exc:
            text, stamp, denied, reason = str(exc), utc_now(), None, f'reader_error: {exc}'
        attempted.append(cache(root, url, text.encode(), 'reader', stamp, reason=reason,
                               evidence='supported reader output; extracted representation, not HTTP bytes'))
        if denied:
            for remaining in pending[i + 1:]:
                cache(root, remaining['source_url'], b'', 'reader', None,
                      reason='not_fetched_rate_limited' if denied[1] == '429' else 'not_fetched_access_denied',
                      evidence='No request made: collector stopped after access denial')
            break
    return attempted


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--root', type=Path, default=DEFAULT_ROOT)
    sub = parser.add_subparsers(dest='command', required=True)
    offline = sub.add_parser('parse', help='Rebuild labels/failures/coverage from verified cached representations')
    offline.add_argument('--start', default='2000-01')
    offline.add_argument('--as-of', default='2026-10-01', help='Inclusive New York calendar release date')
    fetcher = sub.add_parser('fetch', help='Bounded public HTTP acquisition; no retries or gate bypass')
    fetcher.add_argument('--limit', type=int, default=3)
    importer = sub.add_parser('import-reader', help='Import externally retrieved supported-reader evidence')
    importer.add_argument('--url', required=True)
    importer.add_argument('--file', type=Path, required=True)
    importer.add_argument('--retrieved-at', required=True)
    importer.add_argument('--evidence', required=True)
    importer.add_argument('--kind', choices=('index', 'release'), default='release')
    args = parser.parse_args()
    args.root.mkdir(parents=True, exist_ok=True)
    if args.command == 'parse':
        date.fromisoformat(args.as_of)
        datetime.strptime(args.start, '%Y-%m')
        result = parse(args.root, args.start, args.as_of)
    elif args.command == 'import-reader':
        if urlparse(args.url).hostname != 'www.bls.gov':
            parser.error('reader source must be the public BLS host')
        stamp = datetime.fromisoformat(args.retrieved_at)
        if stamp.utcoffset() != timezone.utc.utcoffset(stamp):
            parser.error('--retrieved-at must include UTC offset')
        result = cache(args.root, args.url, args.file.read_bytes(), 'reader', stamp.isoformat(), args.kind, evidence=args.evidence)
    else:
        if args.limit < 1:
            parser.error('--limit must be positive')
        records = load_manifest(args.root)
        indices = [r for r in records if r['kind'] == 'index' and r['acquisition_status'] == 'success']
        index = indices[-1] if indices else fetch_one(args.root, INDEX_URL, 'index')
        if index['acquisition_status'] != 'success':
            print(json.dumps(index, indent=2))
            return 2
        existing = {r['source_url'] for r in records}
        attempted = []
        for month, entry in sorted(index_entries(cached_text(args.root, index)).items()):
            if month < '2000-01' or not entry['source_url'] or entry['source_url'] in existing:
                continue
            record = fetch_one(args.root, entry['source_url'], 'release')
            attempted.append(record)
            if record['http_status'] in (401, 403, 429) or len(attempted) >= args.limit:
                break
            time.sleep(0.5)
        result = attempted
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
