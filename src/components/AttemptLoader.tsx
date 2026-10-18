'use client';

import { useSyncExternalStore } from 'react';
import Link from 'next/link';
import { CircleHelp, House } from 'lucide-react';
import { attemptsSnapshot, findAttempt } from '@/lib/attempts';
import { lastResultIdSnapshot } from '@/lib/active-quiz';
import { ResultsView } from './ResultsView';

const subscribe = () => () => {};
const mountedSnapshot = () => true;
const serverSnapshot = () => false;

function firstAttemptId(raw: string | null): string {
  try {
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) && parsed[0]?.id ? parsed[0].id : '';
  } catch {
    return '';
  }
}

/** Loads an attempt from localStorage — by id, or the most recent result */
export function AttemptLoader({ id }: { id?: string }) {
  const mounted = useSyncExternalStore(subscribe, mountedSnapshot, serverSnapshot);
  const raw = useSyncExternalStore(subscribe, attemptsSnapshot, () => null);
  const lastId = useSyncExternalStore(subscribe, lastResultIdSnapshot, () => null);

  if (!mounted) return null;
  // New tab after a quiz: lastResultId lives in sessionStorage, so fall back to
  // the newest stored attempt when nothing else points at one
  const resolved = id ?? lastId ?? firstAttemptId(raw);
  const attempt = resolved ? findAttempt(raw, resolved) : null;

  if (!attempt) {
    return (
      <main className="container mx-auto flex-grow px-4 py-8">
        <div className="sheet mx-auto max-w-md p-8 text-center">
          <CircleHelp className="mx-auto mb-4 h-10 w-10 text-ink-soft" aria-hidden />
          <h2 className="mb-2 text-2xl font-bold text-ink">No results found</h2>
          <p className="mb-6 text-ink-soft">
            This attempt isn&apos;t stored in this browser; results only live on the device that
            took the quiz.
          </p>
          <Link href="/" className="btn btn-pencil">
            <House className="h-4 w-4" aria-hidden />
            Home
          </Link>
        </div>
      </main>
    );
  }
  return <ResultsView attempt={attempt} review={Boolean(id)} />;
}
