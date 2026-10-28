import { readFileSync, readdirSync, existsSync } from "node:fs";
import { join } from "node:path";
import { parse } from "yaml";
import { z } from "zod";

const CONFIG_DIR = join(process.cwd(), "config");

const CtaSchema = z.object({
  label: z.string().min(1),
  target: z.string().min(1),
});

const UsernameSchema = z.object({
  players: z.array(z.string().min(1)).min(1),
  courses: z.array(z.string().min(1)).min(1),
  colors: z.array(z.string().min(1)).min(1),
});

export const HomepageSchema = z.object({
  title: z.string().min(1),
  intro: z.string().min(1),
  howToPlay: z.array(z.string().min(1)),
  cta: CtaSchema,
  username: UsernameSchema,
});

export const OptionSchema = z.object({
  id: z.string().min(1),
  label: z.string().min(1),
  detail: z.string().min(1),
  prompt: z.string().min(1),
  model: z.string().min(1).optional(),
  thinking: z.union([z.boolean(), z.enum(["low", "medium", "high"])]).optional(),
  skills: z.array(z.string().min(1)).optional(),
});

export const SkillSchema = z.object({
  id: z.string().min(1),
  label: z.string().min(1),
  prompt: z.string().min(1),
});

export const SkillsSchema = z.record(z.string(), SkillSchema);
export const SkillsFileSchema = z.object({ skills: SkillsSchema });

export const ChallengeSchema = z.object({
  id: z.number().int().positive(),
  question: z.string().min(1),
  model: z.string().min(1),
  options: z.array(OptionSchema).min(1),
});

const ModelPriceSchema = z.object({
  input_per_mtok: z.number().nonnegative(),
  output_per_mtok: z.number().nonnegative(),
  reasoning_per_mtok: z.number().nonnegative().nullable(),
});

export const PricingSchema = z.object({
  models: z.record(z.string(), ModelPriceSchema),
});

export type Homepage = z.infer<typeof HomepageSchema>;
export type Challenge = z.infer<typeof ChallengeSchema>;
export type Option = z.infer<typeof OptionSchema>;
export type Pricing = z.infer<typeof PricingSchema>;
export type ModelPrice = z.infer<typeof ModelPriceSchema>;
export type Skill = z.infer<typeof SkillSchema>;
export type Skills = z.infer<typeof SkillsSchema>;

function loadYaml<T>(path: string, schema: z.ZodType<T>): T {
  const raw = parse(readFileSync(path, "utf8"));
  const result = schema.safeParse(raw);
  if (!result.success) {
    throw new Error(`Invalid config at ${path}: ${result.error.message}`);
  }
  return result.data;
}

export function loadHomepage(): Homepage {
  return loadYaml(join(CONFIG_DIR, "homepage.yaml"), HomepageSchema);
}

export function loadPricing(): Pricing {
  return loadYaml(join(CONFIG_DIR, "pricing.yaml"), PricingSchema);
}

function holeDir(challengeId: number): string {
  return `hole-${String(challengeId).padStart(3, "0")}`;
}

export function loadSkills(): Skills {
  return loadYaml(join(CONFIG_DIR, "skills.yaml"), SkillsFileSchema).skills;
}

export function loadChallenge(challengeId: number, configDir: string = CONFIG_DIR): Challenge {
  return loadYaml(
    join(configDir, "challenges", holeDir(challengeId), "challenge.yaml"),
    ChallengeSchema,
  );
}

export function listChallengeIds(): number[] {
  const base = join(CONFIG_DIR, "challenges");
  if (!existsSync(base)) return [];
  return readdirSync(base, { withFileTypes: true })
    .filter((e) => e.isDirectory() && /^hole-\d{3}$/.test(e.name))
    .map((e) => Number(e.name.slice(5)))
    .sort((a, b) => a - b);
}

export const HOLE_DIR = holeDir;
