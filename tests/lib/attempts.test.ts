import { describe, it, expect, beforeEach } from 'vitest';
import {
  getAttempts,
  getAttempt,
  saveAttempt,
  getUserName,
  setUserName,
} from '@/lib/attempts';
import type { Attempt } from '@/lib/types';

const attempt = (id: string): Attempt => ({
  id,
  quiz_type: 'elimination',
  user_name: 'Tester',
  score: 80,
  correct_count: 8,
  incorrect_count: 2,
  total_questions: 10,
  passed: true,
  results: [],
  created_at: new Date().toISOString(),
});

describe('attempts storage', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('round-trips saved attempts, newest first', () => {
    saveAttempt(attempt('a1'));
    saveAttempt(attempt('a2'));
    const all = getAttempts();
    expect(all.map((a) => a.id)).toEqual(['a2', 'a1']);
  });

  it('dedupes by id on re-save', () => {
    saveAttempt(attempt('a1'));
    saveAttempt({ ...attempt('a1'), score: 99 });
    const all = getAttempts();
    expect(all.length).toBe(1);
    expect(all[0].score).toBe(99);
  });

  it('caps stored attempts at 50', () => {
    for (let i = 0; i < 55; i++) saveAttempt(attempt(`a${i}`));
    expect(getAttempts().length).toBe(50);
  });

  it('finds an attempt by id', () => {
    saveAttempt(attempt('xyz'));
    expect(getAttempt('xyz')?.score).toBe(80);
    expect(getAttempt('missing')).toBeUndefined();
  });

  it('survives corrupt localStorage data', () => {
    localStorage.setItem('quizbee_attempts', '{not json');
    expect(getAttempts()).toEqual([]);
    localStorage.setItem('quizbee_attempts', '{"a":1}');
    expect(getAttempts()).toEqual([]);
  });

  it('stores and retrieves the user name', () => {
    expect(getUserName()).toBe('');
    setUserName('Mik');
    expect(getUserName()).toBe('Mik');
  });
});
