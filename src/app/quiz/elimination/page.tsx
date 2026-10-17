import type { Metadata } from 'next';
import { Suspense } from 'react';
import { loadEliminationPool, loadQuestions, sanitize } from '@/lib/questions';
import { EliminationQuiz } from '@/components/EliminationQuiz';
import type { RawQuestion } from '@/lib/types';

export const metadata: Metadata = { title: 'Elimination Mode' };

export default function EliminationPage({
  searchParams,
}: {
  searchParams: Promise<{ topic?: string; subtopic?: string }>;
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
  searchParams: Promise<{ topic?: string; subtopic?: string }>;
}) {
  const { topic, subtopic } = await searchParams;
  const review = Boolean(topic && subtopic);

  let raw: RawQuestion[];
  try {
    raw = review
      ? await loadQuestions(topic!, subtopic!, 10, 'elimination')
      : await loadEliminationPool(100);
  } catch {
    raw = [];
  }

  return (
    <EliminationQuiz
      questions={sanitize(raw, 'elimination')}
      topic={review ? topic : undefined}
      subtopic={review ? subtopic : undefined}
      difficulty={review ? 'medium' : 'mixed'}
    />
  );
}
