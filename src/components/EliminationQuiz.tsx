'use client';

import { useCallback, useEffect, useRef, useState, useSyncExternalStore } from 'react';
import Link from 'next/link';
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
        accent="blue"
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
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <div className="flex items-center justify-between mb-6">
              <div>
                <div className="px-4 py-2 rounded-full font-semibold text-sm bg-blue-100 text-blue-800 inline-block">
                  ⚡ Elimination Mode
                </div>
                <h2 className="text-2xl font-bold text-gray-800 mt-2">
                  {topic ? 'Topic Review' : '100 Questions from All Topics'}
                </h2>
              </div>
              <div className="text-center">
                <div className="text-sm text-gray-600 mb-1">Time Remaining</div>
                <div
                  className={`text-4xl font-bold ${timeLeft <= 300 ? 'text-red-600' : 'text-blue-600'}`}
                >
                  {minutes}:{seconds.toString().padStart(2, '0')}
                </div>
              </div>
            </div>

            <div className="mb-6">
              <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>Progress</span>
                <span>
                  {answeredCount} / {quizQuestions.length}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-blue-600 h-3 rounded-full transition-all"
                  style={{ width: `${(answeredCount / quizQuestions.length) * 100}%` }}
                />
              </div>
            </div>

            <div className="space-y-6">
              {quizQuestions.map((question, qi) => (
                <div key={question.key} className="pb-6 border-b border-gray-200 last:border-b-0">
                  <h3 className="text-lg font-bold text-gray-800 mb-3">
                    {qi + 1}. {question.question}
                  </h3>
                  <div className="text-xs text-gray-500 mb-3">
                    <i className="bi bi-tag-fill" /> {question.topic_name} - {question.subtopic_name}
                  </div>
                  <div className="space-y-2">
                    {(question.options ?? []).map((option, oi) => (
                      <label
                        key={oi}
                        className="flex items-center gap-3 p-3 border-2 border-gray-300 rounded-lg cursor-pointer hover:border-blue-400 hover:bg-blue-50 transition has-[:checked]:border-blue-600 has-[:checked]:bg-blue-50"
                      >
                        <input
                          type="radio"
                          name={`answer_${question.key}`}
                          value={oi}
                          checked={answers[question.key] === String(oi)}
                          onChange={() =>
                            setAnswers((a) => ({ ...a, [question.key]: String(oi) }))
                          }
                          className="w-4 h-4 text-blue-600"
                        />
                        <span className="font-semibold text-gray-700">
                          {['A', 'B', 'C', 'D'][oi]}.
                        </span>
                        <span className="text-gray-800">{option}</span>
                      </label>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <div className="flex gap-4 justify-center mt-8 sticky bottom-4">
              <Link
                href="/"
                className="px-6 py-3 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition"
              >
                <i className="bi bi-arrow-left mr-2" />Back to Home
              </Link>
              <button
                onClick={handleSubmit}
                disabled={submitting}
                className="px-8 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-semibold disabled:opacity-50"
              >
                <i className="bi bi-check-circle-fill mr-2" />
                {submitting ? 'Submitting...' : 'Submit Quiz'}
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
