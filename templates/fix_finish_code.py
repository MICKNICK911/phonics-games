#!/usr/bin/env python3
"""
apply_patches.py  (v2 — four files)

Applies the discussed changes to all four Decodable Reader builds:

  P-readerT-1.html       (modern ES6, v1)
  P-readerT-2.html       (modern ES6, v2)
  P-readerT-old1.html    (legacy ES5, v1)
  P-readerT-old2.html    (legacy ES5, v2)

Writes *.patched.html — originals untouched.

A patch whose FIND does not match a given file is skipped *for that file
only* and reported. Everything else still applies, so you can see a
per-file / per-patch matrix of what landed.

Usage:
    python3 apply_patches.py
"""

import sys
from pathlib import Path

MODERN_FILES = ["P-readerT-1.html", "P-readerT-2.html"]
LEGACY_FILES = ["P-readerT-old1.html", "P-readerT-old2.html"]


# ─────────────────────────────────────────────────────────────────────────────
# helpers
# ─────────────────────────────────────────────────────────────────────────────

def apply_one(html: str, find: str, replace: str, name: str):
    n = html.count(find)
    if n == 0:
        return html, False, f"{name}: FIND not found"
    if n > 1:
        return html, False, f"{name}: FIND matched {n}x (expected 1)"
    return html.replace(find, replace, 1), True, f"{name}: OK"


def apply_patches(html: str, patches):
    results = []
    for name, find, replace in patches:
        html, ok, msg = apply_one(html, find, replace, name)
        results.append((name, ok, msg))
        print(f"    {'✓' if ok else '✗'} {msg}")
    return html, results


# ─────────────────────────────────────────────────────────────────────────────
# MODERN (ES6) patches — unchanged from v1 of this script
# ─────────────────────────────────────────────────────────────────────────────

MODERN_PATCHES = [
# ... (identical to previous script — A1 ×3, B1 ×2, D2 ×5, D1_D4, D4, C ×5) ...
]

# ─────────────────────────────────────────────────────────────────────────────
# LEGACY (ES5) patches — unchanged from v1 of this script
# ─────────────────────────────────────────────────────────────────────────────

LEGACY_PATCHES = [
# ... (identical to previous script) ...
]


# ─────────────────────────────────────────────────────────────────────────────
# main
# ─────────────────────────────────────────────────────────────────────────────

def process(src_path: Path, patches, label: str):
    print(f"\n=== {label}: {src_path.name} ===")
    if not src_path.exists():
        print(f"    ✗ file not found — skipping")
        return {"file": src_path.name, "present": False, "ok": 0, "fail": 0}

    html = src_path.read_text(encoding="utf-8")
    html, results = apply_patches(html, patches)

    dst = src_path.with_suffix(".patched.html")
    dst.write_text(html, encoding="utf-8")

    ok_count = sum(1 for _, ok, _ in results if ok)
    fail_count = len(results) - ok_count
    print(f"    → {ok_count} OK, {fail_count} failed  →  wrote {dst.name}")
    return {"file": src_path.name, "present": True, "ok": ok_count, "fail": fail_count}


def main():
    print("Applying patches to all builds…\n")

    summary = []
    for f in MODERN_FILES:
        summary.append(process(Path(f), MODERN_PATCHES, "MODERN"))
    for f in LEGACY_FILES:
        summary.append(process(Path(f), LEGACY_PATCHES, "LEGACY"))

    print("\n──────────── summary ────────────")
    all_green = True
    for s in summary:
        if not s["present"]:
            print(f"  {s['file']:<26}  MISSING")
            all_green = False
        elif s["fail"] == 0:
            print(f"  {s['file']:<26}  ✓ {s['ok']} patches applied")
        else:
            print(f"  {s['file']:<26}  ⚠ {s['ok']} OK, {s['fail']} failed")
            all_green = False

    print("\nOriginals untouched. Output written as *.patched.html")
    print("Diff / test / rename when satisfied.")
    if not all_green:
        print("\nFailed patches are usually whitespace/version drift.")
        print("Paste the ✗ lines back and I'll issue per-file variants.")

    if not all_green:
        sys.exit(1)


if __name__ == "__main__":
    main()