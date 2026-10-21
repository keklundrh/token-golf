import { describe, it, expect } from "vitest";
import { renderPrompt } from "./llm";
import { loadChallenge } from "./config";

describe("renderPrompt", () => {
  it("substitutes the question into the option template", () => {
    const challenge = loadChallenge(1);
    const prompt = renderPrompt(challenge.options[0], "Why is the sky blue");
    expect(prompt).toContain("Why is the sky blue");
    expect(prompt).not.toContain("{question}");
  });

  it("renders every option without leaving placeholders", () => {
    const challenge = loadChallenge(1);
    for (const option of challenge.options) {
      expect(renderPrompt(option, "test question")).not.toContain("{question}");
    }
  });
});
