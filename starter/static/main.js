// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
let puzzle = [];
let hintsUsed = 0;

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
      input.setAttribute('aria-label', `Row ${i + 1} column ${j + 1}`);
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  hintsUsed = 0;
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
      inp.removeAttribute('aria-readonly');
      inp.removeAttribute('aria-disabled');
      inp.removeAttribute('data-prefilled');
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
}

function getSelectedDifficulty() {
  const select = document.getElementById('difficulty-select');
  return select ? select.value : 'medium';
}

async function newGame() {
  const difficulty = getSelectedDifficulty();
  const params = new URLSearchParams({difficulty});
  const res = await fetch(`/new?${params.toString()}`);
  const data = await res.json();
  renderPuzzle(data.puzzle);
  document.getElementById('message').innerText = '';
}

async function checkSolution() {
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
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.textContent = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0] * SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.className = 'sudoku-cell';
    inp.removeAttribute('aria-invalid');
    if (incorrect.has(idx)) {
      inp.className = 'sudoku-cell incorrect';
      inp.setAttribute('aria-invalid', 'true');
    }
  }
  if (data.complete) {
    msg.style.color = '#388e3c';
    msg.textContent = 'Congratulations! You solved it!';
  } else if (incorrect.size > 0) {
    msg.style.color = '#d32f2f';
    msg.textContent = 'Some cells are incorrect.';
  } else {
    msg.style.color = '#333';
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
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }

  const res = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board}),
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
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
  inp.className = 'sudoku-cell prefilled hinted';
  hintsUsed = data.hints;
  updateHintCount(hintsUsed);
  msg.style.color = '#333';
  msg.textContent = 'Hint applied to one empty cell.';
}

// Wire buttons
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('hint-button').addEventListener('click', requestHint);
  document.getElementById('check-puzzle').addEventListener('click', checkSolution);
  // initialize
  newGame();
});