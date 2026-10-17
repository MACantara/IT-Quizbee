import type { Metadata } from 'next';
import { Suspense } from 'react';
import { AttemptLoader } from '@/components/AttemptLoader';

export const metadata: Metadata = { title: 'Results' };

export default function ResultsPage() {
  return (
    <Suspense>
      <AttemptLoader />
    </Suspense>
  );
}
