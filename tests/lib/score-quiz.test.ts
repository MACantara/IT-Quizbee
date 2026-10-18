import { describe, it, expect } from 'vitest';
import { scoreQuiz } from '@/lib/questions';
import type { RawQuestion } from '@/lib/types';

const elim = (over: Partial<RawQuestion> = {}): RawQuestion => ({
  id: 'e1',
  question: 'Which is an OS?',
  options: ['Linux', 'HTML', 'CSS', 'PNG'],
  correct_answer: '0',
  ...over,
});

const fin = (over: Partial<RawQuestion> = {}): RawQuestion => ({
  id: 'f1',
  question: 'Name the first graphical browser.',
  correct_answer: 'NCSA Mosaic',
  answer: 'NCSA Mosaic',
  alternatives: ['Mosaic'],
  ...over,
});

describe('scoreQuiz — elimination', () => {
  it('grades exact option-index match', () => {
    const r = scoreQuiz([elim()], { e1: '0' }, 'elimination');
    expect(r.correct_count).toBe(1);
    expect(r.results[0].is_correct).toBe(true);
  });

  it('rejects wrong index and case-different answers', () => {
    const r = scoreQuiz([elim(), elim({ id: 'e2' })], { e1: '1', e2: '0 ' }, 'elimination');
    expect(r.correct_count).toBe(0);
  });

  it('treats missing answer as incorrect', () => {
    const r = scoreQuiz([elim()], {}, 'elimination');
    expect(r.correct_count).toBe(0);
  });

  it('passes at 70%', () => {
    const qs = Array.from({ length: 10 }, (_, i) => elim({ id: `e${i}` }));
    const answers = Object.fromEntries(qs.map((q, i) => [q.id, i < 7 ? '0' : '1']));
    const r = scoreQuiz(qs, answers, 'elimination');
    expect(r.score).toBe(70);
    expect(r.passed).toBe(true);
  });
});

describe('scoreQuiz — finals', () => {
  it('matches case-insensitively', () => {
    const r = scoreQuiz([fin()], { f1: 'ncsa mosaic' }, 'finals');
    expect(r.results[0].is_correct).toBe(true);
  });

  it('matches with all whitespace stripped', () => {
    const list = fin({ correct_answer: '[1, 2, 3]', answer: '[1, 2, 3]', alternatives: [] });
    const r = scoreQuiz([list], { f1: '[1,2,3]' }, 'finals');
    expect(r.results[0].is_correct).toBe(true);

    const seq = fin({ correct_answer: 'P1, P3, P4, P0, P2', answer: 'P1, P3, P4, P0, P2', alternatives: [] });
    const r2 = scoreQuiz([seq], { f1: 'p1,p3,p4,p0,p2' }, 'finals');
    expect(r2.results[0].is_correct).toBe(true);
  });

  it('accepts alternatives, whitespace-insensitive too', () => {
    const r = scoreQuiz([fin()], { f1: ' MOSAIC ' }, 'finals');
    expect(r.results[0].is_correct).toBe(true);
  });

  it('rejects wrong answers', () => {
    const r = scoreQuiz([fin()], { f1: 'Netscape' }, 'finals');
    expect(r.results[0].is_correct).toBe(false);
  });

  it('passes at 80%', () => {
    const qs = Array.from({ length: 10 }, (_, i) => fin({ id: `f${i}` }));
    const answers = Object.fromEntries(qs.map((q, i) => [q.id, i < 8 ? 'NCSA Mosaic' : 'wrong']));
    const r = scoreQuiz(qs, answers, 'finals');
    expect(r.score).toBe(80);
    expect(r.passed).toBe(true);
  });
});

describe('scoreQuiz — keys & metadata', () => {
  it('looks up answers by composite key when keys are provided', () => {
    const r = scoreQuiz([elim()], { 'net/osi/easy/e1': '0' }, 'elimination', ['net/osi/easy/e1']);
    expect(r.results[0].is_correct).toBe(true);
    expect(r.results[0].question_id).toBe('net/osi/easy/e1');
  });

  it('handles empty question list without NaN', () => {
    const r = scoreQuiz([], {}, 'elimination');
    expect(r.score).toBe(0);
    expect(r.passed).toBe(false);
  });
});
