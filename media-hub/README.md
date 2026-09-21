# Public rendering package

The broad hub includes a 14-page Croatian media overview and a 12-page companion
on language and public questions, each with PDF and HTML editions. See
`content/long-reports-method.md` in the publication repository for the lexical
measurement boundary and optional PDF regeneration. The two reports retain
author-review-pending status. The HTML editions provide numeric alternatives to
all figures; vocabulary aggregates are available as CSV and JSON.

Requires Python 3.10+ standard library only. Run `python scripts/build.py` from this directory. It creates `dist/`, an exact public ZIP, and QA build hashes without network access or a database.

This package rebuilds the static site from fixed aggregate tables and already rendered publication assets. It does not regenerate the PDFs or article-level analysis. Those require authoring dependencies or authorized access to the restricted source respectively. It includes no vendor article text, identifiers, private paths, manuscript PDF, or keys.

Data and method editions differ between the broad HNB_MEDIA corpus and the frozen inflation study. See content/releases.json. The source snapshot is identified by the hashes in the release manifest; the originating working tree was dirty and is not reproducible from its base commit alone.

With SITE_URL unset, output is a local candidate. For a separately authorized deployment, set SITE_URL to the real HTTPS directory and rebuild. Host the contents of dist, preserving directories. No deployment occurs in this script.

The public URL is recorded in content/releases.json. No DOI, author sign-off or open redistribution license is asserted. See public/downloads/media-reuse.txt. Do not infer rights to underlying articles from the presence of aggregates.
