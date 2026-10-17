import Link from 'next/link';
import { notFound } from 'next/navigation';
import { getSubtopics } from '@/lib/questions';
import { promises as fs } from 'fs';
import path from 'path';

const COLORS = [
  'border-blue-500 hover:bg-blue-50', 'border-purple-500 hover:bg-purple-50',
  'border-green-500 hover:bg-green-50', 'border-yellow-500 hover:bg-yellow-50',
  'border-red-500 hover:bg-red-50', 'border-pink-500 hover:bg-pink-50',
  'border-indigo-500 hover:bg-indigo-50', 'border-teal-500 hover:bg-teal-50',
  'border-orange-500 hover:bg-orange-50', 'border-cyan-500 hover:bg-cyan-50',
];

export default async function SubtopicsPage({ params }: { params: Promise<{ topic: string }> }) {
  const { topic } = await params;

  let subtopics;
  let topicTitle = topic.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  try {
    subtopics = await getSubtopics(topic);
    const index = JSON.parse(
      await fs.readFile(path.join(process.cwd(), 'data', topic, 'index.json'), 'utf-8')
    );
    topicTitle = index.topic_name ?? topicTitle;
  } catch {
    notFound();
  }

  return (
    <main className="container mx-auto px-4 py-8 flex-grow">
      <div className="max-w-6xl mx-auto animate-fade-in">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="mb-6">
            <Link
              href="/topics"
              className="text-blue-600 hover:text-blue-800 font-semibold mb-4 inline-block"
            >
              <i className="bi bi-arrow-left mr-2" />Back to Topics
            </Link>
            <h2 className="text-3xl font-bold text-gray-800 mb-2">{topicTitle}</h2>
            <p className="text-gray-600">Select a subtopic to start reviewing</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {subtopics.map((st, i) => (
              <Link
                key={st.id}
                href={`/mode-selection?topic=${topic}&subtopic=${st.id}`}
                className={`border-l-4 ${COLORS[i % COLORS.length]} p-4 rounded-lg shadow cursor-pointer transform hover:scale-102 transition duration-200 bg-white block`}
              >
                <h3 className="text-lg font-bold text-gray-800 mb-2">{st.name}</h3>
                <p className="text-sm text-gray-600 mb-3">{st.description || ''}</p>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-semibold text-gray-500">10 Questions per mode</span>
                  <i className="bi bi-arrow-right-circle text-xl text-gray-400" />
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
