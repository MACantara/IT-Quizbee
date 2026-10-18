import Link from 'next/link';
import type { Metadata } from 'next';
import type { LucideIcon } from 'lucide-react';
import {
  ChartLine,
  Cog,
  CodeXml,
  Cpu,
  Database,
  ListChecks,
  Network,
  Package,
  Router,
  Server,
  ShoppingCart,
} from 'lucide-react';
import { getTopics } from '@/lib/questions';

export const metadata: Metadata = { title: 'Select Topic' };

const ICONS: LucideIcon[] = [
  Cpu, Network, Cog, CodeXml, Package, Router, Server, Database, ChartLine, ShoppingCart,
];

export default async function TopicsPage() {
  const topics = await getTopics();

  return (
    <main className="container mx-auto px-4 py-8 flex-grow">
      <div className="max-w-6xl mx-auto animate-fade-in">
        <div className="sheet p-6 sm:p-8">
          <div className="mb-8 flex items-center gap-4 border-b border-line pb-6">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center border border-ink">
              <ListChecks className="h-6 w-6 text-ink" aria-hidden />
            </div>
            <div>
              <p className="field-label mb-0">Question Bank</p>
              <h2 className="text-2xl sm:text-3xl font-bold text-ink">Choose Your Topic</h2>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {topics.map((topic, i) => {
              const Icon = ICONS[i % ICONS.length];
              return (
                <Link
                  key={topic.topic_id}
                  href={`/topics/${topic.topic_id}`}
                  className="block border border-ink bg-white p-5 sm:p-6 transition-colors hover:border-pencil"
                >
                  <div className="mb-4 flex items-center justify-between gap-3">
                    <div className="flex h-11 w-11 shrink-0 items-center justify-center border border-ink">
                      <Icon className="h-6 w-6 text-ink" aria-hidden />
                    </div>
                    <span className="num border border-line px-2 py-0.5 text-xs text-ink-soft">
                      {topic.subtopics?.length ?? 0} subtopics
                    </span>
                  </div>
                  <h3 className="text-lg font-bold text-ink mb-1">{topic.topic_name}</h3>
                  <p className="text-sm text-ink-soft">
                    {topic.description || 'Click to view subtopics'}
                  </p>
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </main>
  );
}
