export type QuizMode = 'elimination' | 'finals';
export type Difficulty = 'easy' | 'average' | 'difficult';

export interface SubtopicMeta {
  id: string;
  name: string;
  description?: string;
}

export interface TopicIndex {
  topic_id: string;
  topic_name: string;
  title?: string;
  description?: string;
  subtopics: SubtopicMeta[];
}

/** Question shape as stored in data/*.json (contains answers — server only) */
export interface RawQuestion {
  id: string;
  question: string;
  options?: string[];
  correct?: number;
  correct_answer?: string | number;
  answer?: string;
  alternatives?: string[];
  explanation?: string;
  difficulty?: string;
  topic_name?: string;
  subtopic_name?: string;
  /** Directory ids — set by the loader so questions can be re-found for scoring */
  topic?: string;
  subtopic?: string;
}

/** Sanitized question sent to the browser (no answers/explanations) */
export interface QuizQuestion {
  id: string;
  question: string;
  options?: string[];
  topic_name: string;
  subtopic_name: string;
  topic: string;
  subtopic: string;
  difficulty?: string;
  mode: QuizMode;
}

export interface AnswerResult {
  question_id: string;
  question: string;
  user_answer: string;
  correct_answer: string | number | undefined;
  is_correct: boolean;
  options: string[];
  explanation: string;
  topic_name: string;
  subtopic_name: string;
  difficulty: string;
  mode: QuizMode;
}

export interface ScoreResult {
  score: number;
  correct_count: number;
  incorrect_count: number;
  total_questions: number;
  passed: boolean;
  results: AnswerResult[];
}

/** Attempt record stored in browser localStorage */
export interface Attempt extends ScoreResult {
  id: string;
  quiz_type: QuizMode;
  topic?: string;
  subtopic?: string;
  difficulty?: string;
  user_name: string;
  time_taken?: number;
  created_at: string;
}
