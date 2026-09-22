# Extension edition 2026-09-22.1

This edition extends the recovered public presentation 2026-09-21.3 (commit
`1e46c78`). Corpus HNB_MEDIA 2026-09-21.1 and core retrieval method 1.0 are
unchanged. Indicator specification: HNB_MEDIA_INDICATORS_1.0. Lexical extension:
HNB_MEDIA_LEXICAL_1.1. Public deployment is separate from author approval and
independent validation, both of which remain pending.

## New public evidence

- Source archive rates with the AND threshold of 5,000 background and 50 HNB
  publications; 78 domains qualify over the full window. Three reference windows
  and selected-view CSV exports use matching-filter numerators and denominators.
- Effective domain concentration (38.44), top-ten share (41.98%), annual/monthly
  breadth, title-share history, and all-source/stable-panel/equal-weight rates.
- Latest complete month: August 2026, 200 HNB publications, rate 13.65 per 10,000;
  year-earlier and preceding-twelve-month comparisons are explicitly separate.
- Eight same-body subject bridges on 33,100 distinct bodies. All have assessable
  local body contexts. Linkage ranges from 36.41% for governance/accountability
  to 54.48% for payments/cash. No local-only/whole-negative matches occur.
- Quarterly frequencies for the recovered 52 terms and 12 phrases: 1,472 cells,
  one distinct body per quarter. Latest complete quarter: 2026 Q2. Partial Q3
  contains July–August only. Positive counts below 30 have no displayed frequency.
- Strict peak-screen candidates: January 2023 and January 2026. The screen uses
  the previous 24 complete months within regime and two sample SDs. These are
  un-attributed candidate months, not verified event explanations.
- The original two long reports are expanded to 16 and 14 pages, with HTML
  editions, refreshed covers, aggregate downloads and source-status corrections.
  The bilingual briefs, shorter overview and slides include the new indicators.

Every lexical 1.0 term, phrase and subject-group count was reproduced before
adding 1.1. The bridge excludes titles from both sides to enforce containment;
quarterly vocabulary retains the original explicit-HNB title plus body context.
Those two contexts are deliberately labelled separately.

## Execution ledger and remaining work

| Plan package | Actual state | Remaining gate or work |
|---|---|---|
| P0 | Reconciled | Canonical GitHub edition and lexical sources recovered; rollback source archived |
| A1 | Implemented and release-tested | No unresolved technical gate for this edition |
| A2 comparison/quarterly | Implemented and release-tested | Exploratory measurement; no claim of independent validation |
| A2 unmatched audit | Sample drawn, not coded | 200 of 4,118 publications; seed 20260922; regime × source-volume × body strata; inclusion weights sum to 4,118; 191 nonempty exact-body groups in sample |
| B01 source typology | 201-domain work allocation prepared | Dated primary evidence, assignments, ambiguous-case review and 20% review of remainder; no classifications published |
| B02 story groups | Not implemented or validated | Development method, held-out 100-cluster/100-pair evaluation and uncertainty; V8 deliberately unused |
| B03 events | Strict screen implemented | Corpus membership, story contributions and attributed event cards await matching and B02 evaluation |
| B04 keyness | Not implemented | Raw/standardized contrasts, defining-term exclusions, dominant-outlet and validated-cluster sensitivity remain |
| B05 actors | Original 35-entry dictionary inspected | Dated roles, institution/person distinctions, contextual co-mention analysis remain |
| B06 concordance | Implemented and smoke-tested privately | Read-only, bounded term/date/source/context filtering; no public article interface |
| C1 measurement | Draft codebook/protocol prepared | Two independent Croatian reviewers, calibration, grouped held-out sampling, adjudication and reliability estimates |
| C2 official cases | Source register and pilot protocol prepared | Cash OTS issuer/version unresolved (403); two-reviewer propositions and media matching not completed |
| D conditional modules | Deliberately not started | Named research question and go/no-go evidence, as required by the plan |

The full research programme is **not complete**. This is the narrower, passed
release allowed by the plan. No synthetic human labels, validated-story counts,
stance estimates, causal explanations or communication-effectiveness scores
have been substituted for the unfinished work.

## Reproduction and checks

Ordinary deployment uses committed aggregate inputs and pre-rendered PDFs.
`python scripts/build.py`, `python scripts/build_site.py`,
`python scripts/verify_reports.py`, `python scripts/verify_extensions_release.py`
and `python media-hub/scripts/verify_offline_rebuild.py` run without restricted
data. Indicator production is available in `media-hub/scripts/extensions_aggregates.py`.
Optional lexical regeneration requires the pinned reviewed cache and DuckDB:

```text
python media-hub/scripts/prepare_lexical_extensions.py --database PRIVATE_CACHE --output SEPARATE_AGGREGATE_DIRECTORY
```

The lexical producer opens the cache read-only, reconciles the 33,235/33,136/33,100
counts, verifies all earlier lexical cells, and emits no text or record keys.
`private_research_tools.py` requires an output outside synchronized directories;
it is not included in the public rendering ZIP. Its audit sample has blank coding
fields. No audit-theme proportions or independent reliability results exist yet.

Release verification covers 909 indicator checks, all 1,472 quarterly cells,
four-cell arithmetic, suppression/missing-context fixtures, exact hashes and
public packaging. Browser checks cover both languages at 360/768/1440 px, 200%
text, history, invalid links, selected CSV/SVG exports and no-JavaScript tables.
Every changed PDF page was rendered and visually inspected. The standard-library
rendering-source rebuild is byte-identical within the recorded environment;
this is not a claim of restricted-analysis or cross-platform PDF reproduction.

The root inflation publication files and inputs remain unchanged. The source
rollback is commit `1e46c78`; restoring it requires rebuilding and deploying the
complete prior site, not mixing old HTML with new aggregate files.
