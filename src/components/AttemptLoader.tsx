'use client';

import { useSyncExternalStore } from 'react';
import Link from 'next/link';
import { attemptsSnapshot, findAttempt } from '@/lib/attempts';
import { lastResultIdSnapshot } from '@/lib/active-quiz';
import { ResultsView } from './ResultsView';

const subscribe = () => () => {};
const mountedSnapshot = () => true;
const serverSnapshot = () => false;

/** Loads an attempt from localStorage — by id, or the most recent result */
export function AttemptLoader({ id }: { id?: string }) {
  const mounted = useSyncExternalStore(subscribe, mountedSnapshot, serverSnapshot);
  const raw = useSyncExternalStore(subscribe, attemptsSnapshot, () => null);
  const lastId = useSyncExternalStore(subscribe, lastResultIdSnapshot, () => null);

  if (!mounted) return null;
  const resolved = id ?? lastId ?? '';
  const attempt = resolved ? findAttempt(raw, resolved) : null;

  if (!attempt) {
    return (
      <main className="container mx-auto px-4 py-8 flex-grow">
        <div className="max-w-md mx-auto bg-white rounded-2xl shadow-xl p-8 text-center">
          <i className="bi bi-exclamation-circle text-6xl text-gray-400 mb-4" />
          <h2 className="text-2xl font-bold text-gray-800 mb-2">No results found</h2>
          <p className="text-gray-600 mb-6">
            This attempt isn&apos;t stored in this browser — results only live on the device that
            took the quiz.
          </p>
          <Link
            href="/"
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition inline-block"
          >
            <i className="bi bi-house mr-2" />Home
          </Link>
        </div>
      </main>
    );
  }
  return <ResultsView attempt={attempt} review={Boolean(id)} />;
}
