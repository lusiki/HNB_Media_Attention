# Croatian report pair, 21 September 2026

The 14-page `hnb-u-medijskom-prostoru.pdf` and 12-page
`hnb-od-rijeci-do-javnih-pitanja.pdf` follow the complementary overview/language
approach of the DigiKat reports. They describe HNB_MEDIA, not the DigiKat corpus
or the separate inflation study. Both are public research drafts awaiting author
review. No personal byline or author approval has been inferred.

## Overview

The overview uses the already published HNB_MEDIA 2026-09-21.1 aggregates:
33,235 explicit-mention web publications, 281 domains, 68 full months from January
2021 through August 2026. It retains the January 2024 collection boundary,
matched-denominator rate, overlapping full-text keyword screens and existing
source/retrieval sensitivities. Annual subject percentages sum the monthly
subject counts and divide by that year's publication count; 2026 stops in August.
The selected months illustrate different contexts, not causal explanations for
monthly peaks or a statistically representative sample of events.

## Language companion: HNB_MEDIA_LEXICAL_1.0

The optional `scripts/prepare_report_language.py` reads the previously reviewed
`media` table from the private cache with DuckDB `read_only=True`. It neither
reruns baseline extraction nor changes the database. The ordinary site build uses
the resulting fixed public aggregates and requires no database access.

- Same full-month explicit-mention population. Exclude 99 publications without
  stored bodies. Normalize the remaining 33,136 bodies by lowercase and the
  existing ASCII-whitespace convention, retaining 33,100 exact distinct bodies.
  The earliest publication (ties by domain and normalized URL) supplies the title.
- Split the cleaned body into sentence-like segments at newlines or punctuation
  followed by whitespace and an uppercase letter/digit. Select only segments
  containing an explicit HNB mention, plus the title if it contains such a mention.
  Adjacent sentences are not added. All 33,100 bodies have an eligible context.
- Remove matched HNB abbreviations/full names before counting vocabulary, so
  `banka` is not counted merely as part of the institution's full name.
- Count each of 52 selected concepts and 12 selected adjacent-word phrases once
  per distinct body. The exact inflection patterns are public. This is a curated
  dictionary, not comprehensive lemmatization or unsupervised word discovery.
- Apply the existing eight subject patterns to the extracted context. These
  overlapping subsets differ from the full-title/body publication counts in the
  overview. Within each subset, vocabulary is counted across the selected HNB
  contexts of each text. Two words in that text need not share a sentence.
- Sort frequency ties alphabetically. Word clouds are deterministically packed;
  only font size conveys relative frequency within each cloud. Numeric HTML
  alternatives and a CSV accompany all vocabulary figures.

Counts are lexical presence, not main topics, actor attribution, stance, trust,
reach or policy effects. The sentence splitter, morphological ambiguity,
remaining boilerplate, truncated text and near-duplicates are limitations.
The development checks do not constitute independent human validation or
measured population precision/recall.

## Selected public examples

Examples were chosen for different communicative functions: a practical cash
exchange notice (Hina, 4 January 2023), a lending decision and its introduction
(HNB, 19 March 2025; HRT/Hina, 1 July 2025), and a parliamentary accountability
discussion (Sabor, 27 January 2022). The overview additionally cites the February
2025 consumer-platform meeting (Glas Istre/Hina, 21 February 2025). Public source
links are included where the examples are discussed. Institutional sources
verify context; they are not added to the editorial-media numerator. The analysis
does not infer later legal outcomes, consumer advice or causal policy effects.

## Regeneration

From the publication checkout, `python media-hub/scripts/make_long_reports.py`
regenerates the two PDFs, HTML companions, vocabulary CSV and artifact metadata
using committed aggregates, ReportLab, pypdf and the licensed repository fonts.
`report_overview.py`, `report_language.py` and `report_layout.py` hold the editable
content and layout. Rendering the PDFs is a separate operation from rebuilding
the site. A new restricted-data edition requires repeating the upstream review.

The public output contains no article text or vendor identifiers. The source ZIP
rebuilds the static site using fixed PDFs; its existing reproducibility boundary
does not claim to recreate restricted extraction or lexical measurement.
