# IT Quizbee

An interactive IT knowledge reviewer — a fullstack Next.js quiz app with multiple-choice (Elimination) and identification (Finals) modes, built on the question bank in `data/`.

## Stack

- **Next.js 16** (App Router, Turbopack, Cache Components)
- **React 19**, **TypeScript**, **Tailwind CSS 4**
- No database — questions are read from `data/` server-side; quiz attempts live in the browser (`localStorage`), the active quiz in `sessionStorage`.

## Getting Started

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

```bash
npm run build && npm start   # production
npm run lint                 # eslint
```

## How it works

| Concern | Where |
|---|---|
| Question bank | `data/<topic>/<subtopic>/<mode>/<file>.json` (unchanged from the Flask era) |
| Server reads | `src/lib/questions.ts` (`'use cache'` for index files) |
| Question API | `GET /api/questions` — sanitized, answers never leave the server |
| Scoring API | `POST /api/score` — server reloads questions by id and grades |
| Health check | `GET /api/health` |
| Attempts / review | `localStorage` (`quizbee_attempts`, capped at 50) → `/quiz/results`, `/quiz/review/[id]` |

## Modes

- **Elimination** — 100 random multiple-choice questions across all topics, 60 minutes (or 10 questions for a single subtopic via Review).
- **Finals** — 30 identification questions at mixed difficulty (10 per subtopic at a chosen difficulty via Review), per-question timers (20s/30s/40s).
- **Review** — browse `Topics → Subtopic → Mode` for 10-question focused quizzes.

Attempts are stored only in the browser that took the quiz — review links are not portable across devices.

## Deploy

Deploys to Vercel as-is. `outputFileTracingIncludes` in `next.config.ts` bundles `data/` into the serverless functions.
