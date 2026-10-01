# tabula-nova

Research into tabular foundation models for **macroeconomic forecasting and
superforecasting**: growth, labor, inflation, policy, productivity, forecast
combination, and conditional scenarios. Equity/volatility pilots are supporting
engineering checks. No trading integration.

## Investigation

- [Initial hypotheses and plan](docs/logs/LOG-001.md)
- [Executed probes, failures, and baseline results](docs/logs/LOG-002.md)
- [Revised experiment priorities](docs/logs/LOG-003.md)
- [Authorized local model results and macro-first continuation](docs/logs/LOG-004.md)
- [Connected-project data inventory](docs/DATA-SOURCES.md)
- Original discussions: [markets](docs/chats/001-tabpfn-for-markets.md), [foundation models](docs/chats/002-explain-tabular-foundation-models.md)

## Reproduce the captured volatility pilot

The local `data/research/` directory contains the Schwab SPY payload, request/hash
manifest, baseline predictions, API probes, and archive audit. Vendor data and
credentials are ignored by Git; a checkout alone does not include the input.
See LOG-002 for the exercised acquisition call.

The verified environment uses Python 3.11, TabPFN 9.0.0, Torch 2.10.0+cu128,
numpy 2.4.6, pandas 3.0.6, and scikit-learn 1.9.1:

```sh
uv venv --python 3.11 .venv
uv pip install --python .venv/bin/python 'tabpfn==9.0.0' 'numpy==2.4.6' 'pandas==3.0.6' 'scikit-learn==1.9.1'
uv pip install --python .venv/bin/python 'torch==2.10.0' --index-url https://download.pytorch.org/whl/cu128
.venv/bin/python scripts/volatility_pilot.py --baselines-only
```

The Torch pin matters on this workstation: the unconstrained CUDA 13 build failed
driver initialization. The script freezes the last completed session to
2026-09-30 and reports the input hash; it is a reproducible historical pilot,
not a rolling live forecaster.

The user has accepted the license and supplied local weights. Local inference needs
no API key when using the existing checkpoint:

```sh
.venv/bin/python scripts/volatility_pilot.py \
  --model-path /home/david/Downloads/tabpfn/tabpfn-v3.5-20260909.safetensors \
  --output data/research/volatility_pilot_tabpfn35.json
```

This command successfully ran TabPFN-3.5 on all three folds. Ridge remained the
strongest baseline; see LOG-004 for the complete comparison. LimiX has not been run.

For authenticated downloads or hosted Plus/Thinking, Prior Labs documents
`TABPFN_TOKEN`. The user's key is stored as `TABPFN_API_KEY`; map it to the SDK name
in process memory if needed. This script does not load `.env` automatically.
The public documentation index is https://docs.priorlabs.ai/llms.txt.

The pilot is one ETF, three chronological blocks, and 60 nonoverlapping
five-session outcomes. Its baseline result is not evidence of a trading edge.
Commercial use of either model's weights/outputs requires separate license review.
