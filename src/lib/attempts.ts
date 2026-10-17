'use client';

import type { Attempt } from './types';

const ATTEMPTS_KEY = 'quizbee_attempts';
const NAME_KEY = 'quizUserName';
const MAX_ATTEMPTS = 50;

function readAttempts(): Attempt[] {
  try {
    const raw = localStorage.getItem(ATTEMPTS_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function getAttempts(): Attempt[] {
  return readAttempts();
}

export function getAttempt(id: string): Attempt | undefined {
  return readAttempts().find((a) => a.id === id);
}

/** useSyncExternalStore snapshots — return the raw string so the snapshot is stable */
export function attemptsSnapshot(): string | null {
  return localStorage.getItem(ATTEMPTS_KEY);
}

export function findAttempt(raw: string | null, id: string): Attempt | null {
  try {
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? (parsed.find((a: Attempt) => a.id === id) ?? null) : null;
  } catch {
    return null;
  }
}

export function saveAttempt(attempt: Attempt): void {
  const all = [attempt, ...readAttempts().filter((a) => a.id !== attempt.id)];
  localStorage.setItem(ATTEMPTS_KEY, JSON.stringify(all.slice(0, MAX_ATTEMPTS)));
}

export function getUserName(): string {
  return localStorage.getItem(NAME_KEY) ?? '';
}

export function setUserName(name: string): void {
  localStorage.setItem(NAME_KEY, name);
}
