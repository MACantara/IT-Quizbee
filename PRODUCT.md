# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

IT students preparing for quiz bee competitions. They practice alone on their own device, using the app as a self-review tool that mirrors the real competition format.

## Product Purpose

IT Quizbee lets contestants rehearse IT quiz bees end to end: an elimination round (100 multiple-choice questions, 60 minutes), a finals round (timed identification questions across easy/average/difficult), and a review mode for drilling a single topic or subtopic. Success means a contestant walks into a real quiz bee having already felt its structure and pressure.

## Positioning

It is structured after the actual competition — elimination then finals, timed rounds, identification answers — not a generic flashcard quiz. Practice resumes after a refresh because state persists locally, so a review session can span interruptions without accounts or setup.

## Operating Context

Solo practice sessions on the user's own browser. Attempts and in-progress quizzes live in localStorage/sessionStorage on that device; results are reviewable later on the same device.

## Capabilities and Constraints

- Question bank ships as JSON under `data/`, organized by topic and subtopic, with elimination and finals (easy/average/difficult) pools.
- Elimination: 100 questions across all topics, 60-minute timer; per-topic variant: 10 questions.
- Finals: 30 identification questions (or 10 per difficulty in review), per-question timers of 20/30/40s.
- No accounts, no server-side user data; results only exist on the device that took the quiz.
- Scoring via `/api/score`; answers are case-insensitive strings or option indices.

## Brand Commitments

- Name: "IT Quizbee" stays.
- Competition framing stays: elimination/finals structure and competitive language.

## Evidence on Hand

- Question bank: `data/` (10 topics with subtopics, elimination + finals JSON files).
- No testimonials, logos, or image assets; `public/` holds only framework defaults.

## Product Principles

- Mirror the real competition: timers, rounds, and identification answers match quiz bee rules.
- Zero friction to start: enter a name, answer questions — no signup, no setup.
- Never lose a session: refresh restores the quiz; results persist on-device.
- Every answer teaches: explanations and correct answers are always shown in review.
