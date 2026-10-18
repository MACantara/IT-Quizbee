import Link from 'next/link';
import { notFound } from 'next/navigation';
import { Suspense } from 'react';
import { ArrowLeft, CircleArrowRight } from 'lucide-react';
import { getTopic } from '@/lib/questions';

export default function SubtopicsPage({ params }: { params: Promise<{ topic: string }> }) {
  return (
    <Suspense>
      <Subtopics params={params} />
    </Suspense>
  );
}

async function Subtopics({ params }: { params: Promise<{ topic: string }> }) {
  const { topic } = await params;

  let subtopics;
  let topicTitle = topic.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  try {
    const index = await getTopic(topic);
    subtopics = index.subtopics ?? [];
    topicTitle = index.topic_name ?? topicTitle;
  } catch {
    notFound();
  }

  return (
    <main className="container mx-auto px-4 py-8 flex-grow">
      <div className="max-w-6xl mx-auto animate-fade-in">
        <div className="sheet p-6 sm:p-8">
          <div className="mb-6">
            <Link
              href="/topics"
              className="mb-4 inline-flex items-center gap-1.5 font-semibold text-pencil"
            >
              <ArrowLeft className="h-4 w-4" aria-hidden />Back to Topics
            </Link>
            <h2 className="text-3xl font-bold text-ink mb-2">{topicTitle}</h2>
            <p className="text-ink-soft">Select a subtopic to start reviewing</p>
          </div>
          <div className="sheet divide-y divide-line">
            {subtopics.map((st) => (
              <Link
                key={st.id}
                href={`/mode-selection?topic=${topic}&subtopic=${st.id}`}
                className="flex items-center justify-between gap-4 px-5 py-4 transition-colors hover:bg-pencil-wash"
              >
                <div>
                  <h3 className="font-semibold text-ink">{st.name}</h3>
                  <p className="text-sm text-ink-soft">{st.description || ''}</p>
                </div>
                <div className="flex shrink-0 items-center gap-3">
                  <span className="num text-xs text-ink-soft">10 questions per mode</span>
                  <CircleArrowRight className="h-5 w-5 text-pencil" aria-hidden />
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
