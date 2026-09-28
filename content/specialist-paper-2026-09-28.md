# Specialist paper download update, 28 September 2026

The broad-media hub's specialist-study card now links directly to the refreshed Croatian extended manuscript in PDF and standalone HTML. Both languages identify the 28 September edition, the January 2021-August 2026 monthly window, 68 complete months and 295 fitted weeks, and the primary weekly association of 0.25 percentage points (95% interval 0.11-0.39). Annual controls and the volume specification qualify the association; the paper does not establish a stable link to future consumer expectations.

`media-hub/public/downloads/PAPER_EXT.pdf` and `PAPER_EXT.html` are byte-identical copies of the checked research deliverables. Their integrity, language, period and review status are recorded in `artifacts.json`, and the ordinary build includes them in both the public bundle and the offline rendering package. The HTML uses native MathML and embedded resources; its companion PDF link resolves to the adjacent file.

The updated paper is a separate analytical edition. The broad-media figures, its dated reports, and the earlier interactive inflation pages retain their existing data. The registry identifies the current downloadable paper separately from the earlier interactive edition. No raw archive, article text or private analysis files are published.

Verification: run the existing build and release checks, plus `python scripts/verify_specialist_downloads.py`. The GitHub Pages workflow runs this check before deployment.
