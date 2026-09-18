# Governor-focused resource revision, 18 September 2026

The two briefs and bilingual page interpret the unchanged 17 September manuscript. No new econometric model was estimated. The public presentation no longer includes a pilot offer, example pilot story, communication-path diagram or H/AG mark.

| Claim or figure | Saved evidence and paper locator | Interpretation |
|---|---|---|
| Inflation from 2% to 10%: +1.68 pp gap, 95% interval 0.90 to 2.46 | `primary_magnitude.csv`, S1 weekly `delta_8pp`; `primary_coefficients.csv`, S1 weekly 9b, IAG_primary, pi_t; paper Section 4.2, PDF p. 8 | Coefficient and interval multiplied by 8 and by 100 for percentage points. Other regressors held fixed; not a causal effect or forecast. |
| Time-control comparison: +2.00 (0.72 to 3.29) with trends; +1.08 (-0.47 to 2.63) with year effects | `regimes_common_slope_sensitivity.csv`, weekly trend/year; Appendix A23, PDF p. 28 | Same 8 pp contrast and scale. All models include volume; year-effects interval includes zero. |
| Later gap trend: +0.076 pp/month, interval 0.035 to 0.118 | `regimes_trend.csv`, S3 monthly IAG_primary; Section 4.6, PDF p. 13 | 25 fitted months; observed chart has 26 monthly points. |
| Common-source gap trend: +0.056 pp/month, p=0.045 | `regimes_common_network.csv`, S3 monthly IAG_common | Same source names do not ensure constant coverage composition. |
| Common-source centrality trend: -0.0051 index units/month, interval -0.0129 to 0.0027, p=0.187 | `regimes_common_network.csv`, S3 monthly C_EV_common; Section 4.7, PDF p. 14; Appendix B2, PDF p. 30 | Keep index units; do not multiply centrality by 100. Interval includes zero; no established lasting structural erosion. |
| Expectations horizons: none / weeks 1–2 / month 12 | `expectations_irf.csv`, S1, IAG_ext, continuity, future horizons, exp_linear / exp_step / exp_balance; Section 4.5, Appendices A11–A12 | Bonferroni correction covers 13 horizons per family including contemporaneous. These are article-share results, not primary-gap effects. Additional controls change the pattern. |
| Relevance, prominence, gap and centrality definitions | Sections 3.2, 4.3, 4.7; Appendices A1–A2; `code/02_build_panels.R`, Part G | Centrality is eigenvector centrality in the projected actor network linked by shared sources. Potential reach does not measure exposure. Generic bank terms can include other institutions. |

Full-history display connects the December 2023 and April 2024 observed points, as requested. January–March remains null in the dataset, missing from the selectable observed months and excluded from models. The line supplies no estimated monthly values. No shading or source-boundary marker is drawn; the caption explains the connector and the lack of harmonisation across the collection change. All valid points, including the 2023 spikes, remain unchanged. HICP is still suppressed in those three months to retain the existing aligned sample contract.

The separate 2024–2026 chart supports discussion of the within-period trend, avoiding an inferred economic change across the earlier collection transition. Monthly and weekly baseline values are not interchangeable.

Verification: `scripts/verify.py` compares all public model coefficients, uncertainty intervals, scenario magnitude, centrality, trends, expectation horizon lists and included monthly observations with saved outputs; checks links, PDF page counts, bundle inventory and unchanged source hashes. `scripts/browser_qa.cjs` checks the live interactions and responsive layout. Both pages of each final PDF are rendered with Poppler and reviewed visually.
