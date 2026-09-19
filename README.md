# HNB in Croatia's inflation debate

Bilingual static research publication based on the extended manuscript by Petra Palić and Luka Sikić, dated **17 September 2026**. Presentation version: **2026-09-19.3**. Author review is pending.

This is the canonical publication checkout. [Live site](https://lusiki.github.io/HNB_Media_Attention/) · [Repository](https://github.com/lusiki/HNB_Media_Attention) · [Deployment workflow](https://github.com/lusiki/HNB_Media_Attention/actions/workflows/pages.yml).

Pushes to `main` build, verify and deploy through GitHub Actions. Pull requests run checks without deployment. Only the generated `dist` artifact is published. Ordinary builds use committed publication inputs and the Python standard library; verification additionally requires `requirements-checks.txt`. Neither requires the original research workspace.

## Build and preview

```powershell
python scripts/build.py
python -m http.server 8766 --bind 127.0.0.1 --directory dist
```

Serve only `dist`. English: http://127.0.0.1:8766/; Croatian: http://127.0.0.1:8766/hr.html. Both pages provide the interactive explorer and static chart/table fallbacks. The brief links open on-site readers with rendered pages and selectable text; each reader also offers the original PDF download. The build produces 32 allowlisted files and `hnb-attention-gap-publication.zip`. A local build does not deploy anything.

For production, set `SITE_URL` to the HTTPS directory URL before building. This gives Open Graph metadata absolute image and page URLs. Otherwise metadata uses a relative image for local previews. The 1200 × 630 preview is generated from the saved primary estimate.

## Reading paths

The opening overview links to four research questions. The main chart follows immediately; the indicator guide, worked examples, concise findings and practical investigation agenda follow it. Detailed estimates, methods, research status and downloads provide the longer reading path. Sticky contents marks the active section.

Weighted visibility is the main narrative measure. The attention gap remains available in the chart and technical estimates. The baseline is a historical reference. All empirical values come from saved research outputs; hypothetical examples use the manuscript's actual salience formula.

Both languages use the same interactive controller. Four question lenses configure visibility, source-composition, inflation and public-understanding views. Nine indicator concepts use consistent dialogs with meaning, construction, scope, interpretation, limitations and evidence. Closing restores chart position and focus.

The comparison desk separates selected level, descriptive endpoint movement and evidence for the named finding. It compares primary/common-source series and predefined saved model checks: F1 inflation association, F2 controlled trends, F3 survey assignments and F4 network trends. Units and explicit evidence-label criteria accompany results; they do not grade policy performance.

Media context distinguishes potential reach, exposure, attention and understanding. Concentration summaries cover the largest five source contributions, largest ten item contributions, weighted-numerator HHI and counts. Domain tables start alphabetically and offer named numerical sorts. Fixed records F1–F4 connect claims to models, samples, manuscript locations, sensitivity checks and versioned citations.

## Interactions and public files

- Query parameters `window`, `metric`, `period`, `sample`, `frequency`, `specification`, `lens`, `from`, `to`, `finding`, `mode`, `inspect` and `sort` preserve selections. Language is recorded in shared links. Invalid values fall back to valid defaults.
- Copy controls, Back/Forward and language switches preserve context. Reset restores full history, weighted share, May 2026 and the primary weekly model.
- Selected-view SVGs contain scope, units, selected month, source definition, model context and versions. Period CSVs retain full precision and the selected measure. Separate downloads cover model comparisons and domain contributions. Fixed-scope downloads remain available.
- Interval bounds use extra precision near zero; interpretations use original values, never rounded display values.
- The month panel shows values, edition, transformation and evidence links. Source and item diagnostics use reconciled aggregates from existing scored records.
- `evidence.json` retains its original `period`, `gap`, `inflation` observations. `inspection.json` adds the two source definitions, indicator catalog, aggregate diagnostics and selected comparisons; `findings.json` contains fixed records and revisions. Calendar coordinates preserve actual month spacing. No values are fabricated.
- The English and Croatian briefs are two pages each. The original manuscript is retained in the ignored local research archive, outside the public bundle. Citation and methodological references remain on the pages.
- The research-status panel explains review, saved-output reproduction, the earlier coefficient discrepancy, code availability, reuse and version history. Author profiles and a correction email are linked.

`public/` supplies publication assets. `private/`, `qa/`, `.runtime/`, research inputs and working documentation are not served or bundled. The previous Desktop version is retained in `private/before-2026-09-19-sync/`. Saved inputs for this release are in `private/research-inputs/`, and derived source summaries are in `private/inspection-aggregates/`. These local records are not committed. The pre-design edition is preserved in `private/before-magazine-briefs/`. Both current briefs include the full January 2021–May 2026 timeline; shorter-period estimates retain their stated scope.

## Editing and regeneration

Edit `src/index.html`, `src/hr.html`, `src/styles.css`, `src/app.js`, `src/charts.js`, shared components in `scripts/inspection_components.py` and `content/study.json`. Keep languages and briefs consistent when changing claims. The standard-library build embeds prepared values, saved estimates and static charts.

```powershell
python scripts/build.py
python scripts/verify.py
python scripts/verify_inspection.py
node --check src/app.js
node --check src/charts.js
node scripts/browser_qa.cjs
node scripts/inspection_qa.cjs
node scripts/reader_qa.cjs
```

Install `requirements-authoring.txt` for optional figure/brief regeneration. Source Serif 4 and Source Sans 3 are bundled with licenses and pinned provenance in `assets/fonts/`; the readers use local WOFF2 copies. The palette and font definitions live in `scripts/artifact_style.py`. Run `python scripts/make_figures.py` before `python scripts/make_brief.py`: the latter embeds the vector PDF charts produced by the former. Both briefs use the complete published observation series for the main timeline and saved estimates for model comparisons. Render and visually inspect all four pages after PDF revisions, then run `python scripts/make_readers.py --pdftoppm PATH_TO_PDFTOPPM` and `python scripts/update_publication_hashes.py`. Ordinary builds validate and reuse these committed publication assets without authoring dependencies.

Run `python scripts/prepare_inputs.py --research-root PATH_TO_SAVED_RESEARCH` only for an intentional research refresh. It reads saved outputs, not raw databases, enforces the archived manuscript hash, and applies the public export scope. Research inputs are checked against `content/research-input-hashes.json`.

To intentionally regenerate inspection diagnostics, run `Rscript scripts/aggregate_inspection.R . PATH_TO_SCORED_RDS` (requires `data.table`), then `python scripts/prepare_inspection.py --research-root PATH_TO_SAVED_RESEARCH` and rebuild. The R script writes private monthly/domain/channel summaries without fitting models. Python reconciles weighted numerators and relevant-item counts with the saved monthly panels. The common-source set has 258 labels and restricts both numerator and denominator. The diagnostic HHI describes the institutional weighted numerator, distinct from the broader source-reach regression control. Hashes are recorded in `content/inspection-input-hashes.json`; provenance is documented in `content/inspection-evidence.md`.

## Publishing

Start with `git pull --ff-only`. After editing, build and run the checks above, inspect the page, review `git diff`, commit the intended source/assets, and push `main`. Wait for the Pages workflow to succeed. Private research inputs, backups, screenshots, generated ZIPs and local tooling remain ignored by Git.

## Verification

`verify.py` checks source values, transformations, chart ranges, HTML anchors, public scope, PDF text and links, exact bundle/ZIP contents and research hashes. `browser_qa.cjs` uses an isolated headless Chrome context, the local preview server and Playwright from the Codex runtime. Set `BASE_URL` to check another preview or the deployed repository path. `PLAYWRIGHT_MODULE` selects an installed Playwright module; `BROWSER_EXECUTABLE` selects the browser. The reader suite uses these same settings. Browser tests require a running preview.

Outside the Codex runtime, install Playwright with `npm install --no-save --package-lock=false playwright` and `npx playwright install chromium`. Use `PLAYWRIGHT_MODULE=playwright` to select that installation. These optional browser tools are not needed by the static build or deployment.

`verify_inspection.py` checks both series, numerator/denominator arithmetic, counts, concentration, domain contributions, all 20 saved coefficient comparisons, chart bounds, metadata and embedded data. `inspection_qa.cjs` adds modal focus/return position, cross-language context, every comparison family, source ordering, citations and browser history checks.

Browser checks cover 360/768/1440 px, 200% text enlargement, keyboard navigation, disclosures, active contents, URL restore/reset, copied links, actual SVG/CSV downloads, bilingual deep links, static fallbacks, asset links, console errors and external requests. Tables scroll inside their containers. This is targeted QA, not accessibility certification or new econometric replication.


Standalone checks validate committed input fingerprints in `content/publication-input-hashes.json`, numerical contracts, reader/PDF consistency and bundle contents. When intentionally updating an input, update its SHA-256 entry after reviewing provenance and affected results; JSON, CSV and TXT hashes normalise CRLF to LF so Windows and Linux agree. For upstream comparisons using the saved release inputs held locally:

```powershell
python scripts/verify.py --research-root private/research-inputs
python scripts/verify_inspection.py --research-root private/research-inputs
```

Optional source aggregation needs the scored RDS input supplied explicitly; that input is not distributed. The analytical research workspace is separate from this publication repository.
