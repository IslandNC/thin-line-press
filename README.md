# Thin Line Press

> Where the line breaks.

The website of **Thin Line Press** — fiction for readers at the edge of technology, obsession, and what it means to be human.

**Live site:** <https://islandnc.github.io/thin-line-press/>

The press's debut title is [**CLAWDIA**](https://islandnc.github.io/clawdia-book/), a psychological thriller by Frederic Cornaille.

---

## What's here

A single-page static site. No build step, no dependencies, no framework — open `index.html` in a browser and it runs.

```
index.html          The site (18 KB)
404.html            Branded not-found page
assets/
  clawdia-cover.jpg       Book cover — used as the hero background and the cover plate
  clawdia-quote-card.jpg  Pull-quote card in the "Inside the system" section
  clawdia-title-page.jpg  Title page shown in the brief modal
  og-cover.jpg            1200×630 social sharing card
  favicon.svg             Press mark — a broken line
robots.txt          Crawl policy
sitemap.xml         Single-URL sitemap
.nojekyll           Serve files verbatim; skip GitHub's Jekyll build
```

Fonts (Manrope, Playfair Display, DM Mono) load from Google Fonts. Everything else is served from this repository.

## Local preview

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000>.

Opening `index.html` directly via `file://` also works, though the fonts will need a network connection either way.

## Deployment

GitHub Pages serves the `main` branch from `/ (root)`. Pushing to `main` publishes; there is no build step and no workflow to wait on.

To change the deployment source: **Settings → Pages → Build and deployment**.

## Editing notes

- **Section links are fragment anchors** (`#book`, `#author`, `#press`). Keep them relative — absolute or `file://` URLs break the page once it is deployed.
- **Images are referenced from `assets/`, not embedded.** If you replace one, keep the `width`/`height` attributes on the `<img>` tag in sync to avoid layout shift.
- **Absolute URLs live in the head.** The canonical link, Open Graph tags and JSON-LD all hard-code `https://islandnc.github.io/thin-line-press/`. If the site moves to a custom domain, update those, `robots.txt`, `sitemap.xml`, and the two `/thin-line-press/` links in `404.html`.
- **Social preview** is `assets/og-cover.jpg`. After changing it, re-scrape the URL in the [LinkedIn Post Inspector](https://www.linkedin.com/post-inspector/) — LinkedIn caches aggressively.

## Licence

The site code is available under the MIT Licence (see [LICENSE](LICENSE)).

The book cover, title page, quote card, and all text about CLAWDIA and Thin Line Press are © Frederic Cornaille and are **not** covered by that licence. Please don't reuse them.
