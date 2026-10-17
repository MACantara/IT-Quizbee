# IT-Quizbee MySQL Setup Guide

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure MySQL Connection

Edit or create `.env` file in the project root:

```env
MYSQL_PUBLIC_URL=mysql://username:password@host:port/database
```

### 3. Initialize Database

Create tables:

```bash
python scripts/init_db.py
```

Output:
```
======================================================================
IT-QUIZBEE: Database Initialization
======================================================================

✅ Database initialized successfully!

Created tables:
  • quiz_sessions - Stores active quiz sessions
  • quiz_attempts - Stores quiz submission results

Database configuration:
  • Database URI: [your_database_uri_here]
  • Track Modifications: False
  • Pool Pre-ping: Enabled (connection verification)
  • Pool Recycle: 3600 seconds

======================================================================
✨ Database is ready for use!
```

### 4. Run Application

```bash
python app.py
```

Application starts on `http://localhost:5000`

### 5. Run Tests

```bash
pytest tests/ -v
```

All tests should pass with the new database backend.

## Key Changes

### Session Storage
- **Before**: Flask-Session (file-based, 4KB limit)
- **After**: MySQL database (unlimited size)

### Session Flow
1. User starts quiz → Creates `QuizSession` record in database
2. Session ID stored in HTTP-only cookie
3. User submits quiz → Retrieves session from database
4. Results stored in `QuizAttempt` table
5. Session marked completed and cookie cleared

### Tables Created

**quiz_sessions** - Active quiz sessions
```
id (UUID)              - Session identifier
session_type           - 'elimination' or 'finals'
questions_json         - Quiz questions (JSON)
created_at            - Session creation time
expires_at            - Session expiration time (2 hours)
completed             - Whether quiz was submitted
```

**quiz_attempts** - Quiz submission results
```
id (UUID)              - Attempt identifier
session_id (FK)        - References quiz_sessions
quiz_mode              - 'elimination', 'finals', 'review'
topic_id               - Topic (optional, for review mode)
subtopic_id            - Subtopic (optional, for review mode)
difficulty             - Difficulty level (optional)
total_questions        - Total questions in quiz
correct_answers        - Number of correct answers
score_percentage       - Score as percentage
answers_json           - Detailed answer data (JSON)
created_at             - Attempt creation time
completed_at           - Attempt completion time
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

✅ **Fixed Session Cookie Overflow**
- No more 4KB limit
- Reliable quiz submissions with 100+ questions

✅ **Persistent Storage**
- All quiz attempts saved in database
- Historical data for analytics

✅ **Better Performance**
- Connection pooling with pre-ping
- Automatic connection recycling

✅ **Scalability**
- Database can handle thousands of concurrent sessions
- Easy to add more features (leaderboards, badges, etc.)

✅ **Analytics**
- Track student performance
- Identify difficult topics
- Measure learning trends

## Troubleshooting

### Database Connection Issues
```bash
# Test connection
python -c "from app import app; print(app.config['SQLALCHEMY_DATABASE_URI'])"
```

### View SQL Queries (Debug Mode)
```python
# In app.py
app.config['SQLALCHEMY_ECHO'] = True
```

### Check Database Tables
```bash
mysql -u root -p
USE railway;
SHOW TABLES;
DESCRIBE quiz_sessions;
DESCRIBE quiz_attempts;
```

## Next Steps

1. Run tests to verify setup: `pytest tests/ -v`
2. Explore analytics endpoints
3. Monitor database performance
4. Set up automated backups
5. Implement additional analytics dashboards

## Support

For detailed information, see `MYSQL_MIGRATION.md`

---

**✨ MySQL database successfully integrated! 🎉**
