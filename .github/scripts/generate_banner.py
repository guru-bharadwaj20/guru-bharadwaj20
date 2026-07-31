"""Regenerate the profile banner SVGs with the current profile-view count.

Reads the view count from the komarev counter (the same counter the hidden
pixel in README.md increments), then writes assets/banner-{dark,light}.svg
with that count drawn into the top-right corner of the card.

Fonts are subset to the glyphs the banner uses and inlined as base64, because
GitHub renders these SVGs as images -- a sandboxed context that cannot fetch
external fonts. Standard library only, so the workflow needs no pip install.
"""

import json
import pathlib
import re
import urllib.request

USER = "guru-bharadwaj20"
COUNTER = f"https://komarev.com/ghpvc/?username={USER}&label=v"
UA = {"User-Agent": "Mozilla/5.0 (compatible; profile-banner-generator)"}

ROOT = pathlib.Path(__file__).resolve().parents[2]
FONTS = json.loads((ROOT / ".github/scripts/fonts.json").read_text(encoding="utf-8"))


def fetch_views() -> str:
    """Return the current view count, comma-grouped. Empty string on failure."""
    try:
        with urllib.request.urlopen(
            urllib.request.Request(COUNTER, headers=UA), timeout=30
        ) as r:
            svg = r.read().decode("utf-8", "replace")
    except Exception as exc:  # noqa: BLE001 - never fail the build over a counter
        print(f"warning: could not read counter ({exc}); keeping banner unchanged")
        return ""
    # Badge SVGs render each label twice (drop shadow + fill); the count is last.
    texts = [t.strip() for t in re.findall(r"<text[^>]*>([^<]*)</text>", svg)]
    digits = [t for t in texts if t.replace(",", "").isdigit()]
    if not digits:
        print(f"warning: no count found in counter response: {texts}")
        return ""
    return f"{int(digits[-1].replace(',', '')):,}"


def text_width(s: str, size: float) -> float:
    """Approximate Inter advance width, good enough to right-align the chip."""
    per = {",": 0.28, ".": 0.28}
    return sum(per.get(c, 0.58) for c in s) * size


TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 210" width="1000" height="210"
     role="img" aria-label="Guru R Bharadwaj - Full Stack Developer, AI and Tech Enthusiast">
  <defs>
    <style>
      @font-face {{ font-family:'GB Display'; font-weight:700; src:url(data:font/woff2;base64,{grotesk}) format('woff2'); }}
      @font-face {{ font-family:'GB Text'; font-weight:500; src:url(data:font/woff2;base64,{inter5}) format('woff2'); }}
      @font-face {{ font-family:'GB Text'; font-weight:400; src:url(data:font/woff2;base64,{inter4}) format('woff2'); }}
      .name {{ font-family:'GB Display','Segoe UI',Helvetica,Arial,sans-serif; font-weight:700; }}
      .txt  {{ font-family:'GB Text','Segoe UI',Helvetica,Arial,sans-serif; }}
    </style>

    <clipPath id="round"><rect x="0" y="0" width="1000" height="210" rx="14"/></clipPath>

    <pattern id="grid" width="26" height="26" patternUnits="userSpaceOnUse">
      <path d="M26 0H0V26" fill="none" stroke="{grid}" stroke-width="1"/>
    </pattern>

    <linearGradient id="gridFade" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0.00" stop-color="#fff" stop-opacity="0.25"/>
      <stop offset="0.45" stop-color="#fff" stop-opacity="0.70"/>
      <stop offset="1.00" stop-color="#fff" stop-opacity="1"/>
    </linearGradient>
    <mask id="gridMask"><rect width="1000" height="210" fill="url(#gridFade)"/></mask>

    <linearGradient id="wordFade" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0.00" stop-color="#fff" stop-opacity="0.06"/>
      <stop offset="0.42" stop-color="#fff" stop-opacity="0.38"/>
      <stop offset="0.88" stop-color="#fff" stop-opacity="1"/>
    </linearGradient>
    <mask id="wordMask"><rect width="1000" height="210" fill="url(#wordFade)"/></mask>
  </defs>

  <g clip-path="url(#round)">
    <rect width="1000" height="210" fill="{bg}"/>
    <rect width="1000" height="210" fill="url(#grid)" mask="url(#gridMask)"/>

    <g class="name" mask="url(#wordMask)" fill="{word}" opacity="{wordop}"
       font-size="68" letter-spacing="2">
      <text x="34" y="80">FULL STACK &#183; MACHINE LEARNING</text>
      <text x="-56" y="176">SYSTEMS &#183; DESIGN &#183; CODE &#183; IMPACT</text>
    </g>
{views}
    <text class="name" x="54" y="88" fill="{fg}" font-size="43" letter-spacing="1.5">GURU R BHARADWAJ</text>
    <rect x="56" y="105" width="118" height="3" rx="1.5" fill="{accent}"/>
    <text class="txt" x="55" y="138" fill="{sub}" font-size="16.5" font-weight="500" letter-spacing="0.4">Full Stack Developer &#160;&#183;&#160; AI &amp; Tech Enthusiast</text>
    <text class="txt" x="55" y="164" fill="{dim}" font-size="14" font-weight="400" letter-spacing="0.2">Building tech that blends design, code, and impact</text>
    <text class="txt" x="946" y="164" fill="{dim}" font-size="12.5" font-weight="500" letter-spacing="1.8" text-anchor="end">PES UNIVERSITY &#160;&#183;&#160; BENGALURU</text>
  </g>

  <rect x="0.5" y="0.5" width="999" height="209" rx="14" fill="none" stroke="{border}" stroke-width="1"/>
</svg>
"""

VIEWS_BLOCK = """
    <g transform="translate({eye_x} 34)">
      <path d="M0 9C3.6 3.2 8.4 0.6 11.5 0.6C14.6 0.6 19.4 3.2 23 9C19.4 14.8 14.6 17.4 11.5 17.4C8.4 17.4 3.6 14.8 0 9Z"
            fill="none" stroke="{accent}" stroke-width="1.6" stroke-linejoin="round"/>
      <circle cx="11.5" cy="9" r="3.4" fill="{accent}"/>
    </g>
    <text class="txt" x="946" y="49" fill="{sub}" font-size="15" font-weight="500"
          letter-spacing="0.6" text-anchor="end">{views}</text>
"""

DARK = dict(bg="#0d1117", grid="#22304a", word="#e6edf3", wordop="0.05",
            fg="#e6edf3", sub="#9aa4b1", dim="#6e7c8c", accent="#5bc0be", border="#21262d")
LIGHT = dict(bg="#ffffff", grid="#dbe3ee", word="#1f2328", wordop="0.045",
             fg="#1f2328", sub="#5b6472", dim="#8c959f", accent="#17817f", border="#d0d7de")


def build(theme: dict, views: str) -> str:
    if views:
        # Right edge at x=946; eye sits left of the number with a 10px gap.
        eye_x = 946 - text_width(views, 15) - 10 - 23
        block = VIEWS_BLOCK.format(eye_x=round(eye_x, 1), views=views,
                                   accent=theme["accent"], sub=theme["sub"])
    else:
        block = ""
    return TEMPLATE.format(
        grotesk=FONTS["grotesk700"], inter5=FONTS["inter500"], inter4=FONTS["inter400"],
        views=block, **theme,
    )


def main() -> None:
    views = fetch_views()
    if not views:
        return  # leave the committed banners alone rather than dropping the count
    print(f"profile views: {views}")
    for name, theme in (("banner-dark.svg", DARK), ("banner-light.svg", LIGHT)):
        path = ROOT / "assets" / name
        path.write_text(build(theme, views), encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
