import { createOpenAI } from "@ai-sdk/openai";
import { createAnthropic } from "@ai-sdk/anthropic";
import { type LanguageModel } from "ai";
import type { Option } from "@/lib/config";

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

export function renderPrompt(option: Option, question: string): string {
  return option.prompt.replaceAll("{question}", question);
}

