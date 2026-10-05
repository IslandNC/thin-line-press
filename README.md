# Thin Line Press

> Where the line breaks.

Website of **Thin Line Press**, an independent imprint publishing fiction at the edge of technology, obsession, and what it means to be human. The debut title is **CLAWDIA** by Frederic Cornaille.

Live site: <https://thinlinepress.com.au> (English) and <https://thinlinepress.com.au/fr/> (French).

Book site: <https://clawdia.thinlinepress.com.au> (repository: [IslandNC/clawdia-book](https://github.com/IslandNC/clawdia-book)).

## What this repository is

A static, bilingual (EN/FR) site served by GitHub Pages from the `main` branch. No framework, no server-side code, no analytics. Fonts are self-hosted, so the pages load no third-party fonts.

```
index.html        English home page
fr/               French home page
reviews/          English page for leaving a review
avis/             French page for leaving a review
404.html          Branded not-found page
assets/           Images, stylesheet, script and self-hosted fonts
tools/            check-site.py, a pre-publish check
CNAME             Custom domain
.nojekyll         Serve files verbatim
robots.txt, sitemap.xml
```

## Local preview

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000>. Use a local server rather than `file://`, because the pages use root-relative paths.

## Checks

```bash
python3 tools/check-site.py
```

Run it before pushing. It currently checks `index.html` and `404.html` only: asset references, in-page anchors, JSON-LD, social metadata, and a headless render for overflow and image aspect ratio. The French page and the review pages are not covered yet.

## Deployment

GitHub Pages serves `main` from `/ (root)`. Pushing to `main` publishes. HTTPS is enforced under Settings, Pages.

## Licence

All rights reserved. See [LICENSE](LICENSE). The only exception is `tools/check-site.py`, which is MIT.

## Security

See [SECURITY.md](SECURITY.md).
