# Presentation 2026-09-28.2

The English and Croatian observatory pages now lead with the latest same-month
comparison, source concentration and title presence. The opening identifies Luka
Sikić, provides contact and citation links, and identifies the independent status
of the project. The overview URL remains the general entry point; the existing
`#istrazivanja` link still opens the specialist paper.

The explorer adds time presets and a keyboard-accessible month inspector. Source
tables offer domain search, pagination across all 416 archive domains (281 with
HNB mentions in the full edition), and mobile cards with count and rate together.
Source search does not change rate ranks or share denominators. Source CSV exports
retain all domains for the selected dates, including rows outside the displayed
page or search results. Search, page and inspected month are retained in view URLs.
The main publications graph omits the January 2024 vertical marker in both the
interactive and static view, including its SVG export. Its plotted values are unchanged.

Subject screens display counts and overlapping shares. The language section leads
with three existing whole-body/local comparisons and puts quarterly vocabulary
behind an Advanced analysis disclosure. Peak cards add the leading outlets from
the existing monthly table without attributing causes.

Current reports, the specialist study and earlier editions share one publications
library. A short method summary links to bilingual methods guides. Existing
technical definitions and research records remain available. A dated change log,
correction contact, updated citation and social sharing image accompany the release.

This is a presentation update. Aggregate inputs, collection, matching, denominators,
rate thresholds, research checks, and report/manuscript files are unchanged.

## Local build

```powershell
python media-hub/scripts/build.py
python -m http.server 8765 --bind 127.0.0.1 --directory media-hub/dist
```

English: `http://127.0.0.1:8765/`; Croatian: `http://127.0.0.1:8765/hr.html`.
Building writes local publication output and does not deploy it.
