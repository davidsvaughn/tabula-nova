# Target universe and the priors/calibration gap

Date: 2026-10-02. Companion to [LOG-011](logs/LOG-011.md). **No model, collector or
acquisition was run to produce this document.** It enumerates what could be predicted,
rates each target by the four ingredients a defensible study needs, and states where the
project has under-used the "prior + learned correction" and calibration ideas from
[chat 003](chats/003-explain-probability-calibration.md). Status markers:

- ◇ documented source or acquisition in this repo (`DATA-SOURCES.md`, `references/`, logs)
- ◆ partially acquired here; coverage/verification incomplete (see note)
- ⚠ access/coverage asserted from general knowledge, **not verified in this repo** — audit
  before planning on it
- — not applicable / none

## Status correction before the table

Two statements made verbally during the 2026-10-02 session were wrong and are fixed here:

- **Kalshi economics markets were not "never collected."** JevTrader's *candle* collection
  excluded Economics/Financials, but this project's CPI audit acquired **552 unique CPI
  market tickers / 67 monthly events** (483 historical + 69 live), 63 resolved vendor
  outcomes, 61 matching official monthly targets, and probed cutoff candles for three
  events ([coverage reference](references/cpi-forecast-coverage.md) §Measured result,
  §Actual cutoff quote probes). What remains unverified: full matched cutoff-quote
  coverage per event and strict quote-update age. Status: **◆ partial; do not
  re-acquire; extend and audit.**
- **EIA retail gasoline feasibility is not completed.** LOG-010 Next step 1 is the
  *pending* audit (payload hashes, posting schedule, 2018-05-14 method change, terms,
  matched monthly coverage). Only the public schedule/methodology pages were read. Status:
  **pending gate, not established access.**

## What has been measured so far (for context)

| Claim | Evidence | Reading |
|---|---|---|
| TabPFN/LimiX beat strong conventional methods on macro | SPY vol: ridge won (LOG-004). GDP contraction: direct SPF won (LOG-005–007). CPI lag-only: LimiX ~2.2% CRPS lead, bootstrap SE ≈ 0.005 (LOG-009/010). | No demonstrated foundation-model edge. LOG-010:33–40: the SPY control and lag-only CPI did **not** test the richer organizing hypothesis (timely evidence, forecast combination). Untested, not refuted. |
| Native TabPFN predictive distributions are calibrated on macro data | Never tested; all CPI methods used a shared trailing-residual wrapper (LOG-009:56, LOG-010:37). 80% intervals covered 69–73%. | Open. The wrapper result says nothing about native calibration. |
| Text → "does something move" (JevTrader S1) | AUC 0.761 CV 2025, 0.725 out-of-time 2026 vs context-only 0.688/0.660; logistic gate. | Replicated positive, outside this repo's charter, not tradable (activity ≠ direction). |
| Past-fit isotonic improves Jev probabilities | Materiality Brier 0.194→0.141 on 2026 with a 2025-fit map (J020:30). | Measured calibration gain on a Jev output; directly relevant to the calibration program. |
| Kalshi text-lane prices are mispriced detectably | K2: nothing survives fees on 13,975 liquid markets (J007). | Null for text-lane; economics markets untested. |

## The four ingredients

A target is worth a study only if it has all four:

1. **Independent events** — count outcomes, not rows; correlated thresholds/series/regions
   share shocks.
2. **Original-release labels with vintages** — first prints, not today's revised series.
3. **A strong public prior** — a professional/statistical/market forecast to correct, so the
   question is incremental value, not "can a model forecast at all."
4. **Timely exogenous evidence** not already inside that prior, with a defensible
   availability clock.

GDP contraction failed (1); lag-only CPI omitted (4) by design. Those were the first two
targets tried.

## The universe

Events column = approximate independent outcomes available over ~25 years unless stated.
Consensus history from free aggregators is uniformly ⚠: Bloomberg/Reuters consensus is
paid, and this repo has no acquired monthly economist consensus (LOG-010:13).

| Family | Target | Events | Vintage labels | Public prior | Timely evidence | Notes |
|---|---|---|---|---|---|---|
| **Weekly labor** | Initial jobless claims: level, surprise, revision | ~1,300 | ALFRED ⚠ (vintages exist for ICSA; not pulled here) | consensus ⚠ | state-level claims (DOL state release ⚠), WARN notices ⚠, search-interest proxies ⚠ | Highest-frequency official macro series; best event count of any candidate. |
| **Weekly energy** | EIA natural-gas storage change; crude/gasoline inventory change | ~1,300 | EIA ⚠ (weekly archives public) | published consensus ⚠; API survey ⚠ | heating/cooling degree days ⚠, pipeline flows ⚠ | Prior is very efficient; the surprise is the target. Weekly gasoline *price* series is the pending LOG-010 gate, a different series. |
| **Revisions** | NFP first→third print; GDP advance→third; claims revision | ~300 monthly / ~100 quarterly | RTDSM ◇ (first/second/third GDP acquired); ALFRED ⚠ for NFP | the first print *is* the prior | concurrent indicators: claims, household survey, ISM employment, regional surveys ⚠ | Cleanest residual-form setup: target = correction to a stated prior. Revisions are documented in the literature as partly predictable; verify on our vintages. |
| **Survey chain** | ISM manufacturing/services from the five regional Fed surveys released earlier in the month | ~300 | ISM rarely revised ⚠ | consensus ⚠ | Empire, Philadelphia, Richmond, Dallas, Kansas City ⚠ | Known nowcast chain; tests whether a foundation model finds a better combination than regression. Regional surveys are not five independent shocks. |
| **Two-stage releases** | UMich sentiment preliminary→final; Eurozone HICP flash→final | ~300 | official ⚠ | the preliminary/flash | — | Narrow, near-zero-leakage; small revisions, so small effects. |
| **Monthly prices** | CPI headline/core, PPI, PCE with energy + nowcast evidence | ~300 (318 CPI prints acquired ◇) | BLS archive ◇; RTDSM ◇ | Cleveland nowcast ◇ (4,673 dated estimates); SPF ◇ | EIA weekly gasoline (**pending audit**, LOG-010:107); Kalshi CPI prices ◆ | The LOG-010 study. Correct and in progress; no longer the only candidate. |
| **Monthly activity** | Retail sales, industrial production, housing starts/permits, durable goods, JOLTS | ~300 each | ALFRED ⚠ | consensus ⚠ | permits→starts, mortgage applications ⚠, card-spend proxies ⚠ | Separate cohorts; pooling across series is a panel with `group_col`, rows ≠ events. |
| **Policy** | FOMC decision; statement tone; dot-plot drift | ~8/yr | — | fed-funds futures / CME FedWatch ⚠ (near-perfect for the decision) | Fed speeches, Beige Book, transcripts: public, timestamped ⚠ | The decision is solved by markets. The *text* is where Jev-style features belong (see §Jev). |
| **Cross-country** | ECB/BoE/BoC decisions; foreign CPI/PMI flashes | ×N countries | mixed ⚠ | mixed ⚠ | — | LOG-010 deferred heterogeneous pooling; an event-count multiplier for later. |
| **Panel/regional** | State unemployment; sector employment | 50–100 series/month | BLS ⚠ | — | — | Many rows, few independent shocks. AGENTS: thousands of snapshots ≠ thousands of outcomes. |
| **Nowcast errors** | GDPNow / NY Fed Nowcast error and \|error\| | ~50 quarters | published vintages ⚠ | the nowcast | survey disagreement, data-flow surprises | LOG-010's conditional-uncertainty framing; too few events to resolve small effects. |
| **Market-priced macro** | Kalshi CPI (◆), Fed, jobs, claims markets vs nowcast/consensus | ~12/series/yr since 2021 (CPI: 63 resolved ◇) | settlement ◇ (vendor; 61 match official) | market price ◆ (cutoff quote coverage unverified) | Cleveland ◇, EIA (pending), claims ⚠ | Where Kalshi, priors and calibration meet inside the charter. Extend from the existing 552-contract CPI acquisition; do not duplicate it. Other economics series not yet acquired. |
| **Superforecasting questions** | Recession in 12 m; inflation > X in 12 m; unemployment > Y | few, long-horizon | NBER / official ◇⚠ | SPF density ◇, Kalshi ⚠ | — | Slow validation; prospective portfolio accrual only (LOG-010 complement). |

Ordering by event count: **weekly claims → revisions → survey chain → weekly energy
surprises → monthly prices**. The project started at the bottom of that list.

## Where the priors/calibration ideas are under-used

1. **TabPFN has been used as a point forecaster.** A PFN approximates a posterior
   predictive under a learned prior over data-generating processes; the project wrapped
   its point outputs in the same trailing-residual uncertainty as ridge. Native
   quantiles/CRPS and reliability tables were LOG-010's "bounded secondary method"; they
   should be the primary distributional method in any next study. LimiX's native output
   semantics must be checked separately (LOG-010:101).
2. **The prior went in as a feature, not as an offset.** Chat 003's structure is
   `logit P = logit p_prior + g(x)` / `y = prior + g(x)`: predict the residual of the
   professional prior and shrink toward it. GDP used SPF as one column among several and
   asked TabPFN to re-derive consensus from ten positives. Revisions and the survey chain
   are residual-form by construction.
3. **No reliability curve exists for any prior on a frozen cohort.** Cleveland, SPF
   probabilities and the 61 matched Kalshi CPI settlements have Brier/CRPS scores in places
   but no calibration tables. The chat's hierarchical calibrator (global → domain → regime)
   presupposes that baseline. SPF recession probabilities are reported in the literature as
   miscalibrated at horizon; measuring it here is a result in itself.
4. **Jev has no role on numeric macro.** It cannot do arithmetic or dates (JevTrader
   `jev.py:1–18`). Its one replicated win is text → "does something move." The in-charter
   analog is Fed communication: hundreds of timestamped public speeches/statements per
   year; target = does the 2-year yield or fed-funds-futures price move beyond a threshold
   in the following window; Jev answers k concrete hawkish/dovish/labor/inflation questions
   as features. Public timestamps, no survivor bias, transfers the working pattern rather
   than asking Jev to forecast. Rate/futures intraday data access is ⚠ (Schwab paper
   quotes exist for current context only; no archived futures history, `DATA-SOURCES.md`).

## Proposed order (proposal, not a decision)

1. **Calibration audit of priors already held** — Cleveland, SPF, matched Kalshi CPI
   settlements: reliability tables and proper scores on frozen cohorts. No model fits.
   Establishes the baseline the calibration program needs.
2. **First residual-form study on a high-count target** — weekly claims or NFP revisions,
   native TabPFN predictive distributions scored, prior as offset. Requires an ALFRED
   vintage audit first (⚠).
3. **Extend the Kalshi economics acquisition** from the existing 552-contract CPI base to
   Fed/jobs/claims series via the documented historical route, within rate limits; verify
   cutoff-quote coverage before scoring anything against market prices.
4. **LOG-010's energy/CPI study** runs when its pending EIA/Cleveland gate clears.
5. **Fed-communication reaction with Jev features**, after 1–3, only if intraday rate data
   access is verified.

LOG-011's arms A–D (stock activity, Kalshi text-lane, repricing panel, evidence-conditioned
Jev) remain recorded; A is the fastest engineering check, but none of them is a macro
study. Every item above still requires the LOG-010 pause/authorization gate before any
model inference.
