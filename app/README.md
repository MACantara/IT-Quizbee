# IT Quizbee Application Architecture

## Overview

The IT Quizbee application has been refactored to follow industry-standard design patterns and best practices. The architecture is modular, scalable, and maintainable.

## Design Patterns Implemented

### 🏭 Factory Pattern
- **Location**: `app/__init__.py`
- **Purpose**: Creates Flask app instances with different configurations
- **Benefits**: Flexible configuration, easier testing, clean initialization

### 🧩 Blueprint Pattern
- **Location**: `app/blueprints/`
- **Purpose**: Organize routes into logical modules
- **Blueprints**:
  - `admin_bp` - Admin authentication and dashboard
  - `quiz_bp` - Quiz operations (elimination, finals)
  - `navigation_bp` - Topic browsing and navigation
  - `api_bp` - RESTful API endpoints

### ⚙️ Service Layer Pattern
- **Location**: `app/services/`
- **Purpose**: Separate business logic from controllers
- **Services**:
  - `QuizService` - Quiz creation, submission, scoring
  - `AnalyticsService` - Statistics and analytics
  - `AuthService` - Authentication and authorization

### 🧱 Repository Pattern
- **Location**: `app/repositories/`
- **Purpose**: Abstract data storage operations
- **Repositories**:
  - `BaseRepository` - Generic CRUD over the JSON store
  - `QuizSessionRepository` - Quiz sessions in the user's Flask session
  - `QuizAttemptRepository` - Quiz attempts in `instance/attempts.json`
  - `QuestionReportRepository` - Question reports in `instance/reports.json`

### 🧠 Decorator Pattern
- **Location**: `app/decorators/`
- **Purpose**: Add cross-cutting concerns
- **Decorators**:
  - Auth: `@admin_required`, `@require_admin`, `@optional_auth`
  - Rate Limiting: `@rate_limit`, `@per_user_rate_limit`
  - Logging: `@log_request`, `@monitor_performance`, `@log_errors`, `@audit_log`

### 🔁 Observer Pattern
- **Location**: `app/events/`
- **Purpose**: Event-driven architecture
- **Components**:
  - `EventManager` - Singleton event dispatcher
  - `LoggingObserver` - Logs events
  - `AnalyticsObserver` - Tracks statistics
  - `NotificationObserver` - Queues notifications
  - `PerformanceMonitor` - Monitors performance

## Directory Structure

```
app/
├── __init__.py                 # Application factory
├── blueprints/                 # Route blueprints
│   ├── __init__.py
│   ├── admin.py               # Admin routes
│   ├── quiz.py                # Quiz routes
│   ├── navigation.py          # Navigation routes
│   └── api.py                 # API endpoints
├── services/                   # Business logic layer
│   ├── __init__.py
│   ├── quiz_service.py        # Quiz operations
│   ├── analytics_service.py   # Analytics
│   └── auth_service.py        # Authentication
├── repositories/               # Data access layer
│   ├── __init__.py
│   ├── json_store.py          # Single-file JSON store (upsert-by-id)
│   ├── base_repository.py     # Base CRUD over JsonStore
│   ├── quiz_session_repository.py  # Flask-session-backed
│   ├── quiz_attempt_repository.py
│   └── question_report_repository.py
├── decorators/                 # Reusable decorators
│   ├── __init__.py
│   ├── auth.py                # Auth decorators
│   ├── rate_limit.py          # Rate limiting
│   └── logging.py             # Logging decorators
├── events/                     # Event system
│   ├── __init__.py
│   ├── event_manager.py       # Event dispatcher
│   └── observers.py           # Event observers
└── utils/                      # Utility functions
    └── __init__.py
```

## Architecture Flow

```
┌─────────────┐
│   Request   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│   Decorators    │  (@admin_required, @rate_limit, @log_request)
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│   Blueprints    │  (admin_bp, quiz_bp, navigation_bp, api_bp)
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Service Layer  │  (QuizService, AnalyticsService, AuthService)
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Repositories   │  (QuizSessionRepository, QuizAttemptRepository,
│                 │   QuestionReportRepository)
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  File Storage   │  (JSON store in instance/ + Flask session)
└─────────────────┘

        ┌──────────────┐
        │ Event System │  (Parallel)
        └──────────────┘
```

## Configuration

The application supports three environments:

### Development
```python
from app import create_app
app = create_app('development')
```
- Debug mode enabled
- Filesystem sessions
- JSON store in `instance/`

### Testing
```python
app = create_app('testing')
```
- Store files redirected to a temp dir (`QUIZBEE_STORE_DIR` via conftest)
- CSRF disabled

### Production
```python
app = create_app('production')
```
- Debug mode disabled
- JSON store in `instance/` (relocate with `QUIZBEE_STORE_DIR`)
- Filesystem sessions
- Requires SECRET_KEY environment variable

## Usage Examples

### Creating the App
```python
from app import create_app

app = create_app('development')

if __name__ == '__main__':
    app.run(debug=True)
```

### Using Services
```python
from app.services import QuizService
from app.repositories import QuizSessionRepository, QuizAttemptRepository

session_repo = QuizSessionRepository()
attempt_repo = QuizAttemptRepository()
quiz_service = QuizService(session_repo, attempt_repo)

# Create quiz
session_id, questions = quiz_service.create_elimination_quiz(
    topic='python',
    subtopic='basics',
    difficulty='medium',
    user_name='John Doe'
)

# Submit quiz
results = quiz_service.submit_quiz(
    session_id=session_id,
    answers={'1': 'A', '2': 'B'},
    user_name='John Doe',
    time_taken=300
)
```

### Using Decorators
```python
from app.decorators.auth import admin_required
from app.decorators.rate_limit import rate_limit
from app.decorators.logging import log_request

@admin_required
@rate_limit(max_requests=10, window_seconds=60)
@log_request
def protected_route():
    return "Protected content"
```

### Event System
```python
from app.events import event_manager, Event, EventType

# Trigger event
event_manager.notify(Event(
    EventType.QUIZ_COMPLETED,
    data={'score': 95, 'user': 'John'}
))

# Subscribe to event
def my_handler(event):
    print(f"Quiz completed: {event.data}")

event_manager.subscribe(EventType.QUIZ_COMPLETED, my_handler)
```

## CLI Commands

The application factory registers CLI commands:

```bash
# View statistics
flask stats --days 30
```

## Testing

The modular architecture makes testing easier:

```python
import pytest
from app import create_app
from app.services import QuizService

@pytest.fixture
def app():
    return create_app('testing')

@pytest.fixture
def quiz_service(app):
    session_repo = QuizSessionRepository()
    attempt_repo = QuizAttemptRepository()
    return QuizService(session_repo, attempt_repo)

def test_create_quiz(quiz_service):
    session_id, questions = quiz_service.create_elimination_quiz(
        'python', 'basics', 'easy', 'Test User'
    )
    assert session_id is not None
    assert len(questions) == 10
```

## Benefits of This Architecture

1. **Modularity**: Each component has a single responsibility
2. **Testability**: Easy to mock and test individual layers
3. **Scalability**: Can easily add new features without breaking existing code
4. **Maintainability**: Clear separation of concerns
5. **Flexibility**: Easy to swap implementations (e.g., replace the JSON store with a database)
6. **Reusability**: Decorators and repositories can be reused
7. **Event-Driven**: Loose coupling through observer pattern
8. **Type Safety**: Type hints throughout the codebase

## Migration from Old Architecture

The old monolithic `app.py` has been refactored into:
- Routes → Blueprints
- Data persistence → Repositories
- Business logic → Services
- Cross-cutting concerns → Decorators
- Event handling → Observer pattern

See `docs/DESIGN_PATTERNS.md` for detailed migration guide.

## Related Documentation

- [Design Patterns Guide](../docs/DESIGN_PATTERNS.md)
- [Repository Pattern](./repositories/README.md)
- [Service Layer](./services/README.md)
- [Event System](./events/README.md)
- [Decorators](./decorators/README.md)
- [Blueprints](./blueprints/README.md)

## Future Enhancements

- [ ] Add async processing with Celery
- [ ] Implement Redis caching
- [ ] Add CQRS pattern for complex queries
- [ ] Implement API versioning
- [ ] Add GraphQL endpoint
- [ ] Implement circuit breaker pattern
- [ ] Add distributed tracing

---

**Architecture designed for scalability and maintainability!** 🚀
