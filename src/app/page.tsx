import Link from 'next/link';
import type { LucideIcon } from 'lucide-react';
import {
  BookOpen,
  Check,
  GraduationCap,
  Lightbulb,
  ListChecks,
  Timer,
  Trophy,
  Zap,
} from 'lucide-react';

const FEATURES: { icon: LucideIcon; title: string; sub: string }[] = [
  { icon: ListChecks, title: '10 Topics', sub: 'Comprehensive coverage' },
  { icon: Timer, title: 'Multiple Modes', sub: 'Practice your way' },
  { icon: Trophy, title: 'Three Game Modes', sub: 'Elimination, Finals & Review' },
  { icon: Lightbulb, title: 'Explanations', sub: 'Learn from answers' },
];

const MODES: { href: string; icon: LucideIcon; title: string; items: string[]; cta: string }[] = [
  {
    href: '/quiz/elimination',
    icon: Zap,
    title: 'Elimination',
    items: ['100 random questions', 'From all 10 topics', '60 minutes total'],
    cta: 'Start Elimination',
  },
  {
    href: '/quiz/finals',
    icon: Trophy,
    title: 'Finals',
    items: ['30 identification questions', 'Easy, Average, Difficult', 'Timed questions'],
    cta: 'Start Finals',
  },
  {
    href: '/topics',
    icon: BookOpen,
    title: 'Review',
    items: ['Choose any topic', 'Select subtopics', 'Practice at your pace'],
    cta: 'Start Review',
  },
];

export default function Home() {
  return (
    <main className="container mx-auto px-4 py-8 flex-grow">
      <div className="max-w-6xl mx-auto">
        <div className="sheet p-6 sm:p-8 animate-fade-in">
          <div className="mb-8 flex items-center justify-between gap-4 border-b border-line pb-6">
            <div className="flex h-14 w-14 shrink-0 items-center justify-center border border-ink">
              <GraduationCap className="h-8 w-8 text-ink" aria-hidden />
            </div>
            <span className="num border border-line px-2 py-0.5 text-xs tracking-[0.14em] text-ink-soft">
              FORM Q-1 · REVIEW EDITION
            </span>
          </div>

          <h2 className="text-3xl sm:text-4xl font-bold text-ink mb-2">Welcome to IT Quizbee!</h2>
          <p className="text-lg text-ink-soft mb-8">Test your knowledge across 10 essential IT topics</p>

          <div className="sheet divide-y divide-line mb-10">
            {FEATURES.map((f) => (
              <div key={f.title} className="flex items-center gap-4 px-4 py-4 sm:px-5">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center border border-ink">
                  <f.icon className="h-5 w-5 text-ink" aria-hidden />
                </div>
                <div>
                  <h3 className="font-semibold text-ink">{f.title}</h3>
                  <p className="text-sm text-ink-soft">{f.sub}</p>
                </div>
              </div>
            ))}
          </div>

          <h3 className="field-label mb-4">Choose Your Mode</h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {MODES.map((m, i) => (
              <Link
                key={m.title}
                href={m.href}
                className="block border border-ink bg-white p-6 transition-colors hover:border-pencil"
              >
                <div className="num mb-4 text-xs tracking-[0.2em] text-ink-soft">{i + 1}</div>
                <m.icon className="h-6 w-6 text-ink mb-2" aria-hidden />
                <h3 className="text-xl font-bold text-ink mb-4">{m.title}</h3>
                <ul className="mb-6 text-sm text-ink-soft">
                  {m.items.map((item) => (
                    <li key={item} className="flex items-center gap-2 border-t border-line py-2">
                      <Check className="h-4 w-4 shrink-0 text-pass" aria-hidden />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
                <div className="btn btn-pencil w-full">{m.cta}</div>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
