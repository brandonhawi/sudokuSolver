/** Client for the mlflow scoring server (proxied at /api by the Vite dev server). */

export type CellPrediction = {
  cell: number
  /** probabilities for digits 1..9 */
  probs: number[]
}

/** Ask the model for digit probabilities at each query cell, in one request. */
export async function predictCells(board: number[], cells: number[]): Promise<CellPrediction[]> {
  const payload = {
    dataframe_split: {
      columns: ['board', 'query_cell'],
      data: cells.map((cell) => [board, cell]),
    },
  }
  const res = await fetch('/api/invocations', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    throw new Error(`scoring server returned ${res.status}: ${await res.text()}`)
  }
  const body: { predictions: number[][] } = await res.json()
  return cells.map((cell, i) => ({ cell, probs: body.predictions[i] }))
}
