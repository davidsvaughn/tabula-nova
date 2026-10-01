# Macro forecasting and superforecasting research plan

Updated 2026-10-01. Supersedes the equity-heavy priority ordering in LOG-003. **Objective:** determine whether tabular foundation models improve useful economic probability forecasts and forecast combinations—not whether they can predict stock prices in isolation. Better probability estimates, defensible policy scenarios, and profitable trading are separate claims.

## What has actually been established

- User-licensed standard TabPFN-3.5 runs locally on the laptop, for regression and classification, without an API key or cloud upload.
- Frozen volatility comparison completed: ridge wins; TabPFN does not beat the strongest conventional baseline. [LOG-004](logs/LOG-004.md).
- A genuinely macroeconomic probability experiment completed: 84 next-quarter GDP-contraction events, ten contractions; **direct SPF consensus beats the tested learned corrections overall**. [LOG-005](logs/LOG-005.md). The subsequent six-configuration feature/ensemble matrix preserved that result; respondent-count deletion did not remove late-period errors. [LOG-006](logs/LOG-006.md). These are configuration-level, exploratory results, not an architecture-level verdict.
- **LimiX-2 also completed the same 84-event macro cohort**, using the official 32-pipeline configuration and one query per call to prevent transductive future-feature leakage. Brier/log loss 0.170312/0.526035 versus consensus 0.095373/0.329044; full-feature TabPFN-eight also scored better overall. [LOG-007](logs/LOG-007.md). The user-supplied weights remain in Downloads and the isolated Python 3.12 environment is runnable.
- Public SPF probabilities, publication dates and first-release macro archives can be downloaded without FRED credentials. [Source reference](references/philadelphia-fed-spf.md).
- CPI acquisition/integration completed: **318 archived monthly headline prints**, 317 matching RTDSM First proxies, 155 nominal-cutoff Cleveland comparisons and 61 matching Kalshi vendor outcomes. Both 2025 shutdown monthly targets remain missing despite vendor settlements. The frozen 255-query experiment completed all five models under bounded archival assumptions—not strict PIT certification. **LimiX has a small, uncertain lead: about 2.2% lower later distribution error than boosted trees; neither native model demonstrates an advantage over all conventional baselines.** Nominal 80% intervals cover only 69–73% of later outcomes. Professional-nowcast and market comparisons remain separately gated. [Plain-English evidence and current next steps](logs/LOG-009.md).
- Metaculus public question/criteria/history charts were inspected, but machine-readable archives and **written AI/ML use permission** were not obtained. Do not treat registration as that permission. [Access assessment](references/metaculus-economy-business.md).

The GDP results favor strong consensus; the CPI results show ordinary learned baselines are competitive with these native models. LimiX's small lead is a weak positive hint, not a demonstrated major forecasting advantage. The six-feature lag-only CPI experiment does not test richer timely inputs, direct distributional models or forecast combination; those remain open hypotheses.

**Current direction after the user-requested pause:** [LOG-010](logs/LOG-010.md)
reviews every document and both original chats. Lead question: can timely economic
evidence identify predictable errors or uncertainty in a good existing forecast?
Start with energy-informed CPI around the Cleveland nowcast, only after a bounded
source/clock audit; distinguish information value, correction value and incremental
foundation-model value. Continuous SPF consensus-error correction is the backup,
not an assumed larger or cleaner confirmation sample. No new inference is authorized
by this reassessment itself.

## Three complementary tracks

### A. Recurring macro distributions and forecast combination

Best near-term source of repeated, explicitly resolvable outcomes. The target is a distribution/decision probability, not necessarily a security return.

| Family | Candidate forecast | Data / baseline | Main correctness gate |
|---|---|---|---|
| Growth | Quarterly real GDP-growth distribution; next-quarter contraction probability | SPF means/microdata/distributions and RTDSM; direct consensus, historical/AR forecast, linear/shrunk combinations | GDP versus GNP; first/third/latest-vintage outcomes; actual public forecast and label clocks |
| Inflation | Headline/core CPI and PCE release distributions; threshold ladder | Original BLS/BEA releases, vintage inputs, permitted nowcast/survey/market forecasts | SA monthly versus YoY/annualized units; published rounding; missing releases; precise contract settlement |
| Labor | Payroll first-print distribution; unemployment thresholds | Original BLS releases, vintage-safe covariates, SPF where horizon matches | Household versus establishment survey; revisions/benchmark changes; release and resolution delay |
| Monetary policy | Exhaustive probabilities for decisions at a named meeting or target range at a named date | Official decisions and evidence; independently permission-checked contemporaneous consensus | Upper bound versus midpoint/effective rate; announcement versus end-of-day rule; unscheduled decisions |
| International macro | Country-specific inflation/growth/labor distributions | Candidate official archives/surveys, not yet inventoried | Rebasings, units, calendars, source continuity and permitted reuse; country/time holdouts |

**Experimental sequence and status:**

1. **Completed:** frozen SPF means-only/drop-response-count ablations crossed with two/eight estimators. Original scores and all variants preserved in LOG-006. Removing count did not fix the failure pattern; means-only and eight estimators improved some metrics but did not beat consensus. Stop selecting configurations on this already-seen cohort. A rolling-context experiment, if pursued, must be separately declared rather than silently replacing the frozen blocks.
2. **Completed CPI experiment:** source reconciliation, publication/correction adjudication, both native regression smokes, all five frozen model runs and the paired calendar-block analysis are complete. Neither native model passes the declared stronger-baseline criterion. LOG-009 reports actual scores, interval misses and a plain-English conclusion. Keep bounded archival assumptions distinct from strict PIT certification; dated current-history downloads or candle bucket age do not certify historical information.
3. **Reassessed next study, currently paused:** design evidence-conditioned nowcast correction/uncertainty, not another lag-only rematch. Audit one EIA retail-gasoline series and Cleveland history first, then freeze matched information arms, direct nowcast/simple conditional baselines, practical effect and event-aware power. Existing CPI periods remain seen; historical schedule assumptions must be disclosed. The current EIA pages say Tuesday around 10am ET, not an assumed Monday posting. See LOG-010 for evidence, alternatives and executable next steps.
4. Add another family only after clocks, scoreability and sample counts are sound. A panel can improve diversity, but combining countries or target families requires explicit semantics and holdouts, not arbitrary row inflation.

### B. Broad, judgment-intensive superforecasting

Keep a portfolio beyond scheduled economic releases: recession determinations, policy shifts, energy/supply disruptions, debt/fiscal developments, productivity, AI adoption/investment, and technological milestones with downstream macro effects. Include non-US questions rather than equating macro with US equities.

Use [Metaculus examples](references/metaculus-economy-business.md) to understand how resolution precision changes the problem: a third-estimate GDP event is not an advance-release event; a dated FOMC upper target is not the effective rate; an NBER declaration has delayed label availability; productivity and investment forecasts depend on base-year dollars and specific source vintages.

Two data routes must remain separate:

- **Immediately permitted-source route:** independently authored questions, official evidence, and our own prospectively timestamped forecasts, after checking each incorporated source's reuse terms. This need not wait for Metaculus archives.
- **Metaculus comparison route:** obtain explicit written AI/ML evaluation permission and the necessary aggregate/history entitlement first. Then verify actual archive coverage and collect under that grant. No automatic application, scraping workaround or forecasting action has been taken.

For our own prospective research, predeclare question inclusion, fixed forecast checkpoints, permitted evidence, model versions, and closure/resolution rules. Retain all forecasts, including poor ones and unresolved/annulled cases. Compare a raw LLM forecast, outside-view baseline, statistical model where training data exists, and a genuinely out-of-sample combiner. Long-horizon rare events will not produce a credible accuracy claim quickly; use recurring families for statistical measurement without pretending they validate every structural scenario.

### C. Conditional scenarios and technology-to-macro pathways

[Preseen/Knowledge Lab](references/preseen-science-technology.md) motivates linking question generation, evidence decomposition, dependencies, surprise discovery, and updates. The announced integrated system is mostly proposed; use the idea as a research hypothesis, not an available calibrated engine.

Start with small, explicit conditional structures, for example:

- Energy/supply shock → inflation evidence → policy outlook.
- Productivity/adoption milestone → output/labor-demand outlook.
- Fiscal or regulatory decision → investment incentives → dated measurable outcomes.

Separate sourced observations, conditional probability forecasts, and causal intervention claims. For a binary parent A and child B, require consistent marginalization under the same information set:

`P(B | I) = P(B | A, I) P(A | I) + P(B | not A, I) [1 - P(A | I)]`.

This identity is not a causal identification strategy. Observational rate-cut episodes are selected by economic conditions; changing a model's rate feature cannot establish the effect of forcing a cut. A policy-intervention study requires its own assumptions and identification evidence.

Scenario generation should increase useful prospective coverage, not narrative volume. Record every generated candidate, selection reason, forecast and false alarm. Do not score only remembered successful surprises. Nested thresholds, complements and exhaustive categories need coherence checks; overlapping scenarios must not be added as if mutually exclusive.

## Common research data contract

Use small, explicit event/forecast/evidence tables before building orchestration infrastructure. Proposed logical fields:

- **Question/event:** stable ID; family/geography; original text and rule version; source; format; units; threshold/rounding; reference period; forecast horizon; target-vintage rule; group/dependency IDs; resolution and missing/annulment policy.
- **Information:** observation period; original source publication timestamp; retrieved/received timestamp; revision/vintage ID; source URL and payload hash; availability uncertainty; transformation definition. A scraped-at timestamp does not certify past publication.
- **Forecast:** question ID; creation time; as-of cutoff; method/model/checkpoint; training-data cutoff; complete probability/distribution; baseline inputs and their timestamps; evidence IDs; cost/runtime; superseded forecast ID.
- **Outcome:** target value/event; reference period; official release timestamp; time outcome first became knowable; adjudication timestamp; source/vintage; resolution revision history.

Do not embed access tokens or private brokerage data. Keep third-party raw data local/ignored under its license; logs contain methodology and sanitized aggregate results.

## Evaluation gates

1. **Availability first.** No model comparison until target and feature/forecast clocks are defensible; list residual assumptions. Current historical archives may include corrections.
2. **Real independent units.** Group related thresholds, respondent rows, forecast updates, nested deadlines and overlapping annual targets. Report effective event counts and contraction/rare-event counts. Several predictions about the same quarter are not several independent GDP events.
3. **Equal information.** Match forecast cutoffs and eligible observations. Raw consensus and consensus-plus-model answer different questions from a model-alone forecast. Missing/stale consensus coverage must be disclosed.
4. **Past-only learning.** Chronological folds; labels must be available before training. Fit transforms, calibration and feature selection only on prior data. Hindsight-generated LLM outputs are not contemporaneous base forecasts; retrieving only old articles does not erase pretraining knowledge.
5. **Proper scores.** Binary/categorical Brier and log loss; continuous CRPS/quantile loss/log density with declared units/tails; interval coverage and calibration diagnostics. Brier is not calibration alone. Fixed-horizon research scores are distinct from Metaculus time-weighted/Peer scores.
6. **Baseline and uncertainty.** Include consensus, base rates and simple conventional combinations; paired event/episode-aware uncertainty for confirmatory comparisons. Retain original unfavorable runs. Do not interpret a quiet-block win or an untested recipe as general skill.
7. **Decision threshold.** Advance a learned correction only if a frozen, independently evaluated variant improves relevant proper scores without unacceptable coverage or robustness losses. Otherwise keep consensus and improve data/question definitions.

## Operational constraints

The shared laptop can support these small experiments without simultaneous large model copies. Check total CPU/RAM/swap/GPU/temperature/disk before larger runs and between experiments; current swap occupancy warrants attention, not an automatic halt. Never terminate other agents' processes or change drivers. Continue documentation/source research while waiting for safe compute headroom.

Preserve numbered `docs/logs/LOG-NNN.md` records and commit/push at completed milestones. Keep working local standard weights in their original Downloads location; no API key is required for explicit-path inference. Hosted Plus/Thinking and third-party forecast archives have separate cost, privacy, license and access questions.
