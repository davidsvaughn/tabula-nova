# Philadelphia Fed: public macro probability forecasts and release vintages

Accessed/downloaded 2026-10-01. This is the immediately exercised non-market macro source, not an equity proxy. Primary entrypoints: [SPF data files](https://www.philadelphiafed.org/surveys-and-data/data-files), [FAQ](https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/spf-faqs), [individual forecasts](https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/individual-forecasts), [RECESS definition](https://www.philadelphiafed.org/surveys-and-data/recess), and [RTDSM initial/revised releases](https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/first-second-third).

## Downloaded files and repeatability

Four direct HTTPS GETs returned 200 without credentials. Raw files, exact URL/retrieval-time/byte-count/SHA256 manifest (`sources.json`), and model results remain under ignored `data/research/spf/`. For a clean checkout, download these linked files to the corresponding local names before running the pilot; the inference script intentionally reads the frozen files rather than silently refreshing the sample. Upstream files change over time, so a fresh download is a new data version and must not be presented as an exact rerun.

| Local filename | Primary download | Bytes | SHA256 |
|---|---|---:|---|
| `individual_recess.xlsx` | [Individual_RECESS.xlsx](https://www.philadelphiafed.org/-/media/FRBP/Assets/Surveys-And-Data/survey-of-professional-forecasters/data-files/files/Individual_RECESS.xlsx?sc_lang=en&hash=0D4AF7710877964459FD568F12668CE3) | 310480 | `562a03f9cab7e68f3075ad955e90dcfdfb25967c195f8f07ea393ae6a47756ca` |
| `mean_recess.xlsx` | [Mean_RECESS_Level.xlsx](https://www.philadelphiafed.org/-/media/FRBP/Assets/Surveys-And-Data/survey-of-professional-forecasters/data-files/files/Mean_RECESS_Level.xlsx?sc_lang=en&hash=177B473A08F05FE5EF62292B36352526) | 16277 | `a18636435aefe792377b523cdb64cee9db0d386981f45c1a730911e51866e4e2` |
| `first_gdp.xlsx` | [routput_first_second_third.xlsx](https://www.philadelphiafed.org/-/media/FRBP/Assets/Surveys-And-Data/real-time-data/data-files/xlsx/routput_first_second_third.xlsx?sc_lang=en&hash=AB8BB59BBBF6840DE1448851E90D7A80) | 16432 | `38c7c7316b7ce3f7c8912d110807248a77d3dc1c707f839a1f027cdeb3102c35` |
| `release_dates.txt` | [Historical SPF publication dates](https://www.philadelphiafed.org/-/media/FRBP/Assets/Surveys-And-Data/survey-of-professional-forecasters/spf-release-dates.txt?la=en&sc_lang=en&hash=673DDAC864F629E70FEF0DCB88934863) | 8298 | `c5f4c4dc349068ba9dc1f421c68474be26d0fe613fff83f70aa41eed96696ee3` |

The full individual-forecast workbook is also linked from the individual-forecasts page, but was not downloaded. The small RECESS workbook was sufficient to exercise access and a real classifier comparison without unnecessary laptop memory use.

## What the data means

- Individual RECESS workbook: **9,280 rows**, **232 unique survey quarters**, 1968Q4–2026Q3. Columns: `YEAR, QUARTER, ID, INDUSTRY, RECESS1..RECESS5`.
- Probabilities are percentages. RECESS1 concerns negative real output growth in the survey quarter; RECESS2 the following quarter, through RECESS5 four quarters ahead. The “anxious index” is mean RECESS2.
- These are **not NBER recession probabilities**. They do not predict the joint event of two consecutive negative quarters. Nor does SPF prescribe the particular RTDSM `First` outcome vintage used in our explicitly chosen benchmark.
- Real output was GNP before 1992 and GDP thereafter. The first probe starts survey quarters in 1992 to avoid silently mixing targets.
- Forecasters share outcomes. Thousands of respondent rows do not create thousands of independent GDP realizations. Response count is a survey-administration feature, potentially a calendar/regime proxy; its predictive interpretation is unestablished.
- Actual publication dates are supplied separately from respondent deadlines. Use public publication time for a public-consensus feature; an individual respondent's earlier internal knowledge is not public availability. Intraday publication timestamps were not audited in this experiment.
- True dates before 1990Q2 are unknown; 1990Q2 was collected retrospectively. Government shutdowns delayed some subsequent surveys, including 1996Q1, 2013Q4, 2019Q1 and 2026Q1. Do not synthesize an unvarying mid-quarter date.

## First-release caveats: essential, not optional

Read the [RTDSM computational documentation](https://www.philadelphiafed.org/-/media/FRBP/Assets/Surveys-And-Data/real-time-data/data-files/documentation/Documentation_First_Second_Third_Release_Values.pdf?sc_lang=en&hash=13753FDA92823F62771D93FD41544D88), updated May 21, 2026.

`First`, `Second`, and `Third` are growth rates calculated from the appropriate vintage **levels**, annualized with discrete compounding. They are not literal transcriptions of every rounded press-release print. The archive normally selects the monthly vintage in which a release should appear, with documented adjustments or missing values when timing changes. The latest-vintage `Most_Recent` column is a different outcome definition and must not fill missing first releases.

Observed/ documented exceptions include:

- **1995Q4:** first GDP release marked missing due to the shutdown. Our event table excludes survey 1995Q3, whose next-quarter target is this missing observation.
- **2018Q4:** the delayed February 28, 2019 release is treated as First even though it incorporates more source information than a normal advance estimate; Second is missing.
- **2025Q3/Q4:** First is missing in the downloaded workbook. Documentation explains shutdown-related disruption and restoration of the normal GDP flow with the advance 2026Q1 release.
- CPI, payroll and other monthly series have their own missing-release/revision policies. CPI growth values are annualized in these convenience files; they cannot be copied as rounded monthly BLS percentages.

Consequently the pilot is a **retrospective forecast-combination feasibility study**, not a certified point-in-time backtest. It uses actual SPF publication dates and a deliberately conservative four-quarter target-period embargo for training labels, but does not reconstruct every historical GDP release timestamp or original-vintage SPF file correction.

## Broader opportunity beyond the binary probe

The SPF file index includes real/nominal GDP and components, unemployment, payrolls, industrial production, housing, interest rates, CPI/core CPI/PCE/core PCE, and long-run inflation/productivity expectations. It also provides forecast distributions:

- `PRGDP`: annual-average real GDP growth.
- `PRPGDP`: annual-average output-price inflation.
- `PRCCPI`, `PRCPCE`: Q4/Q4 core CPI/PCE inflation.
- `PRUNEMP`: annual-average unemployment.

Those targets/horizons are not interchangeable. Bin definitions, questionnaire changes, horizon alignment, respondent ID caveats and publication/label clocks need inspection before pooling. Some series begin much later: CPI forecasts begin 1981Q3, PCE 2007Q1 according to the FAQ. Missing early years are not zero outcomes.

A useful next question is whether a model improves **a full macro distribution or a forecast combination**, conditional on survey disagreement and vintage-safe indicators, versus simple consensus and linear/shrunk combinations. More thresholds per quarter improve diagnostic coverage, not independent-event sample size. The completed first test and unfavorable aggregate TabPFN result are preserved in [LOG-005](../logs/LOG-005.md).

The [completed feature/ensemble ablations](../logs/LOG-006.md) preserve that original
result and test the administration-count concern directly. Removing respondent
count did not fix late false alarms; they remain even with the five mean probability
inputs only. Eight estimators modestly improve TabPFN within each feature set but
do not beat consensus overall. This narrows a feature hypothesis, not the general
question of foundation-model macro skill.

[LOG-007](../logs/LOG-007.md) adds an actual LimiX-2 comparison on the same 84
events: all 32 official pipelines, with one query per call because its preprocessing
fits on combined training/query features. LimiX Brier/log loss 0.170312/0.526035
also trails consensus overall. This confirms runtime/data feasibility for both
models, not general macro skill or a causal explanation of late-period errors.
