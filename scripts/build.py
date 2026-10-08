#!/usr/bin/env python3
"""Copy and bake GEO Live vs A+ compare pages into public/ for static deploy."""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
MONOREPO = PROJECT_ROOT.parent
OUT = PROJECT_ROOT / "public"
SRC = MONOREPO / "geo-deliverables"
STUBS = MONOREPO / "local-dev" / "stubs"

IPHONE = SRC / "iphone18pro"
HSV = SRC / "hsvworld"

IPHONE_FILES = (
    "simstd-en-live-vs-aplus-compare.html",
    "simstd-en-live-snapshot.html",
    "simstd-en-geo-aplus.html",
    "simstd-geo-compare.css",
)

HSV_COPY_FILES = (
    "index-en-live-vs-aplus-compare.html",
    "index-en-live-snapshot.html",
    "hsvworld-geo-compare.css",
    "worldplan-geo-liverow-live.css",
    "hsvworld-geo.css",
)

HSV_BAKE_APLUS = "index-en-geo-aplus.html"

INCLUDE_RE = re.compile(
    r"<!--#include\s+virtual=[\"']([^\"']+)[\"']\s*-->",
    re.IGNORECASE,
)
SET_RE = re.compile(
    r"<!--#set\s+var=[\"']([^\"']+)[\"']\s+value=[\"']([^\"']*)[\"']\s*-->",
    re.IGNORECASE,
)
ECHO_RE = re.compile(
    r"<!--#echo\s+var=['\"]([^'\"]+)['\"]\s*-->",
    re.IGNORECASE,
)

PLAN_CSS = "https://web.three.com.hk/plans/plancss/"
GLOBAL_ASSETS = "https://web.three.com.hk/plans/global/assets/"
HKWORLD_IMAGES = "https://web.three.com.hk/3hkworld/images/"

FONT_AWESOME = (
    '<link rel="stylesheet" '
    'href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">\n'
)


def normalize_virtual_path(virtual_path: str) -> Path:
    parts: list[str] = []
    for part in Path(virtual_path).parts:
        if part == "..":
            if parts:
                parts.pop()
        elif part != ".":
            parts.append(part)
    return Path(*parts)


def resolve_include(base_file: Path, virtual_path: str) -> Path | None:
    candidate = (base_file.parent / virtual_path).resolve()
    if candidate.is_file():
        return candidate

    normalized = normalize_virtual_path(virtual_path)
    root_file = (MONOREPO / normalized).resolve()
    try:
        root_file.relative_to(MONOREPO)
        if root_file.is_file():
            return root_file
    except ValueError:
        pass

    stub = (STUBS / normalized).resolve()
    if stub.is_file():
        return stub

    stub_name = normalized.name
    for candidate_stub in (STUBS / stub_name, STUBS / "planinc" / stub_name):
        if candidate_stub.is_file():
            return candidate_stub.resolve()

    return None


class SSIProcessor:
    def __init__(self) -> None:
        self.vars: dict[str, str] = {}

    def process(self, content: str, file_path: Path, depth: int = 0) -> str:
        if depth > 30:
            return content

        def set_repl(match: re.Match[str]) -> str:
            self.vars[match.group(1)] = match.group(2)
            return ""

        content = SET_RE.sub(set_repl, content)

        def echo_repl(match: re.Match[str]) -> str:
            return self.vars.get(match.group(1), "")

        content = ECHO_RE.sub(echo_repl, content)

        def include_repl(match: re.Match[str]) -> str:
            virtual = match.group(1)
            inc_path = resolve_include(file_path, virtual)
            if inc_path is None:
                return f"<!-- build: missing include {virtual} -->"
            inc_content = inc_path.read_text(encoding="utf-8", errors="replace")
            return self.process(inc_content, inc_path, depth + 1)

        return INCLUDE_RE.sub(include_repl, content)


def rewrite_hsv_aplus_for_static(html: str) -> str:
    html = html.replace('href="../../3hkworld/plancss/', f'href="{PLAN_CSS}')
    html = html.replace('src="../world-plan/assets/', f'src="{GLOBAL_ASSETS}')
    html = html.replace('src="../../3hkworld/images/', f'src="{HKWORLD_IMAGES}')
    if "font-awesome" not in html and "all.min.css" not in html:
        html = html.replace("</head>", FONT_AWESOME + "</head>", 1)
    return html


def bake_hsv_geo_aplus(src: Path, dest: Path) -> None:
    processor = SSIProcessor()
    html = processor.process(src.read_text(encoding="utf-8"), src)
    html = rewrite_hsv_aplus_for_static(html)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding="utf-8")


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
    for name in HSV_COPY_FILES:
        src = HSV / name
        if src.is_file():
            copy_file(src, OUT / "hsvworld" / name)

    aplus_src = HSV / HSV_BAKE_APLUS
    if aplus_src.is_file():
        bake_hsv_geo_aplus(aplus_src, OUT / "hsvworld" / HSV_BAKE_APLUS)

    write_index()
    print(f"Built {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
