# Thin Line Press

> Where the line breaks.

The website of **Thin Line Press** — fiction for readers at the edge of technology, obsession, and what it means to be human.

**Live site:** <https://islandnc.github.io/thin-line-press/>

The press's debut title is [**CLAWDIA**](https://islandnc.github.io/clawdia-book/), a psychological thriller by Frederic Cornaille (ISBN 978-1-7646688-0-4).

---

## What's here

A single-page static site. No build step, no dependencies, no framework — open `index.html` in a browser and it runs. Nothing is fetched from a third party at runtime: fonts are served from this repository, so the site makes no external requests at all.

```
index.html          The site
404.html            Branded not-found page
assets/
  clawdia-cover.jpg       Book cover — hero background and cover plate
  clawdia-quote-card.jpg  Pull-quote card in the "Inside the system" section
  clawdia-title-page.jpg  Title page shown in the brief modal
  og-cover.jpg            1200×630 social sharing card
  favicon.svg             Press mark — a broken line
  fonts.css               @font-face declarations
  fonts/                  Self-hosted woff2 (latin + latin-ext subsets)
tools/check-site.py Pre-flight checks — run before pushing
robots.txt          Crawl policy
sitemap.xml         Single-URL sitemap
.nojekyll           Serve files verbatim; skip GitHub's Jekyll build
```

## Local preview

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000>. Opening `index.html` directly via `file://` also works.

## Checks

```bash
python3 tools/check-site.py
```

Run this before pushing. It verifies that every asset reference resolves, every in-page anchor has a target, no local filesystem path leaks into the markup, the JSON-LD parses, the social metadata is present, and nothing is loaded from a third party.

It then renders the page in headless Chrome and measures the result — confirming images load and keep their aspect ratio, and that the page does not overflow horizontally. That render step exists because the two worst bugs this site has had were invisible to static analysis:

- navigation links pointing at absolute `file:///` URLs, which broke every anchor once served and leaked a local directory tree;
- an `<img>` with `width`/`height` attributes but only a CSS `width`, so the height presentational hint survived and the cover rendered at 3.5× its correct height.

Both now fail the checks. The same script runs in CI on every push via `.github/workflows/check.yml`, which also verifies that outbound links still resolve.

Chrome is found automatically on macOS, or via `CHROME_BIN`. If no Chrome is present the render checks are skipped and the static checks still run.

## Deployment

GitHub Pages serves the `main` branch from `/ (root)`. Pushing to `main` publishes; there is no build step.

To change the deployment source: **Settings → Pages → Build and deployment**.

## Editing notes

- **Section links are fragment anchors** (`#book`, `#author`, `#press`). Keep them relative.
- **If you give an `<img>` `width`/`height` attributes, make sure its CSS rule sets a height** (usually `height:auto`). Otherwise the attribute acts as a presentational hint for height and the image is stretched. `check-site.py` enforces this.
- **Absolute URLs live in the head.** The canonical link, Open Graph tags and JSON-LD hard-code `https://islandnc.github.io/thin-line-press/`. If the site moves to a custom domain, update those, `robots.txt`, `sitemap.xml`, and the three `/thin-line-press/` paths in `404.html`.
- **Book facts appear in two places** — the visible `.record-details` list and the JSON-LD `Book` node. Keep the ISBN, page count and price in step with the [CLAWDIA site](https://github.com/IslandNC/clawdia-book), which is the source of truth.
- **Social preview** is `assets/og-cover.jpg`. After changing it, re-scrape in the [LinkedIn Post Inspector](https://www.linkedin.com/post-inspector/) — LinkedIn caches aggressively.
- **Fonts** were generated from the Google Fonts `css2` endpoint, latin and latin-ext only. To add a weight or subset, re-request that endpoint and drop the new woff2 into `assets/fonts/`.

## Licence

The site code is available under the MIT Licence (see [LICENSE](LICENSE)).

The book cover, title page, quote card, and all text about CLAWDIA and Thin Line Press are © Frederic Cornaille and are **not** covered by that licence. The bundled fonts (Manrope, Playfair Display, DM Mono) are licensed under the [SIL Open Font License 1.1](https://openfontlicense.org/).
