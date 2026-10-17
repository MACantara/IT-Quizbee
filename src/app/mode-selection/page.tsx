import Link from 'next/link';
import { redirect } from 'next/navigation';
import { Suspense } from 'react';
import type { Metadata } from 'next';
import { getSubtopics } from '@/lib/questions';

export const metadata: Metadata = { title: 'Select Mode' };

const DIFFICULTIES = [
  { id: 'easy', label: '⭐ Easy (20s per question)', cls: 'bg-green-500 hover:bg-green-600' },
  { id: 'average', label: '⭐⭐ Average (30s per question)', cls: 'bg-yellow-500 hover:bg-yellow-600' },
  { id: 'difficult', label: '⭐⭐⭐ Difficult (40s per question)', cls: 'bg-red-500 hover:bg-red-600' },
];

export default function ModeSelectionPage({
  searchParams,
}: {
  searchParams: Promise<{ topic?: string; subtopic?: string }>;
}) {
  return (
    <Suspense>
      <ModeSelection searchParams={searchParams} />
    </Suspense>
  );
}

async function ModeSelection({
  searchParams,
}: {
  searchParams: Promise<{ topic?: string; subtopic?: string }>;
}) {
  const { topic, subtopic } = await searchParams;
  if (!topic || !subtopic) redirect('/topics');

  let subtopicName = subtopic.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  try {
    const st = (await getSubtopics(topic)).find((s) => s.id === subtopic);
    if (st) subtopicName = st.name;
  } catch {
    redirect('/topics');
  }

  return (
    <main className="container mx-auto px-4 py-8 flex-grow">
      <div className="max-w-4xl mx-auto animate-fade-in">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="mb-6">
            <Link
              href={`/topics/${topic}`}
              className="text-blue-600 hover:text-blue-800 font-semibold mb-4 inline-block"
            >
              <i className="bi bi-arrow-left mr-2" />Back to Subtopics
            </Link>
            <h2 className="text-3xl font-bold text-gray-800 mb-2">{subtopicName}</h2>
            <p className="text-gray-600 mb-6">Choose your game mode</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Link
              href={`/quiz/elimination?topic=${topic}&subtopic=${subtopic}`}
              className="border-4 border-blue-500 rounded-xl p-6 cursor-pointer hover:shadow-xl transition transform hover:scale-105 bg-gradient-to-br from-blue-50 to-blue-100 block"
            >
              <div className="text-center mb-4">
                <i className="bi bi-lightning-charge-fill text-6xl text-blue-600 mb-3" />
                <h3 className="text-2xl font-bold text-gray-800">Elimination Mode</h3>
              </div>
              <ul className="space-y-2 text-gray-700 mb-4">
                {['Competitive preliminary round', '10 questions', 'Perfect for practice'].map((t) => (
                  <li key={t} className="flex items-center gap-2">
                    <i className="bi bi-check-circle-fill text-blue-600" />
                    <span>{t}</span>
                  </li>
                ))}
              </ul>
              <div className="w-full py-3 bg-blue-600 text-white rounded-lg font-semibold text-center">
                Start Elimination
              </div>
            </Link>

            <div className="border-4 border-purple-500 rounded-xl p-6 bg-gradient-to-br from-purple-50 to-purple-100">
              <div className="text-center mb-4">
                <i className="bi bi-trophy-fill text-6xl text-purple-600 mb-3" />
                <h3 className="text-2xl font-bold text-gray-800">Finals Mode</h3>
              </div>
              <ul className="space-y-2 text-gray-700 mb-4">
                {['Championship round', '3 difficulty levels', '10 questions per level'].map((t) => (
                  <li key={t} className="flex items-center gap-2">
                    <i className="bi bi-check-circle-fill text-purple-600" />
                    <span>{t}</span>
                  </li>
                ))}
              </ul>
              <p className="text-sm font-semibold text-gray-700 mb-3">Select Difficulty:</p>
              <div className="space-y-2">
                {DIFFICULTIES.map((d) => (
                  <Link
                    key={d.id}
                    href={`/quiz/finals?topic=${topic}&subtopic=${subtopic}&difficulty=${d.id}`}
                    className={`block w-full py-2 ${d.cls} text-white rounded-lg font-semibold text-center transition`}
                  >
                    {d.label}
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
