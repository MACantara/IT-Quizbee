import Link from 'next/link';
import { redirect } from 'next/navigation';
import { Suspense } from 'react';
import type { Metadata } from 'next';
import { ArrowLeft, Check, Trophy, Zap } from 'lucide-react';
import { getSubtopics } from '@/lib/questions';

export const metadata: Metadata = { title: 'Select Mode' };

const DIFFICULTIES = [
  { id: 'easy', label: 'EASY', time: '20s per question' },
  { id: 'average', label: 'AVERAGE', time: '30s per question' },
  { id: 'difficult', label: 'DIFFICULT', time: '40s per question' },
];

export default function ModeSelectionPage({
  searchParams,
}: {
  searchParams: Promise<{ topic?: string; subtopic?: string }>;
}) {
  return (
    <Suspense>
      <ModeSelection searchParams={searchParams} />
    </Suspense>
  );
}

async function ModeSelection({
  searchParams,
}: {
  searchParams: Promise<{ topic?: string; subtopic?: string }>;
}) {
  const { topic, subtopic } = await searchParams;
  if (!topic || !subtopic) redirect('/topics');

  let subtopicName = subtopic.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  try {
    const st = (await getSubtopics(topic)).find((s) => s.id === subtopic);
    if (st) subtopicName = st.name;
  } catch {
    redirect('/topics');
  }

  return (
    <main className="container mx-auto px-4 py-8 flex-grow">
      <div className="max-w-4xl mx-auto animate-fade-in">
        <div className="sheet p-6 sm:p-8">
          <div className="mb-6">
            <Link
              href={`/topics/${topic}`}
              className="mb-4 inline-flex items-center gap-1.5 font-semibold text-pencil"
            >
              <ArrowLeft className="h-4 w-4" aria-hidden />Back to Subtopics
            </Link>
            <h2 className="text-3xl font-bold text-ink mb-2">{subtopicName}</h2>
            <p className="text-ink-soft mb-6">Choose your game mode</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Link
              href={`/quiz/elimination?topic=${topic}&subtopic=${subtopic}`}
              className="block border border-ink bg-white p-6 transition-colors hover:border-pencil"
            >
              <div className="num mb-4 text-xs tracking-[0.2em] text-ink-soft">1</div>
              <Zap className="h-6 w-6 text-ink mb-2" aria-hidden />
              <h3 className="text-xl font-bold text-ink mb-4">Elimination Mode</h3>
              <ul className="mb-6 text-sm text-ink-soft">
                {['Competitive preliminary round', '10 questions', 'Perfect for practice'].map((t) => (
                  <li key={t} className="flex items-center gap-2 border-t border-line py-2">
                    <Check className="h-4 w-4 shrink-0 text-pass" aria-hidden />
                    <span>{t}</span>
                  </li>
                ))}
              </ul>
              <div className="btn btn-pencil w-full">Start Elimination</div>
            </Link>

            <div className="border border-ink bg-white p-6">
              <div className="num mb-4 text-xs tracking-[0.2em] text-ink-soft">2</div>
              <Trophy className="h-6 w-6 text-ink mb-2" aria-hidden />
              <h3 className="text-xl font-bold text-ink mb-4">Finals Mode</h3>
              <ul className="mb-6 text-sm text-ink-soft">
                {['Championship round', '3 difficulty levels', '10 questions per level'].map((t) => (
                  <li key={t} className="flex items-center gap-2 border-t border-line py-2">
                    <Check className="h-4 w-4 shrink-0 text-pass" aria-hidden />
                    <span>{t}</span>
                  </li>
                ))}
              </ul>
              <p className="field-label">Select Difficulty</p>
              <div className="space-y-2">
                {DIFFICULTIES.map((d) => (
                  <Link
                    key={d.id}
                    href={`/quiz/finals?topic=${topic}&subtopic=${subtopic}&difficulty=${d.id}`}
                    className="flex items-center justify-between border border-line px-4 py-3 transition-colors hover:border-pencil hover:bg-pencil-wash"
                  >
                    <span className="text-sm font-semibold uppercase">{d.label}</span>
                    <span className="num text-xs text-ink-soft">{d.time}</span>
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
