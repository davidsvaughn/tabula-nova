# Prior Labs cookbook and documentation: macro research guide

Accessed 2026-10-01. Primary entrypoints: [cookbook](https://docs.priorlabs.ai/cookbook), [agent/documentation index](https://docs.priorlabs.ai/llms.txt), [quickstart](https://docs.priorlabs.ai/quickstart.md). All were publicly readable without the user's authenticated Chrome session. The index lists direct `.md` pages, sometimes redundantly; use it to discover current paths instead of guessing API names.

## Access and model distinctions

| Surface | Access / relevance | Exercised here |
|---|---|---|
| Local `tabpfn` 9.0.0, standard 3.5 | User-accepted downloaded checkpoint; explicit `model_path` works offline without a token. Same standard file supports classification and regression. | Real GPU regression and binary classification; LOG-004/005. |
| Local 3.5-Fast | Separate alpha checkpoint, different capacity/latency tradeoff. User downloaded it. | File observed; no inference. |
| Experimental multiclass checkpoint | Separate downloaded checkpoint; not needed for binary macro pilot. | File observed; no inference. |
| Hosted `tabpfn-client`, 3.5-Plus / Thinking | Different model/configuration, authentication, metering, data upload. | Documentation only; no hosted dataset upload or paid inference. |
| Forecasting-finetuned TS3 | Separate forecasting checkpoint, not one of the three downloaded 3.5 files. Compare to general 3.5 rather than assuming newer general model wins. | Documentation/source inspection, not execution. |

[Weight access](https://docs.priorlabs.ai/models/accessing-model-weights.md) documents automatic licensed downloads, offline use after download, `TABPFN_MODEL_CACHE_DIR`, and noninteractive `TABPFN_NO_BROWSER`. Direct file paths were sufficient; original files remain under `/home/david/Downloads/tabpfn`.

**The user's `TABPFN_API_KEY` name is usable.** The quickstart convention is `TABPFN_TOKEN`, while the [Jev comparison cookbook](https://docs.priorlabs.ai/cookbook/tabpfn-vs-jev.md) explicitly reads either `TABPFN_API_KEY` or `TABPFN_TOKEN` and calls `tabpfn_client.set_access_token(value)`. Therefore there is no reason to rename `.env`: explicitly pass the value to `set_access_token` for the hosted SDK, or map it in process memory when a component expects `TABPFN_TOKEN`. Loading `.env` is separate from choosing the key name. Never print the value. The locally exercised model paths need neither key nor mapping.

## Highest-value recipes for macro forecasting

### 1. Full predictive distributions, not just point estimates

Sources: [capability](https://docs.priorlabs.ai/capabilities/predictive-distribution.md), [cookbook entry](https://docs.priorlabs.ai/cookbook/predictive_distribution.md).

The capability page documents `predict(X, output_type="full")` with means, medians, quantiles, criterion and logits; quantiles can be requested directly with `output_type="quantiles"` and a specified quantile list. The distribution uses a learned bar/bin representation. These are documented interfaces; the pilots so far used point regression and classifier probabilities, not the full regression-distribution path.

**Proposed macro use:** predict the continuous CPI/payroll/GDP first-print distribution once, then derive multiple nested threshold probabilities from the same CDF. This shares information across strikes and imposes threshold monotonicity, unlike unrelated binary models. Keep each release grouped in evaluation. Score the distribution with CRPS/quantile loss/interval coverage and matched contracts with Brier/log loss; report tail and out-of-support behavior.

Settlement can be based on a **rounded published number**, not an unrounded latent value. `P(print > 0.3)` must honor that definition: modeling rounded prints directly or explicitly applying the rounding map is different from merely evaluating an unrounded CDF at 0.3. Probability mass at ties, strict versus inclusive comparisons, and missing releases require explicit treatment.

Model uncertainty is not proof of empirical calibration under macro regime shifts. Likewise, exponentiating a predicted mean log variance is not the mean variance; a distributional volatility extension would need the appropriate transformed expectation and a tail-integrability check, not an ad hoc bias correction chosen after scoring.

### 2. Grouped validation and Thinking objectives

Sources: [grouped comparison](https://docs.priorlabs.ai/cookbook/grouped_data_model_comparison.md), [Thinking experiment](https://docs.priorlabs.ai/cookbook/experiment_with_thinking_mode.md).

The grouped recipe uses 1,080 measurements from only 72 mice, with whole animals held out. The important transferable point is choosing the real generalization unit: for macro, the underlying release, overlapping annual target, country/episode, or question family—not the row/strike/update snapshot.

Thinking examples expose `thinking_effort`, `thinking_metric`, and, with client >=0.6.0, `group_col`. For probability forecasts, log loss is more aligned with the objective than ROC-AUC. A grouping parameter does **not** automatically enforce chronology, label availability, purging, or a matching forecast horizon. Outer chronological evaluation remains the researcher's responsibility; hosted internal search must also honor temporal restrictions before being used for claims.

These recipes were inspected, not executed. Do not copy their package upgrades wholesale into the working local GPU environment.

### 3. Forecasting wrapper versus explicit event tables

Sources: [forecasting capability](https://docs.priorlabs.ai/capabilities/forecasting.md), [time-series cookbook](https://docs.priorlabs.ai/cookbook/tabpfn_regressor_for_time_series.md), [wrapper changelog](https://github.com/PriorLabs/tabpfn-time-series/blob/main/CHANGELOG.md).

The wrapper reframes history/time features as regression and emits point/quantile forecasts. Earlier source inspection in LOG-001–003 found that the high-level pipeline accepts target history and future-known dynamic inputs but drops past-only and static covariates; separate series' predictions are not automatically a coherent joint macro scenario distribution. Rich release-time tables remain necessary for mixed-frequency vintages, news evidence, survey disagreement, and asynchronous publication clocks.

The current changelog identifies **1.3.0 on 2026-09-16**, requiring local `tabpfn>=9` / client `>=0.5.3`, and recommends comparing general 3.5 with forecasting-finetuned TS3. The README news date was September 15; record the discrepancy rather than invent a single release timestamp. The documented TS3 filename is `tabpfn-v3-regressor-v3_20260506_timeseries.ckpt`, selected through `TabPFNTSPipeline(..., tabpfn_model_config={"model_path": ...})`.

**Documentation drift:** the general forecasting capability page still advertises a compact <20M-parameter model and an older predictor example. Do not apply that size claim to the downloaded 835 MiB 3.5 checkpoint or infer the current wrapper's covariate contract from broad marketing prose. Pin version and inspect the executing implementation. Neither wrapper nor TS3 was installed/run in this continuation.

### 4. Raw mixed features and the division of labor with Jev/LLMs

Sources: [feature guidance](https://docs.priorlabs.ai/improving-performance/feature-engineering.md), [Jev comparison](https://docs.priorlabs.ai/cookbook/tabpfn-vs-jev.md).

The docs recommend raw DataFrames with categories, text, missingness and true datetime columns rather than mandatory one-hot encoding/scaling/imputation. This does not remove the need for domain definitions: publication lags, units, transforms, availability, horizons, and event grouping still determine whether a forecast is valid.

The Jev recipe compares a 44-example Jev context with a much larger TabPFN-Plus training pool on the same 300 held-out fraudulent-job postings (15 positives). It is a useful routing/mixed-text example connected to this project's JevTrader interests, **not a macroeconomic skill result**, matched-training-size comparison, or a reason to copy its random row split into a temporal benchmark. Its Brier discussion is simplified: Brier measures overall probability quality, not calibration alone.

**Proposed division of labor:** use LLMs for sourced question decomposition, evidence extraction and counterarguments; use simple statistical models and TabPFN for structured probability estimation/combination. Score raw LLM, statistical-only and hybrid variants separately on contemporaneously recorded predictions. Today's LLM processing old articles can know the outcome through pretraining even when retrieval is date-filtered.

## Decisions

1. Keep the working local standard 3.5 environment; no need for hosted authentication to continue.
2. Treat scores as configuration-specific. [LOG-006](../logs/LOG-006.md) now records the completed two/eight-estimator macro sensitivity across three feature sets; none beats consensus overall. Fast/Thinking remain untested. Exploratory variants do not replace original unfavorable results or provide an untouched confirmation cohort.
3. Prioritize broad macro distributions and forecast combination. Public SPF and first-release archives provide an immediately exercised path beyond stock prices.
4. Preserve conventional baselines and public consensus. Neither cookbook results nor vendor capability claims establish superiority on this project's tasks.
5. Keep Metaculus permission separate: [its reference note](metaculus-economy-business.md) documents explicit AI/ML evaluation restrictions. A Prior Labs key grants no rights to third-party forecast archives.
