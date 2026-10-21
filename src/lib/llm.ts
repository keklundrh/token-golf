import { createOpenAI } from "@ai-sdk/openai";
import { createAnthropic } from "@ai-sdk/anthropic";
import { type LanguageModel } from "ai";
import type { Option, Skills } from "@/lib/config";

export function modelFor(name: string): LanguageModel {
  const [provider, ...rest] = name.split("/");
  const modelId = rest.join("/");
  if (provider === "openai") {
    return createOpenAI()(modelId);
  }
  if (provider === "anthropic") {
    return createAnthropic()(modelId);
  }
  throw new Error(`unsupported provider: ${provider}`);
}

export function resolveSkillPrompts(
  option: Option,
  skills: Skills,
): string[] {
  if (!option.skills || option.skills.length === 0) return [];
  return option.skills.map((id) => {
    const skill = skills[id];
    if (!skill) throw new Error(`unknown skill: ${id}`);
    return skill.prompt.trim();
  });
}

export function renderPrompt(option: Option, question: string, skills: Skills): string {
  const skillText = resolveSkillPrompts(option, skills);
  const composed =
    skillText.length > 0 ? `${skillText.join("\n\n")}\n\n${option.prompt}` : option.prompt;
  return composed.replaceAll("{question}", question);
}

