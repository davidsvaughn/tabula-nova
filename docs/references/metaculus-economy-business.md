# Metaculus: economy/business and broad superforecasting

Accessed **2026-10-01**. Starting reference: [Economy & Business question feed](https://www.metaculus.com/questions/?categories=economy-business).

## Bottom line

Metaculus is a relevant source of **well-specified economic questions, probabilistic forecasts, and forecasting practice**, not just stock predictions. Its [FAQ](https://www.metaculus.com/faq/#predmarket) explicitly distinguishes its probability aggregation from a prediction market. Examples below cover growth, employment, inflation, monetary policy, recession dating, productivity, and global technology investment.

**Freshly exercised:** logged-out public browser pages exposed question criteria, current forecasts, and historical forecast charts, including a resolved inflation question. The category feed also rendered actual questions in Chromium even though the static reader returned navigation only. **Not obtained:** a machine-readable historical community-forecast dataset, authenticated API results, complete category coverage, or a model evaluation.

**Permission is a separate prerequisite from technical access.** The current [official API documentation](https://www.metaculus.com/api/) explicitly says Metaculus data may not be used to **train, evaluate, or otherwise create/develop AI/ML models or algorithms without prior written permission**, and that commercial use requires a separate written agreement. The [Terms of Use](https://www.metaculus.com/terms-of-use/), marked September 21, 2026, also restrict automated extraction and AI/ML training/development. Public visibility is not a research-data license. This document is a linked source/access assessment, not a downloaded training corpus or permission to benchmark TabPFN on Metaculus data. Request an appropriate grant before that step; none was requested or accepted here.

## Access findings: observed versus documented

| Surface | Fresh observation | What this establishes—and does not |
|---|---|---|
| Supplied category URL, static `read` | Returned feed navigation/category links without question cards. | A static extraction limitation, **not** proof that the feed requires login. |
| Same category URL, managed Chromium | Rendered economic question cards, including US national debt, labor/employment, and technology-business questions. Header displayed **Log In / Sign Up**. | Public rendered discovery works. No user Chrome session was inherited; no relay or user cookies were used. Feed mixes macro, business, and market questions, so category membership alone is not a clean macro benchmark universe. |
| Individual linked pages, static reader | Titles, some aggregate displays, and chart/tab labels were present; detailed criteria were missing. | A partial render. Missing criteria in this response do not imply unavailable criteria. |
| Individual pages, Chromium → **Question Info** | Displayed resolution criteria, fine print, sources, and metadata without login. Content sometimes hydrated after the tab label appeared. | An exercised, reusable public reading route. Comments are not substitutes for the authoritative criteria. |
| `/api/`, static reader | Markdown response was empty. Raw HTML linked Swagger's OpenAPI YAML at `/static/openapi.6835eb50da0b.yml`; that schema was publicly readable. | The API documentation is JavaScript-backed, not absent. The fingerprinted schema URL may change; rediscover it from `/api/`. |
| Three unauthenticated Python GETs: feed, post 41089, download for post 41089 | All returned **HTTP 403, Cloudflare error 1010, `browser_signature_banned`**. | This client was blocked before an API authorization decision could be inferred. We did not treat this error as proof of a missing token or retry that client. |
| Same-origin `fetch('/api/posts/41089/')` in logged-out Chromium | **HTTP 403:** `Permission Error: The API is only available to authenticated users. Please create an account and use your API token to access the API.` | Directly proves authentication is required on the exercised post-detail API route. It does **not** prove that a token grants unrestricted aggregates or archives. |
| Resolved CPI post 41681 → **ALL** forecast timeline | Visible multi-option historical timeline, Jan–Mar 2026, and the resolved 0.2% option; visual screenshot confirmed it. | Historical forecasts are visible on this public UI example. No numerical history export, exact historical snapshot completeness, or historical API entitlement was established. |

Only read-only navigation, question-info/timeline controls, and GET probes were used. No forecast, comment, follow, vote, account change, credential registration, data-access form, or authenticated request was submitted. The managed research tab was closed.

### Official API policy, read on this date

The [linked OpenAPI schema](https://www.metaculus.com/static/openapi.6835eb50da0b.yml) and [March 9, 2026 API-change announcement](https://www.metaculus.com/notebooks/42554/changes-to-the-metaculus-api/) document:

- API authentication uses `Authorization: Token …`. The current schema says all API requests require authentication; the post-detail probe above independently demonstrated that requirement for one endpoint.
- Authenticated accounts can access their own predictions/scores/comments, open question text, and closed-question text/resolution values for questions on which they forecasted. **That is not a general resolved-question archive entitlement.** Do not place forecasts merely to manufacture access.
- Current Community Prediction access is limited to a small set of approximately **50 questions** for ordinary authenticated accounts. Aggregates are otherwise omitted.
- A separate bot-benchmarking tier is described as roughly **250 open and 250 resolved questions**, with current Community Prediction, question text, and resolution access. Application/approval and permitted use remain separate matters; none was exercised. These are documentation figures, not a freshly enumerated catalog, and not necessarily macro questions.
- Staff comments can be requested using `author_is_staff=true`; the documentation notes this returns staff root comments, not necessarily staff replies. Complete rule clarification history therefore needs an explicit availability check.
- `/api/data/download/` is a **restricted** ZIP/CSV endpoint requiring granted access; project-wide exports additionally require project whitelisting. Its existence does not mean an ordinary account can obtain the archive.
- The announcement says aggregates are no longer generally available and invites non-commercial/commercial data requests. The newer schema is more specific than older examples of unrestricted API use. Its generic “Get Started” copy is less precise than its explicit authentication/restriction section; rely on the latter and exercised results.

The official access-request form and `api-requests@metaculus.com` are linked from [the API page](https://www.metaculus.com/api/). A useful request would specify non-commercial macro/superforecasting research, resolved economic questions, timestamped aggregate distributions, resolution/rule revisions, exact permissible AI/ML evaluation uses, retention, and redistribution. This is a proposed request scope, **not an approval**.

## Concrete linked examples

All eight pages below were opened publicly in Chromium and their **Question Info** criteria read. These are concise paraphrases, not replacement settlement rules. The URLs identify posts; grouped posts contain separate subquestions whose API IDs must be retrieved rather than guessed. Format labels below describe the observed forecasting interface; raw API type enums were not retrieved.

| Area and real question | Observed format / horizon | Resolution rule and evaluation trap |
|---|---|---|
| Growth: [Will US GDP decline in Q1, Q2, or Q3 2026?](https://www.metaculus.com/questions/41089/will-us-gdp-decline-in-q1-q2-or-q3-2026/) | Binary; any of three quarters. Open at access. | Yes if BEA reports negative US GDP growth in any listed quarter, **using its third estimate**. If no third estimate for a quarter is released before 2027, use the latest estimate released in calendar 2026. Do not relabel it using the advance release, latest revised GDP, or an NBER recession indicator. |
| Labor: [Will the US unemployment rate reach 10% before 2031?](https://www.metaculus.com/questions/18664/us-unemployment-rate-10-before-2031/) | Binary threshold; through the start of 2031. Open at access. | Positive resolution requires BLS data showing unemployment **at least 10%**, with credible financial-press reports as fallback if BLS no longer exists. Background specifies seasonally adjusted unemployment at any point before January 1, 2031; formal criteria are shorter. Confirm any series/frequency ambiguity before constructing labels instead of silently treating background as an additional rule. |
| Inflation: [US monthly core CPI for February 2026](https://www.metaculus.com/questions/41681/us-core-cpi-for-feb-2026/) | Multiple-choice/categorical display of inflation options; resolved UI marks **0.2%** as Yes. | BLS seasonally adjusted monthly **all items less food and energy**, **initial release only**; later revisions do not re-resolve it. Annulled if relevant data was not published before March 14, 2026. Preserve the actual option list/tails and rounding; do not substitute headline, year-over-year, or revised CPI. The displayed resolution was observed on Metaculus, not independently revalidated against BLS in this task. |
| Monetary policy: [Upper limit of the federal funds target range on listed dates](https://www.metaculus.com/questions/14171/what-will-the-feds-upper-target-be-on-these-dates/) | Group of numeric distributions; displayed dates include March 31, April 30, June 30, July 31, 2026. Post marked resolved at access. | FOMC upper limit of the target range at **11:59 PM ET** on each listed date. Not the effective federal funds rate, target midpoint, or announcement-time rate. Preserve ET-to-UTC conversion and group dependence. |
| Recession: [Will the US enter a recession before the following dates?](https://www.metaculus.com/questions/11600/next-us-economic-recession/) | Group of binary deadlines: 2023, 2024, 2025. Overall post closed/awaiting resolution; two earlier rows shown No. | NBER recession onset during the interval from January 1, 2021 to January 1 of each respective year. Allows **two years** for NBER's delayed declaration, then No. This is not the two-negative-GDP-quarters definition. Closed is not resolved; onset time and label-availability time are different. |
| Productivity: [US GDP per hour worked](https://www.metaculus.com/questions/12916/us-gdp-per-hour-worked-productivity/) | Group of numeric distributions for 2025, 2032, 2052, 2122. | Earliest credible OWID GDP/hour data, expressed in **2017 USD**, with the World Bank GDP deflator or similar fallback. Later routine OWID revisions do not count; significant errors can cause discretionary re-resolution. Missing source/successor-state/civilization conditions have explicit alternatives or Ambiguous outcomes. Labor hours count humans under a detailed definition: automation scenarios cannot casually replace hours with compute. |
| Technology/economy: [Total annual global investment in AI companies](https://www.metaculus.com/questions/12930/total-annual-investment-in-ai-companies/) | Group of numeric distributions for 2025, 2032, 2052, 2122; includes historical and future subquestions. | Earliest credible OWID **annual global corporate investment in AI**, inflation-adjusted to **2021 USD** using CPI or similar fallback. Background identifies Stanford AI Index/NetBase Quid upstream. Later routine revisions ignored; significant-error, unavailable-source, and civilization contingencies apply. This is an investment-flow forecast, not an equity-return forecast. |
| Non-US macro: [Will Nigeria's inflation rate fall below 15% during 2026?](https://www.metaculus.com/questions/44553/will-nigerias-inflation-rate-fall-below-15-during-2026/) | Binary path threshold. Open at access. | NBS official headline **year-over-year** inflation **strictly below 15.0%** in any monthly release during 2026; only first monthly figures qualify. Annulled if comparable monthly data for every month is not released before July 1, 2027. Preserve publication-month/reference-month wording and comparability rules; do not assume rebased/revised series are interchangeable. |

The general [question-type FAQ](https://www.metaculus.com/faq/#question-types) also documents binary, numeric/discrete/date ranges, multiple choice, groups, and conditional pairs. Multiple choice has mutually exclusive exhaustive options; a group need not. Date distributions and open-ended ranges can assign probability beyond their displayed bounds. A binary-only parser would discard much of the useful macroeconomic material.

## Reusable retrieval routes

### Public reading route: exercised successfully

1. Open the supplied category page in a normal JavaScript-capable browser; use its filters/search or linked questions above. Static text extraction alone missed the feed cards.
2. Open a question and select **Question Info**. Wait for the actual criterion paragraph—not merely its heading—to hydrate. Read **Resolution Criteria**, **Fine Print**, source links, timestamps, and any staff clarifications.
3. Select **ALL** in the forecast timeline to inspect displayed history. This worked on resolved CPI post 41681. Treat chart inspection as qualitative/manual access, not an exact machine-readable historical dataset.
4. Record access time separately from each forecast's historical timestamp and question's publication/resolution clocks. Current page text is not proof of what its rules or sources said years ago.

Do not turn this small manual source review into bulk browser scraping to work around API restrictions.

### Documented API route: authentication/access-gated

The current API organizes the feed around **posts**, not standalone questions. Documented read routes and useful parameters are:

```text
GET /api/posts/?categories=economy-business&limit=2&include_descriptions=true&with_cp=true&include_cp_history=true
GET /api/posts/41089/
GET /api/data/download/?post_id=41089
```

The first and third routes were attempted with unauthenticated Python and encountered Cloudflare 1010; the second also received an explicit authentication denial in a logged-out browser. **No successful JSON/ZIP retrieval is claimed.**

This is the exact small browser-side GET pattern used to distinguish the application authentication error from the Python client's Cloudflare block, executed on a public Metaculus page:

```javascript
const response = await fetch('/api/posts/41089/');
console.log(response.status, await response.text());
// Observed: 403, Permission Error: The API is only available to authenticated users...
```

After an appropriate permission/access grant, use the documented `Authorization: Token …` header without logging its value. Useful documented feed parameters include `statuses` (`open`, `closed`, `resolved`, `upcoming`), `forecast_type`, `categories`, `limit`, `offset`, and timestamp filters. `include_descriptions=true` requests description, criteria, and fine print. `with_cp=true` requests entitled aggregates; `include_cp_history=true` requests history but **does not override access restrictions**. Group feed responses with CP only include the top three subquestions; use post detail to inspect all. Pagination and subquestion accounting are required before making any coverage claim.

The schema describes `aggregations.recency_weighted.history`, other aggregation methods, and timestamped forecast records. Restricted ZIP exports describe question/forecast CSVs and optional scores/comments/key factors. Those are **documented shapes, not observed payloads**. The schema itself warns CSV documentation can be stale; use the README supplied with a permitted export. Distinguish actual question IDs from post IDs and do not invent a history endpoint.

## Historical versus live availability

- **Live public UI:** observed current probability/distribution summaries on open examples. These are snapshots, not locally collected histories. No live forecast has been treated as an out-of-time predictor for an already resolved target.
- **Historical public UI:** observed a full-range plotted forecast timeline for resolved CPI and historical/closed displays for rates and recession. The underlying numerical timestamps/distributions were not exported. A screenshot or today's aggregate is insufficient for leakage-safe scoring.
- **Ordinary authenticated API:** current limited CP access and closed-question restrictions are documented, not freshly authenticated here. Neither login nor possession of an API token implies broad historical CP access.
- **Special historical access:** documented export endpoint, access application, and history fields provide a route to ask for authorized archives. Availability, historical completeness, rounding/downsampling, revisions, and macro coverage remain unverified until an approved export is exercised.
- **Prospective collection:** a proposed alternative after permission is to record forecasts contemporaneously at predeclared cutoffs. It cannot retroactively create a past archive and must follow the permitted access route/retention rules.

## Scoring and a proper evaluation design

### Platform rules: sourced facts

The [Scores FAQ](https://www.metaculus.com/help/scores-faq/) explains that Metaculus scores derive from **log scoring**, not trading profit:

- Binary/multiple-choice log score uses the probability assigned to the actual outcome. Continuous scoring uses density (or discrete PMF), with the platform's smoothing, bounds, and discretization conventions. Out-of-range outcomes are scored using probability mass assigned beyond the relevant bound.
- **Baseline score** compares against a fixed equal-probability/uniform baseline with platform rescaling. **Peer score** compares a forecaster's log score with the mean of other forecasters' log scores. It is not simply a difference against the displayed Community Prediction. Legacy Relative scores use different comparisons and should not be mixed without identification.
- Usual scores are **time-averaged**: a standing forecast contributes in proportion to its duration. Missing periods count as zero for these platform scores; early resolution can leave zero-score periods through scheduled close (score truncation). Tournament hidden-period/coverage rules also matter.
- A **spot score** uses a forecast at one specified time, ordinarily the community-reveal time unless otherwise stated. It is not interchangeable with whole-lifetime performance.
- The [Community Prediction FAQ](https://www.metaculus.com/faq/#community-prediction) describes recency-weighted aggregation; do not confuse it with the distinct Metaculus Prediction, an individual expert, or an exchange price.

### Proposed research design—not an executed benchmark

1. **Resolve permission first.** Obtain explicit authorized AI/ML evaluation scope and an archive grant if needed. Do not infer permission from public charts or the bot-tier description.
2. **Freeze a broad, meaningful target universe.** Use separately reported strata: recurring macro releases (growth, inflation, employment, rates), policy/regime events, and longer-horizon productivity/technology questions. Include non-US economies. Define eligible statuses/dates before outcomes; avoid selecting only interesting or easily accessible resolved questions.
3. **Represent each contract precisely.** Store post/subquestion IDs, rule version, format, units, option history, bounds/scaling, initial-versus-revised data policy, source, publication deadline, and ambiguity/annulment rules. Log strict versus inclusive thresholds. Preserve all paired/grouped outcomes rather than counting each as independent evidence.
4. **Choose forecast clocks before scoring.** For release questions use predeclared lead times relative to the scheduled release; for longer questions use predeclared calendar checkpoints or normalized horizons. Compare model, base rate, and available community forecast at the **same** cutoff. Never use a later consensus value or interpolate using future snapshots. Report missing/stale aggregate coverage explicitly.
5. **Respect information and label timing.** Use original-release labels where required (CPI), third-estimate labels where required (the GDP example), and the specified deflator/source vintage for productivity. Use point-in-time macro features. Train/calibrate only on labels whose resolution was knowable before the forecast cutoff; NBER's delayed declarations make recession onset date an invalid training-availability timestamp.
6. **Use chronological, grouped evaluation.** Roll forward in time; group neighboring thresholds, shared releases, nested deadlines, conditionals, and related economic episodes. Purge overlapping target windows. Hundreds of snapshots of one recession are not hundreds of independent outcomes. Fit transforms/tuning/calibration on past folds only.
7. **Match metrics to forecast type.** For binary events report Brier score, log loss, calibration, and paired differences versus simple base rates and strong conventional probability models. For categorical outcomes use multiclass proper scores; for numeric/date distributions use CRPS/appropriate log-density or discretized log scoring plus interval coverage. Freeze clipping, units, tail bins, and scale conventions. A point estimate is not a substitute for a distribution.
8. **Keep two score tracks distinct.** A fixed-horizon scientific comparison and a faithful replay of Metaculus time-weighted/spot/tournament scores answer different questions. Reproducing Peer scores requires other forecasters' contemporaneous score inputs, not merely a CP timeline. Do not claim platform-score reproduction from insufficient data.
9. **Separate independent skill from aggregation skill.** A model using community probabilities as input cannot demonstrate independent superiority to that community on the same data. Report model-alone and permitted model-plus-consensus variants; fit any combiner on out-of-sample, genuinely contemporaneous forecasts. Fresh LLM forecasts on old resolved questions risk training/hindsight contamination.
10. **Report event-level uncertainty and limits.** Compare paired eligible events, report exclusions/annulments and unresolved censoring, and use event/episode-aware intervals. Do not equate forecasting gains with executable returns. Long-horizon questions are useful for scenario reasoning even when too few have resolved for a convincing accuracy claim.

**Research hypothesis:** repeated macro-release questions could support a structured distributional forecasting experiment, while policy/productivity/technology questions provide the broader judgment-intensive superforecasting setting. This is a proposed research split, not evidence that any model beats Metaculus or that enough permitted historical data is already available.
