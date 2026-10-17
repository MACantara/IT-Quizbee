import { NextResponse } from 'next/server';
import { getTopics } from '@/lib/questions';

export async function GET() {
  try {
    const topics = await getTopics();
    return NextResponse.json({
      status: 'healthy',
      topics_loaded: topics.length,
    });
  } catch {
    return NextResponse.json({ status: 'unhealthy' }, { status: 503 });
  }
}
