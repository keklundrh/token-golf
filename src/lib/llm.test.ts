import { describe, it, expect } from "vitest";
import { renderPrompt, resolveSkillPrompts } from "./llm";
import { loadChallenge, loadSkills, type Skills } from "./config";

const skills = loadSkills();

describe("renderPrompt", () => {
  it("substitutes the question into the option template", () => {
    const challenge = loadChallenge(1);
    const prompt = renderPrompt(challenge.options[0], "Why is the sky blue", skills);
    expect(prompt).toContain("Why is the sky blue");
    expect(prompt).not.toContain("{question}");
  });

  it("renders every option without leaving placeholders", () => {
    const challenge = loadChallenge(1);
    for (const option of challenge.options) {
      expect(renderPrompt(option, "test question", skills)).not.toContain("{question}");
    }
  });

  it("leaves no-skills options unchanged", () => {
    const challenge = loadChallenge(1);
    const option = challenge.options[0];
    expect(renderPrompt(option, "Q", skills)).toBe(option.prompt.replaceAll("{question}", "Q"));
  });
});

describe("skills", () => {
  it("loads the shared skills registry", () => {
    expect(Object.keys(skills)).toContain("web-search");
  });

  it("prepends selected skills to the prompt in listed order", () => {
    const challenge = loadChallenge(1);
    const option = { ...challenge.options[0], skills: ["web-search", "cite-sources"] };
    const prompt = renderPrompt(option, "Q", skills);
    const searchIdx = prompt.indexOf("Search the web");
    const citeIdx = prompt.indexOf("Cite every source");
    const promptIdx = prompt.indexOf(option.prompt.trim().slice(0, 20));
    expect(searchIdx).toBeGreaterThanOrEqual(0);
    expect(citeIdx).toBeGreaterThan(searchIdx);
    expect(promptIdx).toBeGreaterThan(citeIdx);
    // the option's own prompt follows the skills, with {question} substituted
    expect(prompt).toContain(": Q");
  });

  it("resolves skill prompts for badge display", () => {
    const challenge = loadChallenge(1);
    const option = { ...challenge.options[0], skills: ["web-search"] };
    expect(resolveSkillPrompts(option, skills)).toHaveLength(1);
  });

  it("throws on unknown skill id", () => {
    const challenge = loadChallenge(1);
    const option = { ...challenge.options[0], skills: ["no-such-skill"] };
    expect(() => renderPrompt(option, "Q", skills)).toThrow("unknown skill: no-such-skill");
  });

  it("accepts empty skills list", () => {
    const challenge = loadChallenge(1);
    const option = { ...challenge.options[0], skills: [] };
    expect(resolveSkillPrompts(option, skills)).toEqual([]);
  });
});
