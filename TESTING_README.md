# IT Quizbee - Automated Testing Documentation

## Overview

This document describes the automated testing setup for the IT Quizbee web application using Playwright and Pytest.

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

## Running Tests

### Run All Tests

```bash
pytest test_quiz_app.py
```

### Run with Verbose Output

```bash
pytest test_quiz_app.py -v
```

### Run Specific Test Class

```bash
pytest test_quiz_app.py::TestWelcomePage
```

### Run Specific Test

```bash
pytest test_quiz_app.py::TestEliminationQuiz::test_elimination_quiz_loads
```

### Run with HTML Report

```bash
pytest test_quiz_app.py --html=report.html --self-contained-html
```

### Run with Coverage

```bash
pytest test_quiz_app.py --cov=app --cov-report=html
```

### Run in Headed Mode (See Browser)

```bash
pytest test_quiz_app.py --headed
```

### Run with Screenshots on Failure

```bash
pytest test_quiz_app.py --screenshot=on
```

### Run Tests in Parallel

```bash
pytest test_quiz_app.py -n auto
```

## Test Structure

### Test Classes

The test suite is organized into logical classes:

1. **TestWelcomePage**: Tests for the home/welcome page
2. **TestTopicsPage**: Tests for topic selection
3. **TestSubtopicsPage**: Tests for subtopic selection
4. **TestModeSelection**: Tests for game mode selection
5. **TestEliminationQuiz**: Tests for elimination mode (multiple choice)
6. **TestFinalsQuiz**: Tests for finals mode (identification)
7. **TestResultsPage**: Tests for quiz results display
8. **TestEndToEndFlow**: Complete user journey tests

### Test Coverage

#### Welcome Page (4 tests)
- Page loads correctly
- Title and heading present
- Start button visible
- Feature cards displayed

#### Topics Page (4 tests)
- Navigation from welcome
- All 10 topics displayed
- Topic cards clickable
- Home button works

#### Subtopics Page (3 tests)
- Subtopics displayed
- Back to topics button
- Navigate to mode selection

#### Mode Selection (6 tests)
- Page displays both modes
- Elimination mode navigation
- Finals easy/average/difficult navigation
- Back button works

#### Elimination Quiz (6 tests)
- Quiz loads with radio buttons
- Can select answers
- Only one option per question
- Submit quiz works
- Results displayed
- Back button works

#### Finals Quiz (4 tests)
- Quiz loads with text inputs
- Can type answers
- Submit quiz works
- All difficulty levels work

#### Results Page (6 tests)
- Elimination results display
- Finals results display
- Retake quiz button
- Try different mode button
- Back to subtopics button
- Home button

#### End-to-End (3 tests)
- Complete elimination flow
- Complete finals flow
- Navigation breadcrumb

**Total: 40+ automated tests**

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
- Ignores HTTPS errors
- Headless by default

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
      run: pytest test_quiz_app.py -v
    
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
pytest test_quiz_app.py --headed --slowmo=1000
```

### Enable Debugging

```bash
PWDEBUG=1 pytest test_quiz_app.py
```

### Take Screenshot on Failure

```bash
pytest test_quiz_app.py --screenshot=only-on-failure
```

### Record Video

```bash
pytest test_quiz_app.py --video=on
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

## Best Practices

### 1. Test Isolation
Each test should be independent and not rely on previous tests.

### 2. Use Explicit Waits
Wait for elements to be visible before interacting:

```python
page.wait_for_selector("text=Submit Quiz")
page.click("text=Submit Quiz")
```

### 3. Use Meaningful Selectors
Prefer text content over CSS selectors when possible:

```python
# Good
page.click("text=Start Quiz")

# Acceptable
page.click("#start-btn")
```

### 4. Clean Up After Tests
Use fixtures to ensure cleanup:

```python
@pytest.fixture
def page(browser):
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()
```

### 5. Test Both Happy and Error Paths
Include tests for:
- Successful operations
- Validation errors
- Edge cases
- Empty states

## Test Maintenance

### Adding New Tests

1. Identify the feature to test
2. Create a descriptive test name: `test_feature_description`
3. Follow AAA pattern:
   - **Arrange**: Set up test data
   - **Act**: Perform action
   - **Assert**: Verify results

Example:

```python
def test_new_feature(self, page: Page):
    # Arrange
    page.goto("http://localhost:5000")
    
    # Act
    page.click("text=New Feature")
    
    # Assert
    expect(page.locator("text=Success")).to_be_visible()
```

### Updating Tests

When updating the application:
1. Run existing tests to catch regressions
2. Update tests to match new UI/functionality
3. Add new tests for new features
4. Remove obsolete tests

## Performance Testing

### Measure Test Execution Time

```bash
pytest test_quiz_app.py --durations=10
```

### Run Tests in Parallel

```bash
pytest test_quiz_app.py -n 4
```

## Reporting

### Generate HTML Report

```bash
pytest test_quiz_app.py --html=report.html --self-contained-html
```

### Generate JUnit XML (for CI)

```bash
pytest test_quiz_app.py --junitxml=results.xml
```

### Generate Coverage Report

```bash
pytest test_quiz_app.py --cov=app --cov-report=html
```

View coverage: Open `htmlcov/index.html` in browser

## Advanced Usage

### Custom Markers

Add markers to categorize tests:

```python
@pytest.mark.smoke
def test_critical_feature(self, page: Page):
    pass
```

Run only smoke tests:

```bash
pytest test_quiz_app.py -m smoke
```

### Parametrized Tests

Test multiple scenarios:

```python
@pytest.mark.parametrize("difficulty", ["easy", "average", "difficult"])
def test_all_difficulties(self, page: Page, difficulty):
    page.goto(f"http://localhost:5000/quiz/topic/subtopic?mode=finals&difficulty={difficulty}")
    expect(page.locator(f"text={difficulty}")).to_be_visible()
```

## Troubleshooting

### Enable Verbose Logging

```bash
pytest test_quiz_app.py -v --log-cli-level=DEBUG
```

### Check Playwright Trace

```python
context = browser.new_context()
context.tracing.start(screenshots=True, snapshots=True)
# ... run tests ...
context.tracing.stop(path="trace.zip")
```

View trace:

```bash
playwright show-trace trace.zip
```

## Resources

- [Playwright Python Docs](https://playwright.dev/python/)
- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-playwright Plugin](https://github.com/microsoft/playwright-pytest)

## Support

For issues or questions:
1. Check test logs for error details
2. Run tests with `--headed` flag to see browser
3. Enable debugging with `PWDEBUG=1`
4. Review Playwright trace files
