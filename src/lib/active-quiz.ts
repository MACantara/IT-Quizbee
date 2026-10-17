'use client';

import type { QuizMode, QuizQuestion } from './types';

const ACTIVE_KEY = 'quizbee_active';
const LAST_RESULT_KEY = 'quizbee_last_result';

export interface ActiveQuiz {
  mode: QuizMode;
  topic?: string;
  subtopic?: string;
  difficulty?: string;
  questions: QuizQuestion[];
  answers: Record<string, string>;
  currentIndex: number;
  userName: string;
  startTime: number;
}

export function saveActiveQuiz(state: ActiveQuiz): void {
  try {
    sessionStorage.setItem(ACTIVE_KEY, JSON.stringify(state));
  } catch {
    /* quota — non-fatal */
  }
}

export function loadActiveQuiz(mode: QuizMode): ActiveQuiz | null {
  try {
    const raw = sessionStorage.getItem(ACTIVE_KEY);
    const parsed = raw ? (JSON.parse(raw) as ActiveQuiz) : null;
    return parsed?.mode === mode && Array.isArray(parsed.questions) ? parsed : null;
  } catch {
    return null;
  }
}

export function clearActiveQuiz(): void {
  sessionStorage.removeItem(ACTIVE_KEY);
}

export function setLastResultId(id: string): void {
  sessionStorage.setItem(LAST_RESULT_KEY, id);
}

export function getLastResultId(): string | null {
  return sessionStorage.getItem(LAST_RESULT_KEY);
}

/** useSyncExternalStore snapshot */
export function lastResultIdSnapshot(): string | null {
  return sessionStorage.getItem(LAST_RESULT_KEY);
}
