#!/usr/bin/env python3
"""
fix_finish_code.py -- add a hard-coded FINISH_CODE that appears on every
results screen of the Decodable Reader app (Grades 1 & 2, modern & legacy).

For each file you pass:
  * Adds  const FINISH_CODE = 'CHANGE-ME';  (or var for legacy)
  * Adds a "Completion code" box below the day pills on the results screen
  * Populates it with the code + student name + date
  * Makes it click-to-copy (with a brief "Copied!" flash)
  * Includes "Finish Code: <code>" in the WhatsApp share text
  * Hides the box entirely if FINISH_CODE is empty or whitespace

Does NOT change: 80% pass threshold, score colours, status line,
best-score tracking, submit cap, or champion logic.

Usage:
    python fix_finish_code.py file1.html [file2.html ...]
                                [--dry-run]

A .bak backup is written next to each file the first time it's patched.
"""
import sys
import os
import shutil

# ===========================================================================
# Patch definitions
# ===========================================================================
# Each patch: (description, old_block, new_block)
# Patches are applied in order. All anchors must match exactly once.

# ---------- 1. Constants: add FINISH_CODE ----------
P_CONST_MODERN = (
    "add FINISH_CODE constant (modern)",
    """  const CHUNK_SIZE = 3;
  const PASS_PCT = 80;
  const MAX_SUBMITS_PER_DAY = 2;
  const TEACHER_WA = '233545800158';
  const STORAGE_KEY = 'decodable_student_v1';""",
    """  const CHUNK_SIZE = 3;
  const PASS_PCT = 80;
  const MAX_SUBMITS_PER_DAY = 2;
  const TEACHER_WA = '233545800158';
  const STORAGE_KEY = 'decodable_student_v1';
  // Completion code shown on every results screen. Set to your own code
  // (e.g. 'ABC123'), or '' to hide the box entirely.
  const FINISH_CODE = 'CHANGE-ME';"""
)

P_CONST_LEGACY = (
    "add FINISH_CODE constant (legacy)",
    """  var CHUNK_SIZE = 3;
  var PASS_PCT = 80;
  var MAX_SUBMITS_PER_DAY = 2;
  var TEACHER_WA = '233545800158';
  var STORAGE_KEY = 'decodable_student_v1';""",
    """  var CHUNK_SIZE = 3;
  var PASS_PCT = 80;
  var MAX_SUBMITS_PER_DAY = 2;
  var TEACHER_WA = '233545800158';
  var STORAGE_KEY = 'decodable_student_v1';
  // Completion code shown on every results screen. Set to your own code
  // (e.g. 'ABC123'), or '' to hide the box entirely.
  var FINISH_CODE = 'CHANGE-ME';"""
)

# ---------- 2. CSS: add finish-code styles (identical for both builds) ----------
P_CSS = (
    "add finish-code CSS",
    """    .result-badge .champ.show { display: inline-flex; }
    .result-actions { max-width: 400px; margin: 0 auto; display: flex; flex-direction: column; gap: 10px; }""",
    """    .result-badge .champ.show { display: inline-flex; }
    .finish-code-box {
      margin: 14px auto 0;
      padding: 12px 16px;
      background: var(--surface-2);
      border: 2px dashed var(--primary);
      border-radius: 14px;
      text-align: center;
      max-width: 320px;
      cursor: pointer;
      -webkit-user-select: none;
      -moz-user-select: none;
      -ms-user-select: none;
      user-select: none;
      -webkit-tap-highlight-color: transparent;
      transition: background 0.15s ease;
    }
    .finish-code-box:hover { background: var(--surface); }
    .finish-code-label {
      font-size: 0.68rem;
      font-weight: 800;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--text-3);
      margin-bottom: 4px;
    }
    .finish-code-value {
      font-family: ui-monospace, Menlo, Consolas, 'Courier New', monospace;
      font-size: 1.75rem;
      font-weight: 800;
      letter-spacing: 0.06em;
      color: var(--primary);
      line-height: 1.1;
      word-break: break-all;
    }
    .finish-code-meta {
      font-size: 0.72rem;
      color: var(--text-3);
      margin-top: 4px;
      font-weight: 600;
    }
    .result-actions { max-width: 400px; margin: 0 auto; display: flex; flex-direction: column; gap: 10px; }"""
)

# ---------- 3. HTML: insert finish-code box before the champion banner ----------
P_HTML = (
    "add finish-code markup",
    """          <div class="day-row" id="resDayPills"></div>
          <div class="champ" id="resChamp">""",
    """          <div class="day-row" id="resDayPills"></div>
          <div class="finish-code-box" id="resFinishCodeBox" style="display:none;">
            <div class="finish-code-label">Completion code</div>
            <div class="finish-code-value" id="resFinishCode" title="Tap to copy">—</div>
            <div class="finish-code-meta" id="resFinishCodeMeta"></div>
          </div>
          <div class="champ" id="resChamp">"""
)

# ---------- 4. renderResults: populate + wire click ----------
P_RENDER_MODERN = (
    "renderResults: populate finish code (modern)",
    """    const champ = document.getElementById('resChamp');
    if (r.highestDay >= 5) champ.classList.add('show');
    else champ.classList.remove('show');

    updateSubmitButton();""",
    """    const champ = document.getElementById('resChamp');
    if (r.highestDay >= 5) champ.classList.add('show');
    else champ.classList.remove('show');

    // Finish code box
    const fcBox = document.getElementById('resFinishCodeBox');
    const fcVal = document.getElementById('resFinishCode');
    const fcMeta = document.getElementById('resFinishCodeMeta');
    if (fcBox && fcVal && fcMeta) {
      const code = String(FINISH_CODE || '').replace(/^\\s+|\\s+$/g, '');
      if (code) {
        fcBox.style.display = '';
        fcVal.textContent = code;
        fcMeta.textContent = profile.name + ' · ' + formatDate(r.date);
        fcBox.onclick = copyFinishCode;
      } else {
        fcBox.style.display = 'none';
      }
    }

    updateSubmitButton();"""
)

P_RENDER_LEGACY = (
    "renderResults: populate finish code (legacy)",
    """    var champ = $('resChamp');
    if (r.highestDay >= 5) addClass(champ, 'show');
    else removeClass(champ, 'show');

    updateSubmitButton();""",
    """    var champ = $('resChamp');
    if (r.highestDay >= 5) addClass(champ, 'show');
    else removeClass(champ, 'show');

    /* Finish code box */
    var fcBox = $('resFinishCodeBox');
    var fcVal = $('resFinishCode');
    var fcMeta = $('resFinishCodeMeta');
    if (fcBox && fcVal && fcMeta) {
      var code = String(FINISH_CODE || '').replace(/^\\s+|\\s+$/g, '');
      if (code) {
        fcBox.style.display = '';
        fcVal.textContent = code;
        fcMeta.textContent = profile.name + ' \\u00b7 ' + formatDate(r.date);
        fcBox.onclick = copyFinishCode;
      } else {
        fcBox.style.display = 'none';
      }
    }

    updateSubmitButton();"""
)

# ---------- 5. Add copyFinishCode function (identical for both builds) ----------
P_COPY_MODERN = (
    "add copyFinishCode helper (modern)",
    """  function formatDate(d) {
    const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    return d.getDate() + ' ' + months[d.getMonth()] + ' ' + d.getFullYear();
  }

  function updateSubmitButton() {""",
    """  function formatDate(d) {
    const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    return d.getDate() + ' ' + months[d.getMonth()] + ' ' + d.getFullYear();
  }

  function copyFinishCode() {
    var code = String(FINISH_CODE || '').replace(/^\\s+|\\s+$/g, '');
    if (!code) return;
    var el = document.getElementById('resFinishCode');
    if (!el) return;
    var showCopied = function () {
      el.textContent = 'Copied!';
      clearTimeout(el._copyTimer);
      el._copyTimer = setTimeout(function () { el.textContent = code; }, 1200);
    };
    var fallback = function () {
      try {
        var ta = document.createElement('textarea');
        ta.value = code;
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.select();
        var ok = document.execCommand('copy');
        document.body.removeChild(ta);
        if (ok) showCopied(); else toast('Copy failed');
      } catch (e) { toast('Copy failed'); }
    };
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(code).then(showCopied, fallback);
      } else {
        fallback();
      }
    } catch (e) { fallback(); }
  }

  function updateSubmitButton() {"""
)

P_COPY_LEGACY = (
    "add copyFinishCode helper (legacy)",
    """  function formatDate(d) {
    var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    return d.getDate() + ' ' + months[d.getMonth()] + ' ' + d.getFullYear();
  }

  function updateSubmitButton() {""",
    """  function formatDate(d) {
    var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    return d.getDate() + ' ' + months[d.getMonth()] + ' ' + d.getFullYear();
  }

  function copyFinishCode() {
    var code = String(FINISH_CODE || '').replace(/^\\s+|\\s+$/g, '');
    if (!code) return;
    var el = document.getElementById('resFinishCode');
    if (!el) return;
    var showCopied = function () {
      el.textContent = 'Copied!';
      clearTimeout(el._copyTimer);
      el._copyTimer = setTimeout(function () { el.textContent = code; }, 1200);
    };
    var fallback = function () {
      try {
        var ta = document.createElement('textarea');
        ta.value = code;
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.select();
        var ok = document.execCommand('copy');
        document.body.removeChild(ta);
        if (ok) showCopied(); else toast('Copy failed');
      } catch (e) { toast('Copy failed'); }
    };
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(code).then(showCopied, fallback);
      } else {
        fallback();
      }
    } catch (e) { fallback(); }
  }

  function updateSubmitButton() {"""
)

# ---------- 6. submitToTeacher: include finish code in share text ----------
P_SHARE = (
    "include finish code in WhatsApp share text",
    """      'Date: ' + formatDate(r.date) + '\\n' +
      'Status: ' + (r.passed ? 'Day ' + r.day + ' Completed' : 'Needs practice');""",
    """      'Date: ' + formatDate(r.date) + '\\n' +
      (String(FINISH_CODE || '').replace(/^\\s+|\\s+$/g, '') ? 'Finish Code: ' + String(FINISH_CODE).replace(/^\\s+|\\s+$/g, '') + '\\n' : '') +
      'Status: ' + (r.passed ? 'Day ' + r.day + ' Completed' : 'Needs practice');"""
)

# ===========================================================================
# Driver
# ===========================================================================

def detect_build(content):
    """Return 'modern' or 'legacy' based on runtime-var style."""
    if 'const PASS_PCT' in content:
        return 'modern'
    if 'var PASS_PCT' in content:
        return 'legacy'
    raise RuntimeError("Cannot detect build style (neither const PASS_PCT nor var PASS_PCT found)")


def apply_patches(content_lf, patches):
    for desc, old, new in patches:
        n = content_lf.count(old)
        if n == 0:
            raise RuntimeError("Anchor not found for: " + desc + "\nFirst 500 chars of anchor:\n" + old[:500])
        if n > 1:
            raise RuntimeError("Anchor matched " + str(n) + " times for: " + desc)
        content_lf = content_lf.replace(old, new, 1)
        print("  [ok] " + desc)
    return content_lf


def patch_file(path, dry_run=False):
    with open(path, 'r', encoding='utf-8', newline='') as f:
        raw = f.read()

    # Basic sanity
    if 'Decodable Reader' not in raw and 'Decodable Reader' not in raw:
        # also try title tag
        if '<title>Decodable Reader' not in raw:
            raise RuntimeError("This does not look like a Decodable Reader file: " + path)

    # If already patched, skip
    if 'FINISH_CODE' in raw and 'srpFinishCode' not in raw and 'resFinishCodeBox' in raw:
        print("  -> already patched, skipping")
        return

    # Detect line-ending convention
    n_crlf = raw.count('\r\n')
    n_lf_only = raw.count('\n') - n_crlf
    if n_crlf and n_lf_only:
        print("  -> WARNING: mixed line endings detected ({} CRLF, {} LF)".format(n_crlf, n_lf_only))
    content_lf = raw.replace('\r\n', '\n')

    build = detect_build(content_lf)
    print("  -> build: " + build)

    patches = []
    if build == 'modern':
        patches.append(P_CONST_MODERN)
    else:
        patches.append(P_CONST_LEGACY)
    patches.append(P_CSS)
    patches.append(P_HTML)
    if build == 'modern':
        patches.append(P_RENDER_MODERN)
        patches.append(P_COPY_MODERN)
    else:
        patches.append(P_RENDER_LEGACY)
        patches.append(P_COPY_LEGACY)
    patches.append(P_SHARE)

    try:
        patched_lf = apply_patches(content_lf, patches)
    except RuntimeError as e:
        print("  FAILED: " + str(e))
        raise

    patched = patched_lf.replace('\n', '\r\n') if n_crlf > 0 else patched_lf

    if dry_run:
        print("  DRY RUN OK -- {} patches would apply cleanly.".format(len(patches)))
        return

    bak = path + '.bak'
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
        print("  backup: " + bak)
    else:
        print("  backup kept: " + bak)

    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(patched)
    print("  DONE -> " + path)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    flags = {a for a in sys.argv[1:] if a.startswith('--')}
    if not args:
        print(__doc__)
        sys.exit(1)

    dry_run = '--dry-run' in flags
    any_failed = False

    for path in args:
        print("=" * 70)
        print(path)
        if not os.path.isfile(path):
            print("  SKIP: file not found")
            any_failed = True
            continue
        try:
            patch_file(path, dry_run=dry_run)
        except Exception as e:
            print("  ERROR: " + str(e))
            any_failed = True
        print()

    if any_failed:
        sys.exit(2)


if __name__ == '__main__':
    main()