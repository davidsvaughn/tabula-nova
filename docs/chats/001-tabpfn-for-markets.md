Shared ChatGPT conversation "TabPFN For Markets", 2026-10-01 03:28 UTC to 2026-10-01 14:40 UTC, model `gpt-6.1-sol-wm`.
Source: https://chatgpt.com/share/6abe7525-7204-83e9-9b70-3a83e4519ac2
Transcribed 2026-10-01: every user and assistant message verbatim, with the tool steps shown between them in italics.
The last two exchanges (choosing a name for this repo) are left out on purpose.

Q: can you explain the recent advances in deep learning and transformer networks for tabular data, TabPFN? what types of problems does this work well on? can it be used to help with stock market prediction, or kalshi?

---

A:

I’ll check the recent TabPFN research, then explain how it works and where it might help with stock prediction or Kalshi probabilities.

*[thinking: Searched the web]*
*[Worked for 21s]*

**TabPFN is a real advance: a transformer that learns how to learn from tables.** It is worth testing for stock and Kalshi prediction, especially when you have a modest dataset with useful features. Its benchmark success, however, does not establish a trading edge.

The surprising part is that **the training examples are entire prediction problems**, rather than individual rows.

### How it works

With conventional supervised learning, you give a model a dataset and optimize its parameters to predict the labels:

\[
D_{\text{train}}\longrightarrow \text{fit a model}\longrightarrow \text{predict new rows}
\]

TabPFN moves much of that learning into a huge pretraining phase:

1. Generate millions of synthetic datasets with different underlying relationships.
2. For each dataset, show the transformer some rows **with their labels**.
3. Ask it to predict labels for other rows.
4. Update its weights based on how well it solves those prediction tasks.

The synthetic generators include varied nonlinear relationships, feature interactions, noise, and causal structures. These are simulated statistical worlds, rather than an LLM inventing spreadsheet rows. The 2025 Nature paper demonstrated strong classification and regression performance on small and medium tables.  ([nature.com](https://www.nature.com/articles/s41586-024-08328-6?utm_source=chatgpt.com))

At deployment, the pretrained network receives your labeled examples and new unlabeled rows together:

\[
p_\theta(y_{\text{new}}\mid x_{\text{new}},D_{\text{train}})
\]

**Your dataset becomes its context.** In the standard in-context workflow, it adapts its predictions without updating its network weights. This was the central idea of the original TabPFN.  ([arxiv.org](https://arxiv.org/abs/2207.01848?utm_source=chatgpt.com))

An analogy: instead of training a new statistician for every dataset, you train one statistician on millions of miniature statistical problems, then hand it a new table.

### Why transformers help here

Attention lets a prediction depend on relationships among the examples supplied in context. In TabPFN v2, the architecture attends across rows and across features, allowing it to identify useful patterns within the current table.  ([Nature](https://www.nature.com/articles/s41586-024-08328-6?utm_source=chatgpt.com))

That addresses a difficult property of tabular data: column 3 might mean age in one dataset, rainfall in another, and trading volume in another. The transferable knowledge is largely **how to infer statistical relationships**, rather than a fixed meaning for each column.

There is also a Bayesian interpretation. The synthetic dataset generator defines a prior over possible data-generating processes; the network learns to approximate prediction after observing a dataset. Its probabilities therefore reflect that learned prior and the supplied observations. They are not automatically calibrated for every deployment domain.  ([arxiv.org](https://arxiv.org/abs/2501.02945?utm_source=chatgpt.com))

### What has advanced recently?

The field has moved beyond the original small-data model:

| Version | Main development |
|---|---|
| **TabPFN v2, January 2025** | Strong classification and regression results around 10,000 rows and 500 features. |
| **TabPFN 2.5, November 2025** | Expanded to a stated design range of 50,000 rows and 2,000 features; stronger results against tuned tree models. |
| **TabPFN 3, May 2026** | Scaled to one million training rows, with faster inference and expanded forecasting and relational capabilities. |
| **TabPFN 3.5, September 2026** | Reports further gains, including on temporal and grouped splits, wide tables, and mixed data types. |

These are the authors’ reported capabilities and benchmark results; they are not guarantees for every dataset.  ([nature.com](https://www.nature.com/articles/s41586-024-08328-6?utm_source=chatgpt.com))

Time-series work is also real: **TabPFN-TS turns forecasting into tabular regression using engineered time features**, with both point and probabilistic predictions. Forecasting benchmarks support this approach, but do not establish profitable stock-return prediction.  ([GitHub](https://github.com/PriorLabs/tabpfn-time-series?utm_source=chatgpt.com))

### What problems suit it?

The following are practical use-case judgments based on its classification and regression capabilities:

| Problem | Why it is a plausible fit |
|---|---|
| Clinical outcomes or experimental science | Limited labeled observations and interacting measurements. |
| Churn, default, equipment failure | Structured predictors and a clearly defined outcome. |
| Event-based financial prediction | Hundreds or thousands of comparable historical events. |
| Forecasting with informative covariates | Predictable structure that can be represented in a table. |

The key condition is **useful predictive information in the features**. Better learning cannot recover information that is absent.

### Stocks: where I would try it

My strongest candidate would be **event-conditioned prediction**, rather than forecasting raw prices from price history alone.

For example, an earnings dataset could contain:

| Inputs known at decision time | Target |
|---|---|
| Earnings surprise, guidance change, valuation, prior momentum, volatility, market regime | Five-day return relative to the sector, or probability of exceeding a return threshold |

Other plausible experiments include breakout follow-through, volatility, drawdown risk, and ranking stocks within a defined universe. Those are hypotheses to test, not demonstrated TabPFN advantages.

The evaluation matters more than the architecture:

- Use chronological walk-forward testing.
- Keep overlapping return windows from leaking across splits.
- Use point-in-time fundamentals, news, and universe membership.
- Compare with simple models and CatBoost/XGBoost.
- Evaluate returns after transaction costs alongside prediction metrics.

A random row split can make a financial model look excellent by letting closely related observations from the same period appear in both training and testing.

### Kalshi: potentially a cleaner fit

**Repeated, similarly structured events are promising experiments.** A dataset of weather threshold markets, economic releases, or another recurring event family gives you a clear binary outcome and potentially useful covariates.

For example:

\[
P(\text{temperature exceeds threshold}\mid
\text{forecast ensemble, location, season, lead time})
\]

You could also build a **conditional calibration model** whose inputs include the market price, an external forecast or LLM probability, time to resolution, and event characteristics. Its target would be the actual settlement outcome.

That would answer: *Under these conditions, how often does this event actually happen?* It could learn corrections that vary with context, provided you have enough comparable resolved events.

For a unique geopolitical question with little comparable history, the tabular setup is much weaker. TabPFN does not supply missing factual evidence simply because it has been pretrained.

For Kalshi, I would prioritize **Brier score, log loss, and calibration**, then assess whether any probability advantage survives executable prices and trading costs. A model’s 60% estimate is not evidence of an edge over a 50¢ quote until its out-of-sample probabilities prove reliable.

**My first experiment would be one narrow event family:** benchmark TabPFN against logistic regression, boosted trees, and the market-implied probability under identical chronological splits. That would tell you whether its ability to learn from limited data provides something useful in your particular domain.

Sources: [nature.com](https://www.nature.com/articles/s41586-024-08328-6?utm_source=chatgpt.com), [arxiv.org](https://arxiv.org/abs/2207.01848?utm_source=chatgpt.com), [GitHub](https://github.com/PriorLabs/tabpfn-time-series?utm_source=chatgpt.com)

---

Q: is TabPFN-3.5 open weight?

---

A:

I’ll check the official weights and license.

*[thinking: Reviewing TabPFN Repository and Model Resources]*
*[Worked for 7s]*

**Yes—TabPFN-3.5 has downloadable weights and can run locally.** But its weights have a **non-commercial license**, while the inference code is Apache 2.0. Commercial use requires a separate license from Prior Labs.  ([GitHub](https://github.com/PriorLabs/TabPFN?utm_source=chatgpt.com))

You can use the [official Python package](https://github.com/PriorLabs/TabPFN); it downloads the checkpoint on first use:

```python
from tabpfn import TabPFNClassifier

model = TabPFNClassifier(device="cuda")
model.fit(X_train, y_train)
probabilities = model.predict_proba(X_test)
```

So: **open weights, with usage restrictions.** For your stock/Kalshi application, check the weight license before using it in a live trading system.

Sources: [GitHub](https://github.com/PriorLabs/TabPFN?utm_source=chatgpt.com)

---

Q: how big is it? num params? file size?

---

A:

I’ll check the checkpoint sizes and parameter counts.

*[thinking: Searched the web]*
*[Worked for 18s]*

**TabPFN-3.5 is about 220 million parameters, with an 876 MB checkpoint.**

| Model | Parameters | Download size |
|---|---:|---:|
| **TabPFN-3.5** | **220M** | **876 MB** |
| **TabPFN-3.5-Fast** | **84M** | **334 MB** |

Parameter counts come from the technical report; file sizes are from the official weight repository.  ([arxiv.org](https://arxiv.org/html/2609.17895v1?utm_source=chatgpt.com))

One checkpoint handles **both classification and regression**. Actual inference memory can be substantially larger than the weight file because it also holds your dataset’s representations and attention cache.  ([Hugging Face](https://huggingface.co/Prior-Labs/tabpfn_3_5?utm_source=chatgpt.com))

Sources: [arxiv.org](https://arxiv.org/html/2609.17895v1?utm_source=chatgpt.com), [huggingface.co](https://huggingface.co/Prior-Labs/tabpfn_3_5/tree/main?utm_source=chatgpt.com)

---

Q: could this be useful at all for financial/economic superforecasting?

---

A:

**Yes—especially as the statistical component of a forecasting system.** I’d be more optimistic about forecasting repeated economic events than predicting short-term stock returns.

The useful distinction is between **estimating an outcome from historical patterns** and **understanding what makes today’s situation different**. TabPFN can help with the first; research, domain judgment, and an LLM can help supply features for the second.

These are plausible applications I would test—not established TabPFN results:

| Forecasting question | How TabPFN could contribute |
|---|---|
| Will next month’s inflation exceed a threshold? | Learn from inflation components, commodity prices, prior releases, and consensus forecasts. |
| Will the Fed cut at the next meeting? | Estimate probabilities from inflation, employment, financial conditions, and the policy trajectory. |
| Will earnings exceed expectations? | Model comparable company-quarter observations. |
| Will a recession begin within 12 months? | Combine indicators, though the small number of independent recessions is a major limitation. |
| Is a Kalshi probability systematically biased? | Learn conditional corrections from comparable resolved markets. |

**The most interesting use may be combining forecasts.** You could give it a table containing:

- Market-implied probability.
- Economist consensus and disagreement.
- Predictions from other statistical models.
- An LLM or human forecast.
- Economic indicators, event category, and time until resolution.

The target is the eventual outcome. TabPFN could then learn **when each source deserves more weight**, including nonlinear interactions. For example, perhaps a particular forecast source adds information only at longer horizons or during certain economic conditions. Whether those patterns exist would need testing.

This connects to your probability-versus-confidence question: **forecast disagreement and measures of evidence quality can themselves be inputs**. The model could learn whether they predict forecast errors. Its output probability would still need calibration checks.

There are three substantial limits:

1. **Few independent events.** Thousands of snapshots of 30 Fed meetings still contain only 30 resolved meeting outcomes. Treating snapshots as independent examples can create very misleading results.
2. **Structural change.** Historical relationships may break when policy, institutions, or market behavior changes. Synthetic pretraining does not supply knowledge of a new economic regime.
3. **Information timing.** Economic data are revised. A valid backtest needs the releases and forecasts actually available at each historical decision time.

The recent TabPFN-3.5 report includes improved results on temporal and grouped splits, which makes it relevant to investigate here. That evidence does **not** demonstrate economic superforecasting skill or a market edge.  ([arxiv.org](https://arxiv.org/html/2609.17895v1?utm_source=chatgpt.com))

**My first experiment would be a single recurring economic-release family**, such as inflation exceeding consensus, with a fixed forecast horizon. Compare TabPFN against market/consensus forecasts, logistic regression, and boosted trees using chronological testing. Judge it first by **Brier score, log loss, and calibration**.

If it improves those forecasts consistently, you have evidence that it contributes to superforecasting. Its most valuable role could be a disciplined probability combiner—even if it never becomes the best standalone forecaster.

Sources: [arxiv.org](https://arxiv.org/html/2609.17895v1?utm_source=chatgpt.com)

---

Q: I thought TabPFN-3.5 was SOTA, but on [https://huggingface.co/spaces/TabArena/leaderboard](https://huggingface.co/spaces/TabArena/leaderboard) I see another model first, LimiX-2 ([https://arxiv.org/abs/2609.17488).](https://arxiv.org/abs/2609.17488\).)
what is this one? can it also handle time series prediction?

---

A:

I’ll check the leaderboard and LimiX-2 paper to see what its ranking measures and whether it supports time-series forecasting.

*[thinking: Searched the web]*
*[Worked for 24s]*

**LimiX-2 is another strong tabular foundation model, and you’re right to question my blanket “SOTA” description.** I should have qualified it by benchmark and model configuration.

One detail matters: **the LimiX-2 paper compares against TabPFN-3, rather than TabPFN-3.5**. Both new papers appeared on September 15. Its reported first-place result therefore doesn’t establish a direct win over 3.5. I could read the leaderboard’s wrapper, but its live ranking table wasn’t accessible through my retrieval tool.  ([arxiv.org](https://arxiv.org/html/2609.17488v1?utm_source=chatgpt.com))

### What is LimiX-2?

It comes from **Stable AI and Tsinghua University**. Like TabPFN, it is a transformer pretrained on synthetic datasets that makes predictions using your dataset as context, without task-specific weight updates. The released model is approximately **400M parameters**, with a **1.63 GB checkpoint** and a non-commercial weight license.  ([arxiv.org](https://arxiv.org/html/2609.17488v1?utm_source=chatgpt.com))

Its distinctive idea is **learning to reconstruct different missing parts of a table**, rather than always predicting one designated label column.

For example, imagine a table containing inflation, employment, interest rates, and GDP growth. During pretraining, it might be asked to infer:

- GDP growth from the other variables.
- Missing employment measurements.
- Several hidden cells under different observation patterns.

The authors call this *context-conditional masked modeling*. They frame it as learning the table’s joint relationships, with supervised prediction as one application.  ([arxiv.org](https://arxiv.org/abs/2609.17488?utm_source=chatgpt.com))

That supports classification, regression, and missing-value imputation through one model. The paper also evaluates causal skeleton recovery—identifying candidate connections among variables. **That is not a guarantee that it can discover valid economic causes or predict the effects of policy interventions.**  ([GitHub](https://github.com/limix-ldm-ai/LimiX?utm_source=chatgpt.com))

### Can it predict time series?

**Yes, by turning forecasting into a tabular prediction problem. But I found no dedicated time-series forecasting evaluation in the LimiX-2 paper.** Its reported evaluations concern tabular prediction and causal skeleton recovery.  ([arxiv.org](https://arxiv.org/html/2609.17488v1?utm_source=chatgpt.com))

Here is a proposed forecasting setup:

| One row represents | Features available at forecast time | Target |
|---|---|---|
| A month | Previous inflation readings, employment changes, commodity returns, consensus forecast | Next month’s inflation |
| A stock-day | Lagged returns, volatility, volume, market indicators | Next five-day return |
| An economic release | Prior releases, consensus, disagreement, market probability | Whether the release exceeds a threshold |

LimiX-2’s regression or classification interface could handle those tables. **You supply the temporal structure through lagged features and targets; it doesn’t automatically understand chronology from row order.** This is an application proposal, not a demonstrated forecasting result.

The masked-table approach also makes a multivariable forecasting experiment conceivable: put past observations and future targets into different columns, then infer unknown targets. But I would first test a simple, explicitly defined target rather than assume its imputation capability produces coherent multi-step forecasts.

### Which would I try for your use case?

| Use case | My assessment |
|---|---|
| Ready-made time-series forecasting | **TabPFN has more direct evidence and tooling**, through TabPFN-TS. |
| Engineered economic or financial feature tables | **Benchmark both LimiX-2 and TabPFN-3.5.** |
| Combining market, economist, and LLM probabilities | Both are plausible candidates; evaluate calibration on future events. |
| Inferring policy effects | Neither model’s tabular ranking establishes this capability. |

TabPFN-TS explicitly provides point and probabilistic forecasting, whereas LimiX-2’s documented interfaces focus on classification, regression, and imputation.  ([github.com](https://github.com/PriorLabs/tabpfn-time-series?utm_source=chatgpt.com))

**For economic superforecasting, LimiX-2 belongs on the shortlist.** Its general tabular ranking is encouraging, but the decisive comparison is on your own chronological, event-separated test set—particularly probability calibration and performance relative to consensus or market prices.

Sources: [arxiv.org](https://arxiv.org/html/2609.17488v1?utm_source=chatgpt.com), [GitHub](https://github.com/limix-ldm-ai/LimiX?utm_source=chatgpt.com), [huggingface.co](https://huggingface.co/stable-ai/LimiX-2/tree/main?utm_source=chatgpt.com)

---

Q: I want to create a new chat thread that I can share with someone.  Help me create a prompt that will prompt chatGPT to explain both of these recent advances (the two just released models), why they are significant and potentially very exciting for time series prediction.... with a special focus on financial prediction, and economic superforecasting. explain that these are both a new type of time series prediction that has never been used before, and so this is largely unexplored territory.

---

A:

I’ll write a shareable prompt and check how to describe the novelty accurately, especially the distinction between tabular models and time-series applications.

*[thinking: Reviewing TabPFN Time-Series Research and Repository]*

I’m using the writing-blocks skill for the copyable prompt. The novelty needs one adjustment: TabPFN time-series work already existed in 2024, so “never used before” is too strong. These new releases make a promising approach more capable; their financial and economic forecasting potential remains an open research question.

*[Worked for 17s]*

Yes—with one adjustment: **“never used before” overstates the novelty**, since TabPFN forecasting work dates to 2024. “An emerging approach whose financial applications remain largely unproven” captures the excitement more accurately.  ([GitHub](https://github.com/PriorLabs/tabpfn-time-series?utm_source=chatgpt.com))

Paste this into a new chat:

:::writing{variant="standard" id="63821"}
Explain two recently released tabular foundation models—**TabPFN-3.5 and LimiX-2**—and why they could be exciting for **time-series prediction, financial forecasting, and economic superforecasting**.

Start by reading these primary sources and checking current official documentation:
- TabPFN-3.5: https://arxiv.org/abs/2609.17895
- LimiX-2: https://arxiv.org/abs/2609.17488
- TabPFN time-series: https://github.com/PriorLabs/tabpfn-time-series
- TabArena leaderboard: https://huggingface.co/spaces/TabArena/leaderboard

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
:::

Sources: [GitHub](https://github.com/PriorLabs/tabpfn-time-series?utm_source=chatgpt.com)
