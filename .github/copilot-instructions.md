# IT Quizbee - AI Coding Agent Instructions

## Architecture Overview

This is a Flask quiz application built with **enterprise design patterns** (Factory, Blueprint, Service Layer, Repository, Decorator, Observer). The codebase was refactored from a monolithic `app.py` to a modular, layered architecture.

### Core Pattern Implementation

**Application Factory** (`app/__init__.py`):
- Use `create_app(config_name)` for all app instances - never import a pre-configured `app` object
- Configs: `development`, `testing`, `production` (defined in `config.py`)
- Scripts must create their own app instance: `from app import create_app; app = create_app('development')`

**Layer Separation** (strict hierarchy):
1. **Blueprints** (`app/blueprints/`) - Route handlers only, no business logic
2. **Services** (`app/services/`) - All business logic lives here
3. **Repositories** (`app/repositories/`) - Database operations only, extends `BaseRepository`
4. **Models** (`models.py`) - SQLAlchemy models at root level (legacy location)

**Blueprint URL Structure**:
- Navigation: `/` (no prefix) - topics, subtopics, mode selection
- Quiz: `/quiz/` prefix - elimination, finals, submission, results
- Admin: `/admin/` prefix - login, dashboard, analytics
- API: `/api/` prefix - statistics endpoints, JSON responses

### Critical Data Flow Pattern

**Question Loading** (hierarchical JSON structure):
```
data/{topic}/index.json                                    # Topic metadata + subtopic list
data/{topic}/{subtopic}/elimination/{subtopic}.json        # 100 MC questions
data/{topic}/{subtopic}/finals/{difficulty}/{subtopic}.json # 10 identification questions per difficulty
```

Always use `QuizService.load_questions(topic, subtopic, mode, difficulty)` - it handles path construction and name resolution from index files.

### Session Management Architecture

**Critical**: Quiz sessions stored in MySQL (`quiz_sessions` table), NOT Flask session
- Create: `QuizService.create_elimination_quiz()` or `create_finals_quiz()` → returns UUID session_id
- Store questions as `questions_json` TEXT field (serialized JSON)
- Sessions expire after 2 hours (`expires_at` timestamp)
- Mark completed with `session.mark_completed()` before creating attempts

**Quiz Attempt Flow**:
1. Service creates session → returns `session_id`
2. Template renders questions from session
3. User submits → Service validates session, calculates score
4. Service creates `QuizAttempt` record, marks session complete
5. Event system triggers observers (logging, analytics, notifications)

### Event System (Observer Pattern)

**When to emit events** (`app/events/event_manager.py`):
```python
from app.events.event_manager import event_manager, Event, EventType

# In service methods AFTER database commit:
event_manager.notify(Event(EventType.QUIZ_COMPLETED, data={
    'session_id': session_id,
    'score': score,
    'user_name': user_name
}))
```

**Available EventTypes**: `QUIZ_STARTED`, `QUIZ_COMPLETED`, `HIGH_SCORE_ACHIEVED`, `USER_REGISTERED`, `ADMIN_LOGIN`

Observers auto-subscribed in `app/__init__.py:init_event_system()`. Never subscribe in route handlers.

### Decorator Usage Patterns

**Authentication** (`app/decorators/auth.py`):
- `@admin_required` - redirect to login if not authenticated
- `@require_admin` - raise 403 if not admin
- `@optional_auth` - inject user info if available

**Rate Limiting** (`app/decorators/rate_limit.py`):
```python
@rate_limit(max_requests=10, window_seconds=60)  # Global rate limit
@per_user_rate_limit(max_requests=5, window_seconds=60)  # Per-user tracking
```

**Logging** (`app/decorators/logging.py`):
```python
@log_request  # Logs all requests
@monitor_performance  # Tracks execution time
@audit_log  # Admin action audit trail
```

Stack decorators: auth → rate limit → logging (top to bottom)

## Development Workflows

### Running the Application

**Always use `run.py`** (not `app.py`, which is legacy):
```powershell
python run.py  # Auto-initializes DB tables, uses FLASK_ENV or defaults to development
```

**Environment switching**:
```powershell
$env:FLASK_ENV="testing"; python run.py
$env:FLASK_ENV="production"; python run.py
```

**Flask CLI commands** (registered in `app/__init__.py:register_cli_commands()`):
```powershell
flask init-db                 # Create tables
flask cleanup                 # Remove expired sessions
flask stats --days 30         # View analytics
```

### Testing (Pytest + Playwright)

**Must start server first**: `python run.py` in separate terminal

**Test categories**:
```powershell
pytest tests/test_*_service.py tests/test_repositories.py  # Unit tests (design patterns)
pytest tests/test_elimination_mode_full.py                  # E2E browser tests
pytest tests/ --cov=app --cov-report=html                   # With coverage
```

**Browser debugging**:
```powershell
pytest tests/test_welcome_page.py --headed --slowmo=1000    # See browser, slow motion
$env:PWDEBUG=1; pytest tests/test_elimination_mode_full.py  # Playwright inspector
```

Test fixtures in `tests/conftest.py` provide: `app`, `client`, `db_session`, `sample_quiz_session`

### Database Scripts

**All scripts at `scripts/`**:
- `init_db.py` - Create tables (also auto-runs in `run.py`)
- `insert_sample_data.py` - Generate 120+ test quiz attempts (use IDs starting with `sample-`)
- `remove_sample_data.py` - Clean test data (preserves real data)
- `add_new_subtopic.py` - Interactive subtopic creation wizard
- `update_topics_md.py` - Regenerate `docs/TOPICS.md` from data folder

Run from project root: `python scripts/script_name.py`

## Project-Specific Conventions

### Service Layer Patterns

**Always inject repositories** (never instantiate in services):
```python
# In blueprints/quiz.py
from app.services.quiz_service import QuizService
from app.repositories import QuizSessionRepository, QuizAttemptRepository

session_repo = QuizSessionRepository()
attempt_repo = QuizAttemptRepository()
quiz_service = QuizService(session_repo, attempt_repo)
```

**Error handling in services**:
- Raise `ValueError` for business logic errors (service layer)
- Raise `APIError` subclasses for API responses (`app/utils/error_handlers.py`)
- Let blueprint error handlers (`app/__init__.py:register_error_handlers()`) convert to responses

### Repository Patterns

**Extend BaseRepository**:
```python
from app.repositories.base_repository import BaseRepository
from models import QuizSession

class QuizSessionRepository(BaseRepository):
    def __init__(self):
        super().__init__(QuizSession)  # Pass model class
    
    def find_active_sessions(self):
        # Custom query - use self.model for the class
        return self.session.query(self.model).filter_by(completed=False).all()
```

Available base methods: `create()`, `get_by_id()`, `get_all()`, `update()`, `delete()`, `save()`, `commit()`, `rollback()`

### Quiz Mode Scoring Rules

**Elimination Mode** (100 MC questions, 60 min):
- Pass threshold: **70%**
- Questions: Random from `elimination/{subtopic}.json`
- All questions shown at once with progress bar

**Finals Mode** (30 identification, timed per question):
- Pass threshold: **80%**
- Structure: 10 easy (20s each) + 10 average (30s) + 10 difficult (40s)
- Questions: From `finals/{difficulty}/{subtopic}.json`
- One question at a time, auto-advance

Scoring calculation in `QuizService.calculate_score()` - handles both modes.

### Admin Dashboard Analytics

**Service**: `AnalyticsService` (`app/services/analytics_service.py`)

**Key methods**:
- `get_dashboard_statistics(days=30)` - Overview stats
- `get_mode_comparison()` - Elimination vs Finals
- `get_difficulty_analysis()` - Performance by difficulty
- `get_topic_performance(topic)` - Topic-specific stats
- `export_statistics(format='json')` - JSON/CSV export

API endpoints in `app/blueprints/api.py` use these services - never query database directly in API routes.

## Common Pitfalls to Avoid

1. **Don't import `app` globally** - Use `from app import create_app; app = create_app()`
2. **Don't put business logic in blueprints** - Move to services
3. **Don't query `db.session` in blueprints** - Use repositories
4. **Don't use Flask session for quiz data** - Use `QuizSession` model
5. **Don't hardcode data paths** - Use `QuizService.data_dir / topic / subtopic`
6. **Don't emit events before database commit** - Events can fail rollback
7. **Don't test without server running** - Playwright tests require `http://localhost:5000`
8. **Don't create tables in app factory** - Let `run.py` handle initialization

## Key Files Reference

- `run.py` - Entry point (use this, not `app.py`)
- `config.py` - All configuration (DB, session, admin, rate limits)
- `models.py` - SQLAlchemy models (QuizSession, QuizAttempt, QuestionReport)
- `app/__init__.py` - Factory, blueprint registration, event system init
- `app/blueprints/__init__.py` - Blueprint exports (`admin_bp`, `quiz_bp`, `navigation_bp`, `api_bp`)
- `app/services/__init__.py` - Service exports (QuizService, AnalyticsService, AuthService)
- `app/events/event_manager.py` - Singleton EventManager, EventType enum
- `docs/DESIGN_PATTERNS.md` - Detailed architecture documentation

## When Adding New Features

**Blueprint**:
1. Create route handler in appropriate blueprint file
2. Apply decorators (auth, rate limit, logging)
3. Inject dependencies (services)
4. Return template or JSON response

**Service method**:
1. Add to existing service or create new service class
2. Accept repository dependencies in `__init__`
3. Implement business logic
4. Emit events after successful operations
5. Raise `ValueError` for errors

**Database model**:
1. Add to `models.py` (root level)
2. Create repository in `app/repositories/`
3. Run `flask init-db` to create table
4. Update services to use new repository

**Event type**:
1. Add to `EventType` enum in `app/events/event_manager.py`
2. Create observer method in `app/events/observers.py` if needed
3. Subscribe in `app/__init__.py:init_event_system()`
