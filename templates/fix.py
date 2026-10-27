#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_spelling.py

Insert the Spelling stage into BOTH reader builds, in one run:

    P-readerT-2.html      -> P-readerT-2_spelling.html       (modern, ES6)
    P-readerT-old2.html   -> P-readerT-old2_spelling.html    (legacy, ES5)

New cycle for both:
    Reading -> Questions -> Sound Hunt -> Spelling -> Results

The legacy patch keeps the legacy IIFE's own helpers ($, on, addClass,
removeClass, hasClass, esc, toast, shuffle, speakText, stopTTS,
renderReading, renderResults, showScreen, completeCycle,
clearSoundHuntTimer, ICONS, DAY_HEX, DAY_TEXT) and extends the
IE10 / old-WebKit flexbox fallback lists so the new cards render there.
"""

import io
import sys

INPUT_MODERN = "P-readerT-1.html"
OUTPUT_MODERN = "P-readerT-1_spelling.html"
INPUT_LEGACY = "P-readerT-old1.html"
OUTPUT_LEGACY = "P-readerT-old1_spelling.html"


# ------------------------------------------------------------------
# File I/O — preserves original CRLF/LF line endings
# ------------------------------------------------------------------
def read_file(path):
    with io.open(path, "rb") as f:
        raw = f.read()
    has_crlf = b"\r\n" in raw
    return raw.decode("utf-8").replace("\r\n", "\n"), has_crlf


def write_file(path, text, has_crlf):
    if has_crlf:
        text = text.replace("\n", "\r\n")
    with io.open(path, "wb") as f:
        f.write(text.encode("utf-8"))


# ------------------------------------------------------------------
# Anchored replacement helpers
# ------------------------------------------------------------------
def replace_once(h, old, new, label):
    n = h.count(old)
    if n != 1:
        raise SystemExit(
            "ANCHOR '%s' matched %d times (expected 1)" % (label, n)
        )
    return h.replace(old, new, 1)


def insert_after(h, anchor, block, label):
    return replace_once(h, anchor, anchor + block, label)


def insert_before(h, anchor, block, label):
    return replace_once(h, anchor, block + anchor, label)


# ==================================================================
# SHARED strings
# ==================================================================

# --- Spelling screen HTML (2-space indented, ends with blank line) ---
HTML_SPELLING_SCREEN = """  <!-- SPELLING -->
  <div id="spellingScreen" class="screen">
    <div class="app-header">
      <button type="button" class="icon-btn" id="spBackBtn" title="Back to story" aria-label="Back to story">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5"/><path d="M12 19l-7-7 7-7"/></svg>
      </button>
      <div style="flex:1;min-width:0">
        <h1 style="font-size:0.95rem">Spell It</h1>
        <div class="meta" id="spMeta"></div>
      </div>
      <button type="button" class="icon-btn" id="themeBtn6" title="Toggle theme" aria-label="Toggle theme"></button>
    </div>
    <div class="content">
      <div class="content-wrap">
        <div class="target-bar">
          <span class="day-chip" id="spDayChip">Day 1</span>
          <span class="sound" id="spTargetSound"></span>
        </div>
        <div class="q-progress" id="spProgress">Word 1 of 5</div>
        <div class="sp-card">
          <div class="sp-audio-row">
            <button type="button" class="sp-speaker-btn" id="spSpeakerBtn" aria-label="Hear the word">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 5 6 9H2v6h4l5 4z"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>
            </button>
            <div class="sp-hint">Tap to hear the word</div>
          </div>
          <div class="sp-slots" id="spSlots"></div>
          <div class="sp-tiles" id="spTiles"></div>
          <div class="feedback-banner" id="spFeedback"></div>
          <div class="sp-controls">
            <button type="button" class="btn btn-outline" id="spClearBtn">Clear</button>
          </div>
        </div>
      </div>
    </div>
    <div class="bottom-bar">
      <button type="button" class="btn btn-primary btn-lg btn-block btn-locked" id="spFinishBtn" disabled></button>
    </div>
  </div>

"""

# --- Results card: resLine4b element ---
HTML_RESLINE4_LINE = (
    '            <div class="res-meta-line muted" id="resLine4" style="display:none;">\u2014</div>\n'
)
HTML_RESLINE4B_LINE = (
    '            <div class="res-meta-line muted" id="resLine4b" style="display:none;">\u2014</div>\n'
)

# --- Spelling CSS (shared; -webkit- prefixes harmless on modern) ---
CSS_SPELLING = """    /* ===== Spelling stage ===== */
    .sp-card {
      background: #ffffff;
      background: var(--surface);
      border: 1px solid #e2e8f0;
      border: 1px solid var(--border);
      border-radius: 16px;
      border-radius: var(--radius);
      padding: 20px 16px 16px;
      box-shadow: 0 4px 20px rgba(15,23,42,0.08);
      box-shadow: var(--shadow);
    }
    .sp-audio-row { text-align: center; margin-bottom: 16px; }
    .sp-speaker-btn {
      width: 64px; height: 64px; border-radius: 50%; border: none;
      background: #f59e0b; background: var(--accent);
      color: #0f172a;
      display: inline-flex; align-items: center; justify-content: center;
      cursor: pointer;
      box-shadow: 0 4px 14px rgba(245,158,11,0.4);
      transition: transform 0.12s, background 0.15s;
      -webkit-tap-highlight-color: transparent;
    }
    .sp-speaker-btn:hover { background: #d97706; background: var(--accent-dark); }
    .sp-speaker-btn:active { transform: scale(0.94); }
    .sp-speaker-btn svg { width: 28px; height: 28px; }
    .sp-speaker-btn.playing {
      -webkit-animation: spPulse 1.4s infinite;
      animation: spPulse 1.4s infinite;
    }
    @-webkit-keyframes spPulse {
      0%,100% { -webkit-box-shadow: 0 4px 14px rgba(245,158,11,0.4); }
      50%     { -webkit-box-shadow: 0 4px 22px rgba(245,158,11,0.85); }
    }
    @keyframes spPulse {
      0%,100% { box-shadow: 0 4px 14px rgba(245,158,11,0.4); }
      50%     { box-shadow: 0 4px 22px rgba(245,158,11,0.85); }
    }
    .sp-hint {
      font-size: 0.78rem; color: #94a3b8; color: var(--text-3);
      font-weight: 600; margin-top: 8px;
    }
    .sp-slots {
      display: flex; justify-content: center; flex-wrap: wrap;
      gap: 6px; margin-bottom: 16px;
    }
    .sp-slots.shake {
      -webkit-animation: sh-shake 0.4s;
      animation: sh-shake 0.4s;
    }
    .sp-slot {
      width: 34px; height: 42px;
      display: flex; align-items: center; justify-content: center;
      font-size: 1.3rem; font-weight: 800;
      border-bottom: 3px solid #e2e8f0; border-bottom: 3px solid var(--border);
      border-radius: 6px;
      background: #f8fafc; background: var(--surface-2);
      color: #0f172a; color: var(--text);
      transition: background 0.15s, border-color 0.15s;
    }
    .sp-slot.filled  { border-bottom-color: #f59e0b; border-bottom-color: var(--accent); }
    .sp-slot.correct {
      background: #dcfce7; color: #166534;
      border-bottom-color: #16a34a; border-bottom-color: var(--success);
    }
    .sp-slot.wrong {
      background: #fee2e2; color: #991b1b;
      border-bottom-color: #dc2626; border-bottom-color: var(--danger);
    }
    [data-theme="dark"] .sp-slot.correct { background: #14532d; color: #bbf7d0; }
    [data-theme="dark"] .sp-slot.wrong   { background: #7f1d1d; color: #fecaca; }
    .sp-tiles {
      display: flex; flex-wrap: wrap; justify-content: center;
      gap: 6px; margin-bottom: 14px;
    }
    .sp-tile {
      width: 40px; height: 44px; border-radius: 10px;
      border: 2px solid #e2e8f0; border: 2px solid var(--border);
      background: #f8fafc; background: var(--surface-2);
      font-family: inherit; font-size: 1.15rem; font-weight: 800;
      color: #0f172a; color: var(--text);
      cursor: pointer;
      transition: border-color 0.15s, transform 0.1s, opacity 0.15s;
      -webkit-tap-highlight-color: transparent;
    }
    .sp-tile:hover:not(:disabled):not(.used) {
      border-color: #f59e0b; border-color: var(--accent);
    }
    .sp-tile:active:not(:disabled):not(.used) { transform: scale(0.94); }
    .sp-tile.used { opacity: 0.28; cursor: default; }
    .sp-controls {
      display: flex; justify-content: center; margin-top: 4px;
    }
    .sp-controls .btn { padding: 10px 20px; font-size: 0.85rem; }
    @media (min-width: 500px) {
      .sp-slot { width: 40px; height: 50px; font-size: 1.5rem; }
      .sp-tile { width: 46px; height: 50px; font-size: 1.3rem; }
    }

"""

# --- Shared rewire pieces (identical in both files) ---
FINISH_SH_OLD = (
    "  function finishSoundHunt() {\n"
    "    if (!soundHunt.passed) return;\n"
    "    completeCycle();\n"
    "    if (lastResult) lastResult.soundHuntAttempts = soundHunt.attempts;\n"
    "    renderResults();\n"
    "    showScreen('resultsScreen');\n"
    "  }\n"
)
FINISH_SH_NEW = (
    "  function finishSoundHunt() {\n"
    "    if (!soundHunt.passed) return;\n"
    "    if (lastResult) lastResult.soundHuntAttempts = soundHunt.attempts;\n"
    "    startSpelling();\n"
    "  }\n"
)

FINISH_QUIZ_OLD = (
    "    if (passed && hasSoundHuntData(currentLesson)) {\n"
    "      startSoundHunt();\n"
    "      showScreen('soundHuntScreen');\n"
    "    } else {\n"
    "      completeCycle();\n"
    "      renderResults();\n"
    "      showScreen('resultsScreen');\n"
    "    }\n"
)
FINISH_QUIZ_NEW = (
    "    if (passed && hasSoundHuntData(currentLesson)) {\n"
    "      startSoundHunt();\n"
    "      showScreen('soundHuntScreen');\n"
    "    } else if (passed && hasSpellingData(currentLesson)) {\n"
    "      startSpelling();\n"
    "    } else {\n"
    "      completeCycle();\n"
    "      renderResults();\n"
    "      showScreen('resultsScreen');\n"
    "    }\n"
)

LINE4_ANCHOR = "      line4.style.display = 'none';\n    }\n"

WHATSAPP_OLD = (
    "      (typeof r.soundHuntAttempts === 'number'\n"
    "        ? 'Sound Hunt: Passed on try ' + r.soundHuntAttempts + '\\n'\n"
    "        : '') +\n"
)
WHATSAPP_NEW = WHATSAPP_OLD + (
    "      (typeof r.spellingMistakes === 'number'\n"
    "        ? 'Spelling: ' + (r.spellingMistakes === 0\n"
    "            ? 'Perfect'\n"
    "            : r.spellingMistakes + ' mistake' +\n"
    "              (r.spellingMistakes === 1 ? '' : 's')) + '\\n'\n"
    "        : '') +\n"
)


def patch_notcounted(h, label):
    """Replace the 'Not counted' hint with the 3-gate version.
    Handles both `\\u2014` (escaped in JS) and literal `—`."""
    old_esc = (
        "      else if (!r.passed) msg = 'Not counted \\u2014 pass the questions "
        "and Sound Hunt to earn the day';\n"
    )
    new_esc = (
        "      else if (!r.passed) msg = 'Not counted \\u2014 pass questions, "
        "Sound Hunt & Spelling to earn the day';\n"
    )
    if h.count(old_esc) == 1:
        return h.replace(old_esc, new_esc, 1)

    old_chr = (
        "      else if (!r.passed) msg = 'Not counted \u2014 pass the questions "
        "and Sound Hunt to earn the day';\n"
    )
    new_chr = (
        "      else if (!r.passed) msg = 'Not counted \u2014 pass questions, "
        "Sound Hunt & Spelling to earn the day';\n"
    )
    if h.count(old_chr) == 1:
        return h.replace(old_chr, new_chr, 1)

    raise SystemExit(label + ": not-counted message not found")


# ==================================================================
# MODERN (P-readerT-2.html) — ES6, classList, arrow fns
# ==================================================================
MODERN_SH_STATE_ANCHOR = (
    "  let soundHunt = { tiles: [], attempts: 0, passed: false, checking: false };\n"
    "  let soundHuntTimer = null;\n"
)

MODERN_STATE = """
  let spelling = {
    words: [],
    index: 0,
    currentWord: '',
    filledCount: 0,
    tiles: [],
    slotValues: [],
    mistakes: 0,
    passed: false,
    checking: false
  };

"""

MODERN_SPELLING_MODULE = r"""  /* ========== SPELLING ========== */
  function hasSpellingData(lesson) {
    return lesson &&
      Array.isArray(lesson.targetWords) && lesson.targetWords.length >= 5;
  }

  function startSpelling() {
    clearSoundHuntTimer();
    if (!hasSpellingData(currentLesson)) {
      if (lastResult) lastResult.spellingMistakes = 0;
      completeCycle();
      renderResults();
      showScreen('resultsScreen');
      return;
    }
    spelling.words = currentLesson.targetWords.slice(0, 5);
    spelling.index = 0;
    spelling.currentWord = '';
    spelling.filledCount = 0;
    spelling.tiles = [];
    spelling.slotValues = [];
    spelling.mistakes = 0;
    spelling.passed = false;
    spelling.checking = false;
    renderSpellingWord();
    showScreen('spellingScreen');
  }

  function renderSpellingWord() {
    if (!currentLesson) return;
    const word = spelling.words[spelling.index] || '';
    spelling.currentWord = word;
    spelling.filledCount = 0;
    spelling.slotValues = [];
    spelling.checking = false;

    document.getElementById('spMeta').textContent = profile.name + ' · Day ' + currentDay;
    const chip = document.getElementById('spDayChip');
    chip.textContent = 'Day ' + currentDay;
    chip.style.background = DAY_HEX[currentDay];
    chip.style.color = DAY_TEXT[currentDay];
    document.getElementById('spTargetSound').textContent = 'Target: ' + currentLesson.targetSound;

    document.getElementById('spProgress').textContent =
      'Word ' + (spelling.index + 1) + ' of ' + spelling.words.length;

    const fb = document.getElementById('spFeedback');
    fb.className = 'feedback-banner';
    fb.textContent = '';

    const slotsBox = document.getElementById('spSlots');
    slotsBox.innerHTML = '';
    slotsBox.classList.remove('shake');
    for (let i = 0; i < word.length; i++) {
      const s = document.createElement('div');
      s.className = 'sp-slot';
      slotsBox.appendChild(s);
    }

    const tilesBox = document.getElementById('spTiles');
    tilesBox.innerHTML = '';
    const shuffled = shuffle(word.split(''));
    spelling.tiles = shuffled.map(ch => ({ ch, used: false }));
    spelling.tiles.forEach((t, i) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'sp-tile';
      b.textContent = t.ch;
      b.dataset.idx = i;
      b.addEventListener('click', () => onSpTileTap(i));
      tilesBox.appendChild(b);
    });

    updateSpFinishBtn();

    if (window.speechSynthesis && typeof window.SpeechSynthesisUtterance === 'function') {
      setTimeout(spSpeakWord, 300);
    }
  }

  function spSpeakWord() {
    if (!spelling.currentWord) return;
    const btn = document.getElementById('spSpeakerBtn');
    if (btn) {
      btn.classList.add('playing');
      setTimeout(() => btn.classList.remove('playing'), 1400);
    }
    speakText(spelling.currentWord);
  }

  function onSpTileTap(idx) {
    if (spelling.checking || spelling.passed) return;
    const tile = spelling.tiles[idx];
    if (!tile || tile.used) return;
    if (spelling.filledCount >= spelling.currentWord.length) return;

    const slotIdx = spelling.filledCount;
    tile.used = true;
    spelling.slotValues[slotIdx] = tile.ch;
    spelling.filledCount++;

    const tiles = document.querySelectorAll('#spTiles .sp-tile');
    if (tiles[idx]) tiles[idx].classList.add('used');
    const slots = document.querySelectorAll('#spSlots .sp-slot');
    if (slots[slotIdx]) {
      slots[slotIdx].textContent = tile.ch;
      slots[slotIdx].classList.add('filled');
    }

    const fb = document.getElementById('spFeedback');
    if (fb && fb.classList.contains('show') && !fb.classList.contains('ok')) {
      fb.className = 'feedback-banner';
      fb.textContent = '';
    }

    if (spelling.filledCount === spelling.currentWord.length) checkSpelling();
  }

  function checkSpelling() {
    spelling.checking = true;
    const userWord = spelling.slotValues.join('');
    const target = spelling.currentWord;
    const fb = document.getElementById('spFeedback');
    const slots = document.querySelectorAll('#spSlots .sp-slot');

    if (userWord === target) {
      slots.forEach(s => s.classList.add('correct'));
      fb.className = 'feedback-banner show ok';
      fb.textContent = '\u2713 Correct!';
      setTimeout(() => {
        spelling.index++;
        if (spelling.index >= spelling.words.length) {
          spelling.passed = true;
          spelling.checking = false;
          onSpellingComplete();
        } else {
          renderSpellingWord();
        }
      }, 900);
    } else {
      spelling.mistakes++;
      document.getElementById('spSlots').classList.add('shake');
      slots.forEach(s => s.classList.add('wrong'));
      fb.className = 'feedback-banner show bad';
      fb.textContent = '\u2717 Try again';
      setTimeout(resetCurrentSpellWord, 1100);
    }
  }

  function resetCurrentSpellWord() {
    spelling.filledCount = 0;
    spelling.slotValues = [];
    spelling.tiles.forEach(t => t.used = false);

    const slotsBox = document.getElementById('spSlots');
    slotsBox.classList.remove('shake');
    slotsBox.querySelectorAll('.sp-slot').forEach(s => {
      s.classList.remove('filled', 'correct', 'wrong');
      s.textContent = '';
    });
    document.querySelectorAll('#spTiles .sp-tile').forEach(t => {
      t.classList.remove('used', 'wrong');
    });

    const fb = document.getElementById('spFeedback');
    fb.className = 'feedback-banner';
    fb.textContent = '';
    spelling.checking = false;
  }

  function onSpellingComplete() {
    const fb = document.getElementById('spFeedback');
    fb.className = 'feedback-banner show ok';
    fb.textContent = '\u2713 All ' + spelling.words.length + ' words spelled!';
    document.getElementById('spProgress').textContent =
      spelling.words.length + ' of ' + spelling.words.length + ' done';
    updateSpFinishBtn();
  }

  function updateSpFinishBtn() {
    const btn = document.getElementById('spFinishBtn');
    if (!btn) return;
    if (spelling.passed) {
      btn.disabled = false;
      btn.classList.remove('btn-locked');
      btn.innerHTML = ICONS.check + 'See Results';
    } else {
      btn.disabled = true;
      btn.classList.add('btn-locked');
      btn.innerHTML = ICONS.lock + 'Spell all 5 words';
    }
  }

  function finishSpelling() {
    if (!spelling.passed || !lastResult) return;
    lastResult.spellingMistakes = spelling.mistakes;
    completeCycle();
    renderResults();
    showScreen('resultsScreen');
  }

  document.getElementById('spFinishBtn').addEventListener('click', finishSpelling);
  document.getElementById('spSpeakerBtn').addEventListener('click', spSpeakWord);
  document.getElementById('spClearBtn').addEventListener('click', () => {
    if (spelling.checking || spelling.passed) return;
    resetCurrentSpellWord();
  });
  document.getElementById('spBackBtn').addEventListener('click', () => {
    stopTTS();
    renderReading();
    showScreen('readingScreen');
  });

"""

MODERN_LINE4B_JS = (
    "\n"
    "    const line4b = document.getElementById('resLine4b');\n"
    "    if (line4b) {\n"
    "      if (typeof r.spellingMistakes === 'number') {\n"
    "        line4b.style.display = '';\n"
    "        line4b.textContent = '\\u270F\\uFE0F Spelling \\u00B7 ' +\n"
    "          (r.spellingMistakes === 0\n"
    "            ? 'Perfect'\n"
    "            : r.spellingMistakes + ' mistake' +\n"
    "              (r.spellingMistakes === 1 ? '' : 's'));\n"
    "      } else {\n"
    "        line4b.style.display = 'none';\n"
    "      }\n"
    "    }\n"
)

MODERN_THEME_ICON_OLD = "    ['themeBtn', 'themeBtn3', 'themeBtn4', 'themeBtn5'].forEach(id => {"
MODERN_THEME_ICON_NEW = "    ['themeBtn', 'themeBtn3', 'themeBtn4', 'themeBtn5', 'themeBtn6'].forEach(id => {"
MODERN_THEME_LISTEN_OLD = "  ['themeBtn', 'themeBtn2', 'themeBtn3', 'themeBtn4', 'themeBtn5'].forEach(id => {"
MODERN_THEME_LISTEN_NEW = "  ['themeBtn', 'themeBtn2', 'themeBtn3', 'themeBtn4', 'themeBtn5', 'themeBtn6'].forEach(id => {"

MODERN_INIT_SH_ANCHOR = (
    "  (function initShButton() {\n"
    "    const btn = document.getElementById('shFinishBtn');\n"
    "    if (btn) btn.innerHTML = ICONS.lock + 'Find all 5 words';\n"
    "  })();\n"
)
MODERN_INIT_SP_BLOCK = (
    "  (function initSpButton() {\n"
    "    const btn = document.getElementById('spFinishBtn');\n"
    "    if (btn) btn.innerHTML = ICONS.lock + 'Spell all 5 words';\n"
    "  })();\n"
)


def patch_modern(html):
    # HTML — spelling screen (before <!-- RESULTS -->)
    html = replace_once(
        html, "  <!-- RESULTS -->",
        HTML_SPELLING_SCREEN + "  <!-- RESULTS -->",
        "modern: html screen",
    )
    # HTML — resLine4b
    html = insert_after(
        html, HTML_RESLINE4_LINE, HTML_RESLINE4B_LINE, "modern: resLine4b"
    )
    # CSS — before </style>
    html = insert_before(html, "  </style>", CSS_SPELLING, "modern: css")
    # JS — state
    html = insert_after(html, MODERN_SH_STATE_ANCHOR, MODERN_STATE, "modern: state")
    # JS — finishSoundHunt hand-off
    html = replace_once(html, FINISH_SH_OLD, FINISH_SH_NEW, "modern: finish sh")
    # JS — Sound Hunt button label
    html = replace_once(
        html,
        "btn.innerHTML = ICONS.check + 'See Results';",
        "btn.innerHTML = ICONS.check + 'Spell It';",
        "modern: sh label",
    )
    # JS — finishQuiz branch
    html = replace_once(html, FINISH_QUIZ_OLD, FINISH_QUIZ_NEW, "modern: finish quiz")
    # JS — spelling module
    html = insert_before(
        html, "  /* ========== RESULTS ========== */",
        MODERN_SPELLING_MODULE, "modern: module",
    )
    # JS — results line4b
    html = insert_after(html, LINE4_ANCHOR, MODERN_LINE4B_JS, "modern: line4b js")
    # JS — "not counted" hint
    html = patch_notcounted(html, "modern")
    # JS — WhatsApp share text
    html = replace_once(html, WHATSAPP_OLD, WHATSAPP_NEW, "modern: whatsapp")
    # JS — theme IDs
    html = replace_once(
        html, MODERN_THEME_ICON_OLD, MODERN_THEME_ICON_NEW, "modern: theme icons"
    )
    html = replace_once(
        html, MODERN_THEME_LISTEN_OLD, MODERN_THEME_LISTEN_NEW, "modern: theme listeners"
    )
    # JS — init button label
    html = insert_after(
        html, MODERN_INIT_SH_ANCHOR, MODERN_INIT_SP_BLOCK, "modern: init sp"
    )
    return html


# ==================================================================
# LEGACY (P-readerT-old2.html) — ES5, helpers, IE10 fallbacks
# ==================================================================
LEGACY_SH_STATE_ANCHOR = (
    "    checking: false\n"
    "  };\n"
    "  var soundHuntTimer = null;\n"
)

LEGACY_STATE = """
  var spelling = {
    words: [],
    index: 0,
    currentWord: '',
    filledCount: 0,
    tiles: [],
    slotValues: [],
    mistakes: 0,
    passed: false,
    checking: false
  };

"""

LEGACY_SPELLING_MODULE = r"""  /* ========== SPELLING ========== */
  function hasSpellingData(lesson) {
    return !!lesson &&
      Array.isArray(lesson.targetWords) && lesson.targetWords.length >= 5;
  }

  function startSpelling() {
    clearSoundHuntTimer();
    if (!hasSpellingData(currentLesson)) {
      if (lastResult) lastResult.spellingMistakes = 0;
      completeCycle();
      renderResults();
      showScreen('resultsScreen');
      return;
    }
    spelling.words = currentLesson.targetWords.slice(0, 5);
    spelling.index = 0;
    spelling.currentWord = '';
    spelling.filledCount = 0;
    spelling.tiles = [];
    spelling.slotValues = [];
    spelling.mistakes = 0;
    spelling.passed = false;
    spelling.checking = false;
    renderSpellingWord();
    showScreen('spellingScreen');
  }

  function renderSpellingWord() {
    if (!currentLesson) return;
    var word = spelling.words[spelling.index] || '';
    spelling.currentWord = word;
    spelling.filledCount = 0;
    spelling.slotValues = [];
    spelling.checking = false;

    $('spMeta').textContent = profile.name + ' \u00B7 Day ' + currentDay;
    var chip = $('spDayChip');
    chip.textContent = 'Day ' + currentDay;
    chip.style.background = DAY_HEX[currentDay];
    chip.style.color = DAY_TEXT[currentDay];
    $('spTargetSound').textContent = 'Target: ' + currentLesson.targetSound;

    $('spProgress').textContent = 'Word ' + (spelling.index + 1) +
      ' of ' + spelling.words.length;

    var fb = $('spFeedback');
    fb.className = 'feedback-banner';
    fb.textContent = '';

    var slotsBox = $('spSlots');
    slotsBox.innerHTML = '';
    removeClass(slotsBox, 'shake');
    for (var i = 0; i < word.length; i++) {
      var s = document.createElement('div');
      s.className = 'sp-slot';
      slotsBox.appendChild(s);
    }

    var tilesBox = $('spTiles');
    tilesBox.innerHTML = '';
    var shuffled = shuffle(word.split(''));
    spelling.tiles = [];
    for (var j = 0; j < shuffled.length; j++) {
      spelling.tiles.push({ ch: shuffled[j], used: false });
    }
    for (var k = 0; k < spelling.tiles.length; k++) {
      (function (idx) {
        var b = document.createElement('button');
        b.type = 'button';
        b.className = 'sp-tile';
        b.textContent = spelling.tiles[idx].ch;
        b.setAttribute('data-idx', String(idx));
        on(b, 'click', function () { onSpTileTap(idx); });
        tilesBox.appendChild(b);
      })(k);
    }

    updateSpFinishBtn();

    if (window.speechSynthesis &&
        typeof window.SpeechSynthesisUtterance === 'function') {
      setTimeout(spSpeakWord, 300);
    }
  }

  function spSpeakWord() {
    if (!spelling.currentWord) return;
    var btn = $('spSpeakerBtn');
    if (btn) {
      addClass(btn, 'playing');
      setTimeout(function () { removeClass(btn, 'playing'); }, 1400);
    }
    speakText(spelling.currentWord);
  }

  function onSpTileTap(idx) {
    if (spelling.checking || spelling.passed) return;
    var tile = spelling.tiles[idx];
    if (!tile || tile.used) return;
    if (spelling.filledCount >= spelling.currentWord.length) return;

    var slotIdx = spelling.filledCount;
    tile.used = true;
    spelling.slotValues[slotIdx] = tile.ch;
    spelling.filledCount++;

    var tileEls = document.querySelectorAll('#spTiles .sp-tile');
    if (tileEls[idx]) addClass(tileEls[idx], 'used');
    var slots = document.querySelectorAll('#spSlots .sp-slot');
    if (slots[slotIdx]) {
      slots[slotIdx].textContent = tile.ch;
      addClass(slots[slotIdx], 'filled');
    }

    var fb = $('spFeedback');
    if (fb && hasClass(fb, 'show') && !hasClass(fb, 'ok')) {
      fb.className = 'feedback-banner';
      fb.textContent = '';
    }

    if (spelling.filledCount === spelling.currentWord.length) checkSpelling();
  }

  function checkSpelling() {
    spelling.checking = true;
    var userWord = spelling.slotValues.join('');
    var target = spelling.currentWord;
    var fb = $('spFeedback');
    var slots = document.querySelectorAll('#spSlots .sp-slot');
    var i;

    if (userWord === target) {
      for (i = 0; i < slots.length; i++) addClass(slots[i], 'correct');
      fb.className = 'feedback-banner show ok';
      fb.textContent = '\u2713 Correct!';
      setTimeout(function () {
        spelling.index++;
        if (spelling.index >= spelling.words.length) {
          spelling.passed = true;
          spelling.checking = false;
          onSpellingComplete();
        } else {
          renderSpellingWord();
        }
      }, 900);
    } else {
      spelling.mistakes++;
      addClass($('spSlots'), 'shake');
      for (i = 0; i < slots.length; i++) addClass(slots[i], 'wrong');
      fb.className = 'feedback-banner show bad';
      fb.textContent = '\u2717 Try again';
      setTimeout(resetCurrentSpellWord, 1100);
    }
  }

  function resetCurrentSpellWord() {
    spelling.filledCount = 0;
    spelling.slotValues = [];
    for (var t = 0; t < spelling.tiles.length; t++) spelling.tiles[t].used = false;

    var slotsBox = $('spSlots');
    removeClass(slotsBox, 'shake');
    var slots = slotsBox.querySelectorAll('.sp-slot');
    for (var i = 0; i < slots.length; i++) {
      removeClass(slots[i], 'filled');
      removeClass(slots[i], 'correct');
      removeClass(slots[i], 'wrong');
      slots[i].textContent = '';
    }
    var tileEls = document.querySelectorAll('#spTiles .sp-tile');
    for (var j = 0; j < tileEls.length; j++) {
      removeClass(tileEls[j], 'used');
      removeClass(tileEls[j], 'wrong');
    }

    var fb = $('spFeedback');
    fb.className = 'feedback-banner';
    fb.textContent = '';
    spelling.checking = false;
  }

  function onSpellingComplete() {
    var fb = $('spFeedback');
    fb.className = 'feedback-banner show ok';
    fb.textContent = '\u2713 All ' + spelling.words.length + ' words spelled!';
    $('spProgress').textContent =
      spelling.words.length + ' of ' + spelling.words.length + ' done';
    updateSpFinishBtn();
  }

  function updateSpFinishBtn() {
    var btn = $('spFinishBtn');
    if (!btn) return;
    if (spelling.passed) {
      btn.disabled = false;
      removeClass(btn, 'btn-locked');
      btn.innerHTML = ICONS.check + 'See Results';
    } else {
      btn.disabled = true;
      addClass(btn, 'btn-locked');
      btn.innerHTML = ICONS.lock + 'Spell all 5 words';
    }
  }

  function finishSpelling() {
    if (!spelling.passed || !lastResult) return;
    lastResult.spellingMistakes = spelling.mistakes;
    completeCycle();
    renderResults();
    showScreen('resultsScreen');
  }

  on($('spFinishBtn'), 'click', finishSpelling);
  on($('spSpeakerBtn'), 'click', spSpeakWord);
  on($('spClearBtn'), 'click', function () {
    if (spelling.checking || spelling.passed) return;
    resetCurrentSpellWord();
  });
  on($('spBackBtn'), 'click', function () {
    stopTTS();
    renderReading();
    showScreen('readingScreen');
  });

"""

LEGACY_LINE4B_JS = (
    "\n"
    "    var line4b = $('resLine4b');\n"
    "    if (line4b) {\n"
    "      if (typeof r.spellingMistakes === 'number') {\n"
    "        line4b.style.display = '';\n"
    "        line4b.textContent = '\\u270F\\uFE0F Spelling \\u00B7 ' +\n"
    "          (r.spellingMistakes === 0\n"
    "            ? 'Perfect'\n"
    "            : r.spellingMistakes + ' mistake' +\n"
    "              (r.spellingMistakes === 1 ? '' : 's'));\n"
    "      } else {\n"
    "        line4b.style.display = 'none';\n"
    "      }\n"
    "    }\n"
)

LEGACY_FALLBACK_COMMENT = (
    "    /* ------------------------------------------------------------------\n"
    "       Legacy flexbox fallbacks for older WebKit / IE10 / Android 4.x.\n"
    "       ------------------------------------------------------------------ */\n"
)

LEGACY_THEME_IDS_OLD = "  var THEME_IDS = ['themeBtn', 'themeBtn2', 'themeBtn3', 'themeBtn4', 'themeBtn5'];"
LEGACY_THEME_IDS_NEW = "  var THEME_IDS = ['themeBtn', 'themeBtn2', 'themeBtn3', 'themeBtn4', 'themeBtn5', 'themeBtn6'];"
LEGACY_THEME_ICON_IDS_OLD = "  var THEME_ICON_IDS = ['themeBtn', 'themeBtn3', 'themeBtn4', 'themeBtn5'];"
LEGACY_THEME_ICON_IDS_NEW = "  var THEME_ICON_IDS = ['themeBtn', 'themeBtn3', 'themeBtn4', 'themeBtn5', 'themeBtn6'];"

LEGACY_INIT_SH_ANCHOR = (
    "  (function initShButton() {\n"
    "    var btn = $('shFinishBtn');\n"
    "    if (btn) btn.innerHTML = ICONS.lock + 'Find all 5 words';\n"
    "  })();\n"
)
LEGACY_INIT_SP_BLOCK = (
    "  (function initSpButton() {\n"
    "    var btn = $('spFinishBtn');\n"
    "    if (btn) btn.innerHTML = ICONS.lock + 'Spell all 5 words';\n"
    "  })();\n"
)

LEGACY_FALLBACK_EXTENSIONS = [
    (
        ".progress-row, .day-pills, .result-badge .details .row,\n"
        "    .result-badge .day-row, .segment-actions, .icon-btn, .story-line,\n"
        "    .segment-word, .data-bar, .menu-item {",
        ".progress-row, .day-pills, .result-badge .details .row,\n"
        "    .result-badge .day-row, .segment-actions, .icon-btn, .story-line,\n"
        "    .segment-word, .data-bar, .menu-item,\n"
        "    .sp-slots, .sp-tiles, .sp-controls {",
    ),
    (
        ".btn, .mastered-badge, .data-btn, .day-chip {",
        ".btn, .mastered-badge, .data-btn, .day-chip, .sp-speaker-btn {",
    ),
    (
        ".segment-actions, .segment-overlay, .segment-word, .data-btn,\n"
        "    .day-chip {",
        ".segment-actions, .segment-overlay, .segment-word, .data-btn,\n"
        "    .day-chip, .sp-slots, .sp-tiles, .sp-controls {",
    ),
    (
        ".app-header, .student-banner, .target-bar, .progress-row, .bottom-bar,\n"
        "    .day-pills, .result-badge .details .row, .result-badge .day-row,\n"
        "    .result-badge .champ, .segment-actions, .btn, .icon-btn,\n"
        "    .segment-banner, .mastered-badge, .data-bar, .data-btn, .menu-item,\n"
        "    .day-chip {",
        ".app-header, .student-banner, .target-bar, .progress-row, .bottom-bar,\n"
        "    .day-pills, .result-badge .details .row, .result-badge .day-row,\n"
        "    .result-badge .champ, .segment-actions, .btn, .icon-btn,\n"
        "    .segment-banner, .mastered-badge, .data-bar, .data-btn, .menu-item,\n"
        "    .day-chip, .sp-speaker-btn, .sp-slot, .sp-tile {",
    ),
]


def patch_legacy(html):
    # HTML — spelling screen
    html = replace_once(
        html, "  <!-- RESULTS -->",
        HTML_SPELLING_SCREEN + "  <!-- RESULTS -->",
        "legacy: html screen",
    )
    # HTML — resLine4b
    html = insert_after(
        html, HTML_RESLINE4_LINE, HTML_RESLINE4B_LINE, "legacy: resLine4b"
    )
    # CSS — before the fallback comment
    html = insert_before(
        html, LEGACY_FALLBACK_COMMENT, CSS_SPELLING, "legacy: css"
    )
    # CSS — extend the four fallback lists
    for old_list, new_list in LEGACY_FALLBACK_EXTENSIONS:
        html = replace_once(html, old_list, new_list, "legacy: fallback list")
    # JS — state
    html = insert_after(html, LEGACY_SH_STATE_ANCHOR, LEGACY_STATE, "legacy: state")
    # JS — finishSoundHunt hand-off
    html = replace_once(html, FINISH_SH_OLD, FINISH_SH_NEW, "legacy: finish sh")
    # JS — Sound Hunt button label
    html = replace_once(
        html,
        "btn.innerHTML = ICONS.check + 'See Results';",
        "btn.innerHTML = ICONS.check + 'Spell It';",
        "legacy: sh label",
    )
    # JS — finishQuiz branch
    html = replace_once(html, FINISH_QUIZ_OLD, FINISH_QUIZ_NEW, "legacy: finish quiz")
    # JS — spelling module
    html = insert_before(
        html, "  /* ========== RESULTS ========== */",
        LEGACY_SPELLING_MODULE, "legacy: module",
    )
    # JS — results line4b
    html = insert_after(html, LINE4_ANCHOR, LEGACY_LINE4B_JS, "legacy: line4b js")
    # JS — "not counted" hint
    html = patch_notcounted(html, "legacy")
    # JS — WhatsApp share text
    html = replace_once(html, WHATSAPP_OLD, WHATSAPP_NEW, "legacy: whatsapp")
    # JS — theme ID constants
    html = replace_once(
        html, LEGACY_THEME_IDS_OLD, LEGACY_THEME_IDS_NEW, "legacy: theme ids"
    )
    html = replace_once(
        html, LEGACY_THEME_ICON_IDS_OLD, LEGACY_THEME_ICON_IDS_NEW,
        "legacy: theme icon ids",
    )
    # JS — init button label
    html = insert_after(
        html, LEGACY_INIT_SH_ANCHOR, LEGACY_INIT_SP_BLOCK, "legacy: init sp"
    )
    return html


# ==================================================================
# Main
# ==================================================================
def process(input_path, output_path, patcher, label):
    try:
        src, has_crlf = read_file(input_path)
    except IOError:
        sys.stderr.write("[%s] could not read %s\n" % (label, input_path))
        return False
    try:
        out = patcher(src)
    except SystemExit as e:
        sys.stderr.write("[%s] %s\n" % (label, e))
        return False
    try:
        write_file(output_path, out, has_crlf)
    except IOError:
        sys.stderr.write("[%s] could not write %s\n" % (label, output_path))
        return False
    print("[%s] OK  %s -> %s" % (label, input_path, output_path))
    return True


def main():
    ok_modern = process(INPUT_MODERN, OUTPUT_MODERN, patch_modern, "modern")
    ok_legacy = process(INPUT_LEGACY, OUTPUT_LEGACY, patch_legacy, "legacy")
    if ok_modern and ok_legacy:
        print()
        print("Both files patched.")
        print("New cycle: Reading -> Questions -> Sound Hunt -> Spelling -> Results")
        return 0
    sys.stderr.write("One or more patches failed; no output written for failures.\n")
    return 2


if __name__ == "__main__":
    sys.exit(main())