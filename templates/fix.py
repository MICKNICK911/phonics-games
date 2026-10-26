#!/usr/bin/env python3
"""
Banner v2: two-line banner + lesson-number config + pulse on waiting state.

Applies to all four reader files:
    P-readerT-1.html, P-readerT-old1.html, P-readerT-2.html, P-readerT-old2.html

Changes:
  1. TARGET_LESSON_TITLE  ->  TARGET_LESSON_NUMBER  (lesson number, not title)
  2. isTargetLesson()     ->  numeric match on lessonNumber
  3. Export CSV           ->  target lesson number + resolved title
  4. Banner HTML          ->  two-line structure (title + status + hint id)
  5. Banner CSS           ->  pulse animation + clickable states + refresh svg size
  6. renderDayBanner()    ->  state-aware title/status/hint + click action
  7. Refresh button       ->  stopPropagation (banner handles its own action)

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

# -------- new pieces ----------------------------------------------------------

NEW_TEACHER_CONFIG = "  var TARGET_LESSON_NUMBER = 1;             /* lesson number (1 to 83) */"

NEW_IS_TARGET = """  function isTargetLesson(l) {
    if (!l) return false;
    var n = parseInt(TARGET_LESSON_NUMBER, 10);
    if (!n || n < 1) return false;
    return l.lessonNumber === n;
  }"""

NEW_EXPORT_ROWS = """    var _targetLesson = null;
    for (var _ti = 0; _ti < LESSONS.length; _ti++) {
      if (isTargetLesson(LESSONS[_ti])) { _targetLesson = LESSONS[_ti]; break; }
    }
    rows.push(['Target lesson number', TARGET_LESSON_NUMBER]);
    rows.push(['Target lesson title', _targetLesson ? _targetLesson.title : '(not found)']);
    rows.push(['Open day', targetDay()]);"""

NEW_HTML = """        <div class="day-banner" id="dayBanner">
          <div class="day-banner-text">
            <div class="day-banner-title" id="dayBannerTitle">Loading&hellip;</div>
            <div class="day-banner-status" id="dayBannerStatus"></div>
          </div>
          <button type="button" class="refresh-btn" id="refreshBtn" aria-label="Refresh"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" width="22" height="22"><path d="M21 12a9 9 0 1 1-3-6.7"/><path d="M21 3v6h-6"/></svg></button>
        </div>
        <div class="day-banner-hint" id="dayBannerHint">Refresh to see latest update</div>
"""

NEW_CSS = """    /* ===== Day banner (Home) ===== */
    .day-banner {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 14px 16px;
      border-radius: var(--radius);
      border: 2px solid var(--border);
      background: var(--surface);
      margin-bottom: 6px;
      line-height: 1.35;
      transition: border-color 0.15s, background 0.15s, transform 0.1s;
    }
    .day-banner-text { flex: 1; min-width: 0; }
    .day-banner-title {
      font-weight: 800;
      font-size: 0.95rem;
      letter-spacing: -0.01em;
      margin-bottom: 3px;
    }
    .day-banner-status {
      font-weight: 700;
      font-size: 0.85rem;
      color: var(--text-2);
    }

    /* Open state */
    .day-banner.is-open {
      border-color: var(--accent);
      background: rgba(245,158,11,0.10);
      cursor: pointer;
    }
    .day-banner.is-open:active { transform: scale(0.99); }
    .day-banner.is-open .day-banner-status { color: var(--accent-dark); }

    /* Done / waiting state — refresh button pulses */
    .day-banner.is-done {
      border-color: var(--success);
      background: rgba(22,163,74,0.08);
      cursor: pointer;
    }
    .day-banner.is-done:active { transform: scale(0.99); }
    .day-banner.is-done .day-banner-status { color: var(--success); }

    /* Champion */
    .day-banner.is-champion {
      border-color: #a855f7;
      background: linear-gradient(135deg, rgba(168,85,247,0.12), rgba(99,102,241,0.12));
      cursor: pointer;
    }
    .day-banner.is-champion .day-banner-status { color: #7c3aed; }

    /* Waiting / error (no lesson configured) */
    .day-banner.is-waiting {
      border-color: var(--border);
      background: var(--surface-2);
    }
    .day-banner.is-waiting .day-banner-status { color: var(--text-2); }

    /* Refresh button */
    .refresh-btn {
      width: 44px;
      height: 44px;
      min-width: 44px;
      border-radius: 50%;
      border: none;
      background: var(--accent);
      color: #0f172a;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      -webkit-tap-highlight-color: transparent;
      transition: transform 0.12s, background 0.15s;
    }
    .refresh-btn svg { width: 22px; height: 22px; }
    .refresh-btn:active { transform: scale(0.94); }

    .day-banner.is-done .refresh-btn {
      background: var(--success);
      color: #fff;
      animation: refreshPulse 1.8s ease-in-out infinite;
    }
    .day-banner.is-champion .refresh-btn { background: #a855f7; color: #fff; }

    @keyframes refreshPulse {
      0%, 100% { box-shadow: 0 0 0 0 rgba(22,163,74,0.55); }
      50%      { box-shadow: 0 0 0 10px rgba(22,163,74,0); }
    }

    .day-banner-hint {
      font-size: 0.72rem;
      color: var(--text-3);
      font-weight: 600;
      margin-bottom: 14px;
      padding-left: 4px;
    }
"""

NEW_RENDER = """  function renderDayBanner() {
    var banner = document.getElementById('dayBanner');
    var title = document.getElementById('dayBannerTitle');
    var status = document.getElementById('dayBannerStatus');
    var hint = document.getElementById('dayBannerHint');
    if (!banner || !title || !status) return;

    var lesson = null;
    for (var i = 0; i < LESSONS.length; i++) {
      if (isTargetLesson(LESSONS[i])) { lesson = LESSONS[i]; break; }
    }

    banner.className = 'day-banner';
    banner.onclick = null;

    if (!lesson) {
      title.textContent = 'Waiting for teacher';
      var n = parseInt(TARGET_LESSON_NUMBER, 10);
      status.textContent = (n && n >= 1)
        ? 'Lesson ' + n + ' not found \\u2014 check the number'
        : 'Lesson number not set';
      banner.className = 'day-banner is-waiting';
      if (hint) hint.textContent = 'Refresh to see latest update';
      return;
    }

    var openDay = targetDay();
    var flags = FlagsMod.get(profile.name, lesson.id);
    var currentDayDone = flags[openDay - 1] === true;
    var allDone = FlagsMod.count(profile.name, lesson.id) === 5;

    title.textContent = 'Lesson ' + lesson.lessonNumber + ': ' + lesson.title;

    if (allDone) {
      status.textContent = '\\uD83C\\uDFC6 All 5 days complete \\u2014 Champion!';
      banner.className = 'day-banner is-champion';
      if (hint) hint.textContent = 'Refresh to see latest update';
      banner.onclick = function () { location.reload(); };
    } else if (currentDayDone) {
      status.textContent = 'Day ' + openDay + ' complete \\u2713 \\u2014 waiting for teacher';
      banner.className = 'day-banner is-done';
      if (hint) hint.textContent = 'Tap \\u21BB to check for a new day';
      banner.onclick = function () { location.reload(); };
    } else {
      status.textContent = 'Day ' + openDay + ' is open \\u2014 read it now!';
      banner.className = 'day-banner is-open';
      if (hint) hint.textContent = 'Refresh to see latest update';
      banner.onclick = function () { openLesson(lesson.id); };
    }
  }

"""

OLD_REFRESH = """  (function initRefreshButton() {
    var refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', function () { location.reload(); });
    }
  })();"""

NEW_REFRESH = """  (function initRefreshButton() {
    var refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', function (e) {
        if (e && e.stopPropagation) e.stopPropagation();
        location.reload();
      });
    }
  })();"""

# -------- helpers -------------------------------------------------------------


def say(prefix, label):
    print(f"    {prefix} {label}")


def replace_between(content, start_marker, end_marker, new_block, label, marker_check=None):
    if marker_check and marker_check in content:
        say("~", f"{label} (already applied)")
        return content
    s = content.find(start_marker)
    if s < 0:
        say("x", f"{label} -- start not found")
        return content
    e = content.find(end_marker, s + len(start_marker))
    if e < 0:
        say("x", f"{label} -- end not found")
        return content
    content = content[:s] + new_block + content[e:]
    say("+", label)
    return content


def apply_changes(content, fname):
    print(f"\n[{fname}]")

    # ---- 1. TARGET_LESSON_TITLE -> TARGET_LESSON_NUMBER ----
    if "var TARGET_LESSON_NUMBER" in content:
        say("~", "teacher config: TARGET_LESSON_NUMBER (already applied)")
    else:
        lines = content.split("\n")
        changed = False
        for i, line in enumerate(lines):
            if line.strip().startswith("var TARGET_LESSON_TITLE"):
                indent = line[: len(line) - len(line.lstrip())]
                lines[i] = indent + NEW_TEACHER_CONFIG.strip()
                content = "\n".join(lines)
                say("+", "teacher config: TARGET_LESSON_TITLE -> TARGET_LESSON_NUMBER")
                changed = True
                break
        if not changed:
            say("x", "teacher config -- TARGET_LESSON_TITLE line not found")

    # ---- 2. isTargetLesson ----
    old_is_target = """  function isTargetLesson(l) {
    if (!l) return false;
    var a = String(l.title).replace(/^\\s+|\\s+$/g, '').toLowerCase();
    var b = String(TARGET_LESSON_TITLE).replace(/^\\s+|\\s+$/g, '').toLowerCase();
    return a === b;
  }"""
    if "parseInt(TARGET_LESSON_NUMBER, 10);\n    if (!n || n < 1) return false;\n    return l.lessonNumber === n;" in content:
        say("~", "isTargetLesson (already applied)")
    elif old_is_target in content:
        content = content.replace(old_is_target, NEW_IS_TARGET, 1)
        say("+", "isTargetLesson -- numeric match")
    else:
        say("x", "isTargetLesson -- anchor not found")

    # ---- 3. Export CSV target rows ----
    old_export = """    rows.push(['Target lesson', TARGET_LESSON_TITLE]);
    rows.push(['Target day', targetDay()]);"""
    if "rows.push(['Target lesson number'" in content:
        say("~", "export CSV target rows (already applied)")
    elif old_export in content:
        content = content.replace(old_export, NEW_EXPORT_ROWS, 1)
        say("+", "export CSV -- number + resolved title")
    else:
        say("x", "export CSV target rows -- anchor not found")

    # ---- 4. Banner HTML ----
    old_html_start = '        <div class="day-banner" id="dayBanner">'
    old_html_end = '        <div id="lessonList"></div>'
    content = replace_between(
        content,
        old_html_start,
        old_html_end,
        NEW_HTML,
        "banner HTML -- two-line structure",
        marker_check='id="dayBannerTitle"',
    )

    # ---- 5. Banner CSS ----
    old_css_start = "    /* ===== Day banner (Home) ===== */"
    old_css_end = "    @media (min-width: 600px) {"
    content = replace_between(
        content,
        old_css_start,
        old_css_end,
        NEW_CSS,
        "banner CSS -- pulse + clickable states",
        marker_check="@keyframes refreshPulse",
    )

    # ---- 6. renderDayBanner() ----
    old_fn_start = "  function renderDayBanner() {"
    old_fn_end = "  function renderHome() {"
    content = replace_between(
        content,
        old_fn_start,
        old_fn_end,
        NEW_RENDER,
        "renderDayBanner() -- state-aware title/status/hint/action",
        marker_check="Tap \\u21BB to check for a new day",
    )

    # ---- 7. Refresh button stopPropagation ----
    if "if (e && e.stopPropagation) e.stopPropagation();" in content and "location.reload();" in content:
        # safer: check for the specific block
        if NEW_REFRESH.strip() in content or "if (e && e.stopPropagation) e.stopPropagation();\n        location.reload();" in content:
            say("~", "refresh button stopPropagation (already applied)")
        elif OLD_REFRESH in content:
            content = content.replace(OLD_REFRESH, NEW_REFRESH, 1)
            say("+", "refresh button -- stopPropagation")
        else:
            say("x", "refresh button -- anchor not found")
    elif OLD_REFRESH in content:
        content = content.replace(OLD_REFRESH, NEW_REFRESH, 1)
        say("+", "refresh button -- stopPropagation")
    else:
        say("x", "refresh button -- anchor not found")

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
        backup = p.with_name(p.stem + ".banner-v2" + p.suffix + ".bak")
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