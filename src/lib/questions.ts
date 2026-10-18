import 'server-only';
import { promises as fs } from 'fs';
import path from 'path';
import type {
  Difficulty,
  QuizMode,
  QuizQuestion,
  RawQuestion,
  ScoreResult,
  SubtopicMeta,
  TopicIndex,
} from './types';

const DATA_DIR = path.join(process.cwd(), 'data');
const FINALS_DIFFICULTIES: Difficulty[] = ['easy', 'average', 'difficult'];
const SLUG = /^[a-z0-9_-]+$/i;

function checkSlug(...parts: (string | undefined)[]): void {
  if (parts.some((p) => !p || !SLUG.test(p))) {
    throw new Error('Invalid question path');
  }
}

async function readJson<T>(file: string): Promise<T> {
  return JSON.parse(await fs.readFile(file, 'utf-8')) as T;
}

async function pathExists(file: string): Promise<boolean> {
  try {
    await fs.access(file);
    return true;
  } catch {
    return false;
  }
}

function sample<T>(items: T[], count: number): T[] {
  const copy = [...items];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy.slice(0, Math.min(count, copy.length));
}

function titleize(slug: string): string {
  return slug
    .split('_')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join(' ');
}

export async function getTopics(): Promise<TopicIndex[]> {
  'use cache';
  const entries = await fs.readdir(DATA_DIR, { withFileTypes: true });
  const topics: TopicIndex[] = [];
  for (const entry of entries) {
    if (!entry.isDirectory()) continue;
    const indexFile = path.join(DATA_DIR, entry.name, 'index.json');
    if (await pathExists(indexFile)) {
      topics.push(await readJson<TopicIndex>(indexFile));
    }
  }
  return topics.sort((a, b) => (a.title ?? a.topic_name).localeCompare(b.title ?? b.topic_name));
}

export async function getSubtopics(topic: string): Promise<SubtopicMeta[]> {
  'use cache';
  checkSlug(topic);
  const indexFile = path.join(DATA_DIR, topic, 'index.json');
  if (!(await pathExists(indexFile))) {
    throw new Error(`Topic not found: ${topic}`);
  }
  const data = await readJson<TopicIndex>(indexFile);
  return data.subtopics ?? [];
}

export async function getTopic(topic: string): Promise<TopicIndex> {
  'use cache';
  checkSlug(topic);
  const indexFile = path.join(DATA_DIR, topic, 'index.json');
  if (!(await pathExists(indexFile))) {
    throw new Error(`Topic not found: ${topic}`);
  }
  return readJson<TopicIndex>(indexFile);
}

function questionsFilePath(
  topic: string,
  subtopic: string,
  mode: QuizMode,
  difficulty?: string
): string {
  return mode === 'elimination'
    ? path.join(DATA_DIR, topic, subtopic, 'elimination', `${subtopic}.json`)
    : path.join(DATA_DIR, topic, subtopic, 'finals', difficulty ?? 'average', `${subtopic}.json`);
}

/**
 * Load questions for a quiz — mirrors the Flask QuizService.load_questions.
 * Returns RAW questions (with answers); sanitize before sending to the client.
 */
export async function loadQuestions(
  topic: string,
  subtopic: string,
  numQuestions: number,
  mode: QuizMode,
  difficulty: string = 'medium'
): Promise<RawQuestion[]> {
  checkSlug(topic, subtopic, difficulty);
  let topicName = titleize(topic);
  let subtopicName = titleize(subtopic);

  const indexFile = path.join(DATA_DIR, topic, 'index.json');
  if (await pathExists(indexFile)) {
    const index = await readJson<TopicIndex>(indexFile);
    topicName = index.topic_name ?? topicName;
    const st = index.subtopics?.find((s) => s.id === subtopic);
    if (st) subtopicName = st.name ?? subtopicName;
  }

  const file = questionsFilePath(topic, subtopic, mode, difficulty);
  if (!(await pathExists(file))) {
    throw new Error(`Questions file not found: ${file}`);
  }
  const data = await readJson<RawQuestion[] | { questions: RawQuestion[]; topic_name?: string; subtopic_name?: string }>(file);

  let all: RawQuestion[];
  if (Array.isArray(data)) {
    all = data;
  } else if (data && Array.isArray(data.questions)) {
    all = data.questions;
    if (data.topic_name) topicName = data.topic_name;
    if (data.subtopic_name) subtopicName = data.subtopic_name;
  } else {
    throw new Error(`Invalid questions file format: ${file}`);
  }

  const valid: RawQuestion[] = [];
  for (const q of all) {
    q.topic_name = topicName;
    q.subtopic_name = subtopicName;
    q.topic = topic;
    q.subtopic = subtopic;
    if (mode === 'finals' && !q.difficulty) q.difficulty = difficulty;
    if (mode === 'elimination') {
      if (q.id && q.question && Array.isArray(q.options)) {
        if (q.correct !== undefined && q.correct_answer === undefined) {
          q.correct_answer = q.correct;
        }
        if (q.correct_answer !== undefined) valid.push(q);
      }
    } else if (mode === 'finals') {
      if (q.id && q.question && q.answer !== undefined) {
        if (q.correct_answer === undefined) q.correct_answer = q.answer;
        valid.push(q);
      }
    }
  }

  return valid.length <= numQuestions ? valid : sample(valid, numQuestions);
}

/** Full-mode elimination: sample from every topic/subtopic pool */
export async function loadEliminationPool(count = 100): Promise<RawQuestion[]> {
  const pool: RawQuestion[] = [];
  for (const topic of await getTopics()) {
    for (const st of await getSubtopics(topic.topic_id)) {
      try {
        pool.push(...(await loadQuestions(topic.topic_id, st.id, 100, 'elimination')));
      } catch {
        continue;
      }
    }
  }
  return sample(pool, count);
}

/** Full-mode finals: 10 each of easy/average/difficult, topped up to `count` */
export async function loadFinalsPool(count = 30): Promise<RawQuestion[]> {
  const pools: Record<Difficulty, RawQuestion[]> = { easy: [], average: [], difficult: [] };
  for (const topic of await getTopics()) {
    for (const st of await getSubtopics(topic.topic_id)) {
      for (const diff of FINALS_DIFFICULTIES) {
        try {
          const qs = await loadQuestions(topic.topic_id, st.id, 20, 'finals', diff);
          for (const q of qs) q.difficulty = diff;
          pools[diff].push(...qs);
        } catch {
          continue;
        }
      }
    }
  }
  const per = Math.floor(count / FINALS_DIFFICULTIES.length);
  const picked = FINALS_DIFFICULTIES.flatMap((d) => sample(pools[d], per));
  if (picked.length < count) {
    // ids repeat across data files — dedupe on composite identity
    const key = (q: RawQuestion) => `${q.topic}/${q.subtopic}/${q.difficulty}/${q.id}`;
    const pickedIds = new Set(picked.map(key));
    const rest = FINALS_DIFFICULTIES.flatMap((d) => pools[d]).filter((q) => !pickedIds.has(key(q)));
    picked.push(...sample(rest, count - picked.length));
  }
  return picked;
}

/** Strip answers/explanations before sending questions to the browser */
export function sanitize(questions: RawQuestion[], mode: QuizMode): QuizQuestion[] {
  return questions.map((q) => ({
    // ids repeat across data files — composite key for client-side identity
    key: `${q.topic}/${q.subtopic}/${q.difficulty ?? ''}/${q.id}`,
    id: String(q.id),
    question: q.question,
    options: q.options,
    topic_name: q.topic_name ?? '',
    subtopic_name: q.subtopic_name ?? '',
    topic: q.topic ?? '',
    subtopic: q.subtopic ?? '',
    difficulty: q.difficulty,
    mode,
  }));
}

export function scoreQuiz(
  questions: RawQuestion[],
  answers: Record<string, string>,
  quizType: QuizMode,
  keys?: string[]
): ScoreResult {
  let correct = 0;
  const results = questions.map((q, i) => {
    const questionId = keys?.[i] ?? String(q.id);
    const userAnswer = answers[questionId] ?? '';
    const correctAnswer = q.correct_answer;
    let isCorrect: boolean;

    if (quizType === 'elimination') {
      isCorrect = String(userAnswer) === String(correctAnswer);
    } else {
      const norm = (s: unknown) => String(s).replace(/\s+/g, '').toLowerCase();
      const ua = norm(userAnswer);
      isCorrect = ua === norm(correctAnswer);
      if (!isCorrect && q.alternatives?.length) {
        isCorrect = q.alternatives.some((a) => ua === norm(a));
      }
    }
    if (isCorrect) correct++;

    return {
      question_id: questionId,
      question: q.question,
      user_answer: userAnswer,
      correct_answer: correctAnswer,
      is_correct: isCorrect,
      options: q.options ?? [],
      explanation: q.explanation ?? '',
      topic_name: q.topic_name ?? '',
      subtopic_name: q.subtopic_name ?? '',
      difficulty: q.difficulty ?? '',
      mode: quizType,
    };
  });

  const total = questions.length;
  const score = total > 0 ? Math.round((correct / total) * 10000) / 100 : 0;
  return {
    score,
    correct_count: correct,
    incorrect_count: total - correct,
    total_questions: total,
    passed: score >= (quizType === 'elimination' ? 70 : 80),
    results,
  };
}
