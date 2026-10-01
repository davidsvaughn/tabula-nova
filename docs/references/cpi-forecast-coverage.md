# CPI forecast and market comparison coverage

Audit date: 2026-10-01. Target: **headline CPI-U seasonally adjusted, nonannualized month-over-month percent change as initially published**. This is a source/coverage audit, not a fitted benchmark. All acquisition was public, read-only, keyless HTTP; no accounts, orders, private keys, commercial services, or models were used.

## Measured result

| Source | Actually acquired coverage | What this does not establish |
|---|---|---|
| Cleveland monthly chart history | 160 target-month charts, 2013-07–2026-10; **4,673 nonblank headline CPI forecast observations for 159 months**, 2013-08–2026-10; forecast dates 2013-08-20–2026-10-01 | Immutable original forecast bytes, exact historical publication clocks, or a no-retroactive-correction policy |
| Cleveland through latest released reference month, 2026-08 | **157 forecast target months**; 155 potentially match an official monthly target after excluding 2025-10 and 2025-11 | Verified first-print labels or complete cutoff availability for every month |
| Kalshi historical metadata, reused | **483 markets / 61 events**, reference months 2021-06–2026-06; empty pagination cursor | 483 independent CPI outcomes, or complete candle history |
| Kalshi live metadata, freshly acquired | **69 markets / 6 events**: July–December 2026; July/August finalized, September–December active; empty cursor | Outcomes for the four future/unresolved months |
| Combined Kalshi metadata | **552 unique market tickers / 67 distinct monthly events**; zero ticker duplicates between tiers | All contracts having identical rules, or exact official labels |
| Kalshi resolved vendor candidates | **508 markets / 63 monthly outcomes**, continuous 2021-06–2026-08; **61 potentially match official monthly targets** after excluding October/November 2025 | BLS certification; vendor fallback values are not official prints |
| Kalshi exact `Above 0.3%` | 53 historical contracts; 59 across both tiers, 55 finalized; **53 finalized after removing the two missing-official-MoM months** | A probability-distribution benchmark or a usable contemporaneous quote for each event |

Candidate monthly outcomes by year: 2021: 7; 2022–2025: 12 each; 2026: 8. Cleveland released-month coverage is 2013: 5; 2014–2025: 12 each; 2026: 8, before excluding the two missing targets. Nothing acquired supplies original forecasts for 2000-01–2013-07 or Kalshi outcomes before 2021-06.

## Cleveland Fed: downloaded history, not a reconstructed backtest

### Exercised routes and formats

The [Inflation Nowcasting page](https://www.clevelandfed.org/indicators-and-data/inflation-nowcasting) embeds chart data directly in its HTML configuration. The exercised download is:

- [`/-/media/files/webcharts/inflationnowcasting/nowcast_month.json?sc_lang=en`](https://www.clevelandfed.org/-/media/files/webcharts/inflationnowcasting/nowcast_month.json?sc_lang=en): HTTP 200, 7,626,647 bytes, one current JSON array containing all 160 monthly charts. The full linked file was needed to inspect the actual history; it was downloaded once, not duplicated as a second archive.
- Each chart has a target `chart.subcaption` such as `2023-12`, MM/DD category labels, four nowcast series, and four corresponding `Actual ...` series. The extraction selects **`CPI Inflation` only**, never core CPI, PCE, year-over-year, quarterly, or `Actual CPI Inflation`.
- July 2013 has PCE history but **zero headline CPI forecasts**. August 2013 has 19 headline forecasts, starting August 20. All subsequent target months through October 2026 have headline forecasts. There are zero duplicate `(reference_month, forecast_date)` pairs and zero category/series alignment failures after excluding chart event-marker categories.
- Forecast horizons are current-month and, after month-end, unreleased prior-month estimates. Observed forecast dates lie 0–77 calendar days after the target month's first day; the maximum is October 2025's December 17 forecast during the shutdown. The first partial month starts August 20 rather than August 1.
- The same page links `nowcast_quarter.json?sc_lang=en` and `nowcast_year.json?sc_lang=en`. Those horizons are not the target and were **not downloaded**. No separate XLSX export was present in the inspected page; the machine-readable monthly chart download was exercised instead.

MM/DD years in the derived CSV are assigned to the calendar year nearest the chart's target month; raw labels are retained. This is an explicit parsing convention, not a source-supplied intraday timestamp. Chart `_comment` was `2026-10-01 00:00` throughout: it is not each historical forecast's publication clock.

### What is original, what is recomputed, and what remains uncertified

The [2023 real-time assessment](https://www.clevelandfed.org/publications/economic-commentary/2023/ec-202306-real-time-assessment-inflation-nowcasting-cleveland-fed), endnote 3, makes the crucial distinction:

- **1999–2013:Q2:** model nowcasts were computed retrospectively using real-time data that would have been available. Those are reconstructed forecasts, not contemporaneously published predictions.
- **2013:Q3 onward:** the study uses forecasts generated and published to the website in real time.

The same article's conclusion says the website has provided daily estimates since early 2014, while its endnote gives 2013:Q3 as the real-time dividing line. The current export actually starts headline forecasts in August 2013. Preserve these distinct source statements rather than inventing a more precise launch date. The study's longer historical sample does **not** establish a downloadable contemporaneous 1999–2013 archive. Its endnote 5 also evaluates against third monthly price estimates, not this audit's initial printed monthly target.

The downloaded history is best described as **a current download of dated historical forecasts represented by Cleveland as real-time forecasts**, not independently captured original vintages. Neither the current FAQ, linked technical FAQ, nor assessment supplied an immutable snapshot index or an explicit guarantee that old rows are never corrected/recomputed. Changing a new day's estimate when new data or revisions arrive is documented; it is not evidence that past rows either are or are not overwritten. Strict immutable-vintage certification remains unresolved.

### Publication clock and shutdown handling

The current FAQ states updates occur **every business day around 10:00 a.m. Eastern**. This nominal schedule precedes the retained 16:00 Eastern cutoff, but the JSON has dates only, not actual daily posting times. Do not turn “around 10” into a verified timestamp; especially do not use a release-day forecast updated after the 08:30 CPI release.

Three observed pre-release-date forecast values illustrate availability joins, not scores:

| Reference month | Forecast date, before verified BLS release | Headline SA MoM forecast (%) |
|---|---|---:|
| 2023-12 | 2024-01-10 | 0.30120238809612 |
| 2026-06 | 2026-07-13 | -0.0612913952296244 |
| 2026-08 | 2026-09-10 | 0.359180537639179 |

The [December 2025 methodological notice](https://www.clevelandfed.org/-/media/project/clevelandfedtenant/clevelandfedsite/indicators-and-data/inflation-nowcasting/inflation-nowcasting-model-methodological-approach-to-missing-october-and-november-2025-cpi-data.pdf) states that neither October nor November 2025 had official monthly CPI/core-CPI inflation readings. Cleveland used its **December 17, 2025 nowcasts** to estimate October price levels, then calculated implied November growth using those estimated October levels and BLS November levels. **Both months' monthly changes are model-dependent, not official BLS prints.**

The acquired chart has 53 October forecasts through December 17 and no October `Actual CPI Inflation` value. November has 31 forecasts through December 17 and an `Actual CPI Inflation` marker on December 18 of **0.0211040487848813**. Despite that series name, this November marker must not be promoted to official monthly truth. The chart's other actual markers also carry unrounded changes, e.g. December 2023 **0.303003731525076**, whereas the original release printed **0.3%**. The 156 chart “actual” markers are therefore not a certified first-print target file.

The page/chart HTML explicitly supplies [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) attribution licensing. The linked 2023 commentary separately displays CC BY-NC 4.0; do not assume the commentary's license and the chart's license are identical. The chart credits BLS, BEA, EIA, Financial Times, and Haver inputs; this audit downloaded Cleveland's published output, not those commercial input series.

## Kalshi: metadata, rules, and vendor outcome candidates

### Reuse, tier routing, and exact endpoints

`data/research/kalshi_cpi_probe.json` was read and reused before new API requests. Its original retrieval time is **2026-10-01T15:20:05.543573+00:00**. It records responses but **no base URL or exact original candle-request URL**. The historical metadata route is recorded in LOG-002; the original host cannot honestly be recovered from this artifact. Current [official API documentation](https://docs.kalshi.com/api-reference/historical/get-historical-market-candlesticks) lists both `https://external-api.kalshi.com/trade-api/v2` and the supported shared host **`https://api.elections.kalshi.com/trade-api/v2`**. All fresh Kalshi calls here used the latter without authentication.

Routes, relative to that base:

- Reused: `/historical/cutoff`; recorded `market_settled_ts=2026-08-02T00:00:00Z`. This is a moving boundary, not a historical constant.
- Reused: `/historical/markets?series_ticker=KXCPI&limit=1000`.
- Fresh: `/markets?series_ticker=KXCPI&limit=1000`.
- Fresh: `/historical/markets?series_ticker=CPI&limit=1000`: HTTP 200, **zero markets**, empty cursor. This does not imply legacy CPI events are absent: the KXCPI query already returned **330 legacy `CPI-*` markets across 41 events**. Keep returned tickers rather than synthesizing a `KXCPI-` prefix for old markets.
- Fresh: `/series/KXCPI`; points to BLS and [CPI contract terms](https://assets.kalshi.com/contract_terms/CPI.pdf), also downloaded.
- Historical candles: `/historical/markets/{ticker}/candlesticks?start_ts={unix}&end_ts={unix}&period_interval={1|60}`.
- Live candles: `/series/KXCPI/markets/{ticker}/candlesticks?start_ts={unix}&end_ts={unix}&period_interval={1|60}`.

The [tier documentation](https://docs.kalshi.com/getting_started/historical_data.md) partitions markets/candles by **settlement time**, not target month or latest expiration time; events/series remain available through their normal endpoints. Historical candle bid/ask fields use `close`, while live candle fields use `close_dollars`; both are dollar strings. Live volume uses `volume_fp`, historical volume uses `volume`. Cursor exhaustion was checked on both market listings; deduplication by market ticker found no overlap. This is a two-time acquisition, not an atomic exchange snapshot.

### Rules and consistency findings

Current CPI terms define the signed one-month, one-decimal, seasonally adjusted CPI-U change and a **strict greater-than** payout. Revisions after expiration are disregarded; that alone does not prove equivalence to the initial release in every exceptional event. The document also specifies a **missing-data fallback based on the twelfth root of a 12-month CPI index ratio**, and contingency/review provisions. Current terms are not a historical rule-version archive.

Event-level extraction found:

- All 63 resolved events have numeric expiration values after removing a literal percent suffix and decimal normalization. All strikes within each event agree numerically. `CPI-23OCT` mixes strings `0.0`/`0.00`; this is formatting, not conflicting outcomes. June 2021 uses `.9%`.
- The 505 finalized markets whose strict numeric threshold could be parsed directly from primary rules have **zero result-versus-expiration-value disagreements**. This is internal vendor consistency, not BLS verification.
- Two October 2021 primary rules contain an unsubstituted `|| percent ||` placeholder; a third says `0.50 percent%`. These three were retained as explicit unparsed-rule exceptions rather than silently filled from titles.
- **`CPI-22JUN-T0.2` has June in its event/title but July 2022 in primary rules.** Exclude that contract from a rule-consistent comparison until authoritative clarification. Other strikes do not repair that contract's rule text.
- Seventeen market primary rules omit an explicit year. Their event ticker supplies the candidate year; it is not independently present in those primary rules.
- **October and November 2025 both have `expiration_value=0.2`** (6 and 5 markets respectively), despite absent official monthly targets. November rules retain a December 10 scheduled-release date while actual close/settlement is December 18. October settled November 22. Do not infer a publication calendar from stale rule text or treat these vendor outcomes as official CPI releases. The exact discretionary/fallback rationale for these settlements was not independently established.

`candidate_labels.jsonl` contains **63 event-level market-vendor candidates**, including the two explicitly excluded missing-target months. Every row includes reference month, normalized/raw expiration values, event/market tickers, all per-market primary/secondary rules, consistency findings, source path/hash, retrieval time, and source route. Historical rows deliberately have `source_url=null` because the original artifact did not record its host. Every row is marked **NOT verified BLS print** and `eligible_as_official_first_print=false`; independent BLS reconciliation belongs in a separate label layer.

## Actual cutoff quote probes

Five new candle requests sampled three events, plus reuse of the saved seven-day June 2026 sample. Actual release clocks were established from original BLS releases: [2024-01-11](https://www.bls.gov/news.release/archives/cpi_01112024.htm), [2026-07-14](https://www.bls.gov/news.release/archives/cpi_07142026.htm), and [2026-09-11](https://www.bls.gov/news.release/archives/cpi_09112026.htm), all 08:30 Eastern. Cutoffs below are 16:00 America/New_York on the preceding federal business day. These particular preceding dates are ordinary weekdays with no intervening federal holiday; this small audit did not implement a replacement full federal-holiday calendar.

| Contract / tier | Cutoff UTC | Query | Returned candles | Latest usable candle end UTC | Candle-end age | Bid / ask / spread ($) |
|---|---|---|---:|---|---:|---|
| `CPI-23DEC-T0.3`, historical | 2024-01-10 21:00 | preceding 6h, hourly | 3 | 2024-01-10 19:00 | 2h | .04 / .07 / .03 |
| Same | Same | preceding 2h, minute | 0 | None | Unknown | None |
| `KXCPI-26JUN-T0.3`, historical | 2026-07-13 20:00 | preceding 6h, hourly | 0 | None | Unknown | None |
| Same, reused original seven-day sample | Same | 30 saved hourly candles, filtered at cutoff | 25 at/before cutoff; 5 later excluded | 2026-07-12 22:00 | **22h** | .00 / .01 / .01 |
| `KXCPI-26AUG-T0.3`, live | 2026-09-10 20:00 | preceding 6h, hourly | 7 | 2026-09-10 20:00 | 0h | .60 / .61 / .01 |
| Same | Same | preceding 2h, minute | 83 | 2026-09-10 20:00 | 0h | .60 / .61 / .01 |

Endpoints include candles ending on or after `start_ts` and on or before `end_ts`; seven hourly endpoints in a six-hour inclusive window is consistent with that schema. Every fresh request returned HTTP 200; empty arrays are substantive coverage gaps, not failed authentication. All exact query URLs, Unix window bounds, response bytes/hashes and retrieval clocks are saved. **No query used later data or future interpolation.** The live `include_latest_before_start` option, documented to synthesize a projected candle, was not requested.

These are **candle-end ages**, not verified ages of the last underlying quote update. Candle responses do not expose original bid/ask order/update timestamps or executable depth. The December 2023 hourly observation is exactly on the two-hour boundary and the minute window is empty; the June observation is stale even by candle-end age. August's closing quotes are available at the cutoff at both resolutions, but exact underlying quote age remains unverified. Therefore **no cohort is certified against the strict two-hour quote-age requirement** by this sample alone. Do not silently redefine quote age as bucket age. Midpoints (.055 for December 2023 and .605 for August 2026) are descriptive, not executable probabilities net of spread/fees.

## Saved evidence and integration prerequisites

Ignored local root: `data/research/cpi/forecasts/`.

- `provenance.json`: 18 source records (17 fresh successful HTTP acquisitions plus the reused probe), UTC retrieval clocks, URLs or explicit missing-URL caveat, raw SHA256, status, response headers, source sizes, explicit gaps, and hashes of derived outputs. No new HTTP access failure occurred.
- `coverage_summary.json`: machine-readable aggregate counts and limitations.
- `cleveland/source.html`, `nowcast_month.json`, `real_time_assessment.html`, `missing_2025_method.pdf`, `technical_faq.pdf`: source bytes.
- `cleveland/forecasts.csv`: 4,673 headline forecast rows with target/date/value/raw date label/source hash; `cleveland/coverage.json`: every chart's forecast range/count and separately identified actual markers. These files never declare a chart actual to be an official print.
- `kalshi/live_markets.json`, `legacy_cpi_historical.json`, `series.json`, `CPI_terms.pdf`, saved API documentation, and five `candles_*` response files.
- `kalshi/event_audit.json`, `kalshi/quote_probe_summary.json`, and top-level `candidate_labels.jsonl`.
- Reused rather than copied: `data/research/kalshi_cpi_probe.json`, SHA256 `12cb5d8519953b56c1982d33b0cc5cfed00c902b3d7ba8cc3e4f7bc6e48e1474`.
- Monthly Cleveland raw JSON SHA256: `ce875bad6db100512dbcd629c50bed0e66d2bdffb778dd80e5c5bc026fe66f2b`.
- Live Kalshi raw JSON SHA256: `dce2251d87ee571693ded3a07423142de0bb766ddab0dff9c1bfa2f3d323d841`.

### Deterministic offline reproduction

From the repository root, reproduce only the two consumed integration inputs with the standard-library producer:

```sh
python scripts/cpi_forecast_derive.py \
  --input-dir data/research/cpi/forecasts \
  --historical-probe data/research/kalshi_cpi_probe.json \
  --output data/research/cpi/forecasts-reproduced
```

The output directory must not exist. The producer verifies all three raw source SHA256 values and byte counts against **the original** `data/research/cpi/forecasts/provenance.json` before parsing any response. It reads exactly:

| Cached input | Observed acquisition URL / route |
|---|---|
| `data/research/cpi/forecasts/cleveland/nowcast_month.json` | `https://www.clevelandfed.org/-/media/files/webcharts/inflationnowcasting/nowcast_month.json?sc_lang=en` |
| `data/research/cpi/forecasts/kalshi/live_markets.json` | `https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=KXCPI&limit=1000` |
| `data/research/kalshi_cpi_probe.json` | Recorded route `/trade-api/v2/historical/markets?series_ticker=KXCPI&limit=1000`; **original host/URL unknown** |

The fresh output contains `cleveland/forecasts.csv` and `candidate_labels.jsonl` with the consumed schemas, plus `cleveland/coverage.json` and `coverage_summary.json` with chart/event counts, rule anomalies, original source metadata/hashes, the original provenance hash, and output hashes. It does not rewrite the original inputs or original coverage. Values and raw date labels are preserved; only `CPI Inflation` is selected. Event-marker categories are discarded, category/series and tooltip/date alignment and duplicate keys are checked, and nearest-year date ties are errors. Event outcomes require exact decimal agreement across all strikes; conflicts are errors, never averages. The October/November 2025 vendor `0.2` values remain explicitly missing-official candidates, all candidates remain ineligible as official first prints, and rule placeholders/month mismatches remain visible rather than being repaired from titles.

**Clean-checkout limitation:** these source caches and original acquisition provenance are ignored and **not in git**. Exact reproduction requires obtaining the original historical snapshot files and their original provenance from the research cache under applicable source terms. Refetching today's mutable URLs does not recreate the 2026-10-01 snapshots and must not be passed off as the original acquisition; changed bytes fail the original hash checks. For a separate new acquisition, Cleveland's observed URL above and Kalshi's live URL above are public routes, subject to their access/attribution/data-use terms. The currently documented historical fetch URL is `https://api.elections.kalshi.com/trade-api/v2/historical/markets?series_ticker=KXCPI&limit=1000`, but it is **not** the observed URL of the reused probe. A new historical listing also cannot recreate the original probe's response wrapper/retrieval clock or overcome the moving tier boundary. Acquire new snapshots with honest new provenance, exhausted pagination, and applicable permission; stop on an access denial rather than retrying or bypassing. The producer itself performs no network requests, and it adds no PIT, publication-clock, licensing, model, or scoring certification.

Acquisition and parsing were actually executed; continuous candidate-month coverage, unique forecast keys, date alignment, numeric within-event agreement, and exclusion of later candles were checked. No unit/build/model run was needed for this investigation. No browser tabs were opened. Public access is not itself a grant of unrestricted Kalshi data redistribution or model-training rights; this audit makes no such licensing determination and sought no additional permission.

Parent integration subsequently acquired all missing original-release documents
from FRASER and parsed **318 archived printed monthly targets**. RTDSM First matches
317 comparable prints, and all **61 non-shutdown Kalshi vendor values** match those
archived prints. Nominal-date Cleveland overlap is **155**. The source-snapshot,
schedule, posting-time and quote-update-age limitations remain; numeric agreement
does not certify every archived byte as an original publication snapshot.
See [LOG-008](../logs/LOG-008.md) for event-table evidence and the frozen protocol.

**Sufficient now:** public source acquisition, a dated Cleveland point-forecast candidate history, continuous vendor outcome candidates for 63 recent months, and evidence that some actual cutoff candles are retrievable. **Not sufficient yet:** a strict point-in-time scored comparison or a claim to beat monthly consensus.

Remaining prerequisites are original-snapshot/correction adjudication and prior-announced release-schedule assurance (numeric original-release reconciliation is now complete, excluding both 2025-10 and 2025-11); immutable-vintage/correction and historical posting-time assurance for Cleveland; rule-exception handling and historically appropriate settlement terms; and an explicitly validated quote-age convention/data source plus full cutoff coverage measurement. Preserve BLS absence rather than filling it from a vendor or model. Monthly contemporaneous survey consensus has not been acquired; quarterly SPF is not a substitute. A Cleveland point estimate is not a forecast distribution without a separately prespecified uncertainty method.

A **proposed full collector is unexecuted**: retain/refresh the moving archive boundary, paginate both metadata tiers, deduplicate by ticker and reference event, use verified BLS release clocks with the parent-owned federal-calendar cutoff implementation, request bounded pre-cutoff minute windows, preserve null/empty/stale observations and rule anomalies, and keep future/unresolved events out of target scoring. Do not fetch every strike's complete candles or start fitting until these coverage and PIT prerequisites are resolved.
