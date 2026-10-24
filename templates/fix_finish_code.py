#!/usr/bin/env python3
"""
apply_patches.py  (complete, four files)

  P-readerT-1.html       (modern ES6, v1)
  P-readerT-2.html       (modern ES6, v2)
  P-readerT-old1.html    (legacy ES5, v1)
  P-readerT-old2.html    (legacy ES5, v2)

Writes *.patched.html — originals untouched.
"""

import sys
from pathlib import Path

MODERN_FILES = ["P-readerT-1.html", "P-readerT-2.html"]
LEGACY_FILES = ["P-readerT-old1.html", "P-readerT-old2.html"]


# ─────────────────────────────────────────────────────────────────────────────
# helpers
# ─────────────────────────────────────────────────────────────────────────────

def apply_one(html, find, replace, name):
    n = html.count(find)
    if n == 0:
        return html, False, f"{name}: FIND not found"
    if n > 1:
        return html, False, f"{name}: FIND matched {n}x (expected 1)"
    return html.replace(find, replace, 1), True, f"{name}: OK"


def apply_patches(html, patches):
    results = []
    for name, find, replace in patches:
        html, ok, msg = apply_one(html, find, replace, name)
        results.append((name, ok, msg))
        print(f"    {'✓' if ok else '✗'} {msg}")
    return html, results


# ─────────────────────────────────────────────────────────────────────────────
# MODERN (ES6) patches
# ─────────────────────────────────────────────────────────────────────────────

MODERN_PATCHES = [

("A1_header_hamburger",
"""      <button class="icon-btn" id="themeBtn" title="Toggle theme" aria-label="Toggle theme"></button>
    </div>
    <div class="content">
      <div class="content-wrap">
        <div class="student-banner">""",
"""      <button class="icon-btn" id="themeBtn" title="Toggle theme" aria-label="Toggle theme"></button>
      <div class="menu-wrap">
        <button class="icon-btn" id="dataMenuBtn" title="Data" aria-label="Data menu" aria-haspopup="true" aria-expanded="false">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
        </button>
        <div class="overflow-menu" id="dataMenu" role="menu" aria-label="Data options">
          <button class="menu-item" id="exportExcelBtn" role="menuitem">
            <span class="menu-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/></svg></span>
            <span class="menu-label">Export Excel</span>
          </button>
          <button class="menu-item" id="backupBtn" role="menuitem">
            <span class="menu-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14a9 3 0 0 0 18 0V5"/><path d="M3 12a9 3 0 0 0 18 0"/></svg></span>
            <span class="menu-label">Backup</span>
          </button>
          <button class="menu-item" id="importBtn" role="menuitem">
            <span class="menu-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg></span>
            <span class="menu-label">Import</span>
          </button>
        </div>
      </div>
    </div>
    <div class="content">
      <div class="content-wrap">
        <div class="student-banner">"""),

("A1_data_bar_remove",
"""        <div class="data-bar">
          <button class="data-btn" id="exportExcelBtn" title="Export progress to Excel (CSV)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/></svg>
            Export Excel
          </button>
          <button class="data-btn" id="backupBtn" title="Save full backup (JSON)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14a9 3 0 0 0 18 0V5"/><path d="M3 12a9 3 0 0 0 18 0"/></svg>
            Backup
          </button>
          <button class="data-btn" id="importBtn" title="Restore from a backup file">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
            Import
          </button>
          <input type="file" id="importFile" accept=".json,application/json" style="display:none" />
        </div>""",
"""        <input type="file" id="importFile" accept=".json,application/json" style="display:none" />"""),

("A1_js_data_menu_wiring",
"""    document.addEventListener('keydown', e => {
      if (!menuOpen) return;
      if (e.key === 'Escape' || e.keyCode === 27) closeOverflowMenu();
    });
  })();""",
"""    document.addEventListener('keydown', e => {
      if (!menuOpen) return;
      if (e.key === 'Escape' || e.keyCode === 27) closeOverflowMenu();
    });
  })();

  /* ========== DATA MENU WIRING (Home) ========== */
  (function initDataMenu() {
    const btn = document.getElementById('dataMenuBtn');
    const menu = document.getElementById('dataMenu');
    if (!btn || !menu) return;
    let open = false;
    function openMenu()  { open = true;  menu.classList.add('open');  btn.setAttribute('aria-expanded','true');  }
    function closeMenu() { open = false; menu.classList.remove('open'); btn.setAttribute('aria-expanded','false'); }
    btn.addEventListener('click', e => { e.stopPropagation(); open ? closeMenu() : openMenu(); });
    menu.addEventListener('click', () => closeMenu());
    document.addEventListener('click', e => {
      if (!open) return;
      const t = e.target;
      if (menu.contains(t) || btn.contains(t)) return;
      closeMenu();
    });
    document.addEventListener('keydown', e => {
      if (!open) return;
      if (e.key === 'Escape' || e.keyCode === 27) closeMenu();
    });
  })();"""),

("B1_header_speaker",
"""      <div class="menu-wrap">
        <button class="icon-btn" id="menuBtn" title="More options" aria-label="More options" aria-haspopup="true" aria-expanded="false">""",
"""      <button class="icon-btn" id="ttsBarBtn" title="Read aloud" aria-label="Read aloud">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 5 6 9H2v6h4l5 4z"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>
      </button>
      <div class="menu-wrap">
        <button class="icon-btn" id="menuBtn" title="More options" aria-label="More options" aria-haspopup="true" aria-expanded="false">"""),

("B1_js_speaker_handler",
"""  document.getElementById('ttsChunkBtn').addEventListener('click', speakCurrentChunk);
  document.getElementById('ttsSpeedBtn').addEventListener('click', toggleTtsSpeed);""",
"""  document.getElementById('ttsChunkBtn').addEventListener('click', speakCurrentChunk);
  document.getElementById('ttsSpeedBtn').addEventListener('click', toggleTtsSpeed);
  const _ttsBarBtn = document.getElementById('ttsBarBtn');
  if (_ttsBarBtn) _ttsBarBtn.addEventListener('click', speakCurrentChunk);"""),

("D2_html_modal",
"""  <div class="toast" id="toast"></div>

<script>""",
"""  <!-- Wrong-answer modal -->
  <div class="wrong-modal-overlay" id="wrongModalOverlay">
    <div class="wrong-modal">
      <div class="wrong-modal-icon">✗</div>
      <div class="wrong-modal-title">Not quite</div>
      <div class="wrong-modal-body">Reread the passage, then try again.</div>
      <button type="button" class="btn btn-danger btn-lg btn-block" id="wrongModalBtn">Back to the story</button>
    </div>
  </div>

  <div class="toast" id="toast"></div>

<script>"""),

("D2_css_modal",
"""    @media (min-width: 600px) {
      .content-wrap { max-width: 520px; margin: 0 auto; width: 100%; }
    }""",
"""    /* Wrong-answer modal */
    .wrong-modal-overlay {
      position: fixed; inset: 0; z-index: 150;
      background: rgba(15,23,42,0.55);
      display: none; align-items: center; justify-content: center; padding: 24px;
      opacity: 0; transition: opacity 0.15s ease;
    }
    .wrong-modal-overlay.show { display: flex; opacity: 1; }
    .wrong-modal {
      background: #fef2f2; border: 2px solid #fca5a5;
      border-radius: 20px; padding: 28px 22px;
      max-width: 360px; width: 100%; text-align: center;
      box-shadow: 0 20px 50px rgba(0,0,0,0.35);
      transform: scale(0.95); transition: transform 0.15s ease;
    }
    .wrong-modal-overlay.show .wrong-modal { transform: scale(1); }
    [data-theme="dark"] .wrong-modal { background: #450a0a; border-color: #7f1d1d; }
    .wrong-modal-icon { font-size: 2.5rem; font-weight: 800; line-height: 1; color: #dc2626; margin-bottom: 10px; }
    [data-theme="dark"] .wrong-modal-icon { color: #fca5a5; }
    .wrong-modal-title { font-size: 1.2rem; font-weight: 800; margin-bottom: 6px; color: #991b1b; }
    [data-theme="dark"] .wrong-modal-title { color: #fecaca; }
    .wrong-modal-body { font-size: 0.9rem; color: #7f1d1d; margin-bottom: 20px; font-weight: 600; }
    [data-theme="dark"] .wrong-modal-body { color: #fecaca; }
    .btn-danger { background: #dc2626; color: #fff; }
    .btn-danger:hover:not(:disabled) { background: #b91c1c; }

    @media (min-width: 600px) {
      .content-wrap { max-width: 520px; margin: 0 auto; width: 100%; }
    }"""),

("D2_startQuiz_resume",
"""  function startQuiz() {
    if (!allWordsTapped()) return;
    const raw = (currentLesson.questions || []).filter(q =>
      q && q.question && Array.isArray(q.options) &&
      q.options.filter(o => o && String(o).trim()).length >= 2
    );
    if (!raw.length) { toast('No questions for this lesson'); return; }
    quiz.questions = raw.map(q => {
      const opts = q.options.map(o => String(o).trim()).filter(Boolean);
      const ci = Math.min(Math.max(0, Number(q.correctIndex) || 0), opts.length - 1);
      const correctText = opts[ci];
      const shuffled = shuffle(opts.slice());
      return { question: q.question, options: shuffled, correctIndex: shuffled.indexOf(correctText) };
    });
    quiz.index = 0;
    quiz.correct = 0;
    quiz.answered = false;
    quiz.triedWrong = false;
    clearQuizTimer();
    renderQuestion();
    showScreen('questionsScreen');
  }""",
"""  function startQuiz() {
    if (!allWordsTapped()) return;

    const isResume = quiz.active
      && quiz.lessonId === currentLesson.id
      && quiz.day === currentDay
      && Array.isArray(quiz.questions) && quiz.questions.length > 0
      && quiz.attemptedCorrect;

    if (!isResume) {
      const raw = (currentLesson.questions || []).filter(q =>
        q && q.question && Array.isArray(q.options) &&
        q.options.filter(o => o && String(o).trim()).length >= 2
      );
      if (!raw.length) { toast('No questions for this lesson'); return; }
      quiz.questions = raw.map(q => {
        const opts = q.options.map(o => String(o).trim()).filter(Boolean);
        const ci = Math.min(Math.max(0, Number(q.correctIndex) || 0), opts.length - 1);
        const correctText = opts[ci];
        const shuffled = shuffle(opts.slice());
        return { question: q.question, options: shuffled, correctIndex: shuffled.indexOf(correctText) };
      });
      quiz.index = 0;
      quiz.correct = 0;
      quiz.answered = false;
      quiz.attemptedCorrect = new Set();
      quiz.wrongQIndices = new Set();
      quiz.active = true;
      quiz.lessonId = currentLesson.id;
      quiz.day = currentDay;
    } else {
      let firstUnanswered = 0;
      while (firstUnanswered < quiz.questions.length && quiz.attemptedCorrect.has(firstUnanswered)) {
        firstUnanswered++;
      }
      quiz.index = firstUnanswered;
      quiz.answered = false;
      if (quiz.index >= quiz.questions.length) {
        finishQuiz();
        return;
      }
    }
    clearQuizTimer();
    renderQuestion();
    showScreen('questionsScreen');
  }"""),

("D2_onAnswer_rewrite",
"""  function onAnswer(chosen, btn) {
    if (quiz.answered) return;
    const q = quiz.questions[quiz.index];
    const correct = chosen === q.correctIndex;
    quiz.answered = true;

    const opts = document.querySelectorAll('#qOptions .q-opt');
    opts.forEach((el, i) => {
      el.disabled = true;
      if (i === q.correctIndex) el.classList.add('correct');
      if (i === chosen && !correct) el.classList.add('wrong');
    });

    const fb = document.getElementById('qFeedback');
    if (correct) {
      if (!quiz.triedWrong) quiz.correct++;
      fb.textContent = '✓ Correct!';
      fb.className = 'feedback-banner show ok';
      clearQuizTimer();
      quizTimer = setTimeout(() => { quizTimer = null; advanceQuiz(); }, 1000);
    } else {
      quiz.triedWrong = true;
      fb.textContent = '✗ Try again';
      fb.className = 'feedback-banner show bad';
      clearQuizTimer();
      quizTimer = setTimeout(() => {
        quizTimer = null;
        const currentOpts = document.querySelectorAll('#qOptions .q-opt');
        currentOpts.forEach(el => { el.disabled = false; el.classList.remove('wrong', 'correct'); });
        fb.className = 'feedback-banner';
        quiz.answered = false;
      }, 1400);
    }
  }""",
"""  function onAnswer(chosen, btn) {
    if (quiz.answered) return;
    const q = quiz.questions[quiz.index];
    const correct = chosen === q.correctIndex;
    quiz.answered = true;

    const opts = document.querySelectorAll('#qOptions .q-opt');
    opts.forEach(el => { el.disabled = true; });

    const fb = document.getElementById('qFeedback');

    if (correct) {
      if (opts[chosen]) opts[chosen].classList.add('correct');
      quiz.correct++;
      quiz.attemptedCorrect.add(quiz.index);
      fb.textContent = '✓ Correct!';
      fb.className = 'feedback-banner show ok';
      clearQuizTimer();
      quizTimer = setTimeout(() => { quizTimer = null; advanceQuiz(); }, 900);
    } else {
      quiz.wrongQIndices.add(quiz.index);
      if (opts[chosen]) opts[chosen].classList.add('wrong');
      clearQuizTimer();
      quizTimer = setTimeout(() => {
        quizTimer = null;
        showWrongModal();
      }, 600);
    }
  }

  function showWrongModal() {
    const overlay = document.getElementById('wrongModalOverlay');
    if (overlay) overlay.classList.add('show');
  }

  function hideWrongModal() {
    const overlay = document.getElementById('wrongModalOverlay');
    if (overlay) overlay.classList.remove('show');
  }

  function exitWrongModalToStory() {
    hideWrongModal();
    renderReading();
    showScreen('readingScreen');
  }"""),

("D2_wrongModal_wiring",
"""  document.getElementById('qToStoryBtn').addEventListener('click', () => {
    clearQuizTimer(); renderReading(); showScreen('readingScreen');
  });""",
"""  document.getElementById('qToStoryBtn').addEventListener('click', () => {
    clearQuizTimer(); renderReading(); showScreen('readingScreen');
  });

  const _wrongModalBtn = document.getElementById('wrongModalBtn');
  if (_wrongModalBtn) _wrongModalBtn.addEventListener('click', exitWrongModalToStory);"""),

("D1_D4_finishQuiz",
"""  function finishQuiz() {
    clearQuizTimer();
    const total = quiz.questions.length;
    const score = quiz.correct;
    const pct = total ? Math.round((score / total) * 100) : 0;
    const passed = pct >= PASS_PCT;

    const p = getProg(currentLesson.id);
    const prev = p.bestScores[currentDay] || 0;
    if (score > prev) p.bestScores[currentDay] = score;

    if (passed && currentDay > p.highestDay) p.highestDay = currentDay;

    p.currentTapped = [];
    p.readingDone = false;
    saveStore();""",
"""  function finishQuiz() {
    clearQuizTimer();
    const total = quiz.questions.length;
    const wrongs = quiz.wrongQIndices ? quiz.wrongQIndices.size : 0;
    const score = Math.max(0, total - wrongs);
    const pct = total ? Math.round((score / total) * 100) : 0;
    const passed = wrongs <= 1;

    const p = getProg(currentLesson.id);
    const prev = p.bestScores[currentDay] || 0;
    if (score > prev) p.bestScores[currentDay] = score;

    if (passed && currentDay > p.highestDay) p.highestDay = currentDay;

    p.currentTapped = [];
    p.readingDone = false;
    quiz.active = false;
    saveStore();"""),

("D4_soundhunt_pass_only",
"""    if (hasSoundHuntData(currentLesson)) {
      startSoundHunt();
      showScreen('soundHuntScreen');
    } else {
      renderResults();
      showScreen('resultsScreen');
    }""",
"""    if (passed && hasSoundHuntData(currentLesson)) {
      startSoundHunt();
      showScreen('soundHuntScreen');
    } else {
      renderResults();
      showScreen('resultsScreen');
    }"""),

("C_results_html",
"""  <!-- RESULTS -->
  <div id="resultsScreen" class="screen">
    <div class="app-header">
      <button class="icon-btn" id="resHomeBtn" title="Home" aria-label="Home">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/></svg>
      </button>
      <h1>Results</h1>
      <button class="icon-btn" id="themeBtn4" title="Toggle theme" aria-label="Toggle theme"></button>
    </div>
    <div class="content">
      <div class="content-wrap">
        <div class="result-badge" id="resultBadge">
          <div class="badge-title">Decodable Reader · Daily Result</div>
          <div class="score-big" id="resScore">0/0</div>
          <div class="day-announce" id="resDayAnnounce">Day 1 Completed</div>
          <div class="details">
            <div class="row"><span class="label">Name</span><span class="val" id="resName">—</span></div>
            <div class="row"><span class="label">Grade</span><span class="val" id="resGrade">—</span></div>
            <div class="row"><span class="label">Lesson</span><span class="val" id="resLesson">—</span></div>
            <div class="row"><span class="label">Target Sound</span><span class="val" id="resSound">—</span></div>
            <div class="row" id="resShRow" style="display:none"><span class="label">Sound Hunt</span><span class="val" id="resShVal">—</span></div>
            <div class="row"><span class="label">Date</span><span class="val" id="resDate">—</span></div>
            <div class="row"><span class="label">Status</span><span class="val" id="resStatus">—</span></div>
          </div>
          <div class="day-row" id="resDayPills"></div>
          <div class="finish-code-box" id="resFinishCodeBox" style="display:none;">
            <div class="finish-code-label">Completion code</div>
            <div class="finish-code-value" id="resFinishCode" title="Tap to copy">—</div>
            <div class="finish-code-meta" id="resFinishCodeMeta"></div>
          </div>
          <div class="champ" id="resChamp">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0z"/></svg>
            All 5 Days Completed — Champion!
          </div>
        </div>
        <div class="result-actions">
          <button class="btn btn-wa btn-lg btn-block" id="submitWaBtn"></button>
          <p class="submit-note" id="submitNote">Shares badge image, then opens teacher chat (works without saved contact)</p>
          <button class="btn btn-outline btn-block" id="resAgainBtn">Read again</button>
          <button class="btn btn-primary btn-block" id="resListBtn">Back to Lessons</button>
        </div>
      </div>
    </div>
  </div>""",
"""  <!-- RESULTS -->
  <div id="resultsScreen" class="screen">
    <div class="app-header">
      <button class="icon-btn" id="resHomeBtn" title="Home" aria-label="Home">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/></svg>
      </button>
      <h1>Result</h1>
      <button class="icon-btn" id="themeBtn4" title="Toggle theme" aria-label="Toggle theme"></button>
    </div>
    <div class="content">
      <div class="content-wrap">
        <div class="result-badge" id="resultBadge">
          <div class="score-big" id="resScore">0/0</div>
          <div class="res-subtitle" id="resSubtitle">—</div>
          <div class="day-row" id="resDayPills"></div>
          <div class="champ" id="resChamp">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0z"/></svg>
            All 5 Days — Champion!
          </div>
          <div class="res-meta">
            <div class="res-meta-line" id="resLine1">—</div>
            <div class="res-meta-line" id="resLine2">—</div>
            <div class="res-meta-line muted" id="resLine3">—</div>
            <div class="res-meta-line muted" id="resLine4" style="display:none;">—</div>
          </div>
          <div class="finish-code-box" id="resFinishCodeBox" style="display:none;">
            <div class="finish-code-label">Completion code</div>
            <div class="finish-code-value" id="resFinishCode" title="Tap to copy">—</div>
          </div>
        </div>
      </div>
    </div>
    <div class="bottom-bar results-bottom-bar">
      <button class="btn btn-wa btn-lg btn-block" id="submitWaBtn"></button>
      <div class="results-secondary-row">
        <button class="btn btn-outline" id="resAgainBtn">Read again</button>
        <button class="btn btn-primary" id="resListBtn">Lessons</button>
      </div>
    </div>
  </div>"""),

("C_css_finish_screen",
"""    @media (min-width: 600px) {
      .content-wrap { max-width: 520px; margin: 0 auto; width: 100%; }
    }""",
"""    .res-subtitle {
      font-size: 0.72rem; font-weight: 800; letter-spacing: 0.06em;
      text-transform: uppercase; margin-bottom: 12px;
    }
    .res-subtitle.pass { color: var(--success); }
    .res-subtitle.fail { color: var(--danger); }
    .res-meta {
      text-align: left; margin-top: 12px; padding-top: 12px;
      border-top: 1px dashed var(--border);
    }
    .res-meta-line {
      font-size: 0.85rem; font-weight: 600; padding: 2px 0; line-height: 1.35;
    }
    .res-meta-line.muted { color: var(--text-3); font-weight: 500; font-size: 0.8rem; }
    .results-bottom-bar { flex-direction: column; gap: 8px; }
    .results-secondary-row { display: flex; gap: 8px; width: 100%; }
    .results-secondary-row .btn { flex: 1; padding: 12px 16px; font-size: 0.9rem; }

    @media (min-width: 600px) {
      .content-wrap { max-width: 520px; margin: 0 auto; width: 100%; }
    }"""),

("C_css_tighten_badge",
"""      max-width: 400px; margin: 0 auto 20px;
    }
    .result-badge .badge-title""",
"""      max-width: 400px; margin: 0 auto;
    }
    .result-badge .badge-title"""),

("C_renderResults_rewrite",
"""  function renderResults() {
    const r = lastResult;
    if (!r) return;

    const scoreEl = document.getElementById('resScore');
    scoreEl.textContent = r.score + '/' + r.total;
    scoreEl.className = 'score-big ' + (r.passed ? 'pass' : 'fail');

    const ann = document.getElementById('resDayAnnounce');
    ann.textContent = r.passed
      ? 'Day ' + r.day + ' Completed!'
      : 'Day ' + r.day + ' — Keep practicing';
    ann.style.background = DAY_HEX[r.day];
    ann.style.color = DAY_TEXT[r.day];

    document.getElementById('resName').textContent = profile.name;
    document.getElementById('resGrade').textContent = profile.grade;
    document.getElementById('resLesson').textContent = r.lessonNumber + ' – ' + r.title;
    document.getElementById('resSound').textContent = r.targetSound;
    document.getElementById('resDate').textContent = formatDate(r.date);
    document.getElementById('resStatus').textContent = r.passed
      ? 'Day ' + r.day + ' Completed ✓'
      : 'Score below 80% — try again';

    const shRow = document.getElementById('resShRow');
    const shVal = document.getElementById('resShVal');
    if (typeof r.soundHuntAttempts === 'number') {
      shRow.style.display = 'flex';
      shVal.textContent = r.soundHuntAttempts === 1
        ? '✓ First try'
        : '✓ After ' + r.soundHuntAttempts + ' tries';
    } else {
      shRow.style.display = 'none';
    }

    const pills = document.getElementById('resDayPills');
    pills.innerHTML = '';
    for (let d = 1; d <= 5; d++) {
      const s = document.createElement('span');
      s.className = 'dp' + (d <= r.highestDay ? ' done d' + d : '');
      if (d <= r.highestDay) {
        s.style.background = DAY_HEX[d];
        s.style.color = DAY_TEXT[d];
      }
      s.textContent = d;
      pills.appendChild(s);
    }

    const champ = document.getElementById('resChamp');
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

    updateSubmitButton();
  }""",
"""  function renderResults() {
    const r = lastResult;
    if (!r) return;

    const scoreEl = document.getElementById('resScore');
    scoreEl.textContent = r.score + '/' + r.total;
    scoreEl.className = 'score-big ' + (r.passed ? 'pass' : 'fail');

    const subEl = document.getElementById('resSubtitle');
    if (subEl) {
      subEl.textContent = r.passed
        ? '✓ Day ' + r.day + ' · Passed'
        : '✗ Day ' + r.day + ' · Keep practicing';
      subEl.className = 'res-subtitle ' + (r.passed ? 'pass' : 'fail');
    }

    document.getElementById('resLine1').textContent =
      profile.name + ' · Grade ' + profile.grade + ' · ' + formatDate(r.date);
    document.getElementById('resLine2').textContent =
      'Lesson ' + r.lessonNumber + ' — ' + r.title;
    document.getElementById('resLine3').textContent = r.targetSound;

    const line4 = document.getElementById('resLine4');
    if (typeof r.soundHuntAttempts === 'number') {
      line4.style.display = '';
      line4.textContent = '🎯 Sound Hunt · ' +
        (r.soundHuntAttempts === 1 ? 'First try' : r.soundHuntAttempts + ' tries');
    } else {
      line4.style.display = 'none';
    }

    const pills = document.getElementById('resDayPills');
    pills.innerHTML = '';
    for (let d = 1; d <= 5; d++) {
      const s = document.createElement('span');
      s.className = 'dp' + (d <= r.highestDay ? ' done d' + d : '');
      if (d <= r.highestDay) {
        s.style.background = DAY_HEX[d];
        s.style.color = DAY_TEXT[d];
      }
      s.textContent = d;
      pills.appendChild(s);
    }

    const champ = document.getElementById('resChamp');
    if (r.highestDay >= 5) champ.classList.add('show');
    else champ.classList.remove('show');

    const fcBox = document.getElementById('resFinishCodeBox');
    const fcVal = document.getElementById('resFinishCode');
    if (fcBox && fcVal) {
      const code = String(FINISH_CODE || '').replace(/^\\s+|\\s+$/g, '');
      if (code) {
        fcBox.style.display = '';
        fcVal.textContent = code;
        fcBox.onclick = copyFinishCode;
      } else {
        fcBox.style.display = 'none';
      }
    }

    updateSubmitButton();
  }"""),

("C_updateSubmitButton",
"""  function updateSubmitButton() {
    if (!lastResult) return;
    const p = getProg(lastResult.lessonId);
    const tk = todayKey();
    const count = p.submits[tk] || 0;
    const btn = document.getElementById('submitWaBtn');
    const note = document.getElementById('submitNote');
    if (count >= MAX_SUBMITS_PER_DAY) {
      btn.disabled = true;
      btn.innerHTML = 'Already submitted twice today';
      note.textContent = 'You can submit again tomorrow';
    } else {
      btn.disabled = false;
      btn.innerHTML = ICONS.send + 'Submit to Teacher';
      note.textContent = 'Shares badge image, then opens teacher chat (works without saved contact) · ' + (MAX_SUBMITS_PER_DAY - count) + ' left today';
    }
  }""",
"""  function updateSubmitButton() {
    if (!lastResult) return;
    const p = getProg(lastResult.lessonId);
    const tk = todayKey();
    const count = p.submits[tk] || 0;
    const btn = document.getElementById('submitWaBtn');
    if (count >= MAX_SUBMITS_PER_DAY) {
      btn.disabled = true;
      btn.innerHTML = 'Already submitted twice today';
    } else {
      btn.disabled = false;
      btn.innerHTML = ICONS.send + 'Submit to Teacher · ' + (MAX_SUBMITS_PER_DAY - count) + ' left';
    }
  }"""),
]


# ─────────────────────────────────────────────────────────────────────────────
# LEGACY (ES5) patches
# ─────────────────────────────────────────────────────────────────────────────

LEGACY_PATCHES = [

("A1_header_hamburger",
"""      <button type="button" class="icon-btn" id="themeBtn" title="Toggle theme" aria-label="Toggle theme"></button>
    </div>
    <div class="content">
      <div class="content-wrap">
        <div class="student-banner">""",
"""      <button type="button" class="icon-btn" id="themeBtn" title="Toggle theme" aria-label="Toggle theme"></button>
      <div class="menu-wrap">
        <button type="button" class="icon-btn" id="dataMenuBtn" title="Data" aria-label="Data menu" aria-haspopup="true" aria-expanded="false">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
        </button>
        <div class="overflow-menu" id="dataMenu" role="menu" aria-label="Data options">
          <button type="button" class="menu-item" id="exportExcelBtn" role="menuitem">
            <span class="menu-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/></svg></span>
            <span class="menu-label">Export Excel</span>
          </button>
          <button type="button" class="menu-item" id="backupBtn" role="menuitem">
            <span class="menu-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14a9 3 0 0 0 18 0V5"/><path d="M3 12a9 3 0 0 0 18 0"/></svg></span>
            <span class="menu-label">Backup</span>
          </button>
          <button type="button" class="menu-item" id="importBtn" role="menuitem">
            <span class="menu-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg></span>
            <span class="menu-label">Import</span>
          </button>
        </div>
      </div>
    </div>
    <div class="content">
      <div class="content-wrap">
        <div class="student-banner">"""),

("A1_data_bar_remove",
"""        <div class="data-bar">
          <button type="button" class="data-btn" id="exportExcelBtn" title="Export progress to Excel (CSV)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/></svg>
            <span>Export Excel</span>
          </button>
          <button type="button" class="data-btn" id="backupBtn" title="Save full backup (JSON)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14a9 3 0 0 0 18 0V5"/><path d="M3 12a9 3 0 0 0 18 0"/></svg>
            <span>Backup</span>
          </button>
          <button type="button" class="data-btn" id="importBtn" title="Restore from a backup file">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
            <span>Import</span>
          </button>
          <input type="file" id="importFile" accept=".json,application/json" style="display:none" />
        </div>""",
"""        <input type="file" id="importFile" accept=".json,application/json" style="display:none" />"""),

("A1_js_data_menu_wiring",
"""    on(document, 'keydown', function (e) {
      if (!menuOpen) return;
      e = e || window.event;
      var k = e.key || '';
      if (k === 'Escape' || e.keyCode === 27) closeOverflowMenu();
    });
  })();""",
"""    on(document, 'keydown', function (e) {
      if (!menuOpen) return;
      e = e || window.event;
      var k = e.key || '';
      if (k === 'Escape' || e.keyCode === 27) closeOverflowMenu();
    });
  })();

  /* DATA MENU (Home) */
  (function initDataMenu() {
    var btn = $('dataMenuBtn');
    var menu = $('dataMenu');
    if (!btn || !menu) return;
    var open = false;
    function openMenu()  { open = true;  addClass(menu, 'open');  btn.setAttribute('aria-expanded', 'true');  }
    function closeMenu() { open = false; removeClass(menu, 'open'); btn.setAttribute('aria-expanded', 'false'); }
    on(btn, 'click', function (e) { stopEvent(e); if (open) closeMenu(); else openMenu(); });
    on(menu, 'click', function () { closeMenu(); });
    on(document, 'click', function (e) {
      if (!open) return;
      var t = evTarget(e);
      if (nodeContains(menu, t) || nodeContains(btn, t)) return;
      closeMenu();
    });
    on(document, 'keydown', function (e) {
      if (!open) return;
      e = e || window.event;
      var k = e.key || '';
      if (k === 'Escape' || e.keyCode === 27) closeMenu();
    });
  })();"""),

("B1_header_speaker",
"""      <div class="menu-wrap">
        <button type="button" class="icon-btn" id="menuBtn" title="More options" aria-label="More options" aria-haspopup="true" aria-expanded="false">""",
"""      <button type="button" class="icon-btn" id="ttsBarBtn" title="Read aloud" aria-label="Read aloud">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 5 6 9H2v6h4l5 4z"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>
      </button>
      <div class="menu-wrap">
        <button type="button" class="icon-btn" id="menuBtn" title="More options" aria-label="More options" aria-haspopup="true" aria-expanded="false">"""),

("B1_js_speaker_handler",
"""  on($('ttsChunkBtn'), 'click', speakCurrentChunk);
  on($('ttsSpeedBtn'), 'click', toggleTtsSpeed);""",
"""  on($('ttsChunkBtn'), 'click', speakCurrentChunk);
  on($('ttsSpeedBtn'), 'click', toggleTtsSpeed);
  on($('ttsBarBtn'), 'click', speakCurrentChunk);"""),

("D2_html_modal",
"""  <div class="toast" id="toast"></div>

<script type="text/javascript">""",
"""  <!-- Wrong-answer modal -->
  <div class="wrong-modal-overlay" id="wrongModalOverlay">
    <div class="wrong-modal">
      <div class="wrong-modal-icon">✗</div>
      <div class="wrong-modal-title">Not quite</div>
      <div class="wrong-modal-body">Reread the passage, then try again.</div>
      <button type="button" class="btn btn-danger btn-lg btn-block" id="wrongModalBtn">Back to the story</button>
    </div>
  </div>

  <div class="toast" id="toast"></div>

<script type="text/javascript">"""),

("D2_css_modal",
"""    @media (min-width: 600px) {
      .content-wrap { max-width: 520px; margin: 0 auto; width: 100%; }
    }

    /* ------------------------------------------------------------------""",
"""    /* Wrong-answer modal (legacy) */
    .wrong-modal-overlay {
      position: fixed; top: 0; right: 0; bottom: 0; left: 0; z-index: 150;
      background: rgba(15,23,42,0.55);
      display: none; align-items: center; justify-content: center; padding: 24px;
      opacity: 0;
      -webkit-transition: opacity 0.15s ease;
      transition: opacity 0.15s ease;
    }
    .wrong-modal-overlay.show { display: -webkit-box; display: -webkit-flex; display: -ms-flexbox; display: flex; opacity: 1; }
    .wrong-modal {
      background: #fef2f2; border: 2px solid #fca5a5;
      border-radius: 20px; padding: 28px 22px;
      max-width: 360px; width: 100%; text-align: center;
      box-shadow: 0 20px 50px rgba(0,0,0,0.35);
      -webkit-transform: scale(0.95); -ms-transform: scale(0.95); transform: scale(0.95);
      -webkit-transition: -webkit-transform 0.15s ease;
      transition: transform 0.15s ease;
    }
    .wrong-modal-overlay.show .wrong-modal {
      -webkit-transform: scale(1); -ms-transform: scale(1); transform: scale(1);
    }
    [data-theme="dark"] .wrong-modal { background: #450a0a; border-color: #7f1d1d; }
    .wrong-modal-icon { font-size: 2.5rem; font-weight: 800; line-height: 1; color: #dc2626; margin-bottom: 10px; }
    [data-theme="dark"] .wrong-modal-icon { color: #fca5a5; }
    .wrong-modal-title { font-size: 1.2rem; font-weight: 800; margin-bottom: 6px; color: #991b1b; }
    [data-theme="dark"] .wrong-modal-title { color: #fecaca; }
    .wrong-modal-body { font-size: 0.9rem; color: #7f1d1d; margin-bottom: 20px; font-weight: 600; }
    [data-theme="dark"] .wrong-modal-body { color: #fecaca; }
    .btn-danger { background: #dc2626; color: #fff; }
    .btn-danger:hover:not(:disabled) { background: #b91c1c; }

    @media (min-width: 600px) {
      .content-wrap { max-width: 520px; margin: 0 auto; width: 100%; }
    }

    /* ------------------------------------------------------------------"""),

("D2_startQuiz_resume",
"""  function startQuiz() {
    if (!allWordsTapped()) return;

    var raw = (currentLesson.questions || []).filter(function (q) {
      if (!q || !q.question || !Array.isArray(q.options)) return false;
      var good = 0;
      for (var i = 0; i < q.options.length; i++) {
        if (q.options[i] && String(q.options[i]).replace(/^\\s+|\\s+$/g, '')) good++;
      }
      return good >= 2;
    });

    if (!raw.length) {
      toast('No questions for this lesson');
      return;
    }

    quiz.questions = raw.map(function (q) {
      var opts = [];
      for (var i = 0; i < q.options.length; i++) {
        var t = String(q.options[i]).replace(/^\\s+|\\s+$/g, '');
        if (t) opts.push(t);
      }
      var ci = Math.min(Math.max(0, Number(q.correctIndex) || 0), opts.length - 1);
      var correctText = opts[ci];
      var shuffled = shuffle(opts.slice());
      return {
        question: q.question,
        options: shuffled,
        correctIndex: shuffled.indexOf(correctText)
      };
    });

    quiz.index = 0;
    quiz.correct = 0;
    quiz.answered = false;
    quiz.triedWrong = false;
    clearQuizTimer();
    renderQuestion();
    showScreen('questionsScreen');
  }""",
"""  function startQuiz() {
    if (!allWordsTapped()) return;

    var isResume = quiz.active
      && quiz.lessonId === currentLesson.id
      && quiz.day === currentDay
      && Array.isArray(quiz.questions) && quiz.questions.length > 0
      && quiz.attemptedCorrect;

    if (!isResume) {
      var raw = (currentLesson.questions || []).filter(function (q) {
        if (!q || !q.question || !Array.isArray(q.options)) return false;
        var good = 0;
        for (var i = 0; i < q.options.length; i++) {
          if (q.options[i] && String(q.options[i]).replace(/^\\s+|\\s+$/g, '')) good++;
        }
        return good >= 2;
      });

      if (!raw.length) {
        toast('No questions for this lesson');
        return;
      }

      quiz.questions = raw.map(function (q) {
        var opts = [];
        for (var i = 0; i < q.options.length; i++) {
          var t = String(q.options[i]).replace(/^\\s+|\\s+$/g, '');
          if (t) opts.push(t);
        }
        var ci = Math.min(Math.max(0, Number(q.correctIndex) || 0), opts.length - 1);
        var correctText = opts[ci];
        var shuffled = shuffle(opts.slice());
        return {
          question: q.question,
          options: shuffled,
          correctIndex: shuffled.indexOf(correctText)
        };
      });

      quiz.index = 0;
      quiz.correct = 0;
      quiz.answered = false;
      quiz.attemptedCorrect = {};
      quiz.wrongQIndices = {};
      quiz.active = true;
      quiz.lessonId = currentLesson.id;
      quiz.day = currentDay;
    } else {
      var firstUnanswered = 0;
      while (firstUnanswered < quiz.questions.length && quiz.attemptedCorrect[firstUnanswered]) {
        firstUnanswered++;
      }
      quiz.index = firstUnanswered;
      quiz.answered = false;
      if (quiz.index >= quiz.questions.length) {
        finishQuiz();
        return;
      }
    }
    clearQuizTimer();
    renderQuestion();
    showScreen('questionsScreen');
  }"""),

("D2_onAnswer_rewrite",
"""  function onAnswer(chosen, btn) {
    if (quiz.answered) return;
    var q = quiz.questions[quiz.index];
    var correct = chosen === q.correctIndex;
    quiz.answered = true;

    var opts = document.querySelectorAll('#qOptions .q-opt');
    for (var i = 0; i < opts.length; i++) {
      var el = opts[i];
      el.disabled = true;
      if (i === q.correctIndex) addClass(el, 'correct');
      if (i === chosen && !correct) addClass(el, 'wrong');
    }

    var fb = $('qFeedback');
    if (correct) {
      if (!quiz.triedWrong) quiz.correct++;
      fb.textContent = '✓ Correct!';
      fb.className = 'feedback-banner show ok';
      clearQuizTimer();
      quizTimer = setTimeout(function () {
        quizTimer = null;
        advanceQuiz();
      }, 1000);
    } else {
      quiz.triedWrong = true;
      fb.textContent = '✗ Try again';
      fb.className = 'feedback-banner show bad';
      clearQuizTimer();
      quizTimer = setTimeout(function () {
        quizTimer = null;
        var currentOpts = document.querySelectorAll('#qOptions .q-opt');
        for (var k = 0; k < currentOpts.length; k++) {
          currentOpts[k].disabled = false;
          removeClass(currentOpts[k], 'wrong');
          removeClass(currentOpts[k], 'correct');
        }
        fb.className = 'feedback-banner';
        quiz.answered = false;
      }, 1400);
    }
  }""",
"""  function onAnswer(chosen, btn) {
    if (quiz.answered) return;
    var q = quiz.questions[quiz.index];
    var correct = chosen === q.correctIndex;
    quiz.answered = true;

    var opts = document.querySelectorAll('#qOptions .q-opt');
    for (var i = 0; i < opts.length; i++) {
      opts[i].disabled = true;
    }

    var fb = $('qFeedback');

    if (correct) {
      if (opts[chosen]) addClass(opts[chosen], 'correct');
      quiz.correct++;
      quiz.attemptedCorrect[quiz.index] = true;
      fb.textContent = '✓ Correct!';
      fb.className = 'feedback-banner show ok';
      clearQuizTimer();
      quizTimer = setTimeout(function () {
        quizTimer = null;
        advanceQuiz();
      }, 900);
    } else {
      quiz.wrongQIndices[quiz.index] = true;
      if (opts[chosen]) addClass(opts[chosen], 'wrong');
      clearQuizTimer();
      quizTimer = setTimeout(function () {
        quizTimer = null;
        showWrongModal();
      }, 600);
    }
  }

  function showWrongModal() { addClass($('wrongModalOverlay'), 'show'); }
  function hideWrongModal() { removeClass($('wrongModalOverlay'), 'show'); }
  function exitWrongModalToStory() {
    hideWrongModal();
    renderReading();
    showScreen('readingScreen');
  }"""),

("D2_wrongModal_wiring",
"""  on($('qToStoryBtn'), 'click', function () {
    clearQuizTimer();
    renderReading();
    showScreen('readingScreen');
  });""",
"""  on($('qToStoryBtn'), 'click', function () {
    clearQuizTimer();
    renderReading();
    showScreen('readingScreen');
  });

  on($('wrongModalBtn'), 'click', exitWrongModalToStory);"""),

("D1_D4_finishQuiz",
"""  function finishQuiz() {
    clearQuizTimer();
    var total = quiz.questions.length;
    var score = quiz.correct;
    var pct = total ? Math.round((score / total) * 100) : 0;
    var passed = pct >= PASS_PCT;

    var p = getProg(currentLesson.id);
    var prev = p.bestScores[currentDay] || 0;
    if (score > prev) p.bestScores[currentDay] = score;

    if (passed && currentDay > p.highestDay) p.highestDay = currentDay;

    p.currentTapped = [];
    p.readingDone = false;
    saveStore();""",
"""  function finishQuiz() {
    clearQuizTimer();
    var total = quiz.questions.length;
    var wrongs = 0;
    if (quiz.wrongQIndices) {
      for (var wk in quiz.wrongQIndices) {
        if (Object.prototype.hasOwnProperty.call(quiz.wrongQIndices, wk)) wrongs++;
      }
    }
    var score = Math.max(0, total - wrongs);
    var pct = total ? Math.round((score / total) * 100) : 0;
    var passed = wrongs <= 1;

    var p = getProg(currentLesson.id);
    var prev = p.bestScores[currentDay] || 0;
    if (score > prev) p.bestScores[currentDay] = score;

    if (passed && currentDay > p.highestDay) p.highestDay = currentDay;

    p.currentTapped = [];
    p.readingDone = false;
    quiz.active = false;
    saveStore();"""),

("D4_soundhunt_pass_only",
"""    if (hasSoundHuntData(currentLesson)) {
      startSoundHunt();
      showScreen('soundHuntScreen');
    } else {
      renderResults();
      showScreen('resultsScreen');
    }""",
"""    if (passed && hasSoundHuntData(currentLesson)) {
      startSoundHunt();
      showScreen('soundHuntScreen');
    } else {
      renderResults();
      showScreen('resultsScreen');
    }"""),

("C_results_html",
"""  <!-- RESULTS -->
  <div id="resultsScreen" class="screen">
    <div class="app-header">
      <button type="button" class="icon-btn" id="resHomeBtn" title="Home" aria-label="Home">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/></svg>
      </button>
      <h1>Results</h1>
      <button type="button" class="icon-btn" id="themeBtn4" title="Toggle theme" aria-label="Toggle theme"></button>
    </div>
    <div class="content">
      <div class="content-wrap">
        <div class="result-badge" id="resultBadge">
          <div class="badge-title">Decodable Reader · Daily Result</div>
          <div class="score-big" id="resScore">0/0</div>
          <div class="day-announce" id="resDayAnnounce">Day 1 Completed</div>
          <div class="details">
            <div class="row"><span class="label">Name</span><span class="val" id="resName">—</span></div>
            <div class="row"><span class="label">Grade</span><span class="val" id="resGrade">—</span></div>
            <div class="row"><span class="label">Lesson</span><span class="val" id="resLesson">—</span></div>
            <div class="row"><span class="label">Target Sound</span><span class="val" id="resSound">—</span></div>
            <div class="row" id="resShRow" style="display:none"><span class="label">Sound Hunt</span><span class="val" id="resShVal">—</span></div>
            <div class="row"><span class="label">Date</span><span class="val" id="resDate">—</span></div>
            <div class="row"><span class="label">Status</span><span class="val" id="resStatus">—</span></div>
          </div>
          <div class="day-row" id="resDayPills"></div>
          <div class="finish-code-box" id="resFinishCodeBox" style="display:none;">
            <div class="finish-code-label">Completion code</div>
            <div class="finish-code-value" id="resFinishCode" title="Tap to copy">—</div>
            <div class="finish-code-meta" id="resFinishCodeMeta"></div>
          </div>
          <div class="champ" id="resChamp">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0z"/></svg>
            All 5 Days Completed — Champion!
          </div>
        </div>
        <div class="result-actions">
          <button type="button" class="btn btn-wa btn-lg btn-block" id="submitWaBtn"></button>
          <p class="submit-note" id="submitNote">Shares badge image, then opens teacher chat (works without saved contact)</p>
          <button type="button" class="btn btn-outline btn-block" id="resAgainBtn">Read again</button>
          <button type="button" class="btn btn-primary btn-block" id="resListBtn">Back to Lessons</button>
        </div>
      </div>
    </div>
  </div>""",
"""  <!-- RESULTS -->
  <div id="resultsScreen" class="screen">
    <div class="app-header">
      <button type="button" class="icon-btn" id="resHomeBtn" title="Home" aria-label="Home">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/></svg>
      </button>
      <h1>Result</h1>
      <button type="button" class="icon-btn" id="themeBtn4" title="Toggle theme" aria-label="Toggle theme"></button>
    </div>
    <div class="content">
      <div class="content-wrap">
        <div class="result-badge" id="resultBadge">
          <div class="score-big" id="resScore">0/0</div>
          <div class="res-subtitle" id="resSubtitle">—</div>
          <div class="day-row" id="resDayPills"></div>
          <div class="champ" id="resChamp">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0z"/></svg>
            All 5 Days — Champion!
          </div>
          <div class="res-meta">
            <div class="res-meta-line" id="resLine1">—</div>
            <div class="res-meta-line" id="resLine2">—</div>
            <div class="res-meta-line muted" id="resLine3">—</div>
            <div class="res-meta-line muted" id="resLine4" style="display:none;">—</div>
          </div>
          <div class="finish-code-box" id="resFinishCodeBox" style="display:none;">
            <div class="finish-code-label">Completion code</div>
            <div class="finish-code-value" id="resFinishCode" title="Tap to copy">—</div>
          </div>
        </div>
      </div>
    </div>
    <div class="bottom-bar results-bottom-bar">
      <button type="button" class="btn btn-wa btn-lg btn-block" id="submitWaBtn"></button>
      <div class="results-secondary-row">
        <button type="button" class="btn btn-outline" id="resAgainBtn">Read again</button>
        <button type="button" class="btn btn-primary" id="resListBtn">Lessons</button>
      </div>
    </div>
  </div>"""),

("C_css_finish_screen",
"""    @media (min-width: 600px) {
      .content-wrap { max-width: 520px; margin: 0 auto; width: 100%; }
    }

    /* ------------------------------------------------------------------""",
"""    /* Finish screen (legacy additions) */
    .res-subtitle {
      font-size: 0.72rem; font-weight: 800; letter-spacing: 0.06em;
      text-transform: uppercase; margin-bottom: 12px;
    }
    .res-subtitle.pass { color: var(--success); }
    .res-subtitle.fail { color: var(--danger); }
    .res-meta {
      text-align: left; margin-top: 12px; padding-top: 12px;
      border-top: 1px dashed var(--border);
    }
    .res-meta-line { font-size: 0.85rem; font-weight: 600; padding: 2px 0; line-height: 1.35; }
    .res-meta-line.muted { color: var(--text-3); font-weight: 500; font-size: 0.8rem; }
    .results-bottom-bar {
      -webkit-box-orient: vertical; -webkit-box-direction: normal;
      -webkit-flex-direction: column; -ms-flex-direction: column;
      flex-direction: column; gap: 8px;
    }
    .results-secondary-row {
      display: -webkit-box; display: -webkit-flex; display: -ms-flexbox;
      display: flex; gap: 8px; width: 100%;
    }
    .results-secondary-row .btn {
      -webkit-box-flex: 1; -webkit-flex: 1; -ms-flex: 1;
      flex: 1; padding: 12px 16px; font-size: 0.9rem;
    }

    @media (min-width: 600px) {
      .content-wrap { max-width: 520px; margin: 0 auto; width: 100%; }
    }

    /* ------------------------------------------------------------------"""),

("C_css_tighten_badge",
"""      max-width: 400px; margin: 0 auto 20px;
    }
    .result-badge .badge-title""",
"""      max-width: 400px; margin: 0 auto;
    }
    .result-badge .badge-title"""),

("C_renderResults_rewrite",
"""  function renderResults() {
    var r = lastResult;
    if (!r) return;

    var scoreEl = $('resScore');
    scoreEl.textContent = r.score + '/' + r.total;
    scoreEl.className = 'score-big ' + (r.passed ? 'pass' : 'fail');

    var ann = $('resDayAnnounce');
    ann.textContent = r.passed
      ? 'Day ' + r.day + ' Completed!'
      : 'Day ' + r.day + ' — Keep practicing';
    ann.style.background = DAY_HEX[r.day];
    ann.style.color = DAY_TEXT[r.day];

    $('resName').textContent = profile.name;
    $('resGrade').textContent = profile.grade;
    $('resLesson').textContent = r.lessonNumber + ' – ' + r.title;
    $('resSound').textContent = r.targetSound;
    $('resDate').textContent = formatDate(r.date);
    $('resStatus').textContent = r.passed
      ? 'Day ' + r.day + ' Completed ✓'
      : 'Score below 80% — try again';

    var shRow = $('resShRow');
    var shVal = $('resShVal');
    if (typeof r.soundHuntAttempts === 'number') {
      shRow.style.display = 'flex';
      shVal.textContent = r.soundHuntAttempts === 1
        ? '✓ First try'
        : '✓ After ' + r.soundHuntAttempts + ' tries';
    } else {
      shRow.style.display = 'none';
    }

    var pills = $('resDayPills');
    pills.innerHTML = '';
    for (var d = 1; d <= 5; d++) {
      var s = document.createElement('span');
      s.className = 'dp' + (d <= r.highestDay ? ' done d' + d : '');
      if (d <= r.highestDay) {
        s.style.background = DAY_HEX[d];
        s.style.color = DAY_TEXT[d];
      }
      s.textContent = String(d);
      pills.appendChild(s);
    }

    var champ = $('resChamp');
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

    updateSubmitButton();
  }""",
"""  function renderResults() {
    var r = lastResult;
    if (!r) return;

    var scoreEl = $('resScore');
    scoreEl.textContent = r.score + '/' + r.total;
    scoreEl.className = 'score-big ' + (r.passed ? 'pass' : 'fail');

    var subEl = $('resSubtitle');
    if (subEl) {
      subEl.textContent = r.passed
        ? '✓ Day ' + r.day + ' · Passed'
        : '✗ Day ' + r.day + ' · Keep practicing';
      subEl.className = 'res-subtitle ' + (r.passed ? 'pass' : 'fail');
    }

    $('resLine1').textContent =
      profile.name + ' · Grade ' + profile.grade + ' · ' + formatDate(r.date);
    $('resLine2').textContent =
      'Lesson ' + r.lessonNumber + ' — ' + r.title;
    $('resLine3').textContent = r.targetSound;

    var line4 = $('resLine4');
    if (typeof r.soundHuntAttempts === 'number') {
      line4.style.display = '';
      line4.textContent = '🎯 Sound Hunt · ' +
        (r.soundHuntAttempts === 1 ? 'First try' : r.soundHuntAttempts + ' tries');
    } else {
      line4.style.display = 'none';
    }

    var pills = $('resDayPills');
    pills.innerHTML = '';
    for (var d = 1; d <= 5; d++) {
      var s = document.createElement('span');
      s.className = 'dp' + (d <= r.highestDay ? ' done d' + d : '');
      if (d <= r.highestDay) {
        s.style.background = DAY_HEX[d];
        s.style.color = DAY_TEXT[d];
      }
      s.textContent = String(d);
      pills.appendChild(s);
    }

    var champ = $('resChamp');
    if (r.highestDay >= 5) addClass(champ, 'show');
    else removeClass(champ, 'show');

    var fcBox = $('resFinishCodeBox');
    var fcVal = $('resFinishCode');
    if (fcBox && fcVal) {
      var code = String(FINISH_CODE || '').replace(/^\\s+|\\s+$/g, '');
      if (code) {
        fcBox.style.display = '';
        fcVal.textContent = code;
        fcBox.onclick = copyFinishCode;
      } else {
        fcBox.style.display = 'none';
      }
    }

    updateSubmitButton();
  }"""),

("C_updateSubmitButton",
"""  function updateSubmitButton() {
    if (!lastResult) return;
    var p = getProg(lastResult.lessonId);
    var tk = todayKey();
    var count = p.submits[tk] || 0;
    var btn = $('submitWaBtn');
    var note = $('submitNote');
    if (count >= MAX_SUBMITS_PER_DAY) {
      btn.disabled = true;
      btn.innerHTML = 'Already submitted twice today';
      note.textContent = 'You can submit again tomorrow';
    } else {
      btn.disabled = false;
      btn.innerHTML = ICONS.send + 'Submit to Teacher';
      note.textContent = 'Shares badge image, then opens teacher chat (works without saved contact) · ' +
        (MAX_SUBMITS_PER_DAY - count) + ' left today';
    }
  }""",
"""  function updateSubmitButton() {
    if (!lastResult) return;
    var p = getProg(lastResult.lessonId);
    var tk = todayKey();
    var count = p.submits[tk] || 0;
    var btn = $('submitWaBtn');
    if (count >= MAX_SUBMITS_PER_DAY) {
      btn.disabled = true;
      btn.innerHTML = 'Already submitted twice today';
    } else {
      btn.disabled = false;
      btn.innerHTML = ICONS.send + 'Submit to Teacher · ' +
        (MAX_SUBMITS_PER_DAY - count) + ' left';
    }
  }"""),
]


# ─────────────────────────────────────────────────────────────────────────────
# main
# ─────────────────────────────────────────────────────────────────────────────

def process(src_path, patches, label):
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
    if not all_green:
        print("\nFailed patches are usually whitespace/version drift.")
        print("Paste the ✗ lines back and I'll issue per-file variants.")
        sys.exit(1)


if __name__ == "__main__":
    main()