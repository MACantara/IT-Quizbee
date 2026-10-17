import type { Metadata } from 'next';
import { Suspense } from 'react';
import { AttemptLoader } from '@/components/AttemptLoader';

export const metadata: Metadata = { title: 'Quiz Review' };

export default function ReviewPage({ params }: { params: Promise<{ id: string }> }) {
  return (
    <Suspense>
      <Review params={params} />
    </Suspense>
  );
}

async function Review({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <AttemptLoader id={id} />;
}
