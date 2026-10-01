# Tabula Nova

## Purpose and current state

Investigate TabPFN-3.5, LimiX-2, and strong conventional baselines for financial
forecasting and economic probabilities. This is a research repository, not a trading
system. Start with `README.md`, `docs/DATA-SOURCES.md`, and the latest numbered logs.
Original supplied discussions are in `docs/chats/`; their claims require verification.

## Logs and checkpoints

- Keep detailed investigation logs in **`docs/logs/LOG-NNN.md`**, increasing numbers.
  Check the existing sequence before creating a log. Record hypotheses before scores,
  commands, sources, failures, results, limitations, and decisions that change the plan.
- Clearly distinguish proposed work, documented past results, freshly measured results,
  and inference. Never report a model score unless that model actually ran.
- **Commit and push frequently at meaningful completed milestones.** Use explicit file
  staging; keep commits cohesive. Do not wait for the whole research program to finish.
  Do not force-push, rewrite user history, or include unrelated user edits. Report push
  failures without claiming a remote checkpoint exists.
- Update README links when adding a major research entrypoint. Preserve original chats.

## Secrets, data, and external projects

- `.env` contains credentials. Load only as needed; never print values, commit it, log
  authorization URLs, export private keys, or dump configuration containing secrets.
- `.venv/` and `data/` are local and ignored. Preserve research payload provenance and
  hashes locally; commit sanitized methodology/results in logs. Respect vendor data
  redistribution terms before adding raw data to version control.
- Connected projects are read-only research sources unless the user specifically asks
  to modify them:
  - `/home/david/code/davidsvaughn/cedar/AlphaPilot`
  - `/home/david/code/davidsvaughn/cedar/alpha-claw`
  - `/home/david/code/davidsvaughn/cedar/JevTrader`
- No orders, account transfers, collector restarts, database migrations, paid Seeking
  Alpha recaptures, or forced OAuth refreshes for a data investigation. Use paper-market
  data credentials rather than real-account credentials. Avoid account endpoints.
- Schwab tokens belong to alpha-claw. Its `SCHWAB_TOKENS_FILE` default is CWD-relative;
  use the existing provider from alpha-claw's CWD or an absolute token path. Do not create
  another token file here. Normal SDK access-token renewal may update the existing file.
- The DB/SA-ingest runtime moved to AlphaPilot; alpha-claw crons and prediction-market
  collectors were stood down. Existing code does not imply a currently running feed.

## Model access and runtime

- Check the current official code/checkpoint versions and licenses. Current TabPFN and
  LimiX weights/outputs have non-commercial restrictions. Do not accept legal terms or
  bypass access gates on the user's behalf, and do not assume research-to-trading use is
  permitted. LimiX specifically restricts commercially motivated research.
- TabPFN 9.0.0 local downloads require explicit Prior Labs license authentication and
  `TABPFN_TOKEN`; an HF token and ungated HF metadata do not satisfy this gate.
- Local verified GPU stack: RTX 3080 Laptop 16GB, Torch `2.10.0+cu128`. An unconstrained
  install selected CUDA 13 Torch and failed driver initialization. Prefer a compatible
  pinned environment, never a system driver change just to run a pilot.
- Disable optional model telemetry for research. Prefer local inference; do not upload
  brokerage/private datasets to hosted services without authorization.
- `scripts/volatility_pilot.py` is a frozen historical pilot, not a live forecasting CLI.
  `--baselines-only` explicitly omits TabPFN; default execution never silently falls back.
  It reads process environment, not `.env` automatically.

## Research invariants

- Freeze target, horizon, information cutoff, universe and metrics before inspecting
  scores. A feature's reference date is not its publication/availability timestamp.
- Use chronological evaluation; train only on labels resolved before decision time;
  purge overlapping label windows. Fit transforms/tuning/calibration using past data.
- Group related releases, thresholds, news items and tickers. Count independent events,
  not just rows. Thousands of snapshots do not create thousands of economic outcomes.
- Macro targets require original releases; features require as-of vintages. Never use
  today's revised CPI index to claim a first-release probability backtest. Keep rounding,
  strict/inclusive thresholds, release delays and missing releases explicit.
- Match prediction-market settlement rules exactly. `Above -0.3%` and `Above 0.3%` are
  different contracts. Query both live/historical tiers using the current archive cutoff.
  Candle prices/volumes can be decimal strings; no future interpolation or stale-price
  assumptions. A midpoint is not an executable quote with depth.
- Archived LLM forecasts generated after an outcome are not contemporaneous forecasts.
  Stacked predictors require out-of-sample base forecasts. Calibrate on past predictions.
- Treat survivor universes, backfilled news text, synthetic receipt clocks and updated
  historical bars as explicit validity limits. Never use future reaction/volume columns
  as predictors in event tables.
- Compare identical eligible events against simple and strong conventional baselines.
  Use Brier/log loss/calibration for probabilities and appropriate volatility losses.
  Quantify uncertainty in confirmatory studies; tiny exploratory wins are not evidence
  of an edge. Prediction improvement and after-cost trading profit are separate claims.
- Exercise real data/model paths for verification. Record failures precisely; no fake
  scores, silent model substitutions, fabricated labels or claims of complete coverage.
