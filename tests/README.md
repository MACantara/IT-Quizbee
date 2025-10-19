# IT Quizbee - Automated Testing Documentation

## Overview

This document describes the comprehensive automated testing setup for the IT Quizbee web application using **Playwright** and **Pytest**. The test suite covers all three game modes: **Elimination Mode**, **Finals Mode**, and **Review Mode**, with a total of **73 automated tests**.

## Test Framework

- **Playwright**: Browser automation framework for end-to-end testing
- **Pytest**: Testing framework with fixtures and plugins
- **Python**: Python 3.8+
- **pytest-playwright**: Pytest plugin for Playwright integration

## Installation

### 1. Install Testing Dependencies

```bash
pip install -r requirements-test.txt
```

### 2. Install Playwright Browsers

```bash
playwright install chromium
```

Or install all browsers:

```bash
playwright install
```

## Test Structure

The test suite is organized into separate modules by feature and game mode:

```
tests/
├── __init__.py                        # Package initialization
├── conftest.py                        # Shared fixtures and configuration
├── test_welcome_page.py               # Welcome/home page (7 tests)
├── test_topics_page.py                # Topics selection (4 tests)
├── test_subtopics_page.py             # Subtopics selection (3 tests)
├── test_mode_selection.py             # Mode selection (6 tests)
├── test_elimination_mode_full.py      # Full Elimination Mode (15 tests)
├── test_finals_mode_full.py           # Full Finals Mode (18 tests)
├── test_review_elimination_quiz.py    # Review Mode elimination (4 tests)
├── test_review_finals_quiz.py         # Review Mode finals (4 tests)
├── test_results_page.py               # Results page (6 tests)
└── test_end_to_end.py                 # Complete flows (6 tests)
```

**Total: 73 automated tests**

## Game Modes Tested

### 1. Elimination Mode (Full Quiz)

- **Route**: `/elimination`
- **Description**: 100 random multiple-choice questions from all 10 topics
- **Time Limit**: 60 minutes total
- **Features Tested**:
  - Question randomization across topics
  - 60-minute countdown timer
  - Progress tracking (0/100 to 100/100)
  - Radio button selections
  - Auto-submit on time expiry
  - Results with score breakdown
- **Test Module**: `test_elimination_mode_full.py`

### 2. Finals Mode (Full Quiz)

- **Route**: `/finals`
- **Description**: 30 identification questions with varying difficulty
- **Structure**: 10 Easy + 10 Average + 10 Difficult
- **Time Limits**:
  - Easy: 20 seconds per question
  - Average: 30 seconds per question
  - Difficult: 40 seconds per question
- **Features Tested**:
  - Per-question timers
  - Difficulty progression
  - Text input validation
  - Auto-advance on submit
  - Auto-submit on completion
  - Timer color changes
- **Test Module**: `test_finals_mode_full.py`

### 3. Review Mode (Topic-Based Practice)

- **Flow**: Topics → Subtopics → Mode Selection → Quiz
- **Description**: User selects specific topics and subtopics to practice
- **Modes Available**: Elimination (multiple choice) or Finals (identification)
- **Features Tested**:
  - Topic selection (10 topics)
  - Subtopic navigation
  - Mode selection (Elimination/Finals)
  - Difficulty selection for Finals
  - Quiz completion
  - Results with retake options
- **Test Modules**: `test_topics_page.py`, `test_subtopics_page.py`, `test_mode_selection.py`, `test_review_elimination_quiz.py`, `test_review_finals_quiz.py`

## Test Modules Breakdown

### Core Navigation Tests

1. **test_welcome_page.py** (7 tests)
   - Welcome page loads correctly
   - Feature cards displayed
   - Three mode buttons visible
   - Navigation to Elimination Mode
   - Navigation to Finals Mode
   - Navigation to Review Mode
   - Page title verification

2. **test_topics_page.py** (4 tests)
   - Navigation from welcome to topics
   - All 10 topics displayed
   - Topic navigation to subtopics
   - Home button functionality

3. **test_subtopics_page.py** (3 tests)
   - Subtopics displayed for selected topic
   - Back to topics button
   - Navigate to mode selection

4. **test_mode_selection.py** (6 tests)
   - Mode selection page displays both modes
   - Elimination mode navigation
   - Finals mode - Easy difficulty
   - Finals mode - Average difficulty
   - Finals mode - Difficult difficulty
   - Back to subtopics button

### Full Quiz Mode Tests

5. **test_elimination_mode_full.py** (15 tests)
   - Page loads with timer and progress bar
   - 100 questions displayed
   - Questions from multiple topics
   - Radio button options (4 per question)
   - Answer selection functionality
   - Progress tracking updates
   - Timer countdown functionality
   - Submit button visibility
   - Back to home button
   - Submit quiz functionality
   - Answer all questions and submit
   - Results display after submission
   - Navigation from results

6. **test_finals_mode_full.py** (18 tests)
   - Page loads with question and timer
   - First question displays
   - Difficulty badge displays
   - Timer displays and counts down
   - Can type answers in text input
   - Submit answer advances to next question
   - Enter key submits answer
   - Answer input clears on new question
   - Progress bar updates correctly
   - Different difficulty levels present
   - Complete all 30 questions
   - Auto-submit on completion
   - Results display after finals quiz
   - Timer color changes with time remaining
   - Empty answers allowed
   - Question content changes between questions

### Review Mode Tests

7. **test_review_elimination_quiz.py** (4 tests)
   - Quiz loads with radio buttons
   - Can select multiple choice answers
   - Only one option per question selectable
   - Submit elimination quiz

8. **test_review_finals_quiz.py** (4 tests)
   - Quiz loads with text inputs
   - Can type answers
   - Submit finals quiz
   - All three difficulty levels work

### Results and Integration Tests

9. **test_results_page.py** (6 tests)
   - Elimination results display correctly
   - Finals results display correctly
   - Retake quiz button functionality
   - Try different mode button
   - Back to subtopics button
   - Home button from results

10. **test_end_to_end.py** (6 tests)
    - Complete Elimination Mode full flow
    - Complete Finals Mode full flow
    - Complete Review Mode elimination flow
    - Complete Review Mode finals flow
    - Navigation between modes from home

## Prerequisites for Testing

**IMPORTANT**: Flask server must be running before executing tests!

Start the Flask application before running tests:

```bash
python app.py
```

The app should be running on `http://localhost:5000`

## Test Data Requirements

Ensure the following test data exists in the `data/` directory:

1. **For Review Mode tests**:
   - `data/computer_architecture/authentication/` with complete question sets
   - Elimination mode: `elimination/authentication.json`
   - Finals mode: `finals/easy/authentication.json`, `finals/average/authentication.json`, `finals/difficult/authentication.json`

2. **For Full Mode tests**:
   - Questions in all 10 topics for randomization
   - At least sufficient questions for 100-question elimination pool
   - At least 10 questions per difficulty level across all topics for finals

3. **Topics structure**:
   - Each topic must have `index.json` with subtopics metadata
   - At least one complete topic with all subtopic question files

## Test Fixtures

All fixtures are provided by the `pytest-playwright` plugin:

### Browser Fixture

- Creates a new Chromium browser instance
- Shared across test session
- Automatically cleaned up after tests

### Page Fixture

- Creates a new page for each test
- Ensures test isolation
- Automatically closes after each test

### Context Options

- Viewport: 1280x720 (desktop size)
- Configured in `pytest.ini`
- Headless by default (use `--headed` to override)

## Running Tests

### Run All Tests

```bash
pytest tests/
```

Or from project root:

```bash
pytest
```

### Run with Verbose Output

```bash
pytest tests/ -v
```

### Run Tests by Mode

```bash
# Full Elimination Mode tests
pytest tests/test_elimination_mode_full.py -v

# Full Finals Mode tests
pytest tests/test_finals_mode_full.py -v

# All Review Mode tests
pytest tests/test_topics_page.py tests/test_subtopics_page.py tests/test_mode_selection.py tests/test_review_elimination_quiz.py tests/test_review_finals_quiz.py -v

# End-to-end integration tests
pytest tests/test_end_to_end.py -v

# All full mode tests (Elimination + Finals)
pytest tests/test_elimination_mode_full.py tests/test_finals_mode_full.py -v
```

### Run Specific Test Module

```bash
pytest tests/test_welcome_page.py
pytest tests/test_elimination_mode_full.py
```

### Run Specific Test Class

```bash
pytest tests/test_elimination_mode_full.py::TestEliminationModeFull
pytest tests/test_finals_mode_full.py::TestFinalsModeFull
pytest tests/test_mode_selection.py::TestModeSelection
```

### Run Specific Test

```bash
pytest tests/test_elimination_mode_full.py::TestEliminationModeFull::test_100_questions_displayed
pytest tests/test_finals_mode_full.py::TestFinalsModeFull::test_timer_displays_and_counts_down
```

### Advanced Options

#### Run in Headed Mode (See Browser)

```bash
pytest tests/ --headed
```

#### Run with Slow Motion (for debugging)

```bash
pytest tests/ --headed --slowmo=1000
```

#### Run with Screenshots on Failure

```bash
pytest tests/ --screenshot=only-on-failure
```

#### Run Tests in Parallel

```bash
pytest tests/ -n auto
```

#### Generate HTML Report

```bash
pytest tests/ --html=report.html --self-contained-html
```

#### Run with Coverage

```bash
pytest tests/ --cov=app --cov-report=html
```

#### Enable Playwright Inspector (Debug Mode)

```bash
PWDEBUG=1 pytest tests/test_welcome_page.py
```

## Common Test Patterns

### Wait for Navigation

```python
page.wait_for_url("**/elimination")
```

### Check Element Visibility

```python
expect(page.locator("text=Quiz Complete!")).to_be_visible()
```

### Fill Form and Submit

```python
page.locator("#answer-input").fill("Answer")
page.click("#submit-answer")
```

### Loop Through Questions

```python
for i in range(100):
    page.locator(f"input[name='answer_{i}']").first.click()
```

## Debugging Tests

### View Test Execution in Browser

```bash
pytest tests/test_welcome_page.py --headed --slowmo=1000
```

### Enable Debug Output

```bash
pytest tests/ -v --log-cli-level=DEBUG
```

### Capture Screenshot on Failure

```bash
pytest tests/ --screenshot=only-on-failure
```

### Use Playwright Inspector

```bash
PWDEBUG=1 pytest tests/test_elimination_mode_full.py::TestEliminationModeFull::test_100_questions_displayed
```

### Check Playwright Trace

```python
# Add to conftest.py or specific test
context = browser.new_context()
context.tracing.start(screenshots=True, snapshots=True)
# ... run tests ...
context.tracing.stop(path="trace.zip")
```

View trace:

```bash
playwright show-trace trace.zip
```

### Debug Specific Test

```bash
# Run with inspector
PWDEBUG=1 pytest tests/test_welcome_page.py::TestWelcomePage::test_welcome_page_loads

# Run in headed mode with slow motion
pytest tests/test_welcome_page.py::TestWelcomePage::test_welcome_page_loads --headed --slowmo=2000
```

## Best Practices

1. **Test Isolation**: Each test is independent and should not rely on previous tests
2. **Explicit Waits**: Use `expect()` for auto-waiting before assertions
3. **Meaningful Selectors**: Prefer text content over CSS selectors
4. **AAA Pattern**: Arrange, Act, Assert
5. **Descriptive Names**: Clear test function names

### Use Explicit Waits

Wait for elements to be visible before interacting:

```python
page.wait_for_selector("text=Submit Quiz")
page.click("text=Submit Quiz")
```

Or use Playwright's auto-waiting with expect:

```python
expect(page.locator("text=Submit Quiz")).to_be_visible()
page.click("text=Submit Quiz")
```

### Use Meaningful Selectors

Prefer text content over CSS selectors when possible:

```python
# Good - resilient to CSS changes
page.click("text=Start Quiz")

# Acceptable - but fragile if CSS changes
page.click("#start-btn")
```

### Organize Tests by Feature

Keep related tests together in the same module for easier maintenance.

### Test Both Happy and Error Paths

Include tests for:
- Successful operations
- Validation errors
- Edge cases
- Empty states

## Test Maintenance

### Adding New Tests

1. Identify the feature/page to test
2. Choose or create appropriate test module
3. Add test to the corresponding class
4. Follow naming convention: `test_feature_description`
5. Use AAA pattern (Arrange, Act, Assert):

```python
def test_new_feature(self, page: Page):
    # Arrange - Set up test data
    page.goto("http://localhost:5000")
    
    # Act - Perform action
    page.click("text=New Feature")
    
    # Assert - Verify results
    expect(page.locator("text=Success")).to_be_visible()
```

### Updating Tests

When updating the application:

1. Run existing tests to catch regressions
2. Update tests to match new UI/functionality
3. Add new tests for new features
4. Remove obsolete tests
5. Keep documentation up to date

### Creating New Test Modules

If adding a new page/feature:

1. Create new file: `tests/test_feature_name.py`
2. Add module docstring
3. Import required modules
4. Create test class
5. Add tests following existing patterns

Example:

```python
"""
Tests for the IT Quizbee New Feature

This module contains tests for...
"""

import pytest
from playwright.sync_api import Page, expect

class TestNewFeature:
    """Tests for new feature"""
    
    def test_feature_loads(self, page: Page):
        """Test that the feature loads correctly"""
        page.goto("http://localhost:5000/new-feature")
        expect(page.locator("text=New Feature")).to_be_visible()
```

## Performance Testing

### Measure Test Execution Time

```bash
pytest tests/ --durations=10
```

### Run Tests in Parallel

```bash
# Auto-detect number of CPUs
pytest tests/ -n auto

# Specify number of workers
pytest tests/ -n 4
```

## Reporting

### Generate HTML Report

```bash
pytest tests/ --html=report.html --self-contained-html
```

### Generate JUnit XML (for CI)

```bash
pytest tests/ --junitxml=results.xml
```

### Generate Coverage Report

```bash
pytest tests/ --cov=app --cov-report=html
```

View coverage: Open `htmlcov/index.html` in browser

## Advanced Usage

### Custom Markers

Add markers to categorize tests (define in `pytest.ini`):

```python
@pytest.mark.smoke
def test_critical_feature(self, page: Page):
    pass
```

Run only smoke tests:

```bash
pytest tests/ -m smoke
```

### Parametrized Tests

Test multiple scenarios with one test:

```python
@pytest.mark.parametrize("difficulty", ["easy", "average", "difficult"])
def test_all_difficulties(self, page: Page, difficulty):
    page.goto(f"http://localhost:5000/quiz/topic/subtopic?mode=finals&difficulty={difficulty}")
    expect(page.locator(f"text={difficulty}")).to_be_visible()
```

### Test Collections

Run specific test collections:

```bash
# Run only welcome and topics tests
pytest tests/test_welcome_page.py tests/test_topics_page.py

# Run all quiz-related tests
pytest tests/test_*quiz*.py

# Run everything except end-to-end tests
pytest tests/ --ignore=tests/test_end_to_end.py
```

## Common Issues and Solutions

### Issue: "Connection refused"

**Solution**: Ensure Flask app is running on port 5000

```bash
python app.py
```

### Issue: "Element not found"

**Solution**: Increase timeout or add explicit waits

```python
page.wait_for_selector("text=Submit Quiz", timeout=10000)
```

### Issue: "Browser not installed"

**Solution**: Install Playwright browsers

```bash
playwright install chromium
```

### Issue: Tests fail inconsistently

**Solution**: Add proper waits and ensure test isolation

```python
page.wait_for_load_state("networkidle")
```

### Issue: Import errors when running tests

**Solution**: Ensure you're running tests from the project root

```bash
# From project root
pytest tests/

# Not from inside tests/ folder
```

## Continuous Integration

### Example GitHub Actions Workflow

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
        playwright install chromium
    
    - name: Start Flask app
      run: |
        python app.py &
        sleep 5
    
    - name: Run tests
      run: pytest tests/ -v --html=report.html --self-contained-html
    
    - name: Upload test results
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: test-results
        path: report.html
```

## Test Metrics

- **Total Tests**: 73
- **Test Modules**: 10
- **Game Modes Covered**: 3 (Elimination, Finals, Review)
- **Average Execution Time**: ~2-3 minutes for full suite (headless)
- **Coverage**: End-to-end user journeys + individual component tests

## Resources

- [Playwright Python Docs](https://playwright.dev/python/)
- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-playwright Plugin](https://github.com/microsoft/playwright-pytest)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)

## Support

For issues or questions:
1. Check test logs for error details: `pytest tests/ -v`
2. Run tests with `--headed` flag to see browser: `pytest tests/ --headed`
3. Enable debugging with `PWDEBUG=1`
4. Review Playwright trace files for detailed execution flow
5. Check that Flask server is running on `http://localhost:5000`
