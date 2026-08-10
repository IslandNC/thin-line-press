#!/usr/bin/env python3
"""Pre-flight checks for the Thin Line Press site.

Two classes of bug have shipped here before, and both were mechanically
catchable:

  * navigation links pointing at absolute file:/// URLs, which broke every
    in-page anchor once the site was served and leaked a local directory tree;
  * an image given width/height attributes but only a CSS width, so the height
    presentational hint survived and the cover rendered at 3.5x its height.

The first is a static check. The second is only visible once something applies
CSS, so this script renders the page in headless Chrome and measures the result.

Usage:  python3 tools/check-site.py
Exits non-zero if any check fails.
"""

import html
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = ["index.html", "404.html"]
SITE_ROOT = "/thin-line-press/"

failures = []
checks = 0


def check(ok, msg):
    global checks
    checks += 1
    print(("  \033[32mPASS\033[0m  " if ok else "  \033[31mFAIL\033[0m  ") + msg)
    if not ok:
        failures.append(msg)


def find_chrome():
    candidates = [
        os.environ.get("CHROME_BIN"),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "google-chrome",
        "google-chrome-stable",
        "chromium",
        "chromium-browser",
    ]
    for c in candidates:
        if not c:
            continue
        p = shutil.which(c) if not os.path.isabs(c) else (c if os.path.exists(c) else None)
        if p:
            return p
    return None


# ---------------------------------------------------------------- static checks

def static_checks():
    for page in PAGES:
        path = os.path.join(ROOT, page)
        s = open(path, encoding="utf-8").read()
        print(f"\n\033[1m{page}\033[0m")

        # No local filesystem paths may reach production.
        check("file:///" not in s and "/Users/" not in s,
              "no local filesystem paths")

        # Every relative asset reference resolves to a file that exists.
        for ref in re.findall(r'(?:src|href)="(?!https?:|#|data:|mailto:)([^"]+)"', s):
            target = ref[len(SITE_ROOT):] if ref.startswith(SITE_ROOT) else ref
            target = target.lstrip("/")
            if target in ("", "index.html"):
                continue  # site root
            check(os.path.exists(os.path.join(ROOT, target)), f"resolves: {ref}")

        # Every in-page anchor has a matching id.
        ids = set(re.findall(r'\bid="([^"]+)"', s))
        for frag in sorted(set(re.findall(r'href="#([\w-]+)"', s))):
            check(frag in ids, f"anchor #{frag} has a target")

        # ids are unique.
        all_ids = re.findall(r'\bid="([^"]+)"', s)
        check(len(all_ids) == len(set(all_ids)), "ids are unique")

        # Images carry alt text.
        imgs = re.findall(r"<img[^>]*>", s)
        check(all("alt=" in i for i in imgs), f"all {len(imgs)} <img> have alt")

        # Any image with width/height attributes must have its height governed
        # by CSS, or the presentational hint distorts it. This is the exact bug
        # that shipped once already.
        for img in imgs:
            if "width=" in img and "height=" in img:
                cls = re.search(r'class="([^"]+)"', img)
                cls = cls.group(1).split()[0] if cls else None
                if cls:
                    rules = re.findall(r"\." + re.escape(cls) + r"\{([^}]*)\}", s)
                    governed = any("height:" in r for r in rules)
                    check(governed,
                          f".{cls} sets height in CSS (width/height attrs present)")

        # New windows must not leak the opener.
        for a in re.findall(r"<a [^>]*target=\"_blank\"[^>]*>", s):
            check('rel="noopener"' in a, "target=_blank carries rel=noopener")

        # Reduced-motion support, since the ticker animates indefinitely.
        if "animation:marquee" in s or "infinite" in s:
            check("prefers-reduced-motion" in s,
                  "infinite animation has a prefers-reduced-motion opt-out")

    # Structured data must parse.
    s = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    print("\n\033[1mstructured data\033[0m")
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)
    check(bool(m), "JSON-LD block present")
    if m:
        try:
            data = json.loads(m.group(1))
            check(True, "JSON-LD parses")
            types = [n.get("@type") for n in data.get("@graph", [])]
            check("Book" in types and "Organization" in types,
                  f"declares Book and Organization ({', '.join(types)})")
        except json.JSONDecodeError as e:
            check(False, f"JSON-LD parses ({e})")

    print("\n\033[1mhead metadata\033[0m")
    for tag in ("og:title", "og:image", "og:url", "twitter:card",
                'rel="canonical"', "theme-color", 'rel="icon"'):
        check(tag in s, f"{tag} present")

    # The site should be self-contained: no third-party runtime requests.
    print("\n\033[1mself-containment\033[0m")
    for page in PAGES:
        p = open(os.path.join(ROOT, page), encoding="utf-8").read()
        ext = set(re.findall(r'(?:src|href)="(https?://[^"]+)"', p))
        remote = {u for u in ext
                  if re.search(r"\.(css|js|woff2?|jpe?g|png|svg|gif)(\?|$)", u)
                  or "fonts.googleapis" in u or "fonts.gstatic" in u}
        check(not remote, f"{page}: no third-party assets ({remote or 'none'})")


# ---------------------------------------------------------------- render checks

PROBE = """
<script>
window.addEventListener('load', () => {
  const out = {images: [], horizontal_overflow:
    document.documentElement.scrollWidth > window.innerWidth + 1};
  for (const i of document.images) {
    const r = i.getBoundingClientRect();
    out.images.push({
      src: i.getAttribute('src'),
      loaded: i.complete && i.naturalWidth > 0,
      natural: [i.naturalWidth, i.naturalHeight],
      rendered: [Math.round(r.width), Math.round(r.height)],
      objectFit: getComputedStyle(i).objectFit
    });
  }
  document.body.setAttribute('data-probe', JSON.stringify(out));
});
</script>
"""


def render_checks(chrome):
    print("\n\033[1mrendered layout (headless Chrome)\033[0m")
    src = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    probe_path = os.path.join(ROOT, "_probe.tmp.html")
    open(probe_path, "w", encoding="utf-8").write(
        src.replace("</body>", PROBE + "</body>"))
    # Note: do not pass --user-data-dir. On macOS it makes Chrome hang
    # indefinitely instead of dumping the DOM.
    try:
        dom = subprocess.run(
            [chrome, "--headless", "--disable-gpu", "--no-sandbox",
             "--no-first-run", "--no-default-browser-check",
             "--window-size=1440,900", "--virtual-time-budget=10000",
             "--dump-dom", "file://" + probe_path],
            capture_output=True, text=True, timeout=90).stdout
    except subprocess.TimeoutExpired:
        check(False, "headless Chrome returned within 90s")
        return
    finally:
        os.remove(probe_path)

    m = re.search(r'data-probe="(.*?)"\s*>', dom, re.S)
    if not m:
        check(False, "page rendered and reported measurements")
        return
    data = json.loads(html.unescape(m.group(1)))

    check(not data["horizontal_overflow"], "no horizontal overflow at 1440px")

    for img in data["images"]:
        name = img["src"].split("/")[-1]
        check(img["loaded"], f"{name} loaded")
        if not img["loaded"]:
            continue
        # cover/contain crop or letterbox rather than distort, so a ratio
        # mismatch there is intentional. The default is "fill", which stretches
        # -- that is the case worth catching.
        if img["objectFit"] in ("cover", "contain"):
            continue
        nat = img["natural"][0] / img["natural"][1]
        ren = img["rendered"][0] / img["rendered"][1] if img["rendered"][1] else 0
        check(abs(nat - ren) < 0.02,
              f"{name} keeps its aspect ratio "
              f"(source {nat:.3f}, rendered {ren:.3f}, "
              f"{img['rendered'][0]}x{img['rendered'][1]})")


def main():
    static_checks()
    chrome = find_chrome()
    if chrome:
        render_checks(chrome)
    else:
        print("\n\033[33mSKIP\033[0m  render checks: no Chrome found "
              "(set CHROME_BIN to enable)")

    print(f"\n{'-' * 60}")
    if failures:
        print(f"\033[31m{len(failures)} of {checks} checks failed:\033[0m")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"\033[32mall {checks} checks passed\033[0m")
    return 0


if __name__ == "__main__":
    sys.exit(main())
