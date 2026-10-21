export interface GeneratedUsername {
  username: string;
  number: number;
}

export function generateUsername(
  players: string[],
  courses: string[],
  colors: string[],
  existing: ReadonlySet<string>,
  random: () => number = Math.random,
): GeneratedUsername {
  const pick = (arr: string[]) => arr[Math.floor(random() * arr.length)];
  for (let n = 1; n <= 999; n++) {
    const candidate = `${pick(players)}-${pick(courses)}-${pick(colors)}-${n}`;
    if (!existing.has(candidate)) {
      return { username: candidate, number: n };
    }
  }
  throw new Error("username space exhausted");
}

