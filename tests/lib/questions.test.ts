import { describe, it, expect } from 'vitest';
import {
  loadQuestions,
  loadEliminationPool,
  loadFinalsPool,
  sanitize,
  getTopics,
  getSubtopics,
} from '@/lib/questions';

describe('loadQuestions — real data', () => {
  it('loads an elimination file and normalizes correct index', async () => {
    const qs = await loadQuestions('it_basics', 'computer_basics', 10, 'elimination');
    expect(qs.length).toBeGreaterThan(0);
    for (const q of qs) {
      expect(q.id).toBeTruthy();
      expect(q.question).toBeTruthy();
      expect(Array.isArray(q.options)).toBe(true);
      expect(q.correct_answer).not.toBeUndefined();
      expect(q.topic).toBe('it_basics');
      expect(q.subtopic).toBe('computer_basics');
    }
  });

  it('loads a finals file with answers and difficulty tag', async () => {
    const qs = await loadQuestions('logic', 'truth_tables', 10, 'finals', 'difficult');
    expect(qs.length).toBeGreaterThan(0);
    for (const q of qs) {
      expect(q.correct_answer).not.toBeUndefined();
      expect(q.difficulty).toBe('difficult');
    }
  });

  it('caps results at numQuestions', async () => {
    const qs = await loadQuestions('networks', 'osi_model', 5, 'elimination');
    expect(qs.length).toBeLessThanOrEqual(5);
  });

  it('rejects invalid slugs (path traversal guard)', async () => {
    await expect(loadQuestions('..', 'x', 1, 'elimination')).rejects.toThrow('Invalid question path');
    await expect(loadQuestions('it_basics', '../secrets', 1, 'elimination')).rejects.toThrow(
      'Invalid question path'
    );
  });

  it('throws for missing files', async () => {
    await expect(loadQuestions('it_basics', 'no_such_subtopic', 1, 'elimination')).rejects.toThrow();
  });
});

describe('topic/subtopic discovery', () => {
  it('discovers all 11 topics from index.json files', async () => {
    const topics = await getTopics();
    expect(topics.length).toBe(11);
    const ids = topics.map((t) => t.topic_id);
    expect(ids).toContain('programming');
    expect(ids).toContain('it_basics');
  });

  it('returns subtopics for a topic', async () => {
    const subs = await getSubtopics('programming');
    const ids = subs.map((s) => s.id);
    expect(ids).toContain('code_tracing');
  });
});

describe('pools', () => {
  it('elimination pool returns requested count across topics', async () => {
    const pool = await loadEliminationPool(30);
    expect(pool.length).toBe(30);
    const topics = new Set(pool.map((q) => q.topic));
    expect(topics.size).toBeGreaterThan(1);
  });

  it('finals pool returns mixed difficulties', async () => {
    const pool = await loadFinalsPool(30);
    expect(pool.length).toBe(30);
    const diffs = new Set(pool.map((q) => q.difficulty));
    expect(diffs.size).toBeGreaterThan(1);
    // composite identity must be unique
    const keys = pool.map((q) => `${q.topic}/${q.subtopic}/${q.difficulty}/${q.id}`);
    expect(new Set(keys).size).toBe(keys.length);
  });
});

describe('sanitize', () => {
  it('strips answers and explanations, adds composite key', async () => {
    const raw = await loadQuestions('it_basics', 'computer_basics', 3, 'elimination');
    const clean = sanitize(raw, 'elimination');
    for (const q of clean) {
      const json = JSON.stringify(q);
      expect(json).not.toContain('correct_answer');
      expect(json).not.toContain('"explanation"');
      expect(json).not.toContain('"answer"');
      expect(q.key).toContain('it_basics/computer_basics/');
      expect(q.mode).toBe('elimination');
    }
  });
});
