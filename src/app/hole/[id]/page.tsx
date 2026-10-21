import { loadChallenge, listChallengeIds } from "@/lib/config";
import ChallengeView from "./challenge-view";

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

  return <ChallengeView challenge={challenge} holeCount={holeCount} />;
}
