# Tabula Nova

## Purpose and current state

Investigate TabPFN-3.5, LimiX-2, and strong conventional baselines for **broad
macroeconomic forecasting and superforecasting**: growth, labor, inflation, policy,
productivity, and conditional scenarios. Stock/volatility prediction is a supporting
engineering check, not the organizing goal. This is research, not a trading system.
Start with `README.md`, `docs/DATA-SOURCES.md`, and the latest numbered logs.
Original supplied discussions are in `docs/chats/`; their claims require verification.

## Logs and checkpoints

- Keep detailed investigation logs in **`docs/logs/LOG-NNN.md`**, increasing numbers.
  Check the existing sequence before creating a log. Record hypotheses before scores,
  commands, sources, failures, results, limitations, and decisions that change the plan.
- **The newest numbered LOG must always contain a clear `## Next steps` section.**
  List the next executable actions in order, prerequisites/access limits, and the
  evidence needed to advance. Update it before each checkpoint and handoff; a link
  to the general roadmap is not a substitute. Distinguish completed work from plans.
- Clearly distinguish proposed work, documented past results, freshly measured results,
  and inference. Never report a model score unless that model actually ran.
- **Commit and push each completed, verified slice immediately.** Separate protocol/
  acquisition, parser/integration, and result checkpoints; do not accumulate them into
  one end-of-phase commit. Push each commit before starting the next lengthy slice.
- **Checkpoint cadence: target 10–15 minutes of active work between remote checkpoints.**
  At 15 minutes, checkpoint any cohesive, verified work already complete. If code is
  not ready, commit a sanitized latest-LOG progress checkpoint stating completed
  evidence, outstanding work and the concrete blocker; never commit broken code merely
  to meet the clock. Checkpoint the frozen protocol before a lengthy acquisition/run,
  then record and push results promptly afterward. Do not interrupt a running model
  just for a timer or stage files another agent is still editing.
- Use explicit file staging and keep commits cohesive. Do not force-push, rewrite user
  history, include unrelated user edits or stage secrets/raw licensed data. A local
  commit is not a remote checkpoint: report push failures immediately without claiming
  success, resolve them when safe, and include the successfully pushed hash in updates.
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
- Metaculus public reading is useful, but its current API guidance requires prior
  written permission for AI/ML training/evaluation/development. Registration or an
  API token does not grant unrestricted historical data rights. See its reference note.

## Model access and runtime

- Check the current official code/checkpoint versions and licenses. Current TabPFN and
  LimiX weights/outputs have non-commercial restrictions. Do not accept legal terms or
  bypass access gates on the user's behalf, and do not assume research-to-trading use is
  permitted. LimiX specifically restricts commercially motivated research.
- The user accepted the TabPFN license and supplied local weights under
  `/home/david/Downloads/tabpfn`. Explicit `model_path` inference works without a key.
  Authenticated downloads and hosted inference use `TABPFN_TOKEN`; the user stores
  their key as `TABPFN_API_KEY` in `.env`. Map it in process memory only when needed.
- User-supplied LimiX-2 weights are at `/home/david/Downloads/limix2/LimiX-2.ckpt`;
  no second project copy exists. Do not delete/move them casually. SHA256 was matched
  to the official Hugging Face blob before pickle loading; see LOG-007.
- LimiX uses its own Python 3.12 environment and pinned source under ignored
  `data/research/limix-runtime/`; do not replace TabPFN's working environment.
  Preserve/apply `patches/limix-local-cache.patch` to avoid the upstream hardcoded
  `/mnt/public` cache path. Attribution: Built with StableAI LimiX.
- LimiX v2 classification preprocesses concatenated training/query features.
  For historical macro forecasts, pass one contemporaneous query per call, not an
  entire future evaluation block. Do not silently accept a resource-reduced ensemble.
- Local verified GPU stack: RTX 3080 Laptop 16GB, Torch `2.10.0+cu128`. An unconstrained
  install selected CUDA 13 Torch and failed driver initialization. Prefer a compatible
  pinned environment, never a system driver change just to run a pilot.
- Disable optional model telemetry for research. Prefer local inference; do not upload
  brokerage/private datasets to hosted services without authorization.
- `scripts/volatility_pilot.py` is a frozen historical pilot, not a live forecasting CLI.
  `--baselines-only` explicitly omits TabPFN; default execution never silently falls back.
  It reads process environment, not `.env` automatically.
- This laptop is shared with other agents. Check total CPU/load, available RAM,
  active swap-in/out, free VRAM, GPU temperature/utilization, and disk before heavier
  runs and between experiments (`uptime`, `free -h`, `vmstat`, `nvidia-smi`, `df`).
  Continue useful work; avoid overlapping our own GPU fits or loading multiple large
  checkpoints unnecessarily. Pause new allocations if headroom collapses or sustained
  swapping/thermal pressure appears. Never kill other agents' processes or alter
  system/driver settings. High occupied swap alone is not evidence of active thrashing.

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
