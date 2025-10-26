# IT Quizbee - Templates Organization

This directory contains all HTML templates for the IT Quizbee application, organized into logical folders for better maintainability.

## Directory Structure

```
templates/
├── base.html                 # Base template with common layout
├── index.html               # Homepage/Welcome page
├── admin/                   # Admin-related templates
│   ├── admin_login.html    # Admin login page
│   └── admin_dashboard.html # Analytics dashboard
├── navigation/              # Topic/Subtopic navigation
│   ├── topics.html         # Topics listing page
│   └── subtopics.html      # Subtopics listing page
└── quiz/                    # Quiz-related templates
    ├── elimination_mode.html # Elimination mode (100 questions)
    ├── finals_mode.html      # Finals mode (30 questions)
    ├── mode_selection.html   # Mode selection page
    ├── quiz.html            # Review mode quiz page
    └── results.html         # Results display page
```

## Template Categories

### Base Templates

**`base.html`**
- Base template that all other templates extend from
- Contains common header, footer, and navigation
- Includes Tailwind CSS and Bootstrap Icons
- Defines blocks: `title`, `extra_css`, `content`, `extra_js`

**`index.html`**
- Welcome/Homepage
- Entry point for the application
- Links to Elimination, Finals, and Topics modes

### Admin Templates (`admin/`)

Templates for admin authentication and analytics dashboard.

**`admin_login.html`**
- Admin login form
- Session-based authentication
- Extends `base.html`

**`admin_dashboard.html`**
- Comprehensive analytics dashboard
- Chart.js visualizations
- Performance metrics and statistics
- Extends `base.html`

### Navigation Templates (`navigation/`)

Templates for browsing topics and subtopics.

**`topics.html`**
- Displays all available topics (10 main topics)
- Shows topic descriptions and subtopic counts
- Links to subtopic pages

**`subtopics.html`**
- Lists subtopics for a selected topic
- Shows subtopic descriptions
- Links to mode selection

### Quiz Templates (`quiz/`)

Templates for quiz gameplay and results.

**`elimination_mode.html`**
- 100 random questions from all topics
- 60-minute timer
- Multiple choice format
- Name input modal for user tracking

**`finals_mode.html`**
- 30 questions (10 easy, 10 average, 10 difficult)
- Timed questions with difficulty-based timers
- Identification format
- Name input modal for user tracking

**`mode_selection.html`**
- Choose between Elimination or Finals mode
- Difficulty selection for Finals mode
- Displayed after selecting a subtopic

**`quiz.html`**
- Review mode quiz page
- 10 questions per subtopic
- No timer, educational focus
- Name input modal for user tracking

**`results.html`**
- Displays quiz results
- Shows score, percentage, and detailed answers
- Color-coded feedback (green/red)
- Explanations for each question

## Template Inheritance

All templates (except `base.html`) extend from `base.html`:

```jinja
{% extends "base.html" %}

{% block title %}Page Title{% endblock %}

{% block content %}
    <!-- Page content here -->
{% endblock %}
```

## Template Blocks

Templates can override these blocks defined in `base.html`:

- **`title`** - Page title (appears in browser tab)
- **`extra_css`** - Additional CSS or scripts in `<head>`
- **`content`** - Main page content
- **`extra_js`** - JavaScript at end of `<body>`

## Routing

Template paths are referenced in `app.py` using folder notation:

```python
# Admin templates
return render_template('admin/admin_login.html')
return render_template('admin/admin_dashboard.html')

# Navigation templates
return render_template('navigation/topics.html')
return render_template('navigation/subtopics.html')

# Quiz templates
return render_template('quiz/elimination_mode.html')
return render_template('quiz/finals_mode.html')
return render_template('quiz/mode_selection.html')
return render_template('quiz/quiz.html')
return render_template('quiz/results.html')
```

## Styling

All templates use:
- **Tailwind CSS** (via CDN) for styling
- **Bootstrap Icons** for iconography
- Responsive design principles
- Consistent color scheme (blue/purple/pink gradients)

## Features Common to All Templates

- ✅ **Responsive Design** - Works on all device sizes
- ✅ **Accessibility** - Semantic HTML and ARIA labels
- ✅ **User-Friendly** - Clear navigation and feedback
- ✅ **Consistent Styling** - Unified look and feel
- ✅ **Performance** - Optimized loading and rendering

## Best Practices

When creating or modifying templates:

1. **Always extend base.html** for consistent layout
2. **Use semantic HTML** for better accessibility
3. **Keep templates focused** - One responsibility per template
4. **Use Tailwind utility classes** for styling
5. **Add descriptive comments** for complex sections
6. **Test responsiveness** on different screen sizes
7. **Validate HTML** to ensure correctness

## Related Documentation

- [Main README](../README.md) - Application overview
- [AUTHENTICATION_README.md](../docs/AUTHENTICATION_README.md) - Admin authentication
- [ADMIN_DASHBOARD.md](../docs/ADMIN_DASHBOARD.md) - Dashboard features

## Template Variables

### Common Variables Passed to Templates

**All Quiz Templates:**
- `questions` - Array of question objects
- `mode` - Quiz mode ('elimination', 'finals', 'review')
- `difficulty` - Difficulty level (for finals/review)

**Results Template:**
- `results` - Object with correct/total/percentage
- `topic_id` - Topic identifier (for review mode)
- `subtopic_id` - Subtopic identifier (for review mode)

**Navigation Templates:**
- `topics` - Array of topic objects
- `subtopics` - Array of subtopic objects
- `topic` - Current topic object

**Admin Dashboard:**
- Data loaded dynamically via AJAX from `/api/analytics/*` endpoints
