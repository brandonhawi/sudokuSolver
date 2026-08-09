'use strict';

const POLL_INTERVAL_MS = 400;
const ERROR_VISIBLE_MS = 2000;

const boardEl = document.getElementById('board');
const statusEl = document.getElementById('status');

let selected = null;
let lastRendered = null;
let errorTimer = null;

function buildBoard() {
    for (let row = 0; row < 9; row++) {
        const tr = document.createElement('tr');
        for (let col = 0; col < 9; col++) {
            const td = document.createElement('td');
            td.id = `cell-${row}-${col}`;
            td.addEventListener('click', () => select(row, col));
            tr.appendChild(td);
        }
        boardEl.appendChild(tr);
    }
}

function cell(row, col) {
    return document.getElementById(`cell-${row}-${col}`);
}

function select(row, col) {
    if (selected) {
        cell(selected.row, selected.col).classList.remove('selected');
    }
    selected = { row, col };
    cell(row, col).classList.add('selected');
}

function render(state) {
    const signature = JSON.stringify(state);
    if (signature === lastRendered) {
        return;
    }
    lastRendered = signature;

    for (let row = 0; row < 9; row++) {
        for (let col = 0; col < 9; col++) {
            const value = state.grid[row][col];
            const td = cell(row, col);
            td.textContent = value === 0 ? '' : value;
            td.classList.toggle('given', state.givens[row][col]);
        }
    }

    if (errorTimer === null) {
        statusEl.textContent = state.solved
            ? `Solved in ${state.moves} moves.`
            : `${state.empty_cells} empty cells left · ${state.moves} moves · ` +
              `${state.rejected_moves} rejected · ${state.difficulty}`;
        statusEl.classList.toggle('solved', state.solved);
    }
}

async function call(path, options) {
    const response = await fetch(path, options);
    const body = await response.json();
    if (!response.ok) {
        flashError(body.error || 'Something went wrong.');
        return null;
    }
    render(body);
    return body;
}

function flashError(message) {
    statusEl.textContent = message;
    statusEl.classList.remove('solved');
    statusEl.classList.add('error');

    clearTimeout(errorTimer);
    errorTimer = setTimeout(() => {
        errorTimer = null;
        statusEl.classList.remove('error');
        lastRendered = null;
    }, ERROR_VISIBLE_MS);
}

function post(path, payload) {
    return call(path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload || {}),
    });
}

document.addEventListener('keydown', (event) => {
    if (!selected) {
        return;
    }
    if (event.key >= '1' && event.key <= '9') {
        post('/api/move', { ...selected, value: Number(event.key) });
    } else if (event.key === 'Backspace' || event.key === 'Delete' || event.key === '0') {
        post('/api/clear', selected);
    }
});

document.querySelectorAll('[data-difficulty]').forEach((button) => {
    button.addEventListener('click', () => {
        post('/api/game', { difficulty: button.dataset.difficulty });
    });
});

document.getElementById('undo').addEventListener('click', () => post('/api/undo'));

buildBoard();
call('/api/game');
setInterval(() => call('/api/game'), POLL_INTERVAL_MS);
