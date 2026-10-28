import { defineConfig } from "vitest/config";
import path from "node:path";
import { mkdirSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

// Test isolation: temp DB + temp config dir for every vitest worker, set in
// the config so they exist before any module reads process.env.
process.env.DATABASE_PATH = join(mkdtempSync(join(tmpdir(), "tg-vitest-")), "test.db");
// env config dir with a broken hole-998 (thinking: "ultra" fails the enum)
process.env.PRACTICE_CONFIG_DIR = mkdtempSync(join(tmpdir(), "tg-vitest-config-"));
mkdirSync(join(process.env.PRACTICE_CONFIG_DIR, "challenges", "hole-998"), { recursive: true });
writeFileSync(
  join(process.env.PRACTICE_CONFIG_DIR, "challenges", "hole-998", "challenge.yaml"),
  'id: 998\nquestion: q\noptions:\n  - id: a\n    label: A\n    detail: d\n    prompt: p\n    thinking: "ultra"\n',
);

export default defineConfig({
  test: {
    environment: "node",
    include: ["src/**/*.test.{ts,tsx}"],
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
