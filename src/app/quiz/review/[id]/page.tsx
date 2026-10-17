import type { Metadata } from 'next';
import { Suspense } from 'react';
import { AttemptLoader } from '@/components/AttemptLoader';

export const metadata: Metadata = { title: 'Quiz Review' };

export default async function ReviewPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <Suspense>
      <AttemptLoader id={id} />
    </Suspense>
  );
}
