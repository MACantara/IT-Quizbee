'use client';

import { useCallback, useEffect, useRef, useState, useSyncExternalStore } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Check, Tag, Zap } from 'lucide-react';
import { NameModal } from './NameModal';
import { useDialog } from './Modal';
import { saveAttempt, getUserName } from '@/lib/attempts';
import {
  clearActiveQuiz,
  loadActiveQuiz,
  saveActiveQuiz,
  setLastResultId,
} from '@/lib/active-quiz';
import type { Attempt, QuizQuestion, ScoreResult } from '@/lib/types';

const DURATION_SECONDS = 60 * 60;
const subscribe = () => () => {};

interface Props {
  questions: QuizQuestion[];
  topic?: string;
  subtopic?: string;
  difficulty?: string;
}

export function EliminationQuiz(props: Props) {
  // Gate on mount so lazy initializers can read sessionStorage (SSR renders nothing)
  const mounted = useSyncExternalStore(subscribe, () => true, () => false);
  if (!mounted) return <main className="container mx-auto px-4 py-8 flex-grow" />;
  return <QuizInner {...props} />;
}

function QuizInner({ questions, topic, subtopic, difficulty }: Props) {
  const router = useRouter();
  const { confirm, warning, dialogElement } = useDialog();

  // A saved quiz for the same mode/selection wins — refresh re-samples server-side
  const [restored] = useState(() => {
    const saved = loadActiveQuiz('elimination');
    return saved &&
      saved.topic === topic &&
      saved.subtopic === subtopic &&
      saved.difficulty === difficulty
      ? saved
      : null;
  });
  const [quizQuestions] = useState(() => restored?.questions ?? questions);
  const [started, setStarted] = useState(() => restored !== null);
  const [userName, setUserName] = useState(() => restored?.userName ?? '');
  const [answers, setAnswers] = useState<Record<string, string>>(() => restored?.answers ?? {});
  const [timeLeft, setTimeLeft] = useState(() =>
    restored
      ? Math.max(0, DURATION_SECONDS - Math.floor((Date.now() - restored.startTime) / 1000))
      : DURATION_SECONDS
  );
  const [submitting, setSubmitting] = useState(false);
  const startTimeRef = useRef(restored?.startTime ?? 0);
  const submittedRef = useRef(false);
  const latestRef = useRef({
    answers,
    warning,
    submit: async () => {},
  });

  const submit = useCallback(async () => {
    if (submittedRef.current) return;
    submittedRef.current = true;
    setSubmitting(true);
    try {
      const res = await fetch('/api/score', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mode: 'elimination',
          questions: quizQuestions.map((q) => ({
            key: q.key,
            id: q.id,
            topic: q.topic,
            subtopic: q.subtopic,
          })),
          answers: latestRef.current.answers,
        }),
      });
      if (!res.ok) throw new Error('Scoring failed');
      const scored = (await res.json()) as ScoreResult;
      const attempt: Attempt = {
        ...scored,
        id: crypto.randomUUID(),
        quiz_type: 'elimination',
        topic,
        subtopic,
        difficulty,
        user_name: userName || getUserName() || 'Anonymous',
        time_taken: Math.floor((Date.now() - startTimeRef.current) / 1000),
        created_at: new Date().toISOString(),
      };
      saveAttempt(attempt);
      setLastResultId(attempt.id);
      clearActiveQuiz();
      router.push('/quiz/results');
    } catch {
      submittedRef.current = false;
      setSubmitting(false);
      latestRef.current.warning('Could not submit your quiz. Please try again.', 'Error');
    }
  }, [quizQuestions, topic, subtopic, difficulty, userName, router]);

  useEffect(() => {
    latestRef.current = { answers, warning, submit };
  });

  // Persist progress so a refresh restores the quiz
  useEffect(() => {
    if (!started) return;
    saveActiveQuiz({
      mode: 'elimination',
      topic,
      subtopic,
      difficulty,
      questions: quizQuestions,
      answers,
      currentIndex: 0,
      userName,
      startTime: startTimeRef.current || Date.now(),
    });
  }, [started, answers, quizQuestions, topic, subtopic, difficulty, userName]);

  // Countdown timer — pure decrement; expiry handled by the watcher below
  useEffect(() => {
    if (!started) return;
    const interval = setInterval(() => setTimeLeft((t) => Math.max(0, t - 1)), 1000);
    return () => clearInterval(interval);
  }, [started]);

  // Time expired → warn and submit immediately (modal doesn't block scoring)
  useEffect(() => {
    if (!started || timeLeft !== 0 || submittedRef.current) return;
    latestRef.current.warning('Time is up! Submitting your answers...', 'Time Expired');
    latestRef.current.submit();
  }, [timeLeft, started]);

  // Warn before leaving mid-quiz
  useEffect(() => {
    if (!started) return;
    const handler = (e: BeforeUnloadEvent) => {
      if (!submittedRef.current) {
        e.preventDefault();
        e.returnValue = '';
      }
    };
    window.addEventListener('beforeunload', handler);
    return () => window.removeEventListener('beforeunload', handler);
  }, [started]);

  const answeredCount = quizQuestions.filter((q) => answers[q.key] !== undefined).length;
  const minutes = Math.floor(timeLeft / 60);
  const seconds = timeLeft % 60;

  const handleSubmit = async () => {
    const missing = quizQuestions.length - answeredCount;
    if (missing > 0) {
      const ok = await confirm(
        `You have ${missing} unanswered question(s). Do you want to submit anyway?`,
        'Incomplete Quiz'
      );
      if (!ok) return;
    }
    submit();
  };

  return (
    <main className="container mx-auto px-4 py-8 flex-grow">
      <NameModal
        title="Elimination Mode"
        description="Please enter your name to begin your 60-minute quiz"
        skip={started}
        onSubmit={(name) => {
          setUserName(name);
          startTimeRef.current = Date.now();
          setStarted(true);
        }}
      />
      {dialogElement}
      {started && (
        <div className="max-w-6xl mx-auto animate-fade-in">
          <div className="sheet p-6 sm:p-8">
            <div className="mb-6 flex items-start justify-between gap-4">
              <div>
                <span className="inline-flex items-center gap-1.5 border border-ink px-2 py-1 text-xs font-semibold uppercase tracking-[0.14em] text-ink">
                  <Zap className="h-3.5 w-3.5" aria-hidden />
                  Elimination
                </span>
                <h2 className="mt-2 text-2xl font-bold text-ink">
                  {topic ? 'Topic Review' : '100 Questions from All Topics'}
                </h2>
              </div>
              <div className="text-right">
                <div className="field-label">Time Remaining</div>
                <div
                  className={`readout text-2xl font-bold ${timeLeft <= 300 ? 'text-mark' : 'text-ink'}`}
                >
                  {minutes}:{seconds.toString().padStart(2, '0')}
                </div>
              </div>
            </div>

            <div className="mb-6">
              <div className="mb-2 flex items-baseline justify-between">
                <span className="field-label mb-0">Progress</span>
                <span className="num text-sm text-ink-soft">
                  {answeredCount} / {quizQuestions.length}
                </span>
              </div>
              <div
                className="flex flex-wrap gap-[3px]"
                role="progressbar"
                aria-valuenow={answeredCount}
                aria-valuemin={0}
                aria-valuemax={quizQuestions.length}
              >
                {quizQuestions.map((q) => (
                  <span
                    key={q.key}
                    aria-hidden
                    className={
                      answers[q.key] !== undefined
                        ? 'h-3 w-3 bg-pencil'
                        : 'h-3 w-3 border border-line bg-white'
                    }
                  />
                ))}
              </div>
            </div>

            <div className="space-y-6">
              {quizQuestions.map((question, qi) => (
                <div key={question.key} className="border-b border-line pb-6 last:border-b-0">
                  <h3 className="mb-3 text-lg font-bold text-ink">
                    <span className="num">{qi + 1}.</span> {question.question}
                  </h3>
                  <div className="mb-3 flex items-center gap-1.5 text-xs text-ink-soft">
                    <Tag className="h-3.5 w-3.5" aria-hidden />
                    {question.topic_name} - {question.subtopic_name}
                  </div>
                  <div className="space-y-2">
                    {(question.options ?? []).map((option, oi) => (
                      <label key={oi} className="choice">
                        <input
                          type="radio"
                          name={`answer_${question.key}`}
                          value={oi}
                          checked={answers[question.key] === String(oi)}
                          onChange={() =>
                            setAnswers((a) => ({ ...a, [question.key]: String(oi) }))
                          }
                          className="sr-only"
                        />
                        <span className="bubble" aria-hidden>
                          {['A', 'B', 'C', 'D'][oi]}
                        </span>
                        <span className="text-ink">{option}</span>
                      </label>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-8 flex justify-center gap-3 border-t border-line pt-6">
              <Link href="/" className="btn btn-line">
                <ArrowLeft className="h-4 w-4" aria-hidden />
                Back to Home
              </Link>
              <button
                onClick={handleSubmit}
                disabled={submitting}
                className="btn btn-pencil"
              >
                <Check className="h-4 w-4" aria-hidden />
                {submitting ? 'Submitting...' : 'Submit Quiz'}
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
