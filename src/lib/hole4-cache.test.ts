import { describe, it, expect } from "vitest";
import { loadChallenge, loadSkills } from "./config";
import { renderPrompt } from "./llm";
const skills = loadSkills();

describe("hole 4 cache challenge", () => {
  const challenge = loadChallenge(4);

  it("has one fresh option and two caching options", () => {
    expect(challenge.options.map((o) => o.id)).toEqual(["fresh", "cache-first", "cache-second"]);
    expect(challenge.options[0].caching).toBeUndefined();
    expect(challenge.options[1].caching).toBe(true);
    expect(challenge.options[2].caching).toBe(true);
  });

  it("renders the two cached options with byte-identical prompts", () => {
    // The cache read only hits when the prefix is byte-identical: the two
    // cached options' prompts must render to the same string.
    const first = renderPrompt(challenge.options[1], challenge.question, skills);
    const second = renderPrompt(challenge.options[2], challenge.question, skills);
    expect(second).toBe(first);
  });

  it("renders the fresh option with the same prefix as the cached options", () => {
    // Same reference block across all three: the fresh option is the
    // honest baseline for the same content.
    const fresh = renderPrompt(challenge.options[0], challenge.question, skills);
    const cached = renderPrompt(challenge.options[1], challenge.question, skills);
    expect(cached.startsWith(fresh.replace(/\n[^\n]*$/, ""))).toBe(true);
  });

  it("includes the reference doc in the rendered prompt (≥1,024 tok for Anthropic's cache threshold)", () => {
    const rendered = renderPrompt(challenge.options[1], challenge.question, skills);
    expect(rendered).toContain("<reference>");
    expect(rendered).toContain("cache_control");
    // Anthropic's minimum cacheable length is ~1,024 tokens on Sonnet —
    // the reference block must clear it or caching silently won't engage.
    expect(rendered.length).toBeGreaterThanOrEqual(4 * 1_024);
  });

  it("leaves no placeholder in any rendered prompt", () => {
    for (const option of challenge.options) {
      expect(renderPrompt(option, challenge.question, skills)).not.toContain("{question}");
      expect(renderPrompt(option, challenge.question, skills)).not.toContain("{context}");
    }
  });
});
