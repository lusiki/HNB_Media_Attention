# Inspection release 2026-09-19.3

The inspection layer introduced in presentation 2026-09-19.2 extends the public presentation of the 17 September 2026 manuscript. It does not re-estimate econometric models. Its descriptive aggregates of existing scored institutional records are reconciled to the saved monthly panels. Presentation 2026-09-19.3 preserves those values and updates the briefs, figures and document readers, including the full January 2021–May 2026 timeline in both briefs.

## Value provenance

| Published component | Input | Calculation or selection |
|---|---|---|
| Primary monthly values | `panel_monthly.csv` | Saved salience–reach numerator and inflation reach denominator; weighted share = 100 × numerator / (denominator + 1). |
| Common-source monthly values | `panel_monthly_commonsrc.csv`; `code/07_common_sources_panel.R` | Same 258 source labels in both corpora, present during 2023 and July–December 2024. Each series uses its own saved baseline. |
| Article share | The two monthly panels | 100 × relevant institutional item count / (inflation item count + 1). |
| Source/item concentration | Existing scored RDS records, processed by `aggregate_inspection.R` | Numerator weights are salience × potential reach × inflation relevance. Sum the five largest source contributions, the ten largest item contributions and squared source shares. Reconcile counts and total weights before publishing. |
| Domain table | Same aggregates | Domain-form labels with relevant institutional items; alphabetical default. Contribution is a fraction of the whole institutional numerator, not a fraction rescaled to the domain table. |
| F1 reference and no-volume alternatives | `primary_coefficients.csv` | S1, weekly/monthly, IAG_primary, pi_t, equations 9b and 9a. |
| F1 time-control alternatives | `regimes_common_slope_sensitivity.csv` | Same frequency; additional period trends and calendar-year effects. |
| F1 source/weight alternatives | `spec_curve_curve.csv` | S1, weekly/monthly, IAG_common or IAG_winsor, HHI_all, controls 3. |
| F2 trends | `regimes_trend.csv`, `regimes_common_network.csv` | S3, weekly/monthly, IAG_primary or IAG_common; controlled trend. |
| F3 expectations | Existing `evidence.json`, checked against `expectations_irf.csv` | S1, IAG_ext, continuity controls; exp_linear, exp_step and exp_balance. Future horizons passing the saved Bonferroni correction. |
| F4 network trends | `regimes_common_network.csv` | S3, weekly/monthly, C_EV_common and C_EV_reconstructed. |

F1/F2 coefficients and bounds are multiplied by −100 to express weighted-share percentage points; transformed bounds are reordered. F4 stays in centrality index units. Weekly and monthly coefficients occupy distinct views and state their time units. F3 labels its mixed frequencies row by row.

The descriptive endpoint difference is not a fitted trend or significance test. The evidence strip always names its research finding and model frequency separately from the selected month. The fixed finding record retains its reference model when display settings change.

The diagnostic HHI measures concentration of institutional salience–reach weight. It is not the broad, source-reach HHI used as a regression control. Item counts represent publication instances. No validated duplicate-story count or ownership classification is asserted. Domain labels alone do not establish editorial independence.

## External context

The media-context paragraph uses the [Reuters Institute's 2025 Croatia profile](https://reutersinstitute.politics.ox.ac.uk/digital-news-report/2025/croatia) and [2025 survey methodology](https://reutersinstitute.politics.ox.ac.uk/digital-news-report/2025/methodology), consulted 19 September 2026. It identifies year, online survey population, YouGov fieldwork, demographic quotas and weighting. It does not apply the 2025 survey across the study's entire date range or treat survey news use as observed exposure to the corpus.

## Version and scope

Data: `extended-2026-09-17`. Method: `extended-manuscript-2026-09-17`. Presentation: `2026-09-19.3`. Aggregate and input hashes are in `inspection-input-hashes.json`; baseline research hashes are in `research-input-hashes.json`. Review remains pending. The four finding records provide English and Croatian claim, model, measure, sample and manuscript location.

The new public JSON contains monthly aggregates, selected saved coefficients and domain-form source labels. The scored input, item text, social account identifiers, aggregate preparation intermediates, QA artifacts and author manuscript remain outside the served bundle. Earlier editorial notes document historical presentations; this release's source and built pages define current behavior.
