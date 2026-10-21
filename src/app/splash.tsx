"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export interface HomepageContent {
  title: string;
  intro: string;
  howToPlay: string[];
  cta: { label: string; target: string };
}

export function useIdentity() {
  const [username, setUsername] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/user", { method: "POST" })
      .then(async (res) => {
        if (!res.ok) throw new Error(`identity failed: ${res.status}`);
        const data = await res.json();
        setUsername(data.username);
      })
      .catch((e: Error) => setError(e.message));
  }, []);

  return { username, error };
}

export default function Splash({ content }: { content: HomepageContent }) {
  const { username, error } = useIdentity();
  const router = useRouter();
  const [starting, setStarting] = useState(false);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-white px-6 text-black">
      <div className="flex w-full max-w-md flex-col items-center gap-8 text-center">
        <h1 className="text-4xl font-semibold tracking-tight">{content.title}</h1>
        <p className="text-lg leading-8 text-zinc-600">{content.intro}</p>
        <ul className="flex w-full flex-col gap-2 text-left text-base text-zinc-700">
          {content.howToPlay.map((step, i) => (
            <li key={i} className="flex gap-3">
              <span className="font-mono text-zinc-400">{i + 1}.</span>
              <span>{step}</span>
            </li>
          ))}
        </ul>
        <p className="text-sm text-zinc-500">
          {error
            ? `Failed to get player name: ${error}`
            : username
              ? `Playing as ${username}`
              : "Getting your player name…"}
        </p>
        <button
          type="button"
          disabled={!username || starting}
          onClick={() => {
            setStarting(true);
            router.push(content.cta.target);
          }}
          className="h-12 w-full rounded-full bg-green-700 text-base font-medium text-white transition-colors hover:bg-green-800 disabled:opacity-40"
        >
          {starting ? "Teeing off…" : content.cta.label}
        </button>
      </div>
    </main>
  );
}
