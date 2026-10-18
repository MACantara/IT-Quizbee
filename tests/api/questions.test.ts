import { describe, it, expect } from 'vitest';
import { NextRequest } from 'next/server';
import { GET } from '@/app/api/questions/route';

const req = (qs: string) => new NextRequest(`http://localhost/api/questions?${qs}`);

describe('GET /api/questions', () => {
  it('rejects invalid mode', async () => {
    const res = await GET(req('mode=clincher'));
    expect(res.status).toBe(400);
  });

  it('rejects slug-injection params', async () => {
    const res = await GET(req('mode=elimination&topic=../etc'));
    expect(res.status).toBe(400);
  });

  it('serves a sanitized review-mode quiz', async () => {
    const res = await GET(req('mode=elimination&topic=it_basics&subtopic=computer_basics'));
    expect(res.status).toBe(200);
    const json = await res.json();
    expect(json.questions.length).toBe(10);
    for (const q of json.questions) {
      expect(JSON.stringify(q)).not.toContain('correct_answer');
      expect(q.key).toBeTruthy();
    }
  });

  it('serves finals review with requested difficulty', async () => {
    const res = await GET(req('mode=finals&topic=logic&subtopic=truth_tables&difficulty=difficult'));
    expect(res.status).toBe(200);
    const json = await res.json();
    expect(json.questions.every((q: { difficulty: string }) => q.difficulty === 'difficult')).toBe(true);
  });

  it('serves full-mode elimination pool', async () => {
    const res = await GET(req('mode=elimination'));
    const json = await res.json();
    expect(json.questions.length).toBe(100);
    expect(json.topic).toBe('all_topics');
  });

  it('404s on a missing subtopic', async () => {
    const res = await GET(req('mode=elimination&topic=it_basics&subtopic=nonexistent'));
    expect(res.status).toBe(404);
  });
});
