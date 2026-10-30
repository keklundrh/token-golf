import { describe, it, expect } from "vitest";
import { renderPrompt, resolveSkillPrompts, modelFor } from "./llm";
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

  it("substitutes {user} with the player's user id", () => {
    const challenge = loadChallenge(4);
    const option = challenge.options[1];
    const prompt = renderPrompt(option, challenge.question, skills, "player-abc-1");
    expect(prompt).toContain("player-abc-1");
    expect(prompt).not.toContain("{user}");
  });

  it("leaves {user} untouched when no user id is passed (badge display paths)", () => {
    const challenge = loadChallenge(4);
    const option = challenge.options[1];
    const prompt = renderPrompt(option, challenge.question, skills);
    // no user: the placeholder stays (display paths never render it)
    expect(prompt).toContain("{user}");
  });

  it("renders different users with different prompts but identical structure", () => {
    const challenge = loadChallenge(4);
    const a = renderPrompt(challenge.options[1], challenge.question, skills, "user-a");
    const b = renderPrompt(challenge.options[1], challenge.question, skills, "user-b");
    expect(a).not.toBe(b);
    expect(a.replace("user-a", "user-b")).toBe(b);
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

describe("modelFor", () => {
  const ORIGINAL = {
    CAI_URL: process.env.AI_BU_CAI_BASE_URL,
    CAI_KEY: process.env.AI_BU_CAI_API_KEY,
    TMM_URL: process.env.AI_BU_TMM_BASE_URL,
    TMM_KEY: process.env.AI_BU_TMM_API_KEY,
  };

  function withEnv(env: Record<string, string | undefined>, run: () => void): void {
    for (const k of Object.keys(ORIGINAL)) delete process.env[k];
    for (const [k, v] of Object.entries(env)) if (v !== undefined) process.env[k] = v;
    try {
      run();
    } finally {
      for (const [k, v] of Object.entries(ORIGINAL)) {
        if (v === undefined) delete process.env[k];
        else process.env[k] = v;
      }
    }
  }

  it("maps ai-bu-cai prefix to a client built from AI_BU_CAI_* env", () => {
    withEnv(
      { AI_BU_CAI_BASE_URL: "https://litemaas.example.com/v1", AI_BU_CAI_API_KEY: "k1" },
      () => {
        const model = modelFor("ai-bu-cai/Qwen3.8-27B") as {
          provider: string;
          modelId: string;
        };
        expect(model.provider).toContain("ai-bu-cai");
        expect(model.modelId).toBe("Qwen3.8-27B");
      },
    );
  });

  it("maps ai-bu-tmm prefix to a client built from AI_BU_TMM_* env", () => {
    withEnv(
      { AI_BU_TMM_BASE_URL: "https://maas.example.com/v1", AI_BU_TMM_API_KEY: "k2" },
      () => {
        const model = modelFor(
          "ai-bu-tmm/publishers/prelude-maas/models/glm-53-flash",
        ) as { provider: string; modelId: string };
        expect(model.provider).toContain("ai-bu-tmm");
        expect(model.modelId).toBe("publishers/prelude-maas/models/glm-53-flash");
      },
    );
  });

  it("keeps the full model id when it contains slashes", () => {
    withEnv({ AI_BU_TMM_BASE_URL: "https://x/v1" }, () => {
      expect((modelFor("ai-bu-tmm/a/b/c") as { modelId: string }).modelId).toBe("a/b/c");
    });
  });

  it("throws on unsupported providers", () => {
    expect(() => modelFor("anthropic-x/m")).toThrow("unsupported provider: anthropic-x");
    expect(() => modelFor("no-slash")).toThrow("unsupported provider: no-slash");
  });
});
