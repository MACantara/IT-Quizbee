'use client';

import { useCallback, useEffect, useRef, useState, useSyncExternalStore } from 'react';
import { useRouter } from 'next/navigation';
import {
  ArrowRight,
  Check,
  CircleCheck,
  CircleX,
  Hourglass,
  Info,
  RotateCcw,
  TriangleAlert,
  Trophy,
} from 'lucide-react';
import { NameModal } from './NameModal';
import { useDialog } from './Modal';
import { saveAttempt, getUserName } from '@/lib/attempts';
import {
  clearActiveQuiz,
  loadActiveQuiz,
  saveActiveQuiz,
  setLastResultId,
} from '@/lib/active-quiz';
import type { AnswerResult, Attempt, QuizQuestion, ScoreResult } from '@/lib/types';

const TIMER: Record<string, number> = { easy: 20, average: 30, difficult: 40 };
const BADGE: Record<string, { text: string; cls: string }> = {
  easy: { text: 'EASY', cls: 'border-line bg-white text-ink' },
  average: { text: 'AVERAGE', cls: 'border-line bg-white text-ink' },
  difficult: { text: 'DIFFICULT', cls: 'border-line bg-white text-ink' },
};
const subscribe = () => () => {};

const difficultyOf = (q: QuizQuestion | undefined) =>
  q?.difficulty && TIMER[q.difficulty] ? q.difficulty : 'average';

interface Props {
  questions: QuizQuestion[];
  topic?: string;
  subtopic?: string;
  difficulty?: string;
}

export function FinalsQuiz(props: Props) {
  // Gate on mount so lazy initializers can read sessionStorage (SSR renders nothing)
  const mounted = useSyncExternalStore(subscribe, () => true, () => false);
  if (!mounted) return <main className="container mx-auto px-4 py-8 flex-grow" />;
  return <QuizInner {...props} />;
}

function QuizInner({ questions, topic, subtopic, difficulty }: Props) {
  const router = useRouter();
  const { warning, dialogElement } = useDialog();

  // A saved quiz for the same mode/selection wins — refresh re-samples server-side
  const [restored] = useState(() => {
    const saved = loadActiveQuiz('finals');
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
  const [index, setIndex] = useState(() =>
    Math.min(restored?.currentIndex ?? 0, quizQuestions.length - 1)
  );
  const [answers, setAnswers] = useState<Record<string, string>>(() => restored?.answers ?? {});
  const [timeLeft, setTimeLeft] = useState(
    () => TIMER[difficultyOf(quizQuestions[Math.min(restored?.currentIndex ?? 0, quizQuestions.length - 1)])]
  );
  const [input, setInput] = useState('');
  const [feedback, setFeedback] = useState<AnswerResult | null>(null);
  const [checking, setChecking] = useState(false);
  const [checkError, setCheckError] = useState(false);
  const [done, setDone] = useState(false);
  const [submitError, setSubmitError] = useState(false);
  const startTimeRef = useRef(restored?.startTime ?? 0);
  const submittedRef = useRef(false);
  const submitTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const latestRef = useRef<{
    answers: Record<string, string>;
    index: number;
    warning: (m: string, t?: string) => Promise<void>;
    submit: () => Promise<void>;
    submitAnswer: (a: string) => void;
    next: () => void;
  }>({
    answers,
    index,
    warning,
    submit: async () => {},
    submitAnswer: () => {},
    next: () => {},
  });

  const question = quizQuestions[index];
  const qdifficulty = difficultyOf(question);

  const submit = useCallback(async () => {
    if (submittedRef.current) return;
    submittedRef.current = true;
    try {
      const res = await fetch('/api/score', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mode: 'finals',
          questions: quizQuestions.map((q) => ({
            key: q.key,
            id: q.id,
            topic: q.topic,
            subtopic: q.subtopic,
            difficulty: q.difficulty,
          })),
          answers: latestRef.current.answers,
        }),
      });
      if (!res.ok) throw new Error('Scoring failed');
      const scored = (await res.json()) as ScoreResult;
      const attempt: Attempt = {
        ...scored,
        id: crypto.randomUUID(),
        quiz_type: 'finals',
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
      setSubmitError(true);
    }
  }, [quizQuestions, topic, subtopic, difficulty, userName, router]);

  // Grade one answer via the score API and show feedback; the timer is paused
  // while checking/feedback is set, so expiry can't fire mid-review
  const submitAnswer = useCallback(
    async (answer: string) => {
      const i = latestRef.current.index;
      const q = quizQuestions[i];
      if (!q) return;
      setAnswers((a) => ({ ...a, [q.key]: answer }));
      setInput('');
      setChecking(true);
      setCheckError(false);
      try {
        const res = await fetch('/api/score', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            mode: 'finals',
            questions: [
              {
                key: q.key,
                id: q.id,
                topic: q.topic,
                subtopic: q.subtopic,
                difficulty: q.difficulty,
              },
            ],
            answers: { [q.key]: answer },
          }),
        });
        if (!res.ok) throw new Error('Check failed');
        const scored = (await res.json()) as ScoreResult;
        setFeedback(scored.results[0] ?? null);
      } catch {
        setCheckError(true);
      } finally {
        setChecking(false);
      }
    },
    [quizQuestions]
  );

  const next = useCallback(() => {
    const i = latestRef.current.index;
    setFeedback(null);
    setCheckError(false);
    if (i + 1 >= quizQuestions.length) {
      setDone(true);
      submitTimeoutRef.current = setTimeout(() => latestRef.current.submit(), 1500);
    } else {
      setTimeLeft(TIMER[difficultyOf(quizQuestions[i + 1])]);
      setIndex(i + 1);
    }
  }, [quizQuestions]);

  useEffect(() => {
    latestRef.current = { answers, index, warning, submit, submitAnswer, next };
  });

  // Clear pending submit navigation on unmount
  useEffect(
    () => () => {
      if (submitTimeoutRef.current) clearTimeout(submitTimeoutRef.current);
    },
    []
  );

  // Per-question countdown — paused while an answer is being checked/reviewed
  useEffect(() => {
    if (!started || done || !question || checking || feedback) return;
    const interval = setInterval(() => setTimeLeft((t) => Math.max(0, t - 1)), 1000);
    return () => clearInterval(interval);
  }, [started, done, index, question, checking, feedback]);

  // Question timer expired → warn, then grade the empty answer (still reveals it)
  useEffect(() => {
    if (!started || done || checking || feedback || timeLeft !== 0) return;
    latestRef.current
      .warning('Time is up for this question!', 'Time Expired')
      .then(() => latestRef.current.submitAnswer(''));
  }, [timeLeft, started, done, checking, feedback]);

  // Persist progress
  useEffect(() => {
    if (!started || done) return;
    saveActiveQuiz({
      mode: 'finals',
      topic,
      subtopic,
      difficulty,
      questions: quizQuestions,
      answers,
      currentIndex: index,
      userName,
      startTime: startTimeRef.current || Date.now(),
    });
  }, [started, done, answers, index, quizQuestions, topic, subtopic, difficulty, userName]);

  // Warn before leaving mid-quiz
  useEffect(() => {
    if (!started || done) return;
    const handler = (e: BeforeUnloadEvent) => {
      if (!submittedRef.current) {
        e.preventDefault();
        e.returnValue = '';
      }
    };
    window.addEventListener('beforeunload', handler);
    return () => window.removeEventListener('beforeunload', handler);
  }, [started, done]);

  const badge = BADGE[qdifficulty] ?? BADGE.average;
  const timerColor =
    timeLeft <= 5 ? 'text-mark' : timeLeft <= 10 ? 'text-warn' : 'text-ink';

  return (
    <main className="container mx-auto px-4 py-8 flex-grow">
      <NameModal
        title="Finals Mode"
        description="Please enter your name to begin your timed quiz"
        skip={started}
        onSubmit={(name) => {
          setUserName(name);
          startTimeRef.current = Date.now();
          setTimeLeft(TIMER[difficultyOf(quizQuestions[0])]);
          setStarted(true);
        }}
      />
      {dialogElement}
      {started && (
        <div className="max-w-4xl mx-auto animate-fade-in">
          <div className="sheet p-6 sm:p-8">
            <div className="mb-6 text-center">
              <span className="mb-2 inline-flex items-center gap-1.5 border border-ink px-2 py-1 text-xs font-semibold uppercase tracking-[0.14em] text-ink">
                <Trophy className="h-3.5 w-3.5" aria-hidden />
                Finals
              </span>
              <h2 className="text-3xl font-bold text-ink">Identification Questions</h2>
              <p className="mt-2 text-ink-soft">Answer each question before the timer runs out!</p>
            </div>

            <div className="mb-6">
              <div className="mb-2 flex items-baseline justify-between">
                <span className="field-label mb-0">Question</span>
                <span className="num text-sm text-ink-soft">
                  {Math.min(index + 1, quizQuestions.length)} / {quizQuestions.length}
                </span>
              </div>
              <div
                className="flex flex-wrap gap-[3px]"
                role="progressbar"
                aria-valuenow={Math.min(index + 1, quizQuestions.length)}
                aria-valuemin={0}
                aria-valuemax={quizQuestions.length}
              >
                {quizQuestions.map((q, i) => (
                  <span
                    key={q.key}
                    aria-hidden
                    className={
                      i <= index
                        ? 'h-3 w-3 bg-pencil'
                        : 'h-3 w-3 border border-line bg-white'
                    }
                  />
                ))}
              </div>
            </div>

            {!done && question ? (
              <div className="min-h-[400px]">
                <div className="mb-8 text-center">
                  <span
                    className={`mb-4 inline-block border px-2 py-1 text-xs font-semibold uppercase tracking-[0.14em] ${badge.cls}`}
                  >
                    {badge.text}
                  </span>
                  <div>
                    <div className={`readout px-5 py-2 text-5xl font-bold ${timerColor}`}>
                      {timeLeft}
                    </div>
                  </div>
                </div>

                <div className="mb-8">
                  <h3 className="mb-6 text-center text-2xl font-bold text-ink">
                    {question.question}
                  </h3>
                  {checking ? (
                    <div className="py-8 text-center">
                      <Hourglass className="mx-auto mb-4 block h-8 w-8 text-ink-soft" aria-hidden />
                      <p className="text-lg text-ink-soft">Checking your answer...</p>
                    </div>
                  ) : feedback ? (
                    <div
                      className={`border p-6 ${
                        feedback.is_correct
                          ? 'border-pass bg-pass-wash'
                          : 'border-mark bg-mark-wash'
                      }`}
                    >
                      <div className="mb-3 flex items-center justify-center gap-2">
                        {feedback.is_correct ? (
                          <CircleCheck className="h-7 w-7 text-pass" aria-hidden />
                        ) : (
                          <CircleX className="h-7 w-7 text-mark" aria-hidden />
                        )}
                        <span
                          className={`text-2xl font-bold ${
                            feedback.is_correct ? 'text-pass' : 'text-mark'
                          }`}
                        >
                          {feedback.is_correct ? 'Correct!' : 'Incorrect'}
                        </span>
                      </div>
                      {!feedback.is_correct && feedback.correct_answer !== undefined && (
                        <p className="mb-2 text-center text-ink">
                          Correct answer:{' '}
                          <span className="font-semibold">{String(feedback.correct_answer)}</span>
                        </p>
                      )}
                      {feedback.explanation && (
                        <p className="text-center text-sm text-ink-soft">
                          {feedback.explanation}
                        </p>
                      )}
                    </div>
                  ) : checkError ? (
                    <div className="border border-warn bg-warn-wash p-6 text-center">
                      <TriangleAlert
                        className="mx-auto mb-2 block h-6 w-6 text-warn"
                        aria-hidden
                      />
                      <p className="mb-4 text-ink">
                        Could not check your answer. Your answer was recorded.
                      </p>
                      <div className="flex justify-center gap-3">
                        <button
                          onClick={() =>
                            latestRef.current.submitAnswer(answers[question.key] ?? '')
                          }
                          className="btn btn-pencil"
                        >
                          Retry
                        </button>
                        <button
                          onClick={() => latestRef.current.next()}
                          className="btn btn-line"
                        >
                          Skip
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <input
                        key={question.key}
                        type="text"
                        id="answer-input"
                        name="answer"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            e.preventDefault();
                            latestRef.current.submitAnswer(input.trim());
                          }
                        }}
                        className="field text-lg"
                        placeholder="Type your answer here..."
                        autoComplete="off"
                        autoFocus
                      />
                      <p className="text-center text-sm text-ink-soft">
                        <Info className="mr-1 inline h-3.5 w-3.5" aria-hidden />
                        Case-insensitive. Be as specific as possible.
                      </p>
                    </div>
                  )}
                </div>

                <div className="flex justify-center gap-3">
                  {feedback ? (
                    <button
                      onClick={() => latestRef.current.next()}
                      autoFocus={feedback !== null}
                      className="btn btn-pencil text-lg"
                    >
                      {index + 1 >= quizQuestions.length ? (
                        <>
                          <Trophy className="h-4 w-4" aria-hidden />
                          See Results
                        </>
                      ) : (
                        <>
                          <ArrowRight className="h-4 w-4" aria-hidden />
                          Next Question
                        </>
                      )}
                    </button>
                  ) : (
                    !checking &&
                    !checkError && (
                      <button
                        onClick={() => latestRef.current.submitAnswer(input.trim())}
                        className="btn btn-pencil text-lg"
                      >
                        <Check className="h-4 w-4" aria-hidden />
                        Submit Answer
                      </button>
                    )
                  )}
                </div>
              </div>
            ) : submitError ? (
              <div className="flex min-h-[400px] flex-col items-center justify-center text-center">
                <TriangleAlert className="mb-4 h-10 w-10 text-warn" aria-hidden />
                <h3 className="mb-4 text-3xl font-bold text-ink">Submission failed</h3>
                <p className="mb-6 text-lg text-ink-soft">
                  Your answers could not be scored. Check your connection and try again.
                </p>
                <button
                  onClick={() => {
                    setSubmitError(false);
                    submit();
                  }}
                  className="btn btn-pencil"
                >
                  <RotateCcw className="h-4 w-4" aria-hidden />
                  Retry
                </button>
              </div>
            ) : (
              <div className="flex min-h-[400px] flex-col items-center justify-center text-center">
                <Trophy className="mb-4 h-10 w-10 text-pencil" aria-hidden />
                <h3 className="mb-4 text-3xl font-bold text-ink">Quiz Complete!</h3>
                <p className="text-lg text-ink-soft">Calculating your results...</p>
              </div>
            )}
          </div>
        </div>
      )}
    </main>
  );
}
