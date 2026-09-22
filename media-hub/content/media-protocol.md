# HNB_MEDIA 1.0 protocol

Additive indicator amendment, 22 September 2026: HNB_MEDIA_INDICATORS_1.0 leaves retrieval method 1.0 and corpus 2026-09-21.1 unchanged. Source rates use sums of `hnb_i` and `background_i`; ranking requires both 5,000 background and 50 HNB publications in the chosen window. Concentration uses every positive-HNB domain, without that threshold. Breadth retains the existing `active_outlets` definition (positive `background_count`) and uses domain unions for annual/window values. Title shares are ratios of summed counts. The public frozen S0 list contains 128 equal-weight domains; a missing/zero member denominator yields null rather than renormalization. Latest-month comparisons exclude the current month from the preceding 12-month mean, withhold simple changes across the collection boundary and avoid percent change from a zero baseline. These are descriptive archive measures; no independent validation or national sampling interval is added. The implemented formulas, weights and input/output hashes are in the extension aggregate package. The original contract below is retained.

Initial descriptive contract recorded on 21 September 2026 before selecting findings; the same-day development corrections below are part of method 1.0. This is an exact-mention study of a documented monitored sample, not a census of Croatian media.

## Population and sources

Query the current merged archive read-only across all dates and subjects. Primary sources are web publications whose exact source-domain label matches a publication domain in the Croatian Agency for Electronic Media register retrieved on 21 September 2026. Use its URL column, never email domains. Registration supplies evidence of Croatian editorial eligibility, not editorial independence, historical ownership, continuous monitoring or registration in every historical month. Retain the register page and entry identifier. An alias requires separate evidence; unmatched domains remain outside the primary population. HNB-owned channels, other institutional own channels, audience/social material, print/radio/TV and unresolved sources remain separately counted in the audit. Publisher social reposts do not enter web publication counts. Record language as vendor metadata without using it to infer nationality.

Current-register selection can miss closed/renamed outlets and create survivorship bias. The source registry identifies institutional own-channel exclusions. A registered editorial publication can have public, commercial or civil-society ownership; source concentration never measures ownership concentration. Unknown beneficial ownership stays unknown.

## Retrieval and attribution

Search original title and stored body for case-insensitive Unicode-bounded HNB (including hyphenated inflection), Croatian inflected full names including 'banci', and 'Croatian National Bank'. Test positive and negative fixtures. Explicit mentions form the primary baseline. A secondary contextual sensitivity accepts the phrase 'hrvatska središnja banka' with inflection. Generic central-bank and officeholder-only matches remain unresolved candidates. A name match does not establish a role, and no governor series is published. Snippet-only matches are diagnostic, not body text or primary hits.

Review a deterministic stratified sample of explicit, generic/contextual, officeholder and independent non-hit records. Inspect non-inflation material. This agent-assisted development audit is not independent human validation or a population precision/recall estimate. Report all observed defects and withhold stronger prominence/stance/role claims. Do not claim exhaustive recall from accepted hits.

## Unit and deduplication

Capture is a stored archive row. A web publication is operationalized by source domain and normalized article URL (scheme, www and fragment removed), with earliest record date across repeated captures. Homepage or missing URLs use source, record day and title hash. Identical URLs with changed headlines remain one publication, so rolling pages and updates may be merged. Retain the longest stored body per publication, with deterministic tie breaks; initial retrieval flags are unions across captures, then primary formal/acronym/title flags are re-evaluated on the retained text after reviewed cleanup. A union-only hit absent from retained text is not accepted. Report capture-to-publication losses, URL conflicts, API identity duplication and missing-key diagnostics. Timestamp semantics are vendor record dates; publication-to-coverage lags are unavailable.

Exact-text groups use a hash of the retained body after lowercasing and whitespace normalization, only where body text exists. These are neither near-duplicate nor story/event clusters. Count unique groups over the selected set, never by summing monthly distinct counts. Retain repeated text across outlets in publication counts. Subject indicators require assessable title/body text.

## Measures and dates

Primary H is the count of explicit HNB publication instances in eligible sources. Unweighted counts and within-HNB source shares lead the release. Outlet breadth counts observed source domains with HNB hits. The common-source sensitivity uses sources with at least one background publication in every full month; this does not prove invariant capture.

The optional rate uses H_i / N_i × 10,000, applying the identical standalone-word i predicate, source registry, URL deduplication and time eligibility to numerator and background. It describes the monitored query-eligible archive, not all output from these outlets or all Croatian media. Legacy vendor selection remains incompletely reconstructed, so cross-batch level changes cannot identify changes in national attention. Counts without i remain separate from H_i. Null/zero background yields no rate. No +1 stabilizer.

Audit every month through the actual endpoint. Full months through August 2026 are candidate headline periods if archive dates support them. September through the 10th is a separate partial diagnostic. January 2024 is a collection/filter boundary, with April 2024 examined as a source-composition diagnostic. Observed days never prove complete collection. Full text can be truncated or contain navigation; non-empty does not imply complete text. No sentiment/reach weights enter the primary measure.

## Subjects and sensitivity

Use eight transparent exploratory lexical tags for prices/inflation, monetary policy/rates, euro/currency, banking stability/supervision, lending/consumers, forecasts/statistics, governance/accountability, and payments/cash. Review examples in title/body and report overlap/unassigned/assessability. Tags describe term presence in captured material; they do not establish a main topic, HNB's role, stance, voice or attribution of every paragraph. Show exploratory counts with that restriction or qualitative themes if the audit reveals inadequate content. A narrow inflation-stem bridge and the legacy broad keyword rule have separate denominators and definitions.

Compare full-name-only, corrected explicit, explicit-plus-context, title mentions, i-harmonized counts, full-text availability, exact-text groups and the observed common-source subset. Report within-batch temporal summaries and concentration without a causal or national trend narrative. Preserve all frozen inflation inputs and results; new collection repairs never backfill that study.

## Reproduction boundary

Python/DuckDB is the documented equivalent of the proposed R entrypoint because the installed Python environment has the required dependencies. Restricted records, text, IDs, linkage maps and audit samples stay outside the synchronized project. Only aggregate results and safe domain registry fields enter results/hub_media and public exports. The offline renderer consumes those aggregates without source-database access. Seed 20260921; separate schema/data/method/presentation identities. Independent human coding, complete historical source registries and publication approval are conditional follow-up work.

## Recorded development amendments

The initial full-name expression was widened from bank to ban[kc] to include banci, with a targeted source correction. The currency-converter block on Zagorje was removed before mention screening; Dnevnik related-content tails and one privately reviewed Vecernji link were removed. Rechecking retained text removed union-only capture hits. Identified association channel hnd.hr was separated from editorial outlets, alongside the other documented own-channel exclusions. The final baseline is 33,235 full-window publications from 281 domains. These are development corrections, not an independently validated classifier. A two-source exclusion sensitivity addresses unresolved related-content contamination.
