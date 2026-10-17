# IT-Quizbee Storage Guide

IT-Quizbee uses **file-based storage** — no database server required.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. (Optional) Configure Environment

Create a `.env` file in the project root if you want to override defaults:

```env
SECRET_KEY=your-secret-key
QUIZBEE_STORE_DIR=/path/to/data/dir   # optional, defaults to ./instance
```

### 3. Run Application

```bash
python run.py
```

Application starts on `http://localhost:5000`. No initialization step is needed — storage files are created automatically on first write.

### 4. Run Tests

```bash
pytest tests/ -v
```

Tests point `QUIZBEE_STORE_DIR` at a temporary directory, so they never touch real data.

## How Storage Works

### Session Storage
- Quiz sessions are stored in the user's **Flask session** via Flask-Session
- `SESSION_TYPE='filesystem'` — session files live under `flask_session/`
- Sessions expire with the browser session, so no cleanup job is needed

### Session Flow
1. User starts quiz → `QuizSession` is serialized into the Flask session
2. User submits quiz → Session is retrieved from the Flask session
3. Results are persisted as a `QuizAttempt` record in `instance/attempts.json`
4. Session marked completed and removed from the Flask session

### JSON Store

Quiz attempts and question reports persist as JSON files in `instance/`:

| File | Contents |
|------|----------|
| `instance/attempts.json` | All `QuizAttempt` records |
| `instance/reports.json` | All `QuestionReport` records |

- `instance/` is gitignored — it holds local runtime data only
- Override the location with the `QUIZBEE_STORE_DIR` environment variable
- Implemented in `app/repositories/json_store.py` — a single-file JSON store
  with upsert-by-id writes, so writes are idempotent

### Record Fields

**QuizSession** (Flask session, not persisted to disk)
```
id (UUID)              - Session identifier
quiz_type              - 'elimination' or 'finals'
questions              - Quiz questions (list)
topic / subtopic       - Optional, for review mode
difficulty             - Difficulty level (optional)
user_name              - Name of the quiz taker (optional)
time_limit             - Time limit in seconds (optional)
created_at             - Session creation time
expires_at             - Session expiration time (default 2 hours)
completed              - Whether quiz was submitted
completed_at           - Completion time (optional)
```

**QuizAttempt** (`instance/attempts.json`)
```
id (UUID)              - Attempt identifier
session_id             - ID of the quiz session
quiz_type              - 'elimination', 'finals', or 'review'
topic / subtopic       - Optional, for review mode
difficulty             - Difficulty level (optional)
user_name              - Name of the quiz taker
score                  - Score as percentage
correct_count          - Number of correct answers
incorrect_count        - Number of incorrect answers
time_taken             - Time taken in seconds (optional)
answers                - Detailed answer data (list)
created_at             - Attempt creation time
completed_at           - Attempt completion time
```

**QuestionReport** (`instance/reports.json`)
```
id (UUID)              - Report identifier
question_id            - ID of the reported question
report_type            - Issue type (incorrect_answer, unclear_question, ...)
reason                 - Detailed explanation from user
user_name              - Reporter name ('Anonymous' default)
topic / subtopic       - Question location
quiz_type / difficulty - Quiz context
question_text          - The question text
question_data          - Full question data
status                 - 'pending' / 'reviewed'
admin_notes            - Admin notes (optional)
reviewed_by            - Admin who reviewed (optional)
reviewed_at            - Review time (optional)
created_at             - Report creation time
```

## Analytics API

### Available Endpoints

#### 1. Overall Summary
```bash
GET /api/analytics/summary
```

Response:
```json
{
  "total_attempts": 150,
  "average_score": 72.5,
  "most_popular_mode": "elimination_full",
  "average_duration_seconds": 1800,
  "completed_sessions": 150
}
```

#### 2. Stats by Mode
```bash
GET /api/analytics/by-mode
```

Response:
```json
{
  "elimination_full": {
    "count": 100,
    "average_score": 75.2,
    "min_score": 40,
    "max_score": 98,
    "total_questions_answered": 10000
  },
  "finals_full": {
    "count": 50,
    "average_score": 68.3,
    "min_score": 30,
    "max_score": 95,
    "total_questions_answered": 1500
  }
}
```

#### 3. Stats by Difficulty
```bash
GET /api/analytics/by-difficulty
```

Response:
```json
{
  "easy": {
    "count": 50,
    "average_score": 85.2,
    "min_score": 60,
    "max_score": 100
  },
  "average": {
    "count": 50,
    "average_score": 68.3,
    "min_score": 30,
    "max_score": 95
  },
  "difficult": {
    "count": 50,
    "average_score": 55.1,
    "min_score": 10,
    "max_score": 90
  }
}
```

#### 4. Recent Attempts
```bash
GET /api/analytics/recent-attempts?limit=10&days=7&mode=elimination_full
```

Response:
```json
[
  {
    "id": "abc123...",
    "quiz_mode": "elimination_full",
    "score": 78.5,
    "correct": 78,
    "total": 100,
    "difficulty": null,
    "created_at": "2024-10-19T15:30:00"
  }
]
```

#### 5. Attempt Details
```bash
GET /api/analytics/attempt/{attempt_id}
```

Response:
```json
{
  "id": "abc123...",
  "session_id": "xyz789...",
  "quiz_mode": "elimination_full",
  "total_questions": 100,
  "correct_answers": 78,
  "score_percentage": 78.0,
  "answers": [
    {
      "question": "What is...?",
      "user_answer": 2,
      "correct_answer": 2,
      "is_correct": true,
      "explanation": "..."
    }
  ],
  "created_at": "2024-10-19T15:30:00"
}
```

#### 6. Performance Trend
```bash
GET /api/analytics/performance-trend?days=30&interval=day
```

Response:
```json
[
  {
    "period": "2024-10-19",
    "average_score": 75.2,
    "attempts": 5
  },
  {
    "period": "2024-10-20",
    "average_score": 72.1,
    "attempts": 8
  }
]
```

## Benefits

✅ **Zero Setup**
- No database server to install or run
- `pip install -r requirements.txt && python run.py` is all it takes

✅ **Persistent Storage**
- All quiz attempts saved in `instance/attempts.json`
- Historical data for analytics

✅ **Portable**
- The whole store is two JSON files — easy to back up, copy, or inspect
- Relocate it with a single env var (`QUIZBEE_STORE_DIR`)

✅ **Analytics**
- Track student performance
- Identify difficult topics
- Measure learning trends

## Troubleshooting

### Data Not Persisting
```bash
# Check that the store directory exists and is writable
ls instance/
```

### Inspect the Store Directly
```bash
# Records are plain JSON — open them in any editor
cat instance/attempts.json
cat instance/reports.json
```

### Reset All Persisted Data
```bash
# Stop the app, then delete the store files
rm instance/attempts.json instance/reports.json
```

### Use a Different Store Location
```bash
export QUIZBEE_STORE_DIR=/tmp/quizbee-store
python run.py
```

## Next Steps

1. Run tests to verify setup: `pytest tests/ -v`
2. Explore analytics endpoints
3. Back up `instance/` if you want to keep attempt history
4. Implement additional analytics dashboards

---

**✨ File-based storage — zero database setup required! 🎉**
