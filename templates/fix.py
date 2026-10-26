#!/usr/bin/env python3
"""
Fix the literal \\u21BB text that appears next to the day banner.
Replaces it with a proper inline SVG refresh icon.
Also fixes the literal \\u2026 in the loading placeholder.
"""
from pathlib import Path

FILES = [
    "P-readerT-1.html",
    "P-readerT-old1.html",
    "P-readerT-2.html",
    "P-readerT-old2.html",
]

# Circular-arrow refresh icon — same style as the rest of the app's icons.
SVG_REFRESH = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" '
    'width="22" height="22">'
    '<path d="M21 12a9 9 0 1 1-3-6.7"/>'
    '<path d="M21 3v6h-6"/>'
    '</svg>'
)

for fname in FILES:
    p = Path(fname)
    if not p.exists():
        print(f"[{fname}] not found, skipping")
        continue

    content = p.read_text(encoding="utf-8")
    orig = content

    # Replace literal 6-char sequence "\u21BB" with the SVG.
    content = content.replace(
        'aria-label="Refresh">\\u21BB</button>',
        'aria-label="Refresh">' + SVG_REFRESH + '</button>',
    )

    # Replace literal 6-char sequence "\u2026" in the placeholder text.
    content = content.replace(
        'Loading\\u2026</span>',
        'Loading&hellip;</span>',
    )

    if content == orig:
        print(f"[{fname}] no fix needed (or already fixed)")
    else:
        p.write_text(content, encoding="utf-8")
        print(f"[{fname}] fixed")