import Link from 'next/link';
import type { Metadata } from 'next';
import { getTopics } from '@/lib/questions';

export const metadata: Metadata = { title: 'Select Topic' };

const ICONS = [
  'bi-cpu-fill', 'bi-diagram-3-fill', 'bi-gear-fill', 'bi-code-slash', 'bi-box-seam',
  'bi-router-fill', 'bi-hdd-rack-fill', 'bi-database-fill', 'bi-graph-up', 'bi-cart-fill',
];
const COLORS = [
  'from-blue-500 to-blue-600', 'from-purple-500 to-purple-600', 'from-green-500 to-green-600',
  'from-yellow-500 to-yellow-600', 'from-red-500 to-red-600', 'from-pink-500 to-pink-600',
  'from-indigo-500 to-indigo-600', 'from-teal-500 to-teal-600', 'from-orange-500 to-orange-600',
  'from-cyan-500 to-cyan-600',
];

export default async function TopicsPage() {
  const topics = await getTopics();

  return (
    <main className="container mx-auto px-4 py-8 flex-grow">
      <div className="max-w-6xl mx-auto animate-fade-in">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h2 className="text-3xl font-bold text-gray-800 mb-6 text-center">
            <i className="bi bi-list-ul mr-3" />Choose Your Topic
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {topics.map((topic, i) => (
              <Link
                key={topic.topic_id}
                href={`/topics/${topic.topic_id}`}
                className={`bg-gradient-to-br ${COLORS[i % COLORS.length]} p-6 rounded-xl shadow-lg cursor-pointer transform hover:scale-105 transition duration-300 text-white`}
              >
                <div className="flex items-center justify-between mb-4">
                  <i className={`bi ${ICONS[i % ICONS.length]} text-4xl`} />
                  <span className="bg-white text-gray-800 px-3 py-1 rounded-full text-sm font-semibold">
                    {topic.subtopics?.length ?? 0} Topics
                  </span>
                </div>
                <h3 className="text-xl font-bold mb-2">{topic.topic_name}</h3>
                <p className="text-sm opacity-90">
                  {topic.description || 'Click to view subtopics'}
                </p>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
