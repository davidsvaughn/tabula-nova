# tabula-nova

Research into tabular foundation models for **macroeconomic forecasting and
superforecasting**: growth, labor, inflation, policy, productivity, forecast
combination, and conditional scenarios. Equity/volatility pilots are supporting
engineering checks. No trading integration.

## Investigation

- [Current macro/superforecasting research plan](docs/MACRO-RESEARCH.md)
- [Initial hypotheses and plan](docs/logs/LOG-001.md)
- [Executed probes, failures, and baseline results](docs/logs/LOG-002.md)
- [Revised experiment priorities](docs/logs/LOG-003.md)
- [Authorized local model results and macro-first continuation](docs/logs/LOG-004.md)
- [GDP-probability results, reference findings, and resource checks](docs/logs/LOG-005.md)
- [Controlled feature and ensemble-size ablations](docs/logs/LOG-006.md)
- [Connected-project data inventory](docs/DATA-SOURCES.md)
- Original discussions: [markets](docs/chats/001-tabpfn-for-markets.md), [foundation models](docs/chats/002-explain-tabular-foundation-models.md)

### Source references

- [Prior Labs cookbook, agent index, and model-access guidance](docs/references/priorlabs-cookbook.md)
- [Philadelphia Fed SPF and first-release macro archives](docs/references/philadelphia-fed-spf.md)
- [Preseen / Knowledge Lab: questions, scenarios, and dependencies](docs/references/preseen-science-technology.md)
- [Metaculus economy/business: examples, scoring, and access restrictions](docs/references/metaculus-economy-business.md)

## Reproduce the captured macro probability pilot

Using the verified environment below, install the spreadsheet reader and run:

```sh
uv pip install --python .venv/bin/python 'openpyxl==3.1.5'
.venv/bin/python scripts/macro_spf_pilot.py \
  --model-path /home/david/Downloads/tabpfn/tabpfn-v3.5-20260909.safetensors
```

Requires four frozen public files under ignored `data/research/spf/`; the
[SPF reference](docs/references/philadelphia-fed-spf.md) gives exact downloads,
local filenames and hashes for a clean checkout. The script does not refresh inputs.
Existing result artifacts are never overwritten; choose a fresh `--output` for a
repeat run. Controlled ablations use `--feature-set all|no-count|means` and
`--estimators 2|8`; their default filenames identify the configuration:

```sh
env OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 \
  .venv/bin/python scripts/macro_spf_pilot.py \
  --model-path /home/david/Downloads/tabpfn/tabpfn-v3.5-20260909.safetensors \
  --feature-set no-count --estimators 8
```


The pilot scored 84 next-quarter GDP-contraction events, with ten contractions.
The subsequent controlled matrix tested three feature sets with two/eight TabPFN
estimators. Direct SPF consensus retained the lowest Brier/log loss (**0.09537 /
0.32904**); the lowest TabPFN Brier was **0.13340** (means only, eight estimators).
Removing respondent count did not fix the late-period false alarms. These are
configuration-level results from an exploratory, already-seen cohort—not a general
verdict on model architecture. See LOG-005/006 for all variants and limitations.
The study uses three frozen contexts, not an NBER recession target or a certified
point-in-time backtest.

### LimiX-2 comparison

The user's `/home/david/Downloads/limix2/LimiX-2.ckpt` is the verified official
400M-parameter LimiX-2 checkpoint, not LimiX-2M. It is used in place: **keep that
directory; there is no second weight copy in this project**.

[LOG-007](docs/logs/LOG-007.md) records the separate Python 3.12 environment,
official source revision, license boundaries, cache-path fix, and frozen protocol.
With that setup:

```sh
env PYTHONHASHSEED=17 OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 \
  data/research/limix-runtime/venv/bin/python scripts/limix_spf_pilot.py \
  --model-path /home/david/Downloads/limix2/LimiX-2.ckpt
```

The command requires the frozen SPF inputs and original/full-feature eight-estimator
TabPFN result artifacts. It runs all 32 official classification pipelines, using one
query quarter per call to avoid future-query preprocessing leakage, and writes a
separate result without overwriting prior work. It checks shared-laptop memory
headroom before each query and rejects resource-altered ensembles.

Built with StableAI LimiX. Non-commercial capability research only; no commercial
rights, hosted service or endorsement is implied.

Completed: all 84 macro events with the official 32-pipeline ensemble. LimiX-2
scored **Brier 0.17031 / log loss 0.52604**, versus full-feature TabPFN-eight
**0.14069 / 0.45922** and direct SPF consensus **0.09537 / 0.32904**.
The same sparse-label, frozen-context and exploratory-cohort caveats apply.
Peak Torch-reserved VRAM was 2.47 GiB; minimum sampled available system RAM was
8.73 GiB. See LOG-007 for complete per-block results and reproducibility details.

Metaculus registration does not grant unrestricted archives or AI/ML evaluation
rights; its official guidance requires written permission. No Metaculus model
benchmark, authenticated API call, or forecast submission was made.

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
strongest baseline; see LOG-004 for the complete comparison. LimiX was not part of
this volatility pilot; its separate macro comparison is documented above.

For authenticated downloads or hosted Plus/Thinking, Prior Labs documents
`TABPFN_TOKEN`. The user's key is stored as `TABPFN_API_KEY`; map it to the SDK name
in process memory if needed. This script does not load `.env` automatically.
The public documentation index is https://docs.priorlabs.ai/llms.txt.

The pilot is one ETF, three chronological blocks, and 60 nonoverlapping
five-session outcomes. Its baseline result is not evidence of a trading edge.
Commercial use of either model's weights/outputs requires separate license review.
