import { NextRequest, NextResponse } from 'next/server';
import {
  loadEliminationPool,
  loadFinalsPool,
  loadQuestions,
  sanitize,
} from '@/lib/questions';
import type { QuizMode } from '@/lib/types';

/**
 * GET /api/questions?mode=elimination|finals[&topic=..&subtopic=..&difficulty=..]
 *
 * Review mode (topic+subtopic given): 10 questions for that subtopic.
 * Full mode (no topic): 100 elimination questions / 30 finals questions across all topics.
 * Responses are sanitized — correct answers never leave the server.
 */
export async function GET(request: NextRequest) {
  const params = request.nextUrl.searchParams;
  const mode = params.get('mode') as QuizMode | null;
  const topic = params.get('topic');
  const subtopic = params.get('subtopic');
  const difficulty = params.get('difficulty') ?? 'average';

  if (mode !== 'elimination' && mode !== 'finals') {
    return NextResponse.json({ error: 'Invalid mode' }, { status: 400 });
  }

  try {
    const review = Boolean(topic && subtopic);
    let questions;
    if (review) {
      questions = await loadQuestions(topic!, subtopic!, 10, mode, difficulty);
    } else if (mode === 'elimination') {
      questions = await loadEliminationPool(100);
    } else {
      questions = await loadFinalsPool(30);
    }

    return NextResponse.json({
      mode,
      topic: review ? topic : 'all_topics',
      subtopic: review ? subtopic : undefined,
      difficulty: review ? difficulty : 'mixed',
      questions: sanitize(questions, mode),
    });
  } catch (e) {
    return NextResponse.json(
      { error: e instanceof Error ? e.message : 'Failed to load questions' },
      { status: 404 }
    );
  }
}
