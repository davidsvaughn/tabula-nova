# tabula-nova

Research into tabular foundation models for financial forecasting and economic probabilities.
No trading integration.

## Investigation

- [Initial hypotheses and plan](docs/logs/LOG-001.md)
- [Executed probes, failures, and baseline results](docs/logs/LOG-002.md)
- [Revised experiment priorities](docs/logs/LOG-003.md)
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

For TabPFN, first review/accept the applicable license at
https://ux.priorlabs.ai and export `TABPFN_TOKEN` in the process environment.
The script does not load `.env` automatically. Then run:

```sh
.venv/bin/python scripts/volatility_pilot.py
```

That command attempts the actual TabPFN-3.5 regressor; it does not silently
substitute another model. The initial attempt reached the license gate and
produced **no TabPFN predictions**. LimiX has not been run.

The pilot is one ETF, three chronological blocks, and 60 nonoverlapping
five-session outcomes. Its baseline result is not evidence of a trading edge.
Commercial use of either model's weights/outputs requires separate license review.
