'use client';

import Link from 'next/link';
import {
  Book,
  BookOpen,
  CircleCheck,
  CircleX,
  ClipboardList,
  House,
  Info,
  ListChecks,
  RotateCcw,
  Tag,
  Trophy,
} from 'lucide-react';
import type { Attempt } from '@/lib/types';

const DIFF_BADGE: Record<string, { text: string; cls: string }> = {
  easy: { text: 'EASY', cls: 'border border-line text-ink-soft' },
  average: { text: 'AVERAGE', cls: 'border border-line text-ink-soft' },
  difficult: { text: 'DIFFICULT', cls: 'border border-line text-ink-soft' },
};

export function ResultsView({ attempt, review = false }: { attempt: Attempt; review?: boolean }) {
  const { score, correct_count, incorrect_count, total_questions, results } = attempt;
  const topic = attempt.topic && attempt.topic !== 'all_topics' ? attempt.topic : undefined;
  const subtopic = attempt.subtopic;

  return (
    <main className="container mx-auto flex-grow px-4 py-8">
      <div className="mx-auto max-w-4xl animate-fade-in">
        <div className="sheet p-6 sm:p-8">
          <div className="mb-6 flex items-start justify-between gap-4">
            <span className="field-label mb-0">RESULT SLIP</span>
            <span className="readout uppercase">{attempt.quiz_type}</span>
          </div>

          <div className="mb-8 text-center">
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center border-2 border-ink">
              {score >= 80 ? (
                <Trophy className="h-10 w-10 text-pass" aria-hidden />
              ) : score >= 60 ? (
                <CircleCheck className="h-10 w-10 text-pass" aria-hidden />
              ) : (
                <BookOpen className="h-10 w-10 text-ink" aria-hidden />
              )}
            </div>
            <h2 className="mb-4 text-3xl font-bold text-ink sm:text-4xl">
              {review ? 'Quiz Review' : 'Quiz Complete!'}
            </h2>
            <div
              className={`num mb-4 text-6xl font-bold ${
                score >= 80 ? 'text-pass' : score >= 60 ? 'text-warn' : 'text-mark'
              }`}
            >
              {score}%
            </div>
            <p className="text-xl text-ink-soft">
              {score >= 80
                ? "Excellent! You've mastered this topic!"
                : score >= 60
                  ? 'Good job! Keep practicing to improve!'
                  : "Keep studying! You'll get better!"}
            </p>
            {attempt.user_name && (
              <p className="mt-2 text-sm text-ink-soft">
                {attempt.user_name} ·{' '}
                <span className="num">{new Date(attempt.created_at).toLocaleString()}</span>
              </p>
            )}
          </div>

          <div className="mb-8 grid grid-cols-3 divide-x divide-line border border-line">
            <div className="bg-white p-4 text-center">
              <CircleCheck className="mx-auto mb-2 h-5 w-5 text-pass" aria-hidden />
              <div className="num text-2xl font-bold text-pass">{correct_count}</div>
              <div className="field-label mb-0">Correct</div>
            </div>
            <div className="bg-white p-4 text-center">
              <CircleX className="mx-auto mb-2 h-5 w-5 text-mark" aria-hidden />
              <div className="num text-2xl font-bold text-mark">{incorrect_count}</div>
              <div className="field-label mb-0">Incorrect</div>
            </div>
            <div className="bg-white p-4 text-center">
              <ListChecks className="mx-auto mb-2 h-5 w-5 text-ink" aria-hidden />
              <div className="num text-2xl font-bold text-ink">{total_questions}</div>
              <div className="field-label mb-0">Total</div>
            </div>
          </div>

          <div className="mb-8">
            <h3 className="mb-4 flex items-center gap-2 text-2xl font-bold text-ink">
              <ClipboardList className="h-5 w-5 text-ink" aria-hidden />
              Detailed Results
            </h3>
            <div className="space-y-4">
              {results.map((r, i) => (
                <div
                  key={i}
                  className={`border border-line p-4 ${r.is_correct ? 'bg-white' : 'bg-mark-wash'}`}
                >
                  <div className="mb-3 flex items-start gap-3">
                    {r.is_correct ? (
                      <CircleCheck className="mt-0.5 h-6 w-6 shrink-0 text-pass" aria-hidden />
                    ) : (
                      <CircleX className="mt-0.5 h-6 w-6 shrink-0 text-mark" aria-hidden />
                    )}
                    <div className="flex-1">
                      <h4 className="mb-2 font-bold text-ink">
                        {i + 1}. {r.question}
                      </h4>
                      {r.topic_name && (
                        <div className="mb-2 text-xs text-ink-soft">
                          <Tag className="mr-1 inline h-3.5 w-3.5" aria-hidden />
                          {r.topic_name}
                          {r.subtopic_name ? ` - ${r.subtopic_name}` : ''}
                          {r.difficulty && DIFF_BADGE[r.difficulty] && (
                            <span
                              className={`ml-2 inline-block px-1.5 py-0.5 text-[10px] font-semibold tracking-wide ${DIFF_BADGE[r.difficulty].cls}`}
                            >
                              {DIFF_BADGE[r.difficulty].text}
                            </span>
                          )}
                        </div>
                      )}
                      <div className="space-y-1 text-sm">
                        {r.options?.length ? (
                          <>
                            <p className="text-ink">
                              <span className="font-semibold">Your answer:</span>{' '}
                              <span className={r.is_correct ? 'text-pass' : 'text-mark'}>
                                {r.user_answer !== '' && r.user_answer !== undefined
                                  ? r.options[Number(r.user_answer)]
                                  : 'Not answered'}
                              </span>
                            </p>
                            {!r.is_correct && (
                              <p className="text-ink">
                                <span className="font-semibold">Correct answer:</span>{' '}
                                <span className="text-pass">
                                  {r.options[Number(r.correct_answer)]}
                                </span>
                              </p>
                            )}
                          </>
                        ) : (
                          <>
                            <p className="text-ink">
                              <span className="font-semibold">Your answer:</span>{' '}
                              <span
                                className={`num ${r.is_correct ? 'text-pass' : 'text-mark'}`}
                              >
                                {r.user_answer ? `"${r.user_answer}"` : 'Not answered'}
                              </span>
                            </p>
                            {!r.is_correct && (
                              <p className="text-ink">
                                <span className="font-semibold">Correct answer:</span>{' '}
                                <span className="num text-pass">
                                  &quot;{r.correct_answer}&quot;
                                </span>
                              </p>
                            )}
                          </>
                        )}
                        {r.explanation && (
                          <p className="mt-2 text-sm italic text-ink-soft">
                            <Info className="mr-1 inline h-3.5 w-3.5" aria-hidden />
                            {r.explanation}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="flex flex-wrap justify-center gap-4">
            {attempt.quiz_type === 'elimination' && !topic && (
              <Link href="/quiz/elimination" className="btn btn-pencil">
                <RotateCcw className="h-4 w-4" aria-hidden />
                Try Elimination Again
              </Link>
            )}
            {attempt.quiz_type === 'finals' && !topic && (
              <Link href="/quiz/finals" className="btn btn-pencil">
                <RotateCcw className="h-4 w-4" aria-hidden />
                Try Finals Again
              </Link>
            )}
            {topic && subtopic && (
              <>
                <Link
                  href={`/mode-selection?topic=${topic}&subtopic=${subtopic}`}
                  className="btn btn-pencil"
                >
                  <RotateCcw className="h-4 w-4" aria-hidden />
                  Change Mode
                </Link>
                <Link href={`/topics/${topic}`} className="btn btn-line">
                  <ListChecks className="h-4 w-4" aria-hidden />
                  Choose Subtopic
                </Link>
              </>
            )}
            <Link href="/topics" className="btn btn-line">
              <Book className="h-4 w-4" aria-hidden />
              Browse Topics
            </Link>
            <Link href="/" className="btn btn-line">
              <House className="h-4 w-4" aria-hidden />
              Home
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}
