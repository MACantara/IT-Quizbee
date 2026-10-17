'use client';

import { useCallback, useEffect, useRef, useState, useSyncExternalStore } from 'react';
import { useRouter } from 'next/navigation';
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

const TIMER: Record<string, number> = { easy: 20, average: 30, difficult: 40 };
const BADGE: Record<string, { text: string; cls: string }> = {
  easy: { text: '⭐ Easy', cls: 'bg-green-100 text-green-800' },
  average: { text: '⭐⭐ Average', cls: 'bg-yellow-100 text-yellow-800' },
  difficult: { text: '⭐⭐⭐ Difficult', cls: 'bg-red-100 text-red-800' },
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
    advance: (a: string) => void;
  }>({ answers, index, warning, submit: async () => {}, advance: () => {} });

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

  const advance = useCallback(
    (answer: string) => {
      const i = latestRef.current.index;
      const q = quizQuestions[i];
      if (!q) return;
      setAnswers((a) => ({ ...a, [q.key]: answer }));
      setInput('');
      if (i + 1 >= quizQuestions.length) {
        setDone(true);
        submitTimeoutRef.current = setTimeout(() => latestRef.current.submit(), 1500);
      } else {
        setTimeLeft(TIMER[difficultyOf(quizQuestions[i + 1])]);
        setIndex(i + 1);
      }
    },
    [quizQuestions]
  );

  useEffect(() => {
    latestRef.current = { answers, index, warning, submit, advance };
  });

  // Clear pending submit navigation on unmount
  useEffect(
    () => () => {
      if (submitTimeoutRef.current) clearTimeout(submitTimeoutRef.current);
    },
    []
  );

  // Per-question countdown — pure decrement; expiry handled by the watcher below
  useEffect(() => {
    if (!started || done || !question) return;
    const interval = setInterval(() => setTimeLeft((t) => Math.max(0, t - 1)), 1000);
    return () => clearInterval(interval);
  }, [started, done, index, question]);

  // Question timer expired → warn, then advance with an empty answer
  useEffect(() => {
    if (!started || done || timeLeft !== 0) return;
    latestRef.current
      .warning('Time is up for this question!', 'Time Expired')
      .then(() => latestRef.current.advance(''));
  }, [timeLeft, started, done]);

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
    timeLeft <= 5 ? 'text-red-600' : timeLeft <= 10 ? 'text-yellow-600' : 'text-purple-600';

  return (
    <main className="container mx-auto px-4 py-8 flex-grow">
      <NameModal
        title="Finals Mode"
        description="Please enter your name to begin your timed quiz"
        accent="purple"
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
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <div className="text-center mb-6">
              <div className="px-4 py-2 rounded-full font-semibold text-sm bg-purple-100 text-purple-800 inline-block mb-2">
                🏆 Finals Mode
              </div>
              <h2 className="text-3xl font-bold text-gray-800">Identification Questions</h2>
              <p className="text-gray-600 mt-2">Answer each question before the timer runs out!</p>
            </div>

            <div className="mb-6">
              <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>Question</span>
                <span>
                  {Math.min(index + 1, quizQuestions.length)} / {quizQuestions.length}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-purple-600 h-3 rounded-full transition-all"
                  style={{ width: `${((index + 1) / quizQuestions.length) * 100}%` }}
                />
              </div>
            </div>

            {!done && question ? (
              <div className="min-h-[400px]">
                <div className="text-center mb-8">
                  <div
                    className={`inline-block px-4 py-2 rounded-full font-semibold text-sm mb-4 ${badge.cls}`}
                  >
                    {badge.text}
                  </div>
                  <div className={`text-6xl font-bold mb-4 ${timerColor}`}>{timeLeft}</div>
                </div>

                <div className="mb-8">
                  <h3 className="text-2xl font-bold text-gray-800 mb-6 text-center">
                    {question.question}
                  </h3>
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
                          latestRef.current.advance(input.trim());
                        }
                      }}
                      className="w-full px-6 py-4 text-xl border-2 border-gray-300 rounded-lg focus:border-purple-500 focus:ring-2 focus:ring-purple-200 outline-none transition"
                      placeholder="Type your answer here..."
                      autoComplete="off"
                      autoFocus
                    />
                    <p className="text-sm text-gray-500 text-center">
                      <i className="bi bi-info-circle mr-1" />Case-insensitive. Be as specific as
                      possible.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4 justify-center">
                  <button
                    onClick={() => latestRef.current.advance(input.trim())}
                    className="px-8 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition font-semibold text-lg"
                  >
                    <i className="bi bi-check-circle-fill mr-2" />Submit Answer
                  </button>
                </div>
              </div>
            ) : submitError ? (
              <div className="text-center min-h-[400px] flex flex-col items-center justify-center">
                <i className="bi bi-exclamation-triangle-fill text-8xl text-yellow-500 mb-4" />
                <h3 className="text-3xl font-bold text-gray-800 mb-4">Submission failed</h3>
                <p className="text-lg text-gray-600 mb-6">
                  Your answers could not be scored. Check your connection and try again.
                </p>
                <button
                  onClick={() => {
                    setSubmitError(false);
                    submit();
                  }}
                  className="px-8 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition font-semibold"
                >
                  <i className="bi bi-arrow-repeat mr-2" />Retry
                </button>
              </div>
            ) : (
              <div className="text-center min-h-[400px] flex flex-col items-center justify-center">
                <i className="bi bi-trophy-fill text-8xl text-purple-600 mb-4" />
                <h3 className="text-3xl font-bold text-gray-800 mb-4">Quiz Complete!</h3>
                <p className="text-lg text-gray-600 mb-6">Calculating your results...</p>
              </div>
            )}
          </div>
        </div>
      )}
    </main>
  );
}
