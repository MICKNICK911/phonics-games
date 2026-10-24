#!/usr/bin/env python3
"""fix_data_bar.py — finish A1_data_bar_remove on the legacy builds.

Reads the .patched.html files (13/14 applied), removes the data-bar div
if still present, writes back to the real .html.
"""

import re
from pathlib import Path

BASES = ["P-readerT-old1", "P-readerT-old2"]
MARKER = '<!-- DATA_MENU_MOVED_TO_HEADER -->'
DEFAULT_INPUT = '<input type="file" id="importFile" accept=".json,application/json" style="display:none" />'


def remove_data_bar(html):
    """Return (new_html, status)."""
    if MARKER in html:
        return html, "ALREADY_DONE"

    start = html.find('<div class="data-bar">')
    if start == -1:
        return html, "NO_DATA_BAR"

    # Balance divs from <div class="data-bar"> to its matching </div>
    i = start + len('<div class="data-bar">')
    depth = 1
    while i < len(html) and depth > 0:
        nopen = html.find('<div', i)
        nclose = html.find('</div>', i)
        if nclose == -1:
            return html, "UNBALANCED"
        if nopen != -1 and nopen < nclose:
            depth += 1
            i = nopen + 4
        else:
            depth -= 1
            i = nclose + 6

    block = html[start:i]
    m = re.search(r'<input type="file" id="importFile"[^>]*>', block)
    preserved = m.group(0) if m else DEFAULT_INPUT

    replacement = f'{MARKER}\n        {preserved}'
    return html[:start] + replacement + html[i:], "REMOVED"


def main():
    print("Fixing A1_data_bar_remove on legacy builds…\n")
    for base in BASES:
        patched = Path(base + ".html.patched.html")
        final = Path(base + ".html")

        if not patched.exists():
            print(f"  ✗ {patched.name} not found — skipping")
            continue

        html = patched.read_text(encoding="utf-8")
        html, status = remove_data_bar(html)

        if status == "UNBALANCED":
            print(f"  ✗ {base}: unbalanced divs, not written")
            continue

        final.write_text(html, encoding="utf-8")
        print(f"  ✓ {base}: {status}  →  {final.name}")

    print("\nDone.")


if __name__ == "__main__":
    main()