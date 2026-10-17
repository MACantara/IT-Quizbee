import { NextRequest, NextResponse } from 'next/server';
import { loadQuestions, scoreQuiz } from '@/lib/questions';
import type { QuizMode, RawQuestion } from '@/lib/types';

interface ScoredRef {
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

  const { mode, questions: refs, answers = {} } = body;
  if ((mode !== 'elimination' && mode !== 'finals') || !Array.isArray(refs) || refs.length === 0) {
    return NextResponse.json({ error: 'Invalid request' }, { status: 400 });
  }

  try {
    // Group refs by their source file, load each file once, index by question id
    const raw = new Map<string, RawQuestion>();
    const groups = new Map<string, ScoredRef[]>();
    for (const ref of refs) {
      const key = [ref.topic, ref.subtopic, mode === 'finals' ? ref.difficulty : ''].join('|');
      const list = groups.get(key) ?? [];
      list.push(ref);
      groups.set(key, list);
    }

    for (const group of groups.values()) {
      const { topic, subtopic, difficulty } = group[0];
      // Load the whole file (large count) so every referenced id is found
      const loaded = await loadQuestions(topic, subtopic, 1000, mode, difficulty);
      for (const q of loaded) raw.set(String(q.id), q);
    }

    const ordered = refs
      .map((r) => raw.get(String(r.id)))
      .filter((q): q is RawQuestion => q !== undefined);
    if (ordered.length === 0) {
      return NextResponse.json({ error: 'No matching questions found' }, { status: 404 });
    }

    return NextResponse.json(scoreQuiz(ordered, answers, mode));
  } catch (e) {
    return NextResponse.json(
      { error: e instanceof Error ? e.message : 'Scoring failed' },
      { status: 500 }
    );
  }
}
