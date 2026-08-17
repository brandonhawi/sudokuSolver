import { useCallback, useRef, useState } from 'react'
import { predictCells } from './api'
import { PRESETS, parseBoard } from './puzzles'
import './App.css'

// dataviz sequential blue ramp, steps 100..700: low -> high confidence
const CONFIDENCE_RAMP = [
  '#cde2fb', '#b7d3f6', '#9ec5f4', '#86b6ef', '#6da7ec', '#5598e7', '#3987e5',
  '#2a78d6', '#256abf', '#1c5cab', '#184f95', '#104281', '#0d366b',
]

function confidenceColor(p: number): string {
  // map softmax max-prob (1/9 = chance .. 1.0) onto the ramp
  const norm = Math.max(0, Math.min(1, (p - 1 / 9) / (1 - 1 / 9)))
  return CONFIDENCE_RAMP[Math.round(norm * (CONFIDENCE_RAMP.length - 1))]
}

type Fill = { digit: number; confidence: number; correct: boolean | null }

type LastStep = { cell: number; probs: number[]; digit: number }

export default function App() {
  const [presetIdx, setPresetIdx] = useState(0)
  const [givens, setGivens] = useState<number[]>(() => parseBoard(PRESETS[0].puzzle)!)
  const [solution, setSolution] = useState<string | null>(PRESETS[0].solution)
  const [fills, setFills] = useState<Map<number, Fill>>(new Map())
  const [lastStep, setLastStep] = useState<LastStep | null>(null)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [pasteText, setPasteText] = useState('')
  const cancelRef = useRef(false)

  const board = givens.map((v, i) => fills.get(i)?.digit ?? v)
  const blanks = board.map((v, i) => (v === 0 ? i : -1)).filter((i) => i >= 0)
  const wrongCount = [...fills.values()].filter((f) => f.correct === false).length

  const loadPreset = (idx: number) => {
    cancelRef.current = true
    setPresetIdx(idx)
    setGivens(parseBoard(PRESETS[idx].puzzle)!)
    setSolution(PRESETS[idx].solution)
    setFills(new Map())
    setLastStep(null)
    setError(null)
  }

  const loadPasted = () => {
    const parsed = parseBoard(pasteText)
    if (!parsed) {
      setError('Paste needs exactly 81 digits (0 = blank).')
      return
    }
    cancelRef.current = true
    setGivens(parsed)
    setSolution(null)
    setFills(new Map())
    setLastStep(null)
    setError(null)
  }

  const reset = () => {
    cancelRef.current = true
    setFills(new Map())
    setLastStep(null)
    setError(null)
  }

  /** One solve iteration: predict every blank, fill the most confident one. */
  const step = useCallback(
    async (curBoard: number[], curFills: Map<number, Fill>) => {
      const curBlanks = curBoard.map((v, i) => (v === 0 ? i : -1)).filter((i) => i >= 0)
      if (curBlanks.length === 0) return null
      const preds = await predictCells(curBoard, curBlanks)
      const best = preds.reduce((a, b) => (Math.max(...b.probs) > Math.max(...a.probs) ? b : a))
      const digit = best.probs.indexOf(Math.max(...best.probs)) + 1
      const confidence = Math.max(...best.probs)
      const correct = solution ? Number(solution[best.cell]) === digit : null
      const nextFills = new Map(curFills)
      nextFills.set(best.cell, { digit, confidence, correct })
      setFills(nextFills)
      setLastStep({ cell: best.cell, probs: best.probs, digit })
      const nextBoard = [...curBoard]
      nextBoard[best.cell] = digit
      return { nextBoard, nextFills }
    },
    [solution],
  )

  const runStep = async () => {
    setRunning(true)
    setError(null)
    try {
      await step(board, fills)
    } catch (e) {
      setError(String(e))
    } finally {
      setRunning(false)
    }
  }

  const runSolve = async () => {
    setRunning(true)
    setError(null)
    cancelRef.current = false
    try {
      let cur: { nextBoard: number[]; nextFills: Map<number, Fill> } | null = {
        nextBoard: board,
        nextFills: fills,
      }
      while (cur && !cancelRef.current) {
        cur = await step(cur.nextBoard, cur.nextFills)
        if (cur) await new Promise((r) => setTimeout(r, 120))
      }
    } catch (e) {
      setError(String(e))
    } finally {
      setRunning(false)
    }
  }

  return (
    <main className="app">
      <h1>Sudoku Solver</h1>
      <p className="subtitle">
        One MLP, one cell at a time: every blank is scored, the most confident cell is filled.
      </p>

      <div className="controls">
        <select
          value={presetIdx}
          onChange={(e) => loadPreset(Number(e.target.value))}
          disabled={running}
        >
          {PRESETS.map((p, i) => (
            <option key={p.name} value={i}>
              {p.name}
            </option>
          ))}
        </select>
        <button onClick={runStep} disabled={running || blanks.length === 0}>
          Step
        </button>
        <button onClick={runSolve} disabled={running || blanks.length === 0}>
          Solve
        </button>
        <button onClick={reset} disabled={fills.size === 0}>
          Reset
        </button>
      </div>

      <div className="board" role="grid" aria-label="sudoku board">
        {board.map((digit, i) => {
          const fill = fills.get(i)
          const isLast = lastStep?.cell === i
          return (
            <div
              key={i}
              role="gridcell"
              className={[
                'cell',
                givens[i] !== 0 ? 'given' : '',
                fill ? 'filled' : '',
                fill?.correct === false ? 'wrong' : '',
                isLast ? 'last' : '',
              ].join(' ')}
              style={fill ? { background: confidenceColor(fill.confidence) } : undefined}
              title={
                fill
                  ? `model: ${fill.digit} (${(fill.confidence * 100).toFixed(1)}% confident)`
                  : undefined
              }
            >
              {fill?.correct === false ? (
                <>
                  <span className="guess">{digit}</span>
                  <span className="answer">{solution?.[i]}</span>
                </>
              ) : digit !== 0 ? (
                digit
              ) : (
                ''
              )}
            </div>
          )
        })}
      </div>

      <div className="legend">
        <span>low confidence</span>
        <div className="legend-ramp" />
        <span>high</span>
        {solution && (
          <span className="score">
            {fills.size - wrongCount}/{fills.size} correct
          </span>
        )}
      </div>
      {solution && wrongCount > 0 && (
        <p className="wrong-key">
          <span className="wrong-key-swatch">
            <span className="guess">5</span>
            <span className="answer">3</span>
          </span>
          = the model guessed 5 (struck out); the real answer was 3
        </p>
      )}

      {lastStep && (
        <section className="probs">
          <h2>
            Last cell (r{Math.floor(lastStep.cell / 9) + 1}c{(lastStep.cell % 9) + 1}) — digit
            probabilities
          </h2>
          <div className="prob-bars">
            {lastStep.probs.map((p, d) => (
              <div key={d} className="prob-col">
                <div
                  className={'prob-bar' + (d + 1 === lastStep.digit ? ' chosen' : '')}
                  style={{ height: `${Math.max(2, p * 120)}px` }}
                  title={`${(p * 100).toFixed(1)}%`}
                />
                <span className="prob-label">{d + 1}</span>
              </div>
            ))}
          </div>
        </section>
      )}

      <details className="paste">
        <summary>Load a custom puzzle</summary>
        <textarea
          rows={2}
          placeholder="81 digits, 0 for blanks"
          value={pasteText}
          onChange={(e) => setPasteText(e.target.value)}
        />
        <button onClick={loadPasted}>Load</button>
      </details>

      {error && <p className="error">{error}</p>}
    </main>
  )
}
