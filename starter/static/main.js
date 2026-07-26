// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const LEADERBOARD_STORAGE_KEY = 'sudokuLeaderboard';
const THEME_STORAGE_KEY = 'sudokuThemePreference';
let puzzle = [];
let conflictPositions = new Set();
let hintsUsed = 0;
let timerInterval = null;
let elapsedSeconds = 0;
let currentDifficulty = 'medium';
let leaderboardUpdatedThisGame = false;

function getRegionIndex(row, col) {
  return Math.floor(row / 3) * 3 + Math.floor(col / 3);
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.inputMode = 'numeric';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.dataset.regionIndex = getRegionIndex(i, j);
      input.setAttribute('aria-label', `Row ${i + 1} column ${j + 1}`);
      input.addEventListener('input', async (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        if (e.target.disabled) {
          return;
        }
        if (val === '') {
          applyConflictHighlighting([]);
          return;
        }
        await validateCurrentEntry(e.target);
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
}

function updateTimerDisplay() {
  const timerElement = document.getElementById('timer');
  if (timerElement) {
    timerElement.textContent = formatTime(elapsedSeconds);
  }
}

function loadLeaderboard() {
  const raw = localStorage.getItem(LEADERBOARD_STORAGE_KEY);
  if (!raw) {
    return [];
  }

  try {
    const entries = JSON.parse(raw);
    if (!Array.isArray(entries)) {
      return [];
    }
    return entries.map((entry) => ({
      name: String(entry.name || 'Anonymous').trim() || 'Anonymous',
      time: Number(entry.time) || 0,
      difficulty: String(entry.difficulty || 'medium'),
      hints: Number(entry.hints) || 0,
    })).sort((a, b) => a.time - b.time);
  } catch (error) {
    return [];
  }
}

function saveLeaderboard(entries) {
  localStorage.setItem(LEADERBOARD_STORAGE_KEY, JSON.stringify(entries));
}

function addLeaderboardEntry(entry) {
  const normalized = {
    name: String(entry.name || 'Anonymous').trim() || 'Anonymous',
    time: Number(entry.time) || 0,
    difficulty: String(entry.difficulty || 'medium'),
    hints: Number(entry.hints) || 0,
  };

  const entries = loadLeaderboard();
  entries.push(normalized);
  entries.sort((a, b) => a.time - b.time);
  const topEntries = entries.slice(0, 10);
  saveLeaderboard(topEntries);
  return topEntries;
}

function renderLeaderboard(entries) {
  const body = document.getElementById('leaderboard-body');
  const empty = document.getElementById('leaderboard-empty');

  if (!body || !empty) {
    return;
  }

  body.innerHTML = '';

  if (entries.length === 0) {
    empty.style.display = 'block';
    return;
  }

  empty.style.display = 'none';

  entries.forEach((entry, index) => {
    const row = document.createElement('tr');
    const placeCell = document.createElement('td');
    const nameCell = document.createElement('td');
    const timeCell = document.createElement('td');
    const difficultyCell = document.createElement('td');
    const hintsCell = document.createElement('td');

    placeCell.textContent = String(index + 1);
    nameCell.textContent = entry.name;
    timeCell.textContent = formatTime(entry.time);
    difficultyCell.textContent = entry.difficulty;
    hintsCell.textContent = String(entry.hints);

    row.appendChild(placeCell);
    row.appendChild(nameCell);
    row.appendChild(timeCell);
    row.appendChild(difficultyCell);
    row.appendChild(hintsCell);
    body.appendChild(row);
  });
}

function updateLeaderboardDisplay() {
  renderLeaderboard(loadLeaderboard());
}

function handleGameComplete() {
  if (leaderboardUpdatedThisGame) {
    return;
  }

  leaderboardUpdatedThisGame = true;
  let name = prompt('Congratulations! Enter your name for the Top 10 leaderboard:', 'Anonymous');
  if (name === null) {
    name = 'Anonymous';
  }
  name = name.trim() || 'Anonymous';

  addLeaderboardEntry({
    name,
    time: elapsedSeconds,
    difficulty: currentDifficulty,
    hints: hintsUsed,
  });
  updateLeaderboardDisplay();
}

function stopTimer() {
  if (timerInterval !== null) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}

function resetTimer() {
  stopTimer();
  elapsedSeconds = 0;
  updateTimerDisplay();
}

function startTimer() {
  stopTimer();
  timerInterval = setInterval(() => {
    elapsedSeconds += 1;
    updateTimerDisplay();
  }, 1000);
}

function getBoardFromInputs() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  return board;
}

function applyConflictHighlighting(conflicts) {
  conflictPositions = new Set(conflicts.map(([row, col]) => `${row}-${col}`));
  const boardDiv = document.getElementById('sudoku-board');
  if (!boardDiv) {
    return;
  }
  const inputs = boardDiv.getElementsByTagName('input');
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    const key = `${inp.dataset.row}-${inp.dataset.col}`;
    const isConflict = conflictPositions.has(key);
    inp.classList.toggle('conflict', isConflict);
    inp.toggleAttribute('aria-invalid', isConflict);
  }
}

function clearConflictHighlighting() {
  applyConflictHighlighting([]);
}

async function validateCurrentEntry(input) {
  const board = getBoardFromInputs();
  const row = Number(input.dataset.row);
  const col = Number(input.dataset.col);
  const value = input.value ? parseInt(input.value, 10) : 0;
  const res = await fetch('/validate-entry', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board, row, col, value})
  });
  const data = await res.json();
  if (data.error) {
    clearConflictHighlighting();
    return;
  }
  const conflicts = (data.conflicts || []).map(([conflictRow, conflictCol]) => [conflictRow, conflictCol]);
  if (conflicts.length > 0) {
    conflicts.push([row, col]);
  }
  applyConflictHighlighting(conflicts);
}

function renderPuzzle(puz) {
  puzzle = puz;
  hintsUsed = 0;
  leaderboardUpdatedThisGame = false;
  updateHintCount(hintsUsed);
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      inp.className = 'sudoku-cell';
      inp.dataset.regionIndex = getRegionIndex(i, j);
      inp.removeAttribute('aria-readonly');
      inp.removeAttribute('aria-disabled');
      inp.removeAttribute('data-prefilled');
      inp.classList.remove('prefilled', 'hinted', 'incorrect', 'conflict');
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.setAttribute('aria-disabled', 'true');
        inp.dataset.prefilled = 'true';
        inp.classList.add('prefilled');
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
  clearConflictHighlighting();
}

function getSelectedDifficulty() {
  const select = document.getElementById('difficulty-select');
  return select ? select.value : 'medium';
}

async function newGame() {
  const difficulty = getSelectedDifficulty();
  currentDifficulty = difficulty;
  const params = new URLSearchParams({difficulty});
  const res = await fetch(`/new?${params.toString()}`);
  const data = await res.json();
  renderPuzzle(data.puzzle);
  document.getElementById('message').innerText = '';
  resetTimer();
  startTimer();
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = getBoardFromInputs();
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.classList.remove('error', 'success', 'info');
    msg.classList.add('error');
    msg.textContent = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0] * SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.classList.remove('incorrect');
    inp.removeAttribute('aria-invalid');
    if (incorrect.has(idx)) {
      inp.classList.add('incorrect');
      inp.setAttribute('aria-invalid', 'true');
    }
  }
  msg.classList.remove('error', 'success', 'info');
  if (data.complete) {
    stopTimer();
    msg.classList.add('success');
    msg.textContent = 'Congratulations! You solved it!';
    handleGameComplete();
  } else if (incorrect.size > 0) {
    msg.classList.add('error');
    msg.textContent = 'Some cells are incorrect.';
  } else {
    msg.classList.add('info');
    msg.textContent = 'No incorrect entries yet. Keep going!';
  }
}

function updateHintCount(count) {
  const hintCounter = document.getElementById('hints-used');
  if (hintCounter) {
    hintCounter.textContent = String(count);
  }
}

async function requestHint() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = getBoardFromInputs();

  const res = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board}),
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.classList.remove('error', 'success', 'info');
    msg.classList.add('error');
    msg.textContent = data.error;
    return;
  }

  const {row, col, value} = data.hint;
  const idx = row * SIZE + col;
  const inp = inputs[idx];
  inp.value = value;
  inp.disabled = true;
  inp.setAttribute('aria-disabled', 'true');
  inp.dataset.prefilled = 'true';
  inp.className = 'sudoku-cell';
  inp.dataset.regionIndex = getRegionIndex(row, col);
  inp.classList.add('prefilled', 'hinted');
  hintsUsed = data.hints;
  updateHintCount(hintsUsed);
  clearConflictHighlighting();
  msg.classList.remove('error', 'success', 'info');
  msg.classList.add('info');
  msg.textContent = 'Hint applied to one empty cell.';
}

function applyTheme(theme) {
  const isDark = theme === 'dark';
  document.body.classList.toggle('dark-mode', isDark);
  const toggle = document.getElementById('theme-toggle');
  if (toggle) {
    toggle.textContent = isDark ? 'Light Mode' : 'Dark Mode';
    toggle.setAttribute('aria-pressed', String(isDark));
  }
}

function saveThemePreference(theme) {
  localStorage.setItem(THEME_STORAGE_KEY, theme);
}

function loadThemePreference() {
  const stored = localStorage.getItem(THEME_STORAGE_KEY);
  return stored === 'dark' ? 'dark' : 'light';
}

function toggleTheme() {
  const nextTheme = document.body.classList.contains('dark-mode') ? 'light' : 'dark';
  applyTheme(nextTheme);
  saveThemePreference(nextTheme);
}

function initializeTheme() {
  applyTheme(loadThemePreference());
}

// Wire buttons
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('hint-button').addEventListener('click', requestHint);
  document.getElementById('check-puzzle').addEventListener('click', checkSolution);
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
  updateLeaderboardDisplay();
  initializeTheme();
  newGame();
});