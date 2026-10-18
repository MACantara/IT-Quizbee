'use client';

import { RotateCcw, TriangleAlert } from 'lucide-react';

export default function Error({ reset }: { error: Error; reset: () => void }) {
  return (
    <main className="container mx-auto flex flex-grow items-center justify-center px-4 py-8">
      <div className="sheet w-full max-w-md p-8 text-center">
        <TriangleAlert className="mx-auto mb-4 h-10 w-10 text-warn" aria-hidden />
        <h2 className="mb-2 text-2xl font-bold text-ink">Something went wrong</h2>
        <p className="mb-6 text-ink-soft">An unexpected error occurred.</p>
        <button onClick={reset} className="btn btn-pencil">
          <RotateCcw className="h-4 w-4" aria-hidden />
          Try Again
        </button>
      </div>
    </main>
  );
}
