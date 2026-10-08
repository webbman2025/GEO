#!/usr/bin/env python3
"""Copy GEO Live vs A+ compare pages into public/ for static deploy."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
MONOREPO = PROJECT_ROOT.parent
OUT = PROJECT_ROOT / "public"
SRC = MONOREPO / "geo-deliverables"

IPHONE = SRC / "iphone18pro"
HSV = SRC / "hsvworld"

IPHONE_FILES = (
    "simstd-en-live-vs-aplus-compare.html",
    "simstd-en-live-snapshot.html",
    "simstd-en-geo-aplus.html",
    "simstd-geo-compare.css",
)

HSV_FILES = (
    "index-en-live-vs-aplus-compare.html",
    "index-en-live-snapshot.html",
    "index-en-geo-aplus.html",
    "hsvworld-geo-compare.css",
    "worldplan-geo-liverow-live.css",
    "hsvworld-geo.css",
)


def copy_file(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def write_index() -> None:
    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>3HK GEO — Live vs A+ compare</title>
<style>
  body { font-family: system-ui, sans-serif; max-width: 40rem; margin: 2rem auto; padding: 0 1rem; line-height: 1.5; }
  h1 { font-size: 1.25rem; }
  ul { padding-left: 1.2rem; }
  a { color: #774fda; }
</style>
</head>
<body>
<h1>GEO compare previews</h1>
<ul>
  <li><a href="/iphone18pro/simstd-en-live-vs-aplus-compare.html">iPhone 18 simstd-en — Live vs GEO A+</a></li>
  <li><a href="/hsvworld/index-en-live-vs-aplus-compare.html">WORLD PLAN hsvworld EN — Live vs GEO A+</a></li>
</ul>
</body>
</html>
"""
    (OUT / "index.html").write_text(html, encoding="utf-8")


def main() -> int:
    if not IPHONE.is_dir() or not HSV.is_dir():
        print("Missing geo-deliverables; run from 3hkweb monorepo.", file=sys.stderr)
        return 1

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    for name in IPHONE_FILES:
        copy_file(IPHONE / name, OUT / "iphone18pro" / name)
    for name in HSV_FILES:
        src = HSV / name
        if src.is_file():
            copy_file(src, OUT / "hsvworld" / name)

    write_index()
    print(f"Built {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
