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

Quiz attempts persist as a JSON file in `instance/`:

| File | Contents |
|------|----------|
| `instance/attempts.json` | All `QuizAttempt` records |

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

## Benefits

✅ **Zero Setup**
- No database server to install or run
- `pip install -r requirements.txt && python run.py` is all it takes

✅ **Persistent Storage**
- All quiz attempts saved in `instance/attempts.json`
- Attempt history powers quiz review (`/quiz/review/<attempt_id>`)

✅ **Portable**
- The whole store is a single JSON file — easy to back up, copy, or inspect
- Relocate it with a single env var (`QUIZBEE_STORE_DIR`)

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
```

### Reset All Persisted Data
```bash
# Stop the app, then delete the store file
rm instance/attempts.json
```

### Use a Different Store Location
```bash
export QUIZBEE_STORE_DIR=/tmp/quizbee-store
python run.py
```

## Next Steps

1. Run tests to verify setup: `pytest tests/ -v`
2. Review a completed attempt at `/quiz/review/<attempt_id>`
3. Back up `instance/` if you want to keep attempt history

---

**✨ File-based storage — zero database setup required! 🎉**
