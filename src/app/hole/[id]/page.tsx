import { loadChallenge, listChallengeIds, loadSkills, loadPricing, type ModelPrice } from "@/lib/config";
import type { ModelRates } from "@/lib/currency";
import ChallengeView from "./challenge-view";

/** Per-option resolved model rates for the pre-swing price line (#8). */
function ratesFor(
  modelSpec: string,
  pricing: Record<string, ModelPrice>,
): ModelRates {
  const price = pricing[modelSpec];
  if (!price) {
    throw new Error(`no pricing for model: ${modelSpec}`);
  }
  return {
    inputPerMtok: price.input_per_mtok,
    outputPerMtok: price.output_per_mtok,
    reasoningPerMtok: price.reasoning_per_mtok,
  };
}

export function buildOptionRates(
  options: Array<{ id: string; model?: string }>,
  challengeModel: string,
  pricing: Record<string, ModelPrice>,
): Record<string, { modelId: string; rates: ModelRates }> {
  const out: Record<string, { modelId: string; rates: ModelRates }> = {};
  for (const option of options) {
    const modelSpec = option.model ?? challengeModel;
    out[option.id] = { modelId: modelSpec, rates: ratesFor(modelSpec, pricing) };
  }
  return out;
}

export function generateStaticParams(): Array<{ id: string }> {
  return listChallengeIds().map((id) => ({ id: String(id) }));
}

export default async function Hole({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const challengeId = Number(id);
  const challenge = loadChallenge(challengeId);
  const holeCount = listChallengeIds().length;
  const pricing = loadPricing().models;
  const optionRates = buildOptionRates(challenge.options, challenge.model, pricing);

  return (
    <ChallengeView
      key={challengeId}
      challenge={challenge}
      holeCount={holeCount}
      skills={loadSkills()}
      optionRates={optionRates}
    />
  );
}
