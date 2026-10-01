Shared ChatGPT conversation "Explain Tabular Foundation Models", 2026-10-01 06:41 UTC to 2026-10-01 06:42 UTC, model `gpt-6-astra-wm`.
Source: https://chatgpt.com/share/6abe7579-78e0-83ea-9d72-28582fca9a21
Transcribed 2026-10-01: every user and assistant message verbatim, with the tool steps shown between them in italics.

Q: Yes—with one adjustment: **“never used before” overstates the novelty**, since TabPFN forecasting work dates to 2024. “An emerging approach whose financial applications remain largely unproven” captures the excitement more accurately. [GitHub](https://github.com/PriorLabs/tabpfn-time-series?utm_source=chatgpt.com)

Paste this into a new chat:

Explain two recently released tabular foundation models—**TabPFN-3.5 and LimiX-2**—and why they could be exciting for **time-series prediction, financial forecasting, and economic superforecasting**.

Start by reading these primary sources and checking current official documentation:

- TabPFN-3.5: [https://arxiv.org/abs/2609.17895](https://arxiv.org/abs/2609.17895)
- LimiX-2: [https://arxiv.org/abs/2609.17488](https://arxiv.org/abs/2609.17488)
- TabPFN time-series: [https://github.com/PriorLabs/tabpfn-time-series](https://github.com/PriorLabs/tabpfn-time-series)
- TabArena leaderboard: [https://huggingface.co/spaces/TabArena/leaderboard](https://huggingface.co/spaces/TabArena/leaderboard)

Write a clear, engaging explanation for an intelligent reader who understands basic machine learning but is unfamiliar with tabular foundation models. Build intuition before introducing technical details.

Please cover:

1. **The conceptual breakthrough.** Explain how pretraining on vast collections of synthetic prediction problems lets a transformer learn transferable statistical inference. Contrast fitting a separate model to each dataset with supplying labeled examples as context to a pretrained model. Explain why this differs from asking a language model to guess numbers.
2. **What distinguishes the two models.** Explain TabPFN’s prior-data fitted approach and LimiX-2’s context-conditional masked modeling and emphasis on joint relationships among variables. Describe what each new release adds, what benchmark results actually establish, and how leaderboard configurations affect comparisons.
3. **Why this opens interesting forecasting possibilities.** Explain how a time series can become a table of lagged observations, external predictors, calendar information, and future targets. Distinguish dedicated forecasting tools and demonstrated results from plausible applications of a general tabular model. Discuss whether these models could help when historical data are limited and useful relationships involve nonlinear interactions.
4. **Financial applications.** Explore earnings surprises, post-earnings returns, volatility, drawdown risk, and event-conditioned stock prediction. Explain why predicting raw stock prices is a different challenge from forecasting a recurring event with informative features.
5. **Economic superforecasting and prediction markets.** Explore inflation releases, employment reports, central-bank decisions, and recurring Kalshi event families. Pay particular attention to combining market probabilities, economist consensus, statistical models, and human or LLM forecasts. Could these models learn when each source deserves more weight and produce better-calibrated probabilities?
6. **What is new—and what remains unexplored.** Convey the potential significance of this emerging approach without claiming it has never been used for time series: earlier TabPFN forecasting work exists. Identify which capabilities have evidence, which applications are reasonable hypotheses, and where financial or economic forecasting evidence is still missing. Explain what would make this a meaningful new research direction.
7. **A concrete first experiment.** Propose one manageable economic forecasting experiment comparing both models with logistic regression, boosted trees, and market or consensus forecasts. Explain chronological testing, separating related events, using information available at the forecast date, and measuring Brier score, log loss, and calibration. Distinguish better forecasts from profitable trading after costs.

Make the opportunity tangible with examples. Be enthusiastic where the evidence supports enthusiasm, but clearly separate demonstrated advances from speculative potential. Cite primary sources, and do not assume that tabular benchmark leadership establishes a financial forecasting edge.

---

A:

I’ll check the papers, forecasting repository, and leaderboard, then separate demonstrated results from promising financial applications.

*[thinking: Searched the web and ⁨used⁩ ⁨GitHub⁩]*

The repository confirms that TabPFN forecasting predates these releases and now defaults to 3.5. One practical detail matters: its forecasting wrapper drops past-only external predictors, so the financial experiments you describe would be better built as explicit prediction tables.

*[thinking: Searched the web]*
*[Worked for 57s]*

**The exciting possibility is that a model can learn how to learn from a small table—and then apply that ability to a new forecasting problem.** TabPFN-3.5 and LimiX-2 offer strong evidence that this approach works for tabular prediction. Whether it produces an edge in financial or economic forecasting remains an open empirical question.

Imagine having only 150 historical inflation releases, each accompanied by economic indicators and forecasts. That is a small dataset for training a deep network from scratch. But a pretrained model could arrive already equipped with useful statistical expectations about nonlinear relationships, irrelevant features, noise, and missing information. Your 150 examples would tell it which relationships appear relevant here.

That is the opportunity worth investigating.

**Learning statistical inference from synthetic problems**

In conventional supervised learning, you choose a model and fit its parameters to a particular dataset. Repeat that process for every new problem.

The foundational PFN idea moves much of that learning into pretraining:

1. Generate a synthetic prediction problem.
2. Show a transformer some labeled examples.
3. Hide another example’s label and ask it to predict.
4. Repeat across a vast range of generated problems.

The resulting network learns an approximate inference procedure: given a dataset and a new input, produce a predictive distribution. Its weights can stay fixed while the labeled examples supplied as context change. This is the central idea behind *Prior-Data Fitted Networks*.  ([arxiv.org](https://arxiv.org/abs/2112.10510?utm_source=chatgpt.com))

An analogy is a statistician who has solved countless simulated problems before encountering yours. They still need your observations, but they do not need to rediscover every useful statistical principle.

The synthetic generator matters enormously. It determines which kinds of relationships the model has practiced recognizing. Synthetic data do not manufacture information about tomorrow’s economy; they supply an inductive bias that may help extract information from limited observations.

This differs from asking a language model to guess a number. The model’s inputs are structured observations, and its training directly rewards statistical prediction across datasets. A transformer is the computational architecture; natural-language generation is not the task.

**What the two releases contribute**

| Model | Central approach | What the new release adds |
|---|---|---|
| **TabPFN-3.5** | Predict a designated target from features and labeled context: \(p(y\mid x,D)\). | Better numerical encodings, including within-column ranks; greater capacity; shared classification/regression training; broader synthetic priors; several speed and inference configurations. |
| **LimiX-2** | Learn relationships across variables through context-conditional masked modeling, targeting joint structure \(p(x,y\mid D)\). | Scaled model and synthetic data generation, revised cell-level processing, and richer task representations. |

TabPFN-3.5 reports strong tabular results, including harder distribution-shift settings. However, tuned neural baselines still lead on some large temporal and grouped subsets. Its forecasting evaluation is particularly informative: the general checkpoint, without time-series fine-tuning, ranks **sixth of 29 methods on fev-bench**, improving over the earlier specialized TabPFN-TS-3 checkpoint.  ([arxiv.org](https://arxiv.org/html/2609.17895v2?utm_source=chatgpt.com))

LimiX-2’s masked objective asks the model to infer different hidden variables from available evidence. Conceptually, it practices understanding a table’s interconnected dependencies rather than only one designated output. The paper reports leading results among its comparisons on TabArena, TALENT, and BCCO, plus causal-skeleton recovery experiments. Its TabArena comparisons include TabPFN-3, not a direct comparison against 3.5.  ([arxiv.org](https://arxiv.org/html/2609.17488v1?utm_source=chatgpt.com))

The causal results deserve a careful interpretation: recovering dependency structure in benchmark settings does **not** establish that the model can identify the causal effects of monetary policy from observational economic data.

The current LimiX repository provides a roughly 400-million-parameter LimiX-2 checkpoint and classification, regression, and imputation interfaces. LimiX-2 and the much smaller **LimiX-2M** are different models.  ([GitHub](https://github.com/limix-ldm/LimiX/?utm_source=chatgpt.com))

Leaderboard leadership also needs a configuration attached to it. Default models, tuned models, ensembles, and systems with larger inference budgets answer different questions. TabArena explicitly incorporates tuning and ensembling into its evaluation framework.  ([github.com](https://github.com/autogluon/tabarena?utm_source=chatgpt.com)) I could read the papers and leaderboard documentation, but could not retrieve the live leaderboard’s underlying CSV, so I cannot independently certify today’s exact ordering.

**How a forecasting problem becomes a table**

Suppose the goal is predicting an inflation release. Construct one row per historical forecast date:

| Information in the row | Example |
|---|---|
| Lagged observations | Previous inflation readings and recent changes |
| External predictors | Energy-price changes, wage indicators, available surveys |
| Calendar information | Month, season, forecast horizon |
| Existing forecasts | Economist consensus and a statistical nowcast |
| Target | The subsequently released inflation value, or whether it exceeded a threshold |

At prediction time, supply historical rows with known outcomes and a new row whose outcome is hidden.

A stock task can use the same structure: one row per company earnings event, with a future return or volatility measure as the target.

**Converting time series to supervised tables is established practice. The emerging contribution is the pretrained inference engine applied to those tables.**

There is already direct evidence for this bridge. Earlier TabPFN-TS work combines temporal features with a tabular model for point and probabilistic forecasting; the repository records workshop work in 2024.  ([arxiv.org](https://arxiv.org/abs/2501.02945?utm_source=chatgpt.com))

There is also a practical distinction between a general tabular model and a packaged forecasting pipeline. The current TabPFN-TS wrapper uses target history and known-future covariates, drops past-only dynamic and static covariates, and handles multiple targets as separate univariate forecasts. An explicit event table would therefore be a better starting point for the richer financial applications discussed here.  ([GitHub](https://github.com/PriorLabs/tabpfn-time-series?utm_source=chatgpt.com))

The small-data hypothesis is attractive: perhaps pretraining helps distinguish a meaningful nonlinear interaction from noise when historical examples are scarce. But scarcity remains scarcity. Fifty observations cannot reliably establish every interaction, and a strong pretrained bias can be wrong when a new economic regime differs from its assumptions.

**Where financial applications become interesting**

The following are research hypotheses, not demonstrated capabilities of these releases:

| Application | Possible target | Why the formulation is useful |
|---|---|---|
| Earnings surprises | Probability earnings exceed a precisely defined consensus | Repeated events with comparable inputs |
| Post-earnings returns | Probability of positive sector-adjusted return over the next five sessions | Tests the response to news, conditional on expectations and initial reaction |
| Volatility | Future realized volatility or probability of exceeding a threshold | Focuses on movement magnitude |
| Drawdown risk | Probability of a specified decline within a fixed horizon | Directly connects prediction to a risk event |
| Event-conditioned stock prediction | Return distribution following a specified event class | Makes the information cutoff and comparison population explicit |

For example, a hypothesis might be:

> A positive earnings surprise predicts subsequent returns differently depending on valuation, guidance, and how much the stock already moved.

A tabular foundation model could potentially infer that interaction from historical events. Boosted trees can also learn it; the research question is whether pretraining improves generalization with the available sample.

Predicting a raw future price is a different objective. A forecast close to today’s price may achieve low numerical error while adding almost no information about future returns. Event-based targets make it easier to ask whether the model learned something useful beyond an obvious baseline.

They also make leakage easier to identify: an earnings surprise belongs in a **post-release** forecast, but not in a forecast made before the announcement.

**Economic superforecasting: learning how to combine forecasters**

A particularly interesting hypothesis is to use these models as **conditional forecast combiners**.

For an inflation threshold, payroll release, or central-bank decision, provide:

- Market-implied probability.
- Economist consensus and forecast dispersion.
- Statistical-model forecasts.
- Timestamped human or LLM probabilities.
- Context such as recent surprises, forecast age, and market liquidity.

Then predict the resolved outcome.

A conventional average gives sources fixed weights. A learned combiner could potentially discover that a source is useful under particular conditions—for example, that a market quote is less informative when stale, or that a statistical forecast adds information when consensus dispersion is unusually wide.

Conceptually:

\[
P(\text{event}\mid
\text{source forecasts},\ \text{economic context})
\]

This need not literally be a weighted average. It could learn interactions and systematic probability corrections.

Recurring prediction-market event families are appealing because they offer repeated, similarly defined questions. But inflation releases, employment reports, and rate decisions should not automatically be pooled as interchangeable observations. Their mechanisms, horizons, and settlement definitions differ.

**Better calibration is possible, but it is not guaranteed.** If a system issues 70% probabilities, approximately 70% of comparable events should occur over enough observations. Producing probabilities—or being pretrained with a probabilistic objective—does not ensure that property after a regime shift.

Calibration alone is also insufficient: always forecasting the historical event rate can be calibrated yet uninformative. The goal is calibrated probabilities that meaningfully distinguish more likely events from less likely ones.

Another complication is shared information. Economists, markets, humans, and LLMs may all react to the same release. Their agreement is not equivalent to independent evidence. A useful combiner must learn incremental value, not simply count agreeing sources.

**What remains to be demonstrated**

The sources support strong general tabular prediction and an established TabPFN forecasting pathway. They do not establish that either new model:

- Beats well-constructed economic consensus forecasts prospectively.
- Adds information beyond a contemporaneous prediction-market price.
- Maintains calibration through financial regime changes.
- Produces profitable trades after execution costs.

Nor would I call forecast combination itself new. The meaningful research direction is testing whether **synthetically pretrained inference improves small-sample, context-dependent forecast combination**, compared with simpler methods under the same information constraints.

**A manageable first experiment**

I would start with one question:

> At a fixed time on the business day before each US CPI release, what is the probability that the initially reported headline monthly inflation rate exceeds 0.3%?

Fix the series, seasonal-adjustment convention, rounding, and strict-versus-inclusive threshold before collecting results.

Use a compact feature set: recent inflation readings, available energy-price changes, one statistical nowcast, and a timestamped economist consensus. Add a matching market probability wherever a valid historical quote exists.

Compare these methods:

| Method | Purpose |
|---|---|
| Historical event frequency | Minimal baseline |
| Consensus converted into a probability | Strong external forecast baseline |
| Market probability, when available | Tests incremental information beyond market expectations |
| Regularized logistic regression | Simple learned relationship |
| Boosted trees | Strong nonlinear tabular baseline |
| TabPFN-3.5 | Pretrained conditional prediction |
| LimiX-2 | Alternative pretrained structured-data model |

A point consensus is not a probability. Convert it using a distribution of **past** consensus errors, estimated only from releases available before each forecast date. Generate statistical-model forecasts in the same rolling manner.

Run each learned method first with economic features, then with external forecasts added. That distinguishes forecasting the release from learning to improve existing forecasts.

The evaluation should follow these rules:

1. **Walk forward chronologically.** Use earlier releases as context or training data, forecast the next release, record the prediction, then advance. Tune only within earlier periods.

2. **Reconstruct what was actually known.** Use historical data vintages rather than today’s revised series. ALFRED supports retrieving information known at a past date; intraday cutoffs still require release-time checks.  ([fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/fred/realtime_period.html?utm_source=chatgpt.com))

3. **Keep related events together.** If later expanding to several thresholds or forecast horizons, keep every row from the same release in the same evaluation block. Twenty thresholds for one CPI report do not create twenty independent economic events.

4. **Use identical comparison samples.** Evaluate market-inclusive methods on the same months with valid quotes. Report the longer consensus-only history separately.

5. **Avoid retrospective LLM contamination.** A modern LLM asked about an old release may already know its outcome. Use genuinely archived forecasts or collect new forecasts prospectively.

6. **Report probability quality and uncertainty.** Use Brier score, log loss, and reliability plots, with uncertainty estimated by resampling release dates or chronological blocks. Monthly data provide relatively few independent tests, so small apparent wins require caution.

For a binary outcome \(y\) and predicted probability \(p\):

\[
\text{Brier score}=\frac{1}{N}\sum_i(p_i-y_i)^2
\]

\[
\text{Log loss}
=-\frac{1}{N}\sum_i
\left[y_i\log p_i+(1-y_i)\log(1-p_i)\right]
\]

Lower is better for both. Log loss especially penalizes confident mistakes. Any recalibration must also be fitted on earlier predictions, never on the final test outcomes.

The most persuasive result would be a repeatable improvement over consensus, market probability, and simpler models across successive unseen releases. Only after establishing that should a trading simulation ask whether the improvement exceeds bid–ask spreads, fees, slippage, and executable-price constraints. **A better probability forecast is a scientific result; a profitable trading strategy is a further result that needs its own evidence.**

Sources: [arxiv.org](https://arxiv.org/abs/2112.10510?utm_source=chatgpt.com), [GitHub](https://github.com/limix-ldm/LimiX/?utm_source=chatgpt.com), [fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/fred/realtime_period.html?utm_source=chatgpt.com)
