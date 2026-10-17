'use client';

import Link from 'next/link';
import type { Attempt } from '@/lib/types';

const DIFF_BADGE: Record<string, { text: string; cls: string }> = {
  easy: { text: '⭐ Easy', cls: 'bg-green-100 text-green-800' },
  average: { text: '⭐⭐ Average', cls: 'bg-yellow-100 text-yellow-800' },
  difficult: { text: '⭐⭐⭐ Difficult', cls: 'bg-red-100 text-red-800' },
};

export function ResultsView({ attempt, review = false }: { attempt: Attempt; review?: boolean }) {
  const { score, correct_count, incorrect_count, total_questions, results } = attempt;
  const topic = attempt.topic && attempt.topic !== 'all_topics' ? attempt.topic : undefined;
  const subtopic = attempt.subtopic;

  return (
    <main className="container mx-auto px-4 py-8 flex-grow">
      <div className="max-w-4xl mx-auto animate-fade-in">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="text-center mb-8">
            <div className="text-8xl mb-4">{score >= 80 ? '🏆' : score >= 60 ? '😊' : '📚'}</div>
            <h2 className="text-4xl font-bold text-gray-800 mb-4">
              {review ? 'Quiz Review' : 'Quiz Complete!'}
            </h2>
            <div
              className={`text-6xl font-bold mb-4 ${
                score >= 80 ? 'text-green-600' : score >= 60 ? 'text-yellow-600' : 'text-red-600'
              }`}
            >
              {score}%
            </div>
            <p className="text-xl text-gray-600">
              {score >= 80
                ? "Excellent! You've mastered this topic! 🎉"
                : score >= 60
                  ? 'Good job! Keep practicing to improve! 💪'
                  : "Keep studying! You'll get better! 📖"}
            </p>
            {attempt.user_name && (
              <p className="text-sm text-gray-500 mt-2">
                {attempt.user_name} · {new Date(attempt.created_at).toLocaleString()}
              </p>
            )}
          </div>

          <div className="grid grid-cols-3 gap-4 mb-8">
            <div className="bg-green-50 p-4 rounded-lg text-center">
              <i className="bi bi-check-circle-fill text-3xl text-green-600 mb-2" />
              <div className="text-2xl font-bold text-green-600">{correct_count}</div>
              <div className="text-sm text-gray-600">Correct</div>
            </div>
            <div className="bg-red-50 p-4 rounded-lg text-center">
              <i className="bi bi-x-circle-fill text-3xl text-red-600 mb-2" />
              <div className="text-2xl font-bold text-red-600">{incorrect_count}</div>
              <div className="text-sm text-gray-600">Incorrect</div>
            </div>
            <div className="bg-blue-50 p-4 rounded-lg text-center">
              <i className="bi bi-list-ol text-3xl text-blue-600 mb-2" />
              <div className="text-2xl font-bold text-blue-600">{total_questions}</div>
              <div className="text-sm text-gray-600">Total</div>
            </div>
          </div>

          <div className="mb-8">
            <h3 className="text-2xl font-bold text-gray-800 mb-4">
              <i className="bi bi-clipboard-check mr-2" />Detailed Results
            </h3>
            <div className="space-y-4">
              {results.map((r, i) => (
                <div
                  key={r.question_id}
                  className={`p-4 rounded-lg border-2 ${
                    r.is_correct ? 'border-green-300 bg-green-50' : 'border-red-300 bg-red-50'
                  }`}
                >
                  <div className="flex items-start gap-3 mb-3">
                    <i
                      className={`bi ${
                        r.is_correct
                          ? 'bi-check-circle-fill text-green-600'
                          : 'bi-x-circle-fill text-red-600'
                      } text-2xl mt-1`}
                    />
                    <div className="flex-1">
                      <h4 className="font-bold text-gray-800 mb-2">
                        {i + 1}. {r.question}
                      </h4>
                      {r.topic_name && (
                        <div className="text-xs text-gray-500 mb-2">
                          <i className="bi bi-tag-fill" /> {r.topic_name}
                          {r.subtopic_name ? ` - ${r.subtopic_name}` : ''}
                          {r.difficulty && DIFF_BADGE[r.difficulty] && (
                            <span
                              className={`ml-2 px-2 py-1 rounded ${DIFF_BADGE[r.difficulty].cls}`}
                            >
                              {DIFF_BADGE[r.difficulty].text}
                            </span>
                          )}
                        </div>
                      )}
                      <div className="space-y-1 text-sm">
                        {r.options?.length ? (
                          <>
                            <p className="text-gray-700">
                              <span className="font-semibold">Your answer:</span>{' '}
                              <span className={r.is_correct ? 'text-green-700' : 'text-red-700'}>
                                {r.user_answer !== '' && r.user_answer !== undefined
                                  ? r.options[Number(r.user_answer)]
                                  : 'Not answered'}
                              </span>
                            </p>
                            {!r.is_correct && (
                              <p className="text-gray-700">
                                <span className="font-semibold">Correct answer:</span>{' '}
                                <span className="text-green-700">
                                  {r.options[Number(r.correct_answer)]}
                                </span>
                              </p>
                            )}
                          </>
                        ) : (
                          <>
                            <p className="text-gray-700">
                              <span className="font-semibold">Your answer:</span>{' '}
                              <span
                                className={`${
                                  r.is_correct ? 'text-green-700' : 'text-red-700'
                                } font-mono bg-white px-2 py-1 rounded`}
                              >
                                {r.user_answer ? `"${r.user_answer}"` : 'Not answered'}
                              </span>
                            </p>
                            {!r.is_correct && (
                              <p className="text-gray-700">
                                <span className="font-semibold">Correct answer:</span>{' '}
                                <span className="text-green-700 font-mono bg-white px-2 py-1 rounded">
                                  &quot;{r.correct_answer}&quot;
                                </span>
                              </p>
                            )}
                          </>
                        )}
                        {r.explanation && (
                          <p className="text-gray-600 mt-2 italic">
                            <i className="bi bi-info-circle mr-1" />
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

          <div className="flex gap-4 justify-center flex-wrap">
            {attempt.quiz_type === 'elimination' && !topic && (
              <Link
                href="/quiz/elimination"
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                <i className="bi bi-arrow-repeat mr-2" />Try Elimination Again
              </Link>
            )}
            {attempt.quiz_type === 'finals' && !topic && (
              <Link
                href="/quiz/finals"
                className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
              >
                <i className="bi bi-arrow-repeat mr-2" />Try Finals Again
              </Link>
            )}
            {topic && subtopic && (
              <>
                <Link
                  href={`/mode-selection?topic=${topic}&subtopic=${subtopic}`}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                >
                  <i className="bi bi-arrow-repeat mr-2" />Change Mode
                </Link>
                <Link
                  href={`/topics/${topic}`}
                  className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition"
                >
                  <i className="bi bi-list-ul mr-2" />Choose Subtopic
                </Link>
              </>
            )}
            <Link
              href="/topics"
              className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition"
            >
              <i className="bi bi-book mr-2" />Browse Topics
            </Link>
            <Link
              href="/"
              className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-lg transition"
            >
              <i className="bi bi-house mr-2" />Home
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}
