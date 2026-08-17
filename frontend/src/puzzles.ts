export type Preset = {
  name: string
  puzzle: string
  solution: string
}

/** Boards built from Kaggle-dataset solutions with k cells blanked (0 = blank).
 * The model trains on 1-20 blanks, so presets stay in that range. */
export const PRESETS: Preset[] = [
  {
    name: '12 blanks',
    puzzle:
      '864371009325849061971265843436190587198657032250483910089734125703528694502016308',
    solution:
      '864371259325849761971265843436192587198657432257483916689734125713528694542916378',
  },
  {
    name: '16 blanks',
    puzzle:
      '346109058187523904529608371065800417470916005813754609798061503631000792254397186',
    solution:
      '346179258187523964529648371965832417472916835813754629798261543631485792254397186',
  },
  {
    name: '20 blanks',
    puzzle:
      '690120384108450672724830905050064709003981546046503021317692450489700263562340190',
    solution:
      '695127384138459672724836915851264739273981546946573821317692458489715263562348197',
  },
]

export function parseBoard(text: string): number[] | null {
  const digits = text.replace(/\D/g, '')
  if (digits.length !== 81) return null
  return [...digits].map(Number)
}
