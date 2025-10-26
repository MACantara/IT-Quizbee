# IT Quizbee - Interactive IT Quiz Reviewer

A comprehensive web-based quiz application built with Flask, featuring 10 essential IT topics, each with 10 subtopics, totaling 100 subtopics with 10 questions each (1000 questions total).

## 🎯 New! Design Pattern Architecture

This application has been refactored to follow industry-standard design patterns:

- 🏭 **Factory Pattern** - Flexible app creation with multiple configurations
- 🧩 **Blueprint Pattern** - Modular route organization
- ⚙️ **Service Layer Pattern** - Clean business logic separation
- 🧱 **Repository Pattern** - Database abstraction layer
- 🧠 **Decorator Pattern** - Reusable cross-cutting concerns
- 🔁 **Observer Pattern** - Event-driven architecture

See [docs/DESIGN_PATTERNS.md](docs/DESIGN_PATTERNS.md) for detailed documentation.

## Features

- 🎯 **10 IT Topics**: Extensive coverage of IT concepts
  - **Basic Computer Concepts & IT**
  - **Database Management System**
  - **Data Science & Analytics**
  - **Computer Networks & Telecommunication**
  - **Operating Systems**
  - **Object Oriented Programming**
  - **Software Engineering**
  - **Logic Formulation**
  - **Computer Architecture & IT Security**
  - **E-commerce & Web Design**

See topics breakdown in [TOPICS.md](docs/TOPICS.md)

- ✨ **Interactive UI**: Built with Tailwind CSS and Bootstrap Icons
- 📊 **Instant Results**: Get immediate feedback with detailed explanations
- 📱 **Responsive Design**: Works on all devices
- 🎓 **Educational**: Learn from detailed answer explanations
- 🔄 **Hierarchical Navigation**: Topic → Subtopic → Quiz flow
- 📈 **Admin Dashboard**: Comprehensive analytics with charts and statistics (see [ADMIN_DASHBOARD.md](docs/ADMIN_DASHBOARD.md))
- 💾 **MySQL Storage**: Persistent storage of quiz sessions and attempts
- 📊 **Analytics API**: RESTful API for quiz performance data

## Technologies Used

- **Backend**: Python Flask with Design Patterns
- **Architecture**: Factory, Blueprint, Service Layer, Repository, Decorator, Observer
- **Database**: MySQL with SQLAlchemy ORM
- **Frontend**: HTML, CSS, JavaScript
- **Styling**: Tailwind CSS (via CDN)
- **Icons**: Bootstrap Icons
- **Charts**: Chart.js (for admin dashboard)
- **Data**: JSON format for questions
- **Session Management**: Flask-Session

## Installation

1. **Clone or navigate to the project directory**:
```bash
cd IT-Quizbee
```

2. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up MySQL database**:
```bash
# See docs/MYSQL_SETUP.md for detailed instructions
python scripts/init_db.py
```

4. **Configure environment variables** (optional):
Create a `.env` file:
```env
MYSQL_PUBLIC_URL=mysql://username:password@host:port/database
SECRET_KEY=your-secret-key
```

## Running the Application

### Quick Start

```bash
# Using the new run.py entry point
python run.py
```

### Alternative Methods

```bash
# Using Flask CLI
export FLASK_APP=run.py
flask run

# Or the old way (legacy support)
python app.py
```

### Environment Configuration

```bash
# Development mode (default)
python run.py

# Testing mode
export FLASK_ENV=testing
python run.py

# Production mode
export FLASK_ENV=production
python run.py
```

### Access the Application

- **Main App**: `http://localhost:5000`
- **Admin Dashboard**: `http://localhost:5000/admin/dashboard`
- **Admin Login**: `http://localhost:5000/admin/login`
- **API Documentation**: `http://localhost:5000/api/health`

### CLI Commands

```bash
# Initialize database
flask init-db

# Cleanup expired sessions
flask cleanup

# View statistics
flask stats --days 30
```

## Project Structure

```
IT-Quizbee/
│
├── app/                            # Main application package (NEW!)
│   ├── __init__.py                # Application factory
│   ├── blueprints/                # Route blueprints (modular routing)
│   │   ├── admin.py              # Admin routes
│   │   ├── quiz.py               # Quiz routes
│   │   ├── navigation.py         # Navigation routes
│   │   └── api.py                # API endpoints
│   ├── services/                  # Business logic layer
│   │   ├── quiz_service.py       # Quiz operations
│   │   ├── analytics_service.py  # Analytics
│   │   └── auth_service.py       # Authentication
│   ├── repositories/              # Data access layer
│   │   ├── base_repository.py
│   │   ├── quiz_session_repository.py
│   │   └── quiz_attempt_repository.py
│   ├── decorators/                # Reusable decorators
│   │   ├── auth.py               # Authentication
│   │   ├── rate_limit.py         # Rate limiting
│   │   └── logging.py            # Logging
│   ├── events/                    # Event system (Observer pattern)
│   │   ├── event_manager.py      # Event dispatcher
│   │   └── observers.py          # Event observers
│   └── utils/                     # Utility functions
│
├── run.py                         # Application entry point (NEW!)
├── app.py                         # Legacy entry point (still works)
├── models.py                      # Database models
├── requirements.txt               # Python dependencies
│
├── scripts/                       # Utility scripts (organized!)
│   ├── init_db.py
│   ├── add_new_subtopic.py
│   └── update_topics_md.py
│
├── templates/                     # HTML templates (organized!)
│   ├── base.html                 # Base template
│   ├── index.html                # Landing page
│   ├── admin/                    # Admin templates
│   │   ├── admin_login.html
│   │   └── admin_dashboard.html
│   ├── navigation/               # Navigation templates
│   │   ├── topics.html
│   │   └── subtopics.html
│   ├── quiz/                     # Quiz templates
│   │   ├── mode_selection.html
│   │   ├── elimination_mode.html
│   │   ├── finals_mode.html
│   │   ├── quiz.html
│   │   └── results.html
│   └── errors/                   # Error pages
│       ├── 404.html
│       ├── 403.html
│       └── 500.html
│
├── static/                        # Static files
│   └── script.js                 # Frontend JavaScript
│
├── docs/                          # Documentation
│   ├── DESIGN_PATTERNS.md        # Design patterns guide
│   ├── MIGRATION_GUIDE.md        # Migration instructions
│   ├── TOPICS.md
│   ├── ADMIN_DASHBOARD.md
│   └── MYSQL_SETUP.md
│
└── data/                          # Hierarchical quiz data structure
    ├── it_basics/
    │   ├── index.json              # Topic metadata and subtopic list
    │   ├── hardware_basics.json    # 10 questions
    │   ├── software_fundamentals.json
    │   ├── input_output_devices.json
    │   ├── memory_storage.json
    │   ├── number_systems.json
    │   ├── computer_basics.json
    │   ├── internet_basics.json
    │   ├── file_management.json
    │   ├── computer_history.json
    │   └── it_terminology.json
    │
    ├── logic/
    │   ├── index.json
    │   └── [10 subtopic files]
    │
    ├── operating_systems/
    │   ├── index.json
    │   └── [10 subtopic files]
    │
    ├── software_engineering/
    │   ├── index.json
    │   └── [10 subtopic files]
    │
    ├── oop/
    │   ├── index.json
    │   └── [10 subtopic files]
    │
    ├── networks/
    │   ├── index.json
    │   └── [10 subtopic files]
    │
    ├── computer_architecture/
    │   ├── index.json
    │   └── [10 subtopic files]
    │
    ├── dbms/
    │   ├── index.json
    │   └── [10 subtopic files]
    │
    ├── data_science/
    │   ├── index.json
    │   └── [10 subtopic files]
    │
    └── ecommerce_web/
        ├── index.json
        └── [10 subtopic files]
```

## API Endpoints

### Navigation Routes (Blueprint: `navigation`)
- `GET /` - Main application page
- `GET /topics` - Browse all topics
- `GET /topics/<topic>/subtopics` - View subtopics
- `GET /mode-selection` - Quiz mode selection

### Quiz Routes (Blueprint: `quiz`)
- `GET /quiz/elimination` - Elimination mode
- `POST /quiz/elimination` - Start elimination quiz
- `GET /quiz/finals` - Finals mode
- `POST /quiz/finals` - Start finals quiz
- `POST /quiz/submit` - Submit quiz answers
- `GET /quiz/results` - View quiz results
- `GET /quiz/review/<attempt_id>` - Review completed quiz

### Admin Routes (Blueprint: `admin`)
- `GET /admin/login` - Admin login page
- `POST /admin/login` - Process login
- `GET /admin/logout` - Admin logout
- `GET /admin/dashboard` - Admin dashboard with analytics
- `GET /admin/analytics` - Detailed analytics
- `GET /admin/users` - User management

### API Routes (Blueprint: `api`)
- `GET /api/statistics/overview` - Overall statistics
- `GET /api/statistics/mode-comparison` - Compare quiz modes
- `GET /api/statistics/difficulty` - Difficulty analysis
- `GET /api/statistics/topic/<topic>` - Topic performance
- `GET /api/statistics/user/<user_name>` - User performance
- `GET /api/statistics/export` - Export statistics (admin only)
- `GET /api/topics` - Get all topics (JSON)
- `GET /api/topics/<topic>/subtopics` - Get subtopics (JSON)
- `POST /api/quiz/validate-session` - Validate quiz session
- `GET /api/health` - Health check

See [docs/DESIGN_PATTERNS.md](docs/DESIGN_PATTERNS.md) for architecture details.

## Testing the Admin Dashboard

To test the admin dashboard with sample data:

```bash
# Insert sample quiz attempts
python scripts/insert_sample_data.py

# View the dashboard
# Open http://localhost:5000/admin

# Remove sample data when done
python scripts/remove_sample_data.py
```

See [SAMPLE_DATA_README.md](SAMPLE_DATA_README.md) for detailed testing instructions.

## Usage

1. Click **Start Quiz** on the welcome page
2. Select a main topic from the 10 available options
3. Choose a subtopic from the 10 subtopics within that topic
4. Answer each question (10 questions per subtopic)
5. Navigate through questions using Previous/Next buttons
6. Submit the quiz when complete
7. Review your results with detailed explanations
8. Retake the same quiz or go back to choose another subtopic

## Data Structure

### Topic Index File (`index.json`)
Each topic folder contains an `index.json` with metadata:
```json
{
  "topic_id": "it_basics",
  "topic_name": "Basic Computer Concepts & IT",
  "description": "Fundamental concepts...",
  "subtopics": [
    {
      "id": "hardware_basics",
      "name": "Hardware Basics",
      "description": "Computer hardware components..."
    }
  ]
}
```

### Subtopic File (`subtopic_id.json`)
Each subtopic file contains 10 questions:
```json
{
  "subtopic_id": "hardware_basics",
  "subtopic_name": "Hardware Basics",
  "questions": [
    {
      "question": "Your question here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct": 0,
      "explanation": "Explanation of the correct answer"
    }
  ]
}
```

## Architecture Benefits

### Why Design Patterns?

✅ **Modularity** - Each component has a single responsibility  
✅ **Testability** - Easy to mock and test individual layers  
✅ **Scalability** - Add new features without breaking existing code  
✅ **Maintainability** - Clear separation of concerns  
✅ **Reusability** - Decorators and repositories can be reused  
✅ **Flexibility** - Easy to swap implementations  
✅ **Type Safety** - Type hints throughout the codebase  

### Design Pattern Usage

**Factory Pattern** - Creates app instances with different configs (dev, test, prod)  
**Blueprint Pattern** - Organizes routes into logical modules  
**Service Layer** - Separates business logic from controllers  
**Repository Pattern** - Abstracts database operations  
**Decorator Pattern** - Adds auth, logging, rate limiting without modifying routes  
**Observer Pattern** - Event-driven architecture for loose coupling  

See [docs/DESIGN_PATTERNS.md](docs/DESIGN_PATTERNS.md) for implementation details.

## Customization

### Adding New Questions

1. Navigate to `data/<topic>/<subtopic>/questions.json`
2. Add your question following the format
3. Questions now include ID, question, options, correct_answer, explanation

### Adding New Subtopics

```bash
# Use the utility script
python scripts/add_new_subtopic.py
```

See [ADD_SUBTOPIC_README.md](ADD_SUBTOPIC_README.md) for details.

### Adding New Topics

1. Create folder in `data/`
2. Create `index.json` with topic metadata
3. Create subtopic folders with `questions.json`
4. Update `TOPICS.md`

### Extending the Architecture

**Add New Blueprint:**
```python
# Create app/blueprints/my_feature.py
my_bp = Blueprint('my_feature', __name__)

# Register in app/__init__.py
app.register_blueprint(my_bp)
```

**Add New Service:**
```python
# Create app/services/my_service.py
class MyService:
    def __init__(self, repo):
        self.repo = repo
```

**Add New Observer:**
```python
# Add to app/events/observers.py
class MyObserver:
    def handle_event(self, event):
        pass
```

## Documentation

- 📘 [Design Patterns Guide](docs/DESIGN_PATTERNS.md) - Comprehensive pattern documentation
- 🔄 [Migration Guide](docs/MIGRATION_GUIDE.md) - Migrate from old to new architecture
- 📊 [Admin Dashboard](docs/ADMIN_DASHBOARD.md) - Analytics and reporting
- 🗄️ [MySQL Setup](docs/MYSQL_SETUP.md) - Database configuration
- 📚 [Topics](docs/TOPICS.md) - Complete topics breakdown
- 🏗️ [App Architecture](app/README.md) - Application structure details

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Follow the design pattern architecture
4. Write tests for new features
5. Submit a pull request

## Testing

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

See [tests/README.md](tests/README.md) for testing guidelines.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## Author

- Michael Angelo R. Cantara — https://github.com/MACantara

## Acknowledgments

- Design patterns inspired by industry best practices
- Flask community for excellent documentation
- Contributors and testers

---

Created with ❤️ for IT learners everywhere!

**Now with enterprise-grade architecture!** 🚀
