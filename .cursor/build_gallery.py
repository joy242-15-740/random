#!/usr/bin/env python3
"""Generate a static preview gallery (gallery.html) for the image assets.

This is an environment/dev-experience helper: the repository is a collection of
image assets with no build system, so this script produces a single self-contained
HTML page that lets you browse every asset in the browser. It is idempotent and has
no third-party dependencies.
"""
from __future__ import annotations

import html
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
IMAGE_EXTENSIONS = {".webp", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".avif"}
ASSET_DIRS = ["backgrounds", "cover", "icons"]
OUTPUT = REPO_ROOT / "gallery.html"


def collect_images() -> dict[str, list[Path]]:
    groups: dict[str, list[Path]] = {}
    for group in ASSET_DIRS:
        base = REPO_ROOT / group
        if not base.is_dir():
            continue
        images = sorted(
            p for p in base.rglob("*") if p.suffix.lower() in IMAGE_EXTENSIONS
        )
        if images:
            groups[group] = images
    return groups


def render(groups: dict[str, list[Path]]) -> str:
    total = sum(len(v) for v in groups.values())
    sections: list[str] = []
    for group, images in groups.items():
        cards: list[str] = []
        for img in images:
            rel = img.relative_to(REPO_ROOT).as_posix()
            src = "/" + "/".join(html.escape(part) for part in rel.split("/"))
            name = html.escape(img.name)
            size_kb = img.stat().st_size / 1024
            cards.append(
                f'<figure class="card">'
                f'<a href="{src}" target="_blank" rel="noopener">'
                f'<img loading="lazy" src="{src}" alt="{name}"></a>'
                f'<figcaption><span class="name">{name}</span>'
                f'<span class="meta">{size_kb:.0f} KB</span></figcaption>'
                f"</figure>"
            )
        sections.append(
            f'<section><h2>{html.escape(group)} '
            f'<span class="count">{len(images)}</span></h2>'
            f'<div class="grid">{"".join(cards)}</div></section>'
        )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Asset Preview Gallery</title>
<style>
  :root {{ color-scheme: light dark; }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
         background: #0f1115; color: #e7e9ee; }}
  header {{ padding: 28px 32px; border-bottom: 1px solid #262a33;
            position: sticky; top: 0; background: #0f1115ee; backdrop-filter: blur(6px); }}
  header h1 {{ margin: 0 0 4px; font-size: 22px; }}
  header p {{ margin: 0; color: #9aa3b2; font-size: 14px; }}
  main {{ padding: 24px 32px 64px; }}
  section {{ margin-bottom: 40px; }}
  h2 {{ font-size: 16px; text-transform: capitalize; color: #cdd3df;
        border-left: 3px solid #4c8bf5; padding-left: 10px; }}
  .count {{ background: #262a33; color: #9aa3b2; font-size: 12px;
            border-radius: 10px; padding: 2px 8px; margin-left: 6px; }}
  .grid {{ display: grid; gap: 16px;
           grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); }}
  .card {{ margin: 0; background: #171a21; border: 1px solid #262a33;
           border-radius: 10px; overflow: hidden; }}
  .card img {{ width: 100%; height: 160px; object-fit: contain;
               background: repeating-conic-gradient(#20242d 0% 25%, #171a21 0% 50%) 50% / 24px 24px;
               display: block; }}
  figcaption {{ display: flex; justify-content: space-between; gap: 8px;
                padding: 8px 10px; font-size: 12px; }}
  .name {{ overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
  .meta {{ color: #9aa3b2; flex: none; }}
</style>
</head>
<body>
<header>
  <h1>Asset Preview Gallery</h1>
  <p>{total} image assets across {len(groups)} folders</p>
</header>
<main>
{''.join(sections) if sections else '<p>No image assets found.</p>'}
</main>
</body>
</html>
"""


def main() -> None:
    groups = collect_images()
    OUTPUT.write_text(render(groups), encoding="utf-8")
    total = sum(len(v) for v in groups.values())
    print(f"Wrote {OUTPUT.relative_to(REPO_ROOT)} with {total} assets "
          f"across {len(groups)} folders.")


if __name__ == "__main__":
    main()
