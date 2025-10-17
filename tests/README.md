# IT Quizbee - Automated Testing Documentation

## Overview

This document describes the automated testing setup for the IT Quizbee web application using Playwright and Pytest. Tests are organized by feature into separate modules for better maintainability.

## Test Framework

- **Playwright**: Browser automation framework
- **Pytest**: Testing framework with fixtures and plugins
- **Python**: Python 3.8+

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

The test suite is organized into separate modules by feature:

```
tests/
├── __init__.py              # Package initialization
├── conftest.py              # Shared fixtures and configuration
├── test_welcome_page.py     # Welcome/home page tests (2 tests)
├── test_topics_page.py      # Topics selection tests (4 tests)
├── test_subtopics_page.py   # Subtopics selection tests (3 tests)
├── test_mode_selection.py   # Mode selection tests (6 tests)
├── test_elimination_quiz.py # Elimination quiz tests (4 tests)
├── test_finals_quiz.py      # Finals quiz tests (4 tests)
├── test_results_page.py     # Results page tests (6 tests)
└── test_end_to_end.py       # Complete flow tests (2 tests)
```

**Total: 31 automated tests**

### Test Modules

1. **test_welcome_page.py**: Tests for the home/welcome page
   - Page loads correctly
   - Title and heading present
   - Start button visible
   - Feature cards displayed

2. **test_topics_page.py**: Tests for topic selection
   - Navigation from welcome
   - All 10 topics displayed
   - Topic cards clickable
   - Home button works

3. **test_subtopics_page.py**: Tests for subtopic selection
   - Subtopics displayed
   - Back to topics button
   - Navigate to mode selection

4. **test_mode_selection.py**: Tests for game mode selection
   - Page displays both modes
   - Elimination mode navigation
   - Finals easy/average/difficult navigation
   - Back button works

5. **test_elimination_quiz.py**: Tests for elimination mode (multiple choice)
   - Quiz loads with radio buttons
   - Can select answers
   - Only one option per question
   - Submit quiz works

6. **test_finals_quiz.py**: Tests for finals mode (identification)
   - Quiz loads with text inputs
   - Can type answers
   - Submit quiz works
   - All difficulty levels work

7. **test_results_page.py**: Tests for quiz results display
   - Elimination results display
   - Finals results display
   - Retake quiz button
   - Try different mode button
   - Back to subtopics button
   - Home button

8. **test_end_to_end.py**: Complete user journey tests
   - Complete elimination flow
   - Complete finals flow

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

### Run Specific Test Module

```bash
pytest tests/test_welcome_page.py
```

### Run Specific Test Class

```bash
pytest tests/test_mode_selection.py::TestModeSelection
```

### Run Specific Test

```bash
pytest tests/test_elimination_quiz.py::TestEliminationQuiz::test_elimination_quiz_loads
```

### Run with HTML Report

```bash
pytest tests/ --html=report.html --self-contained-html
```

### Run with Coverage

```bash
pytest tests/ --cov=app --cov-report=html
```

### Run in Headed Mode (See Browser)

```bash
pytest tests/ --headed
```

### Run with Slow Motion (for debugging)

```bash
pytest tests/ --headed --slowmo=1000
```

### Run with Screenshots on Failure

```bash
pytest tests/ --screenshot=only-on-failure
```

### Run Tests in Parallel

```bash
pytest tests/ -n auto
```

### Run Only Specific Feature Tests

```bash
# Run only quiz-related tests
pytest tests/test_elimination_quiz.py tests/test_finals_quiz.py

# Run only navigation tests
pytest tests/test_welcome_page.py tests/test_topics_page.py tests/test_subtopics_page.py
```

## Prerequisites for Testing

### 1. Flask Server Must Be Running

Start the Flask application before running tests:

```bash
python app.py
```

The app should be running on `http://localhost:5000`

### 2. Test Data Required

Ensure the following test data exists:
- `data/computer_architecture/authentication/` with all mode files
- At least one topic with complete question sets

## Test Fixtures

All fixtures are provided by the `pytest-playwright` plugin:

### Browser Fixture
- Creates a new Chromium browser instance
- Shared across test session
- Automatically cleaned up

### Page Fixture
- Creates a new page for each test
- Ensures test isolation
- Automatically closes after test

### Context Options
- Viewport: 1280x720 (desktop size)
- Configured in `pytest.ini`
- Headless by default (override with `--headed`)

## Continuous Integration

### GitHub Actions Example

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
      run: pytest tests/ -v
    
    - name: Upload test results
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: test-results
        path: report.html
```

## Debugging Tests

### Enable Headed Mode

```bash
pytest tests/ --headed --slowmo=1000
```

### Enable Playwright Inspector

```bash
PWDEBUG=1 pytest tests/test_welcome_page.py
```

### Take Screenshot on Failure

```bash
pytest tests/ --screenshot=only-on-failure
```

### Record Video

```bash
pytest tests/ --video=on
```

### View Test Execution Time

```bash
pytest tests/ --durations=10
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

## Best Practices

### 1. Test Isolation
Each test should be independent and not rely on previous tests. The `page` fixture ensures each test gets a clean browser page.

### 2. Use Explicit Waits
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

### 3. Use Meaningful Selectors
Prefer text content over CSS selectors when possible:

```python
# Good - resilient to CSS changes
page.click("text=Start Quiz")

# Acceptable - but fragile if CSS changes
page.click("#start-btn")
```

### 4. Organize Tests by Feature
Keep related tests together in the same module. This makes it easier to:
- Find tests related to a specific feature
- Run subset of tests for specific features
- Maintain and update tests

### 5. Test Both Happy and Error Paths
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

## Troubleshooting

### Enable Verbose Logging

```bash
pytest tests/ -v --log-cli-level=DEBUG
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
