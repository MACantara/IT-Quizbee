import { describe, it, expect } from 'vitest';
import { NextRequest } from 'next/server';
import { POST } from '@/app/api/score/route';
import { loadQuestions } from '@/lib/questions';

const req = (body: unknown) =>
  new NextRequest('http://localhost/api/score', {
    method: 'POST',
    body: typeof body === 'string' ? body : JSON.stringify(body),
    headers: { 'content-type': 'application/json' },
  });

describe('POST /api/score — validation', () => {
  it('rejects invalid JSON', async () => {
    const res = await POST(req('{oops'));
    expect(res.status).toBe(400);
  });

  it('rejects missing/invalid mode', async () => {
    const res = await POST(req({ mode: 'clincher', questions: [{}], answers: {} }));
    expect(res.status).toBe(400);
  });

  it('rejects empty refs and oversized payloads', async () => {
    expect((await POST(req({ mode: 'elimination', questions: [], answers: {} }))).status).toBe(400);
    const big = { mode: 'elimination', questions: Array(501).fill({ key: 'k', id: 'x', topic: 'a', subtopic: 'b' }), answers: {} };
    expect((await POST(req(big))).status).toBe(400);
  });

  it('rejects refs with invalid slugs', async () => {
    const body = {
      mode: 'elimination',
      questions: [{ key: 'k', id: 'x', topic: '../etc', subtopic: 'b' }],
      answers: {},
    };
    expect((await POST(req(body))).status).toBe(400);
  });
});

describe('POST /api/score — grading against real data', () => {
  it('grades an elimination question round-trip', async () => {
    const [q] = await loadQuestions('it_basics', 'computer_basics', 1, 'elimination');
    const key = `it_basics/computer_basics//${q.id}`;
    const body = {
      mode: 'elimination',
      questions: [{ key, id: String(q.id), topic: 'it_basics', subtopic: 'computer_basics' }],
      answers: { [key]: String(q.correct_answer) },
    };
    const res = await POST(req(body));
    expect(res.status).toBe(200);
    const json = await res.json();
    expect(json.correct_count).toBe(1);
    expect(json.results[0].is_correct).toBe(true);
    // server re-derives correct_answer; client never supplies it
    expect(String(json.results[0].correct_answer)).toBe(String(q.correct_answer));
  });

  it('grades a finals question with whitespace-insensitive matching', async () => {
    const [q] = await loadQuestions('logic', 'truth_tables', 1, 'finals', 'easy');
    const key = `logic/truth_tables/easy/${q.id}`;
    const body = {
      mode: 'finals',
      questions: [{ key, id: String(q.id), topic: 'logic', subtopic: 'truth_tables', difficulty: 'easy' }],
      answers: { [key]: `  ${String(q.correct_answer).toUpperCase()} ` },
    };
    const res = await POST(req(body));
    const json = await res.json();
    expect(json.results[0].is_correct).toBe(true);
  });

  it('rejects an unknown question reference', async () => {
    const body = {
      mode: 'elimination',
      questions: [{ key: 'k', id: 'nonexistent_id_xyz', topic: 'it_basics', subtopic: 'computer_basics' }],
      answers: { k: '0' },
    };
    const res = await POST(req(body));
    expect(res.status).toBe(400);
  });
});
