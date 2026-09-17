# HNB Media Attention

A static research observatory presenting **The HNB Attention Gap**, based on the extended Croatian research draft by Petra Palić and Luka Sikić, dated 17 September 2026.

- **Observatory:** https://lusiki.github.io/HNB_Media_Attention/
- **Repository:** https://github.com/lusiki/HNB_Media_Attention
- **Deployment:** [Build and deploy observatory](https://github.com/lusiki/HNB_Media_Attention/actions/workflows/pages.yml)

The page includes three qualified findings, an interactive view of the selected monthly aggregates, model comparisons, methods, authors, a two-page English brief and the unchanged 32-page Croatian paper. The manuscript remains labelled **research draft; author review pending**. Hosting it does not establish peer review, HNB endorsement or resolution of the legacy replication discrepancy.

## Local preview

Run these commands from this repository:

```powershell
python scripts/build.py
python -m http.server 8765 --bind 127.0.0.1 --directory dist
```

Open http://127.0.0.1:8765/. Stop the server with Ctrl+C. Serve only `dist`, which is the allowlisted public output. The build uses Python 3.12 or later and its standard library; it works from this checkout alone without R, a database, the original research folder or private files.

## Future changes and publishing

This checkout's `origin` is `lusiki/HNB_Media_Attention`, and its `main` branch tracks `origin/main`. Changes pushed to `main` automatically build, verify and deploy the site through GitHub Actions. Pull requests run checks without deploying. The workflow can also be run manually from the Actions tab.

1. Before editing, run `git pull --ff-only` to obtain changes made elsewhere.
2. Edit the source files described below. Update the brief too when changing its claims.
3. Build, check and inspect the local page.
4. Review, commit and push the intended changes:

```powershell
python -m pip install -r requirements-checks.txt
python scripts/build.py
python scripts/verify.py
git status
git diff
git add src content public scripts README.md .github requirements-authoring.txt requirements-checks.txt .gitignore .gitattributes
git commit -m "Describe the observatory update"
git push
```

Wait for the deployment workflow to succeed before expecting the online page to reflect the update. GitHub Pages is configured to use **GitHub Actions**; only the generated `dist` artifact is deployed. The workflow follows [GitHub's documented Pages workflow](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages), with official actions pinned to commit IDs.

## Files to edit

| Location | Purpose |
| --- | --- |
| `content/study.json` | Study metadata, authors, publication status, findings and source locators |
| `src/index.html` | Page structure, explanations and methods |
| `src/styles.css` | Responsive design |
| `src/app.js` | Chart and model controls |
| `public/data/evidence.json` | Canonical selected aggregate observations and model results |
| `public/data/monthly-series.csv` | Downloadable aggregate series, checked against the JSON |
| `public/downloads/` | Paper, two-page brief and citation |
| `public/figures/` | Figure download and chart input for the brief |
| `scripts/build.py` | Static build and publication package |
| `scripts/make_brief.py` | Editable two-page brief source |
| `scripts/make_figures.py` | Static figure source |
| `scripts/verify.py` | Publication, PDF and data-contract checks |

`dist/`, `qa/`, `.runtime/`, private notes, raw research stores and generated ZIPs are ignored by Git. No private engagement note or raw media records are included in this repository. The source research project remains separate and unchanged.

## Regenerate publication assets

Ordinary website builds deploy the committed PDFs and figures unchanged. For deliberate figure/brief revisions, install the optional authoring requirements and run:

```powershell
python -m pip install -r requirements-authoring.txt
python scripts/make_figures.py
python scripts/make_brief.py
python scripts/build.py
python scripts/verify.py
```

On Windows the brief uses installed Arial and Georgia. `OBS_FONT_DIR` can select another folder containing those fonts; Linux can use DejaVu Sans/Serif. Fonts can change pagination, so **render and inspect both PDF pages after regenerating the brief**, and commit the revised PDF with its source. Automatic deployment checks page count, selectable text, companion links and file integrity; it does not substitute for visual review of new PDFs.

The paper PDF is checked against its selected edition's SHA-256. Replacing it requires reviewing its provenance and deliberately updating the edition metadata and the checks in `prepare_inputs.py` and `verify.py`.

## Optional refresh from the original research project

This operation is separate from building or publishing. It reads only saved aggregate outputs and the selected PDF, never a research database. Supply the research folder explicitly:

```powershell
python scripts/prepare_inputs.py --research-root "PATH_TO_EXTENDED_DATASET"
python scripts/build.py
python scripts/verify.py --research-root "PATH_TO_EXTENDED_DATASET"
```

It creates provenance and claim/figure registers under ignored `private/`. Do not add those files to GitHub. Without `--research-root`, verification runs entirely from this checkout and clearly reports that upstream comparisons were not rerun. After changing research inputs, regenerate and review all affected figures, claims and briefing content before committing. The current extraction rules intentionally describe the September 2026 edition; they do not automatically adopt newer data.

## Optional browser checks

With Playwright installed (`npm install --no-save --package-lock=false playwright`, then `npx playwright install chromium`), start the local server and run:

```powershell
node scripts/browser_qa.cjs
```

`BASE_URL` selects a different preview or the deployed site, including its repository prefix. `BROWSER_EXECUTABLE` optionally selects an installed browser; `PLAYWRIGHT_MODULE` optionally selects an existing Playwright installation. These are local environment settings, not credentials. Screenshots and reports go to ignored `qa/`.

## Research scope

The primary sample covers January 2021–May 2026, excluding unusable periods. The monthly display leaves January–March 2024 blank and marks the April 2024 source change. Later-source levels are not claimed to be harmonised with the earlier source. The gap is displayed as 100 times its stored share-unit value; inflation has its own axis. No smoothing or interpolated media observations are added.

Public findings were matched to saved outputs, not independently re-estimated for this website. Potential reach is not observed exposure or trust. The manuscript's causal limits, specification sensitivity, missing contact/contribution details and unresolved legacy discrepancy remain visible. This is a publication of one study, not an automated monitoring service.
