# Macroeconomic, forecasting, and financial data inventory

Audited 2026-10-01. Project roots below are under `/home/david/code/davidsvaughn/cedar/`. **Implemented** means code exists, not that a subscription is currently live. **Archived** means reusable historical material exists or is documented. Freshly exercised checks are explicitly marked; historical counts are not presented as fresh database queries. No account/order endpoints were called.

## Source map

| Source | Implemented access / evidence | Research value and limits |
|---|---|---|
| Schwab | `alpha-claw/alpha_claw/retrieval/providers.py`: quotes, price history, instruments/fundamentals; `schwab_stream/` L1 ingestion | **Fresh probe succeeded:** 1,255 SPY daily candles, 2021-10-01–2026-10-01. Current partial session must be excluded. Fundamental snapshots are not historical fundamentals. L1 is not a complete trade tape. |
| Alpaca market data | `AlphaPilot/scripts/research/pull_ap_daily_bars.py`, `pull_ap_minute_bars.py`; `JevTrader/scripts/exp013_archive_pipeline.py` | SIP daily/minute OHLCV archives; longer historical REST access documented. Use paper data credentials, not real-account keys. Pin SIP versus IEX, adjustment and timestamp semantics. |
| Alpaca/Benzinga news | `JevTrader/scripts/alpaca_news_crawl.py`; alpha-claw news-stream adapter | 430,274 archived items over 2025-01-01–2026-09-22 according to project research. Retrieved text can be updated text; `created_at` is not a true receipt timestamp. |
| Seeking Alpha | AlphaPilot browser-extension ingest, Alpha Picks captures, SA articles/Ask-SA; alpha-claw `sa_stream/` | Paid capture workflow: reuse existing material; no new paid page captures performed. Quant history and Alpha Picks events support equity research, with retrospective/survivorship/timing caveats below. |
| Gmail SA alerts | `AlphaPilot/alphapilot/email_lane/watcher.py` | Arrival timestamps support Alpha Picks announcement studies. Do not export raw emails: bodies can contain authentication links. |
| yfinance | `alpha-claw/alpha_claw/retrieval/providers.py`; factor-replication research | Long daily OHLCV, company/enrichment data. Current estimates/options/info are not historical snapshots. Adjustment policy and ticker identity need validation. |
| Finnhub | Same providers module: company news/profile/metrics, earnings, recommendations, insiders; earnings-calendar daemon | Earnings/news/fundamental features; period-end dates must not masquerade as publication dates. **Fresh economic-calendar request returned 403.** Stock candles also documented as entitlement-blocked. |
| SEC EDGAR | alpha-claw company filings/facts, sec-stream, suspensions | As-filed filings with acceptance times are useful event evidence. Current companyfacts responses need accession/filing/revision-aware selection, not just a fiscal-period join. |
| Nasdaq Trader | alpha-claw market-events stream / `market_halts` | Halt timing and execution exclusions. |
| InsightSentry | alpha-claw news-stream, crypto bars and historical research | News archive with actual local receipt timestamps; subscription cancellation documented in sibling research. Treat as archive until live entitlement is confirmed. |
| Adanos | alpha-claw sentiment providers and stream/backfill | Archived social/market sentiment; key documented dead. Includes Polymarket aggregate signals, not contract-level probability history. |
| GDELT DOC | alpha-claw `gdelt_article_search` | News discovery; throttled API and timestamp semantics require care. No fresh availability/depth claim made. |
| Hacker News | alpha-claw Algolia/Firebase query/feed | Public technology/news context, not financial ground truth. |
| openFDA | alpha-claw `fda_enforcement` | Regulatory event discovery; enforcement records are not a complete drug-approval calendar. |
| Jina / Wayback | alpha-claw article extraction and URL evidence | Extraction / historical evidence, not independent forecast providers. |
| Coinbase | alpha-claw `crypto_stream/reference.py` | Public crypto reference prices. |
| CoinGecko / alternative.me | alpha-claw `crypto_stream/regime.py` | Trending and Fear & Greed; daily snapshots and first-seen provenance. |
| CME futures via Schwab | alpha-claw futures quote polling | Current context; a live endpoint is not a long futures archive. |
| Kalshi | `JevTrader/jevtrader/kalshi.py`; alpha-claw `docs/meta/kalshi-poly/scripts/kalshi_client.py` | Public GET market/history data; auth only needed for other surfaces. **Fresh historical probe:** 483 KXCPI markets across 61 events, 53 exact `Above 0.3%` contracts. Candles successfully retrieved for one exact matching contract. |
| Polymarket | alpha-claw `docs/meta/kalshi-poly/polymarket/scripts/` | Keyless CLOB/Gamma/Data research, frozen books/cross-venue archives. Matching settlement rules matters more than similar market titles. |
| TypeSafe Jev / OpenRouter | `JevTrader/jevtrader/jev.py`, `llm.py` | Feature/forecast generators, not financial data ground truth. Archived historical LLM outputs must be checked for contemporaneous generation versus hindsight contamination. |
| Other LLM/search providers | alpha-claw research/cost registry; `.env` configuration | OpenAI, Google, DeepSeek, xAI, Parallel and related tools. A configured credential alone is not evidence of a working data integration. |

## AlphaPilot: ready archives and pitfalls

Principal evidence: `scripts/research/README.md`, `docs/research/stop-loss-overlay/appendix-repo-inventory.md`, `appendix-alpaca.md`, `docs/research/funding-policy.md`, `docs/reports/research/noon-bump.md`.

- `data/research/ap_daily_bars.csv`: approximately 37.6k split-adjusted rows, 45 Alpha Picks symbols, 2023-04-03–2026-08-24.
- `data/research/ap_daily_bars_tr.csv`: approximately 37.8k split/dividend-adjusted rows through 2026-08-28.
- `data/research/minute/*.npz`: 45 symbols, regular-session minute bars, approximately 13M rows according to documentation. Keys: `ts, dayord, mod, o, h, l, c, v`.
- Shared DB `sa_quant_rating_history`: documented 2026-08-24 inventory has 1,414,756 rows, 1,023 tickers, dates 2018-02-08–2026-08-06. This is a retrospective scrape, not a contemporaneously accumulated eight-year observation archive.
- `~/.cache/alpha-claw/sa-backtest/panel.npz`: referenced approximately 1,000-name quant/total-return panel; current S&P1500 membership introduces survivor bias. Not freshly loaded here.
- Cached Alpha Picks bars cover current/open picks, not a historical complete universe. Closed picks are missing. Historical entry prices at the open are not executable after a noon announcement.
- Raw SA page retention differs from derived capture retention. `received_at_utc` on a retrospective scrape is the scrape clock, not historical publication time.
- No native CPI/FRED/ALFRED or Kalshi history integration in this project.

## JevTrader: strongest immediately reusable experiment assets

Principal evidence: `scripts/exp005_*`, `exp007_semantic_calibration.py`, `exp013_archive_pipeline.py`, `exp018_online_calibration_and_threshold.py`, `exp022_out_of_time_2026.py`, `exp023_execution_reality.py`, `docs/log/001-digest-and-landscape.md`, `024-is-a-faster-news-feed-worth-it.md`, `TODO.md`.

Fresh local shape audit saved in `../data/research/local_archive_audit.json`:

| Archive | Fresh measurement |
|---|---:|
| `data/exp013/events.parquet` | 75,907 rows |
| `data/exp013/events_2026.parquet` | 47,480 rows |
| `data/exp005/settled_snapshots.jsonl` | 22,920 raw rows |
| Unique Kalshi tickers | 22,823; 97 duplicate rows |
| Unique Kalshi event tickers | 2,403 |
| Valid 24-hour midpoint + binary outcome | 8,955 markets across 1,583 event tickers |

The fresh snapshot count supersedes older approximately 21k-market counts in the research logs. Duplicate handling in the shape audit used the last row by ticker; conflicting duplicates still need an explicit reconciliation audit before training.

- News event tables contain `ar_pre5`, `ar_pre30`, `vol_pre30`, `dollar_vol_pre`, `n_prior_3d`; future `ar_5/ar_30/ar_60`, `vol_post30`, `vol_ratio_30` are **labels, not contemporaneous predictors**.
- `data/alpaca_bars/1min/`: approximately 431 daily parquet files, 2025-01-02–2026-09-22. SPY is continuous; other tickers are selected because they had news that day. Do not treat this as an unbiased full-equity panel.
- Event table `received_at_utc` is synthesized from news `created_at` in the historical crawler. The column name does not certify a real arrival clock. Avoid `*_before_leakfix.parquet` artifacts.
- Existing return columns are log abnormal returns, not directly tradable simple returns. Minute bars require the existing pre-news availability guard. Current archived text may include later edits.
- Kalshi snapshots contain hourly bid/ask/mid/last/OI at fixed horizons. They are carried-forward candles, not full order-book depth or proof of executable size. Related threshold markets share outcomes and must stay grouped.
- Existing candle collection deliberately excluded Economics and Financials. Metadata exists, but CPI price histories must be fetched separately. This is a collection gap, **not an API impossibility**; our historical CPI probe succeeded.
- Existing forecast records: `data/exp014/forecasts.jsonl`, `exp015/`, `exp016/scan_2026-09-23.jsonl`, `exp019/sign_scores.parquet`, `exp022/scored_2026.parquet`. Establish prediction creation time and whether they were retrospective before using them as combiner features.

## alpha-claw: broadest integration and provenance layer

Principal evidence: `alpha_claw/retrieval/registry.py`, `providers.py`, `services.py`, `settings.py`, `docs/runbooks/host-crons.md`, `docs/data-sources/data-source-audit-2026-07.md`, Schwab stream README, `docs/meta/kalshi-poly/`.

- Most ingestion tables carry local `received_at_utc`; vendor timestamps remain separate claims.
- Relevant tables include `insight_sentry_news`, `alpaca_news`, `sec_filing_events`, `market_trade_halts`, `earnings_calendar_events`, `schwab_l1_events`, `market_time_series*`, `crypto_exchange_bars`, `crypto_regime_daily`, `adanos_*`, `seeking_alpha_*`, `sa_quant_rating_history`, `analyst_estimate_snapshots`, `strategy_*`, `helm_journal`.
- The historical time-series cache can overwrite revised bars; inspect raw fetch records to reconstruct vintages. Database presence alone does not establish complete PIT coverage.
- Analyst-estimate daily snapshots are documented only 2026-07-31–2026-08-13. A 45-day lag on quarterly period-end data is a heuristic, not proof of actual filing-time availability.
- Operational docs say crons stood down 2026-08-13; DB/SA-ingest moved to AlphaPilot on the same shared volume/port 55433. Do not restart alpha-claw collectors or apply migrations for research.
- Kalshi/Polymarket collectors stopped 2026-08-07. Frozen Kalshi spool observed by scout for 2026-08-02–08-07; approximately 5.4GB Kalshi and 8GB Polymarket archives documented.
- Kalshi `data/paper_ledger.jsonl` contains 176 rows with probability, timestamp, executable quote and later scores. This is a potential combiner/provenance seed, not necessarily 176 independent events. Read the existing `notes/13-class1-postmortem.md` before revisiting that trading thesis.
- Polymarket cross-venue pair/outcome confirmations and price history are available under `docs/meta/kalshi-poly/polymarket/`. Settlement equivalence must be verified, not assumed.

### Schwab token convention

`schwab` is an alpha-claw wrapper. `SCHWAB_TOKENS_FILE` defaults to `data/schwab_tokens.json`, **relative to CWD**. Run the existing provider from alpha-claw's root or set the absolute path. Do not create a new token file in tabula-nova or force OAuth.

Our probe invoked alpha-claw's existing `.venv/bin/python`, imported `schwab_price_history`, and ran in that repository's CWD. This bypasses `alpha market history` cache writes and uses only the provider request. Normal SDK access-token renewal may rewrite the existing token file; no forced seven-day refresh was requested. The user's successful refresh is accepted; the repo wrapper copy's argument-forwarding discrepancy does not invalidate it.

Older capability notes say roughly 10 trading days for minute history; a later July audit reports roughly 45 days. Neither was freshly probed here. Daily-history access was actually exercised.

## Additional primary-source candidates

- [BLS CPI release archive](https://www.bls.gov/bls/news-release/cpi.htm): original published target values and embargo/release times. Read-tool access worked; direct Python HTTP returned 403. Example [January 11, 2024 release](https://www.bls.gov/news.release/archives/cpi_01112024.htm) reports December 2023 headline SA monthly 0.3%, therefore false for strict `>0.3%`.
- [ALFRED/FRED real-time API](https://fred.stlouisfed.org/docs/api/fred/realtime_period.html): vintage macro features; requires release-clock validation as well as vintage dates. No FRED credential found in tabula-nova `.env`; no archive client found in connected projects.
- [Cleveland Fed nowcasts](https://www.clevelandfed.org/indicators-and-data/inflation-nowcasting): daily approximately 10am ET updates, historical chart sequences and first-release comparison documented. Historical export and timestamp reproducibility not yet exercised. The October 2025 missing CPI handling requires an explicit missing-label policy.
- [Kalshi historical API](https://docs.kalshi.com/getting_started/historical_data): newly verified route to older CPI markets/candles, independent of JevTrader's text-only archive. Public requests do not need the user's private key.
- [Philadelphia Fed SPF](https://www.philadelphiafed.org/surveys-and-data/data-files):
  now freshly exercised, not merely a candidate. Downloaded 9,280 individual RECESS
  rows across 232 quarters, means, publication dates, and [RTDSM first GDP releases](https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/first-second-third).
  Files and SHA256 provenance are under ignored `data/research/spf/`; LOG-004/005
  document a completed 84-event macro probability comparison. RECESS2 is next-quarter
  negative GDP growth, not an NBER recession. Missing first-release values remain
  missing; vintage-derived growth is not automatically an exact rounded release print.
- [Metaculus economy/business](references/metaculus-economy-business.md): public question
  criteria and historical charts verified in Chromium. Authenticated machine-readable
  histories were not obtained. Explicit written AI/ML evaluation permission and any
  archive entitlement are separate prerequisites; do not bulk scrape around them.
- [Preseen / Knowledge Lab](references/preseen-science-technology.md): question/dependency
  design and hybrid forecasting ideas, not a downloaded macro dataset or demonstrated
  causal model. Third-by-score tournament result corroborated; integration mostly proposed.
- Potential later candidates, **not claimed available/probed**: EIA energy releases,
  NOAA/NWS forecast archives, and broader international survey archives. Do not substitute
  quarterly SPF probabilities for monthly pre-release CPI consensus.

## Credential names used or relevant

`SCHWAB_APP_KEY`, `SCHWAB_APP_SECRET`, `SCHWAB_TOKENS_FILE`; paper-only
`ALPACA_API_KEY_1`/`ALPACA_SECRET_KEY_1` and slot 3 equivalents; `FINNHUB_API_KEY`;
`KALSHI_API_KEY_ID`/`KALSHI_PRIVATE_KEY_FILE` (not needed for exercised public requests);
`HF_READ_TOKEN`; `TABPFN_API_KEY` (user supplied after license acceptance). Prior Labs'
quickstart uses `TABPFN_TOKEN`; its Jev cookbook also explicitly accepts `TABPFN_API_KEY`
via `set_access_token`. Local inference with the downloaded checkpoint needs neither.
No FRED credential was found in the initial inspection. No values belong in this inventory.
