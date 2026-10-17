import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { Suspense } from 'react';
import { loadFinalsPool, loadQuestions, sanitize } from '@/lib/questions';
import { FinalsQuiz } from '@/components/FinalsQuiz';
import type { RawQuestion } from '@/lib/types';

export const metadata: Metadata = { title: 'Finals Mode' };

const VALID_DIFFICULTIES = new Set(['easy', 'average', 'difficult']);

export default function FinalsPage({
  searchParams,
}: {
  searchParams: Promise<{ topic?: string; subtopic?: string; difficulty?: string }>;
}) {
  return (
    <Suspense>
      <Quiz searchParams={searchParams} />
    </Suspense>
  );
}

async function Quiz({
  searchParams,
}: {
  searchParams: Promise<{ topic?: string; subtopic?: string; difficulty?: string }>;
}) {
  const { topic, subtopic, difficulty: rawDifficulty } = await searchParams;
  const difficulty = VALID_DIFFICULTIES.has(rawDifficulty ?? '')
    ? (rawDifficulty as 'easy' | 'average' | 'difficult')
    : 'average';
  const review = Boolean(topic && subtopic);

  let raw: RawQuestion[];
  try {
    raw = review
      ? await loadQuestions(topic!, subtopic!, 10, 'finals', difficulty)
      : await loadFinalsPool(30);
  } catch {
    notFound();
  }
  if (raw.length === 0) notFound();

  return (
    <FinalsQuiz
      questions={sanitize(raw, 'finals')}
      topic={review ? topic : undefined}
      subtopic={review ? subtopic : undefined}
      difficulty={review ? difficulty : 'mixed'}
    />
  );
}
