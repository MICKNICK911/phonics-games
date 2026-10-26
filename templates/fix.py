#!/usr/bin/env python3
"""
Apply: seed removal + submit gate until pass + button emphasis swap.

Applies to all four reader files:
    P-readerT-1.html, P-readerT-old1.html, P-readerT-2.html, P-readerT-old2.html

Changes:
  1. Remove the Day-1 seed from FlagsMod.ensure()
  2. updateSubmitButton() — hide button when !passed, reset display when passed
  3. submitToTeacher() — runtime guard: refuse to submit when !passed
  4. Results line 5 — reorder: !isTarget before !passed; update !passed text
  5. Results buttons — swap emphasis when failed: Read again becomes amber
     primary, Lessons becomes outline. Reverts when passed.

Idempotent — safe to re-run.
"""

import sys
from pathlib import Path

FILES = [
    "P-readerT-1.html",
    "P-readerT-old1.html",
    "P-readerT-2.html",
    "P-readerT-old2.html",
]

# ---------- change 1: seed removal ----------
OLD_SEED = "        if (LESSONS.length && lessonId === LESSONS[0].id) rec.day1 = true;"
NEW_SEED = """        /* Day-1 seed removed 2026-10-26. Existing students keep their earned
           flags in IndexedDB; new students start at 0/5 on every lesson.
           Do NOT re-add this line unless intentionally granting Day 1 to
           every new student account. */"""

# ---------- change 2a: updateSubmitButton guard ----------
OLD_PRACTICE_GUARD = """    if (!lastResult.isTarget) {
      btn.disabled = true;
      btn.innerHTML = 'Practice only \\u2014 nothing to submit';
      return;
    }"""

NEW_PRACTICE_GUARD = """    btn.style.display = '';

    if (!lastResult.isTarget) {
      btn.disabled = true;
      btn.innerHTML = 'Practice only \\u2014 nothing to submit';
      return;
    }

    if (!lastResult.passed) {
      btn.style.display = 'none';
      return;
    }"""

# ---------- change 2b: submitToTeacher guard ----------
OLD_SUBMIT_TOP = """  async function submitToTeacher() {
    if (!lastResult) return;"""

NEW_SUBMIT_TOP = """  async function submitToTeacher() {
    if (!lastResult) return;
    if (!lastResult.passed) { toast('Not submitted \\u2014 pass the quiz first'); return; }"""

# ---------- change 2c: line 5 reorder ----------
OLD_LINE5 = """      if (r.counted) msg = '\\u2605 Day ' + r.day + ' counted for this lesson';
      else if (r.alreadyCounted) msg = '\\u2713 Day ' + r.day + ' already earned \\u2014 replay doesn\\'t count again';
      else if (!r.passed) msg = 'Not counted \\u2014 pass the questions and Sound Hunt to earn the day';
      else if (!r.isTarget) msg = 'Practice lesson \\u2014 not today\\'s target, so no day earned';
      else msg = '\\u26A0 Day mismatch \\u2014 refresh the app and try again';"""

NEW_LINE5 = """      if (r.counted) msg = '\\u2605 Day ' + r.day + ' counted for this lesson';
      else if (r.alreadyCounted) msg = '\\u2713 Day ' + r.day + ' already earned \\u2014 replay doesn\\'t count again';
      else if (!r.isTarget) msg = 'Practice lesson \\u2014 not today\\'s target, so no day earned';
      else if (!r.passed) msg = '\\u2717 Not counted \\u2014 read again and retry the quiz';
      else msg = '\\u26A0 Day mismatch \\u2014 refresh the app and try again';"""

# ---------- change 2d + 2e: helper + call from renderResults ----------
OLD_UPDATE_CALL = """    updateSubmitButton();
  }

  function formatDate(d) {"""

NEW_UPDATE_CALL = """    updateSubmitButton();
    updateResultButtonEmphasis(r);
  }

  function updateResultButtonEmphasis(r) {
    var againBtn = document.getElementById('resAgainBtn');
    var listBtn = document.getElementById('resListBtn');
    if (!againBtn || !listBtn) return;
    if (r.passed) {
      againBtn.className = 'btn btn-outline';
      listBtn.className = 'btn btn-primary';
    } else {
      againBtn.className = 'btn btn-primary';
      listBtn.className = 'btn btn-outline';
    }
  }

  function formatDate(d) {"""


def replace_once(content, old, new, label, marker=None):
    if marker and marker in content:
        print(f"    ~ {label} (already applied)")
        return content
    if old not in content:
        print(f"    x {label} -- anchor not found")
        return content
    content = content.replace(old, new, 1)
    print(f"    + {label}")
    return content


def apply_changes(content, fname):
    print(f"\n[{fname}]")

    # 1. Seed removal
    content = replace_once(
        content, OLD_SEED, NEW_SEED,
        "remove Day-1 seed from FlagsMod.ensure()",
        marker="Day-1 seed removed 2026-10-26",
    )

    # 2a. updateSubmitButton guard + display reset
    content = replace_once(
        content, OLD_PRACTICE_GUARD, NEW_PRACTICE_GUARD,
        "updateSubmitButton() -- hide button when !passed, reset display",
        marker="btn.style.display = 'none';\n      return;\n    }\n\n    if (count >= MAX_SUBMITS_PER_DAY)",
    )

    # 2b. submitToTeacher runtime guard
    content = replace_once(
        content, OLD_SUBMIT_TOP, NEW_SUBMIT_TOP,
        "submitToTeacher() -- refuse when !passed",
        marker="toast('Not submitted \\u2014 pass the quiz first')",
    )

    # 2c. Line 5 reorder
    content = replace_once(
        content, OLD_LINE5, NEW_LINE5,
        "results line 5 -- reorder !isTarget before !passed",
        marker="else if (!r.isTarget) msg = 'Practice lesson \\u2014 not today\\'s target, so no day earned';\n      else if (!r.passed) msg = '\\u2717 Not counted \\u2014 read again and retry the quiz';",
    )

    # 2d + 2e. Helper + call
    content = replace_once(
        content, OLD_UPDATE_CALL, NEW_UPDATE_CALL,
        "renderResults() -- call updateResultButtonEmphasis()",
        marker="function updateResultButtonEmphasis(r)",
    )

    return content


def main():
    files = sys.argv[1:] if len(sys.argv) > 1 else FILES
    any_changed = False
    missing = []

    for fname in files:
        p = Path(fname)
        if not p.exists():
            missing.append(fname)
            print(f"[{fname}] -- not found, skipping")
            continue

        original = p.read_text(encoding="utf-8")
        backup = p.with_name(p.stem + ".submit-gate" + p.suffix + ".bak")
        if not backup.exists():
            backup.write_text(original, encoding="utf-8")
            print(f"\n[{fname}] backup -> {backup.name}")

        updated = apply_changes(original, fname)

        if updated == original:
            print(f"\n[{fname}] no changes made")
        else:
            p.write_text(updated, encoding="utf-8")
            print(f"\n[{fname}] written OK")
            any_changed = True

    if missing:
        print("\nMissing:", ", ".join(missing))

    print("\nDone." if any_changed else "\nDone (nothing to change).")


if __name__ == "__main__":
    main()