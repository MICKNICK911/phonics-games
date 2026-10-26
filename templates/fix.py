#!/usr/bin/env python3
"""
Apply the agreed changes to all four reader files:
    P-readerT-1.html       (modern Reader 1)
    P-readerT-old1.html    (legacy Reader 1)
    P-readerT-2.html       (modern Reader 2)
    P-readerT-old2.html    (legacy Reader 2)

Changes:
  1.  TARGET_DAY  ->  OPEN_DAY
  2.  Home day banner: "Day N is open" / "Day N complete — waiting for teacher"
      / "Champion!" / "Waiting for teacher"
  3.  Refresh button on Home only (location.reload) with hint text
  4.  completeCycle() reads flag before write (counted vs alreadyCounted)
  5.  Results line 5: honest message + stale-device fall-through
  6.  WhatsApp: (new) / (replay — already earned) / Not counted, plus submits count
  7.  updateSubmitButton(): practice-only guard, no "N left" counter
  8.  Persist lastResult to localStorage on Results render
  9.  Restore lastResult on init; route to Results if present
  10. Clear lastResult when leaving Results

Backs up each original to <file>.bak on first run.
Idempotent — safe to run twice.
"""

import sys
from pathlib import Path

DEFAULT_FILES = [
    "P-readerT-1.html",
    "P-readerT-old1.html",
    "P-readerT-2.html",
    "P-readerT-old2.html",
]


def safe_replace(content, old, new, label, marker):
    if marker in content:
        print(f"    ~ {label} (already applied)")
        return content, True
    if old not in content:
        print(f"    x {label} -- anchor not found")
        return content, False
    content = content.replace(old, new, 1)
    print(f"    + {label}")
    return content, True


def apply_changes(content, path):
    print(f"\n[{path}]")

    # ---------- 1. TARGET_DAY -> OPEN_DAY ----------
    content, _ = safe_replace(
        content,
        "var TARGET_DAY = ",
        "var OPEN_DAY = ",
        "rename TARGET_DAY declaration",
        marker="var OPEN_DAY = ",
    )
    content, _ = safe_replace(
        content,
        "parseInt(TARGET_DAY, 10)",
        "parseInt(OPEN_DAY, 10)",
        "rename TARGET_DAY usage inside targetDay()",
        marker="parseInt(OPEN_DAY, 10)",
    )

    # ---------- 2. alreadyCounted init in lastResult ----------
    content, _ = safe_replace(
        content,
        "counted: false,\n      date: new Date(),",
        "counted: false,\n      alreadyCounted: false,\n      date: new Date(),",
        "add alreadyCounted: false to lastResult",
        marker="alreadyCounted: false,\n      date: new Date(),",
    )

    # ---------- 3. completeCycle() - read before write ----------
    old_cc = """function completeCycle() {
    if (!lastResult || !lastResult.passed) return;
    if (!isTargetLesson(currentLesson) || lastResult.day !== targetDay()) { lastResult.counted = false; return; }
    FlagsMod.setDay(profile.name, currentLesson.id, lastResult.day);
    lastResult.counted = true;
  }"""
    new_cc = """function completeCycle() {
    if (!lastResult || !lastResult.passed) return;

    if (!isTargetLesson(currentLesson) || lastResult.day !== targetDay()) {
      lastResult.counted = false;
      lastResult.alreadyCounted = false;
      return;
    }

    var flags = FlagsMod.get(profile.name, currentLesson.id);
    var had = flags[lastResult.day - 1] === true;
    var earned = FlagsMod.setDay(profile.name, currentLesson.id, lastResult.day);

    lastResult.counted = earned;
    lastResult.alreadyCounted = had && !earned;
  }"""
    content, _ = safe_replace(
        content, old_cc, new_cc,
        "completeCycle() - read flag before write",
        marker="lastResult.alreadyCounted = had && !earned",
    )

    # ---------- 4. Results line 5 ----------
    old_l5 = (
        "      if (r.counted) msg = '\\u2605 Day ' + r.day + ' counted for this lesson';\n"
        "      else if (!r.passed) msg = 'Not counted \\u2014 pass the questions and Sound Hunt to earn the day';\n"
        "      else if (!r.isTarget) msg = 'Practice lesson \\u2014 not today\\u2019s target, so no day earned';"
    )
    new_l5 = (
        "      if (r.counted) msg = '\\u2605 Day ' + r.day + ' counted for this lesson';\n"
        "      else if (r.alreadyCounted) msg = '\\u2713 Day ' + r.day + ' already earned \\u2014 replay doesn\\'t count again';\n"
        "      else if (!r.passed) msg = 'Not counted \\u2014 pass the questions and Sound Hunt to earn the day';\n"
        "      else if (!r.isTarget) msg = 'Practice lesson \\u2014 not today\\u2019s target, so no day earned';\n"
        "      else msg = '\\u26A0 Day mismatch \\u2014 refresh the app and try again';"
    )
    content, _ = safe_replace(
        content, old_l5, new_l5,
        "results line 5 - alreadyCounted + stale-device fall-through",
        marker="r.alreadyCounted) msg = '\\u2713 Day '",
    )

    # ---------- 5. WhatsApp message ----------
    old_wa = "      (r.counted ? 'Counted: Day ' + r.day + '\\n' : '') +"
    new_wa = (
        "      (r.counted\n"
        "        ? 'Counted: Day ' + r.day + ' (new)\\n'\n"
        "        : r.alreadyCounted\n"
        "          ? 'Day ' + r.day + ' (replay \\u2014 already earned)\\n'\n"
        "          : 'Not counted\\n') +\n"
        "      'Submits today: ' + ((p.submits[tk] || 0) + 1) + ' of ' + MAX_SUBMITS_PER_DAY + '\\n' +"
    )
    content, _ = safe_replace(
        content, old_wa, new_wa,
        "WhatsApp - honest counted/replay + submits-today count",
        marker="'Submits today: ' + ((p.submits[tk] || 0) + 1)",
    )

    # ---------- 6. updateSubmitButton - practice-only guard ----------
    # Anchor on the button body (identical in both modern and legacy).
    guard_anchor = (
        "    if (count >= MAX_SUBMITS_PER_DAY) {\n"
        "      btn.disabled = true;\n"
        "      btn.innerHTML = 'Already submitted twice today';"
    )
    guard_replacement = (
        "    if (!lastResult.isTarget) {\n"
        "      btn.disabled = true;\n"
        "      btn.innerHTML = 'Practice only \\u2014 nothing to submit';\n"
        "      return;\n"
        "    }\n\n" + guard_anchor
    )
    content, _ = safe_replace(
        content, guard_anchor, guard_replacement,
        "updateSubmitButton() - practice-only guard",
        marker="'Practice only \\u2014 nothing to submit'",
    )

    # ---------- 7. updateSubmitButton - remove "N left" counter ----------
    # Multi-line variant (legacy)
    content, _ = safe_replace(
        content,
        "      btn.innerHTML = ICONS.send + 'Submit to Teacher \\u00b7 ' +\n"
        "        (MAX_SUBMITS_PER_DAY - count) + ' left';",
        "      btn.innerHTML = ICONS.send + 'Submit to Teacher';",
        "updateSubmitButton() - remove 'N left' counter (multi-line)",
        marker="btn.innerHTML = ICONS.send + 'Submit to Teacher';",
    )
    # Single-line variant (modern)
    content, _ = safe_replace(
        content,
        "      btn.innerHTML = ICONS.send + 'Submit to Teacher \\u00b7 ' + (MAX_SUBMITS_PER_DAY - count) + ' left';",
        "      btn.innerHTML = ICONS.send + 'Submit to Teacher';",
        "updateSubmitButton() - remove 'N left' counter (single line)",
        marker="btn.innerHTML = ICONS.send + 'Submit to Teacher';",
    )

    # ---------- 8. Persist lastResult on Results render ----------
    marker_persist = "localStorage.setItem('decodable_lastResult'"
    if marker_persist in content:
        print("    ~ renderResults() - persist lastResult (already applied)")
    else:
        applied = False
        for old_open in (
            "  function renderResults() {\n    var r = lastResult;\n    if (!r) return;",
            "  function renderResults() {\n    const r = lastResult;\n    if (!r) return;",
        ):
            if old_open in content:
                new_open = old_open + "\n\n    try { localStorage.setItem('decodable_lastResult', JSON.stringify(r)); } catch (e) {}"
                content = content.replace(old_open, new_open, 1)
                print("    + renderResults() - persist lastResult to localStorage")
                applied = True
                break
        if not applied:
            print("    x renderResults() - persist lastResult -- anchor not found")

    # ---------- 9. Restore lastResult on init ----------
    old_init = """  FlagsMod.init(function () {
    if (profile.name && profile.grade) {
      FlagsMod.ensureStudent(profile.name);
      renderHome();
      showScreen('homeScreen');
    } else {
      showScreen('profileScreen');
    }
  });"""
    new_init = """  FlagsMod.init(function () {
    var savedLR = null;
    try { savedLR = localStorage.getItem('decodable_lastResult'); } catch (e) {}
    if (savedLR) {
      try {
        lastResult = JSON.parse(savedLR);
        if (lastResult && typeof lastResult.date === 'string') {
          lastResult.date = new Date(lastResult.date);
        }
      } catch (e) { lastResult = null; }
    }

    if (lastResult) {
      renderResults();
      showScreen('resultsScreen');
    } else if (profile.name && profile.grade) {
      FlagsMod.ensureStudent(profile.name);
      renderHome();
      showScreen('homeScreen');
    } else {
      showScreen('profileScreen');
    }
  });"""
    content, _ = safe_replace(
        content, old_init, new_init,
        "init - restore lastResult, route to Results",
        marker="savedLR = localStorage.getItem('decodable_lastResult')",
    )

    # ---------- 10. Clear lastResult on Results exit ----------
    # modern block
    old_exit_modern = """  document.getElementById('resHomeBtn').addEventListener('click', () => { renderHome(); showScreen('homeScreen'); });
  document.getElementById('resListBtn').addEventListener('click', () => { renderHome(); showScreen('homeScreen'); });
  document.getElementById('resAgainBtn').addEventListener('click', () => {
    if (lastResult) openLesson(lastResult.lessonId);
  });"""
    new_exit_modern = """  function clearLastResult() {
    lastResult = null;
    try { localStorage.removeItem('decodable_lastResult'); } catch (e) {}
  }

  document.getElementById('resHomeBtn').addEventListener('click', () => { clearLastResult(); renderHome(); showScreen('homeScreen'); });
  document.getElementById('resListBtn').addEventListener('click', () => { clearLastResult(); renderHome(); showScreen('homeScreen'); });
  document.getElementById('resAgainBtn').addEventListener('click', () => {
    var keepId = lastResult && lastResult.lessonId;
    clearLastResult();
    if (keepId) openLesson(keepId);
  });"""

    # legacy block
    old_exit_legacy = """  on($('resHomeBtn'), 'click', function () { renderHome(); showScreen('homeScreen'); });
  on($('resListBtn'), 'click', function () { renderHome(); showScreen('homeScreen'); });
  on($('resAgainBtn'), 'click', function () {
    if (lastResult) openLesson(lastResult.lessonId);
  });"""
    new_exit_legacy = """  function clearLastResult() {
    lastResult = null;
    try { localStorage.removeItem('decodable_lastResult'); } catch (e) {}
  }

  on($('resHomeBtn'), 'click', function () { clearLastResult(); renderHome(); showScreen('homeScreen'); });
  on($('resListBtn'), 'click', function () { clearLastResult(); renderHome(); showScreen('homeScreen'); });
  on($('resAgainBtn'), 'click', function () {
    var keepId = lastResult && lastResult.lessonId;
    clearLastResult();
    if (keepId) openLesson(keepId);
  });"""

    if "function clearLastResult()" in content:
        print("    ~ Results exit - clearLastResult (already applied)")
    else:
        applied = False
        for old_b, new_b in ((old_exit_modern, new_exit_modern), (old_exit_legacy, new_exit_legacy)):
            if old_b in content:
                content = content.replace(old_b, new_b, 1)
                print("    + Results exit - clearLastResult + hooked to 3 buttons")
                applied = True
                break
        if not applied:
            print("    x Results exit - clearLastResult -- anchor not found")

    # ---------- 11. Home HTML: day banner + refresh button ----------
    old_html = (
        "        <input type=\"file\" id=\"importFile\" accept=\".json,application/json\" style=\"display:none\" />\n"
        "        <div id=\"lessonList\"></div>"
    )
    new_html = (
        "        <input type=\"file\" id=\"importFile\" accept=\".json,application/json\" style=\"display:none\" />\n"
        "        <div class=\"day-banner\" id=\"dayBanner\">\n"
        "          <span class=\"day-banner-text\" id=\"dayBannerText\">Loading\\u2026</span>\n"
        "          <button type=\"button\" class=\"refresh-btn\" id=\"refreshBtn\" aria-label=\"Refresh\">\\u21BB</button>\n"
        "        </div>\n"
        "        <div class=\"day-banner-hint\">Refresh to see latest update</div>\n"
        "        <div id=\"lessonList\"></div>"
    )
    content, _ = safe_replace(
        content, old_html, new_html,
        "Home HTML - day banner + refresh button",
        marker="id=\"dayBanner\"",
    )

    # ---------- 12. CSS: day banner + refresh button styles ----------
    css_anchor = """    @media (min-width: 600px) {
      .content-wrap { max-width: 520px; margin: 0 auto; width: 100%; }
    }"""
    css_add = """    /* ===== Day banner (Home) ===== */
    .day-banner {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 14px 16px;
      border-radius: var(--radius);
      border: 2px solid var(--border);
      background: var(--surface);
      margin-bottom: 8px;
      font-weight: 700;
      font-size: 0.9rem;
      line-height: 1.3;
    }
    .day-banner-text { flex: 1; min-width: 0; }
    .day-banner.is-open { border-color: var(--accent); background: rgba(245,158,11,0.10); }
    .day-banner.is-done { border-color: var(--success); background: rgba(22,163,74,0.08); }
    .day-banner.is-champion {
      border-color: #a855f7;
      background: linear-gradient(135deg, rgba(168,85,247,0.12), rgba(99,102,241,0.12));
    }
    .day-banner.is-waiting { border-color: var(--border); background: var(--surface-2); color: var(--text-2); }
    .refresh-btn {
      width: 44px; height: 44px; min-width: 44px;
      border-radius: 50%; border: none;
      background: var(--accent); color: #0f172a;
      font-size: 1.3rem; font-weight: 800; cursor: pointer;
      display: flex; align-items: center; justify-content: center;
      -webkit-tap-highlight-color: transparent;
    }
    .refresh-btn:active { transform: scale(0.94); }
    .day-banner.is-champion .refresh-btn { background: #a855f7; color: #fff; }
    .day-banner.is-done .refresh-btn { background: var(--success); color: #fff; }
    .day-banner-hint {
      font-size: 0.72rem; color: var(--text-3); font-weight: 600;
      margin-bottom: 14px; padding-left: 4px;
    }
""" + css_anchor
    content, _ = safe_replace(
        content, css_anchor, css_add,
        "CSS - day banner + refresh button",
        marker=".day-banner {",
    )

    # ---------- 13. renderDayBanner() function ----------
    day_banner_fn = """  function renderDayBanner() {
    var banner = document.getElementById('dayBanner');
    var text = document.getElementById('dayBannerText');
    if (!banner || !text) return;

    var lesson = null;
    for (var i = 0; i < LESSONS.length; i++) {
      if (isTargetLesson(LESSONS[i])) { lesson = LESSONS[i]; break; }
    }

    banner.className = 'day-banner';

    if (!lesson) {
      text.textContent = 'Waiting for teacher to set today\\u2019s lesson';
      banner.className = 'day-banner is-waiting';
      return;
    }

    var openDay = targetDay();
    var flags = FlagsMod.get(profile.name, lesson.id);
    var currentDayDone = flags[openDay - 1] === true;
    var allDone = FlagsMod.count(profile.name, lesson.id) === 5;

    if (allDone) {
      text.textContent = '\\uD83C\\uDFC6 All 5 days complete \\u2014 Champion!';
      banner.className = 'day-banner is-champion';
    } else if (currentDayDone) {
      text.textContent = 'Day ' + openDay + ' complete \\u2713 \\u2014 waiting for teacher';
      banner.className = 'day-banner is-done';
    } else {
      text.textContent = 'Day ' + openDay + ' is open \\u2014 read it now!';
      banner.className = 'day-banner is-open';
    }
  }

  function renderHome() {"""
    content, _ = safe_replace(
        content,
        "  function renderHome() {",
        day_banner_fn,
        "add renderDayBanner() function",
        marker="function renderDayBanner",
    )

    # ---------- 13b. Call renderDayBanner() from renderHome() ----------
    old_scroll = """    if (targetCard && !homeScrolledOnce) {
      homeScrolledOnce = true;"""
    new_scroll = """    renderDayBanner();

    if (targetCard && !homeScrolledOnce) {
      homeScrolledOnce = true;"""
    content, _ = safe_replace(
        content, old_scroll, new_scroll,
        "renderHome() - call renderDayBanner()",
        marker="    renderDayBanner();",
    )

    # ---------- 14. Refresh button wiring ----------
    refresh_init = """  (function initRefreshButton() {
    var refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', function () { location.reload(); });
    }
  })();

  FlagsMod.init(function () {"""
    content, _ = safe_replace(
        content,
        "  FlagsMod.init(function () {",
        refresh_init,
        "wiring - refresh button -> location.reload()",
        marker="initRefreshButton",
    )

    return content


def main():
    files = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_FILES
    any_changed = False
    missing = []

    for fname in files:
        p = Path(fname)
        if not p.exists():
            missing.append(fname)
            print(f"[{fname}] -- file not found, skipping")
            continue

        original = p.read_text(encoding="utf-8")
        backup = p.with_suffix(p.suffix + ".bak")
        if not backup.exists():
            backup.write_text(original, encoding="utf-8")
            print(f"\n[{fname}] backup saved to {backup.name}")

        updated = apply_changes(original, fname)

        if updated == original:
            print(f"\n[{fname}] no changes made")
        else:
            p.write_text(updated, encoding="utf-8")
            print(f"\n[{fname}] written OK")
            any_changed = True

    if missing:
        print("\nMissing files:", ", ".join(missing))
        print("Copy them next to this script, or pass full paths as arguments.")

    print("\nDone." if any_changed else "\nDone (nothing to change).")


if __name__ == "__main__":
    main()