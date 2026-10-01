# Preseen / Knowledge Lab: forecasting questions, dependencies, and surprise

## Source metadata and scope

- **Reference:** [Predicting Science and Technology: Preseen Partners with UChicago's Knowledge Lab](https://blog.preseen.com/p/predicting-science-and-technology).
- **Author / publisher:** Preseen, on its own blog (Substack).
- **Published:** 2026-09-28. **Accessed:** 2026-10-01; all linked-source checks below use that access date.
- **Document type:** Attributed research digest, not a reproduction of the article. The originating article is a company partnership announcement, not an evaluation paper.
- **Project relevance:** Broad macroeconomic superforecasting—economic releases, policy decisions, growth/inflation regimes, and technological shocks—not a stock-price prediction recipe.
- **Evidence labels:** **Reported** means a source's claim; **corroborated** means checked against another primary source; **proposal / hypothesis** means this repository's suggested work, not a demonstrated capability or measured result.

## Executive assessment

The useful idea is a forecasting workflow: turn broad concerns into dated resolvable questions, research components, model dependencies, generate overlooked branches, and update probabilities when evidence changes. Preseen reports an existing agentic forecasting service and strong public tournament performance. The proposed integration with Knowledge Lab (KLab)—especially recursively generated scenario graphs and coherent conditional updates—is described largely in future tense. It should not be treated as a published, validated implementation.

Two substantive checks were possible:

1. **Tournament result substantially corroborated.** The public Spring 2026 Metaculus Cup leaderboard places Preseen-Chestnut's total score between the second- and third-ranked prize entrants; a separately resolved Metaculus question gives the best bot's position as third. The exact **1,283 participant** denominator remains an article-reported figure, not independently verified here.
2. **APTO's research scope corroborated, successful delivery not established.** UChicago describes the funded chronological-model / virtual-laboratory research agenda, and NSF's solicitation explicitly requires causal investment models and out-of-time evaluation. Neither is evidence that the announced KLab–Preseen integration has achieved those aims or transfers successfully to macroeconomic forecasting.

No private product was accessed, no forecast was submitted, and no forecasting model was run for this digest.

## What the article says—and what it does not demonstrate

| Topic | Attributed finding from Preseen | Evidence boundary |
|---|---|---|
| Question definition and decomposition | Start with an outcome and time horizon; agents break the question into parts, research evidence in parallel, and combine findings into a probability with an explanation. | **Reported current workflow.** No decomposition algorithm, aggregation rule, prompts, evidence-quality audit, or component ablation is supplied. A convincing explanation is not an accuracy measurement. |
| Conditional dependencies | Connect individual milestones, assess how an event changes another event's likelihood, and keep forecasts consistent when assumptions change. | **Research proposal.** The article says the partners plan to examine these dependencies. It does not specify a joint probability model, inference algorithm, or demonstrated consistency guarantees. |
| Surprise | KLab models are described as using anomalous or overlooked findings to identify developments with downstream importance. The article says AI systems struggle on genuinely unexpected answers. | **Reported research motivation/capability.** No operational surprise metric, forecast benchmark, or effect size is included in the article. Rarity, model surprisal, economic importance, and predictable downstream impact are different quantities. |
| Open-ended scenario generation | A system led by postdoc Robbie Ward is described as starting with an actual or possible technological advance and recursively generating subsequent developments and probabilities, drawing on papers, patents, policy documents, and clinical trials. | **Reported work being built.** No public runnable artifact or evaluation for this particular system was established by the sources checked here. Do not infer that the entire system is deployed or calibrated. |
| Forecast updates | The proposed integration would let Preseen re-evaluate conditional probabilities on generated graphs; KLab could expand Preseen outputs into downstream branches. | **Integration proposal.** No update frequency, information-clock protocol, handling of conflicting evidence, or measured benefit over one-shot forecasting is reported. |
| Calibration | The article explains calibration using the frequency interpretation of probabilities. | **Objective, not a supplied result.** A high tournament rank alone does not establish calibration, conditional calibration, or performance on rare macroeconomic regime shifts. |

The article's five-step sequence is useful to retain in paraphrase: discover candidate advances; represent dependencies; define dated testable questions; forecast them; monitor and revise probabilities. Its novelty for this project is the connection between **question generation** and **forecasting**, rather than simply asking a language model for another number.

## Primary-source checks

### 1. What the Metaculus evidence actually establishes

**Sources:** [Spring 2026 Metaculus Cup](https://www.metaculus.com/tournament/metaculus-cup-spring-2026/) and [resolved question: top bot's tournament rank](https://www.metaculus.com/questions/42913/spring-2026-metaculus-cup-top-bot-rank/).

The tournament's static reader response omitted the leaderboard, so it was opened in a logged-out browser, the Leaderboard panel expanded, and its rendered table and screenshot inspected. The visible rows were:

| Score order | Forecaster | Displayed total score | Displayed prize rank / prize |
|---|---|---:|---|
| 1 | tejvn | 1156.626 | 1 / $285 |
| 2 | NathanpmYoung | 1127.147 | 2 / $271 |
| 3 | Preseen-Chestnut | 1059.811 | Information marker / no prize |
| 4 | Adonis | 1016.349 | 3 / $220 |
| 5 | benshindel | 1008.631 | 4 / $217 |

The bot is third **by displayed score**, not the recipient of the third-place prize shown in the table. The separately resolved question reports **3 Place** for the top bot. Together these support the article's third-overall / highest-bot characterization without conflating score order with prize eligibility. The site describes 43 tournament questions; its scoring terminology identifies question scores as **Peer Scores**. These are not percentages correct or Brier scores.

**Not established here:** the 1,283-participant count; entrants' activity or coverage; question-level Preseen probability histories; exact aggregation and time-weighting of total scores; uncertainty in rank differences; independence among questions; absence of human assistance or information contamination; stability across tournaments; or the contribution of any particular model/component. The tournament has mixed subjects (the visible sample includes geopolitics, commodity prices, consumer sentiment, and entertainment). It is evidence of a strong result on that contest, not a macroeconomic release benchmark and not validation of the later September partnership's proposed methods.

### 2. APTO is a causal-research ambition with explicit evaluation requirements

**Sources:** [UChicago's $20 million project announcement](https://news.uchicago.edu/story/nsf-awards-20-million-build-ai-models-predict-scientific-discoveries-and-technological), [Knowledge Lab initiatives](https://knowledgelab.org/initiatives/), and [NSF 23-600 APTO solicitation](https://www.nsf.gov/funding/opportunities/apto-assessing-predicting-technology-outcomes/506195/nsf23-600/solicitation), posted 2023-06-22 and now archived.

- UChicago identifies James Evans as project lead, the Allen Institute for AI as a partner, and a $20 million award. It describes mapping funded proposals, papers, patents, and products to build chronological models that can recognize developments relative to what was known earlier. A virtual laboratory is proposed to explore funding/policy/partnership outcomes; development and testing are described as a staged five-year effort. These are an institutional announcement's account of funding and planned research, not reported forecast scores.
- NSF explicitly distinguishes **capabilities**, **production**, and **use** of technologies. Its goal is not only predicting what happens, but determining which investments change outcomes and by how much. The solicitation acknowledges that intermediate work may identify only correlation, have poor out-of-sample predictive power, or remain difficult to explain.
- NSF calls for out-of-sample prediction, information-based losses such as log loss, trend-extrapolation baselines, and holdouts across time and technologies. Predictions should be evaluated at least five years beyond the latest model input data, with reporting no finer than annual. It also flags the possibility of overfitting historical evaluations.
- The lab's initiatives page names an Innovation Policy Lab and Global Innovation Observatory, consistent with this agenda. It does not publish accuracy results for the specific integration described by Preseen.

**Implication:** The primary program source supports taking causality and chronology seriously; it does not license calling a predictive dependency graph causal. APTO's long-horizon technology remit also differs materially from next-month CPI or the next central-bank meeting. Any macro transfer is a hypothesis.

**Access limits:** The linked NSF award-search URL for award 2404109 returned a redirect to generic search rather than award detail in the reader. A searched NSF/Elsevier project-page alternative returned HTTP 404. Consequently the award amount is attributed to UChicago (also repeated on KLab's home page), not claimed freshly verified in a federal award record. KLab's [news page](https://knowledgelab.org/news/) links [Designing for Surprise](https://www.science.org/doi/10.1126/science.aej4257), but the publisher returned HTTP 403. Its contents or empirical findings are not asserted here. Press coverage linked by Preseen was not used as independent methodological validation.

## Translating this to macroeconomic superforecasting

Everything in this section is a **project proposal / hypothesis**, not a claim about implemented Preseen functionality or demonstrated TabPFN performance.

### Define a portfolio of resolvable questions before building a narrative

Use recurring targets for measurable calibration, while reserving a separate track for sparse, longer-horizon scenarios:

- **Inflation:** probability that a specified month's original headline CPI-U seasonally adjusted monthly change, rounded as published, is strictly above a fixed threshold. Specify release source, cutoff, missing-release policy, and whether first release or later revision resolves the question.
- **Monetary policy:** probabilities over an exhaustive set of target-range decisions at a named FOMC meeting. Specify the announcement used for resolution and treatment of unscheduled changes.
- **Labor and growth:** original payroll-change or advance GDP-growth thresholds, with units, period, annualization, publication vintage, and resolution date explicit.
- **Macro regimes and structural shocks:** recession determinations, energy disruptions, technology diffusion, or productivity outcomes. Define the adjudicating institution and a deadline for observing the determination. Do not retrospectively date a recession label as if it had been known at the time.

These are distinct event families, not interchangeable rows. A regime question can have a much longer label delay than a scheduled release; train only on outcomes actually known before the forecast cutoff.

### Decompose without manufacturing independence

For an inflation question, separate energy, shelter, goods, and services evidence and distinguish mechanical aggregation of price changes from probabilities of crossing a rounded headline threshold. For policy, separate inflation/labor evidence, stated reaction-function evidence, and institutional/calendar constraints.

A graph is an organizing device until its joint distribution is justified. If A is an energy disruption and B is an inflation threshold event, coherent observational forecasts satisfy:

`P(B | I) = P(B | A, I) P(A | I) + P(B | not A, I) P(not A | I)`

where I is the same information set and event definitions/horizons are aligned. This identity does not assume A and B are independent. Multiplying marginal milestone probabilities generally does. Arbitrary pairwise conditionals can also be incompatible with any joint distribution; a larger graph needs a specified factorization and checked assumptions, not merely arrows drawn by an LLM.

Use checks for complementary probabilities, nested threshold monotonicity, and consistent marginalization. Keep original and reconciled probabilities separately if reconciliation is applied; evaluate whether coherence changes improve proper scores rather than assuming they do.

### Keep observation, scenarios, and interventions separate

`P(recession | rate cut, I)` describes an observational conditional: cuts may occur because growth is already weakening. It is not `P(recession | do(rate cut), I)`, the effect of forcing a rate cut while otherwise defining an intervention on the system. Selecting historical cut episodes or changing a tabular policy-rate input cannot identify that intervention by itself.

Similarly, the article's example about a specified NSF investment can mean either forecasting in worlds where that investment occurs or evaluating the effect of choosing to invest. Those are different questions. Policy advice requires an identification strategy and assumptions about confounding, anticipation, transmission, and policy selection—potentially a defensible structural model, experimental/quasi-experimental evidence, or explicitly assumption-dependent sensitivity analysis. An LLM rationale or TabPFN prediction does not supply identification automatically.

### Use surprise to broaden coverage, not inflate probabilities

An LLM scenario pass could ask which plausible developments are absent from the current question portfolio: shipping interruptions, policy reversals, energy supply changes, labor-supply shocks, or unexpectedly rapid technology adoption. Convert selected branches into pre-registered, dated questions with evidence and disconfirmation criteria.

Do not treat more generated stories as more independent information, equate unfamiliarity with low probability, or add probabilities across overlapping scenarios. An exhaustive mutually exclusive partition needs an explicit residual category; a non-exhaustive collection of overlapping scenarios should remain clearly labelled as such. Evaluate generation separately from numeric forecasting: Did it identify useful developments before they became obvious, at an acceptable false-alarm rate? Avoid scoring only the branches remembered after a shock.

### Update on evidence with an auditable clock

Archive each forecast version, information cutoff, new evidence, source publication/receipt times, and the reason for any probability change. Repeated reporting of one source should not be counted as multiple independent observations. Predeclare fixed-horizon evaluation and/or a time-weighted scoring schedule so extra last-minute updates cannot silently change the benchmark. Forecast snapshots of the same release remain one correlated event cluster, not new independent labels.

## Candidate hybrid: LLM evidence layer + TabPFN statistical/calibration layer

This is a proposed division of labor, **not a claim that either reference evaluated this hybrid**:

1. **Question and evidence layer:** LLM assistance structures questions, retrieves timestamped primary evidence, extracts compact predefined features, identifies counterevidence and scenario assumptions, and optionally issues a separately recorded raw probability. Preserve citations and distinguish source facts from the model's interpretation.
2. **As-of event table:** Join evidence features to vintage-safe macro data, properly matched market/consensus/nowcast forecasts where available, horizon, and source-age/coverage fields. Keep target-family semantics explicit; do not pool a GDP threshold with a rate decision just because both can be encoded as binary.
3. **Statistical layer:** Evaluate TabPFN as an event-probability estimator or conditional forecast combiner using those tabular inputs. A learned correction to LLM/market probabilities is a candidate use, not automatically a calibrated forecast. Compare against raw forecasts, historical frequencies, regularized logistic calibration/combination, and other appropriate conventional baselines.
4. **Calibration and coherence:** Fit any post-hoc calibration only on earlier out-of-sample predictions. Separate this empirical calibration from logical graph checks and from causal claims. If all steps use the same small fitting sample, apparent calibration can be misleading.
5. **Explanations and monitoring:** Ground explanations in cited inputs and actual statistical outputs. An LLM must not invent why TabPFN changed a probability. Log disagreement between evidence-only and statistical forecasts; evaluate subsequent revisions rather than overriding a model simply because a narrative sounds compelling.

Training a combiner requires **out-of-sample base predictions**, with their original creation times. A current LLM applied to old news may already know the outcome through pretraining; a historical retrieval cutoff alone does not make its output contemporaneous. Such exercises must be labelled retrospective and separated from a forward-recorded forecasting evaluation.

The repository's [data inventory](../DATA-SOURCES.md) already identifies vintage/consensus gaps and hindsight risks. Those limitations remain even with a sophisticated question graph. A large number of prompts, threshold contracts, or update snapshots cannot compensate for a small number of independent macroeconomic outcomes.

## Actionable hypotheses and decision rules

These are research candidates to pre-register, not completed experiments or a claim of available datasets.

| Hypothesis | Controlled comparison | Evidence needed / failure mode |
|---|---|---|
| Structured evidence adds value beyond a bare LLM probability. | Same events, cutoffs, base model and retrieval budget: raw probability versus probability plus predefined evidence features in a regularized combiner and TabPFN. | Prospectively timestamped forecasts or defensible historical model cutoffs; event-clustered Brier/log-loss comparison. Gains that disappear versus simple logistic combination do not establish a TabPFN advantage. |
| Dependency-aware forecasting improves policy/inflation joint outlooks. | Predeclared small event graph versus independent question forecasts; score marginal predictions and check coherence separately. | Enough resolved parent/child cases, explicit conditionals, no independence shortcuts. A coherent but less accurate forecast is not a forecasting win. |
| Open-ended scenario generation improves early coverage. | Fixed question list versus the same list plus a budgeted, prospectively frozen generation process. | Retain all generated candidates, selection rules, and false alarms. Judge coverage/lead time separately from probability accuracy; no post-outcome selection of successful stories. |
| Evidence-triggered updates improve fixed-horizon forecasts. | Frozen initial forecast, scheduled refresh, and predeclared event-triggered refresh on the same outcomes. | Versioned evidence and forecast clocks, equal resource accounting, identical scoring window. Repeated snapshots do not increase the independent-event sample size. |

Use chronological evaluation, identical eligible events across systems, past-only transformations/calibration, and grouped uncertainty estimates. Stratify by target family and horizon. Long-horizon rare scenarios may need prolonged prospective observation; do not substitute short-horizon tournament rank as evidence for them. Prediction quality, causal policy usefulness, and after-cost trading performance are separate claims.

## Bottom line

The strongest supported takeaway is architectural: **generate better questions, preserve dependencies and information timing, and distinguish evidence gathering from probability estimation**. Preseen's strong contest placement is visible in primary public evidence. The broader conditional/open-ended partnership remains a research and product proposal in the inspected sources. A macroeconomic LLM–TabPFN hybrid is worth testing under strict prospective or vintage-safe evaluation, but neither this article nor its linked APTO material demonstrates its effectiveness.
