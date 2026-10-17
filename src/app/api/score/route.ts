import { NextRequest, NextResponse } from 'next/server';
import { loadQuestions, scoreQuiz } from '@/lib/questions';
import type { QuizMode, RawQuestion } from '@/lib/types';

const SLUG = /^[a-z0-9_-]+$/i;

interface ScoredRef {
  /** Client-side composite key — used to look up the submitted answer */
  key: string;
  id: string;
  topic: string;
  subtopic: string;
  difficulty?: string;
}

/**
 * POST /api/score
 * Body: { mode, questions: [{id, topic, subtopic, difficulty?}], answers: {id: answer} }
 *
 * The server reloads the referenced questions from data/ by id (never trusting
 * client-supplied answers), grades, and returns full results including the
 * correct answers and explanations for the results/review pages.
 */
export async function POST(request: NextRequest) {
  let body: { mode?: QuizMode; questions?: ScoredRef[]; answers?: Record<string, string> };
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: 'Invalid JSON' }, { status: 400 });
  }

  const { mode, questions: refs, answers } = body;
  if (
    (mode !== 'elimination' && mode !== 'finals') ||
    !Array.isArray(refs) ||
    refs.length === 0 ||
    refs.length > 500 ||
    refs.some(
      (r) =>
        !r ||
        typeof r.key !== 'string' ||
        typeof r.id !== 'string' ||
        !SLUG.test(r.topic) ||
        !SLUG.test(r.subtopic) ||
        (r.difficulty !== undefined && !SLUG.test(r.difficulty))
    ) ||
    answers === null ||
    typeof answers !== 'object'
  ) {
    return NextResponse.json({ error: 'Invalid request' }, { status: 400 });
  }

  try {
    // Group refs by their source file; question ids repeat across files, so
    // index by composite group+id — a ref can only match its own file's questions
    const fileKey = (r: ScoredRef) =>
      [r.topic, r.subtopic, mode === 'finals' ? r.difficulty : ''].join('|');
    const raw = new Map<string, RawQuestion>();
    const groups = new Map<string, ScoredRef[]>();
    for (const ref of refs) {
      const list = groups.get(fileKey(ref)) ?? [];
      list.push(ref);
      groups.set(fileKey(ref), list);
    }

    for (const [key, group] of groups) {
      const { topic, subtopic, difficulty } = group[0];
      // Load the whole file (large count) so every referenced id is found
      const loaded = await loadQuestions(topic, subtopic, 1000, mode, difficulty);
      for (const q of loaded) raw.set(`${key}|${q.id}`, q);
    }

    const ordered: RawQuestion[] = [];
    for (const r of refs) {
      const q = raw.get(`${fileKey(r)}|${r.id}`);
      if (!q) {
        return NextResponse.json({ error: 'Unknown question reference' }, { status: 400 });
      }
      ordered.push(q);
    }

    // Answers are keyed by the client's composite ref key, not the raw question id
    return NextResponse.json(
      scoreQuiz(ordered, answers as Record<string, string>, mode, refs.map((r) => r.key))
    );
  } catch {
    return NextResponse.json({ error: 'Scoring failed' }, { status: 500 });
  }
}
