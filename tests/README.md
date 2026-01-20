# Tests for runlog-ai

This directory contains the test suite for the runlog-ai project, using pytest.

## Installation

Install test dependencies:

```bash
pip install -r requirements.txt
```

This will install pytest, pytest-cov, and pytest-mock along with the main project dependencies.

## Running Tests

### Run all tests
```bash
pytest
```

### Run tests with verbose output
```bash
pytest -v
```

### Run tests for a specific module
```bash
pytest tests/test_parse_coros_data.py
pytest tests/test_create_training_log.py
pytest tests/test_view_training_data.py
```

### Run a specific test class or function
```bash
pytest tests/test_parse_coros_data.py::TestCorosDataParser
pytest tests/test_parse_coros_data.py::TestCorosDataParser::test_parse_csv_splits
```

### Run tests with coverage report
```bash
pytest --cov=. --cov-report=html
```

After running, open `htmlcov/index.html` in your browser to view the coverage report.

### Run tests without coverage (faster)
```bash
pytest --no-cov
```

## Test Structure

- `conftest.py` - Shared pytest fixtures and configuration
- `test_parse_coros_data.py` - Tests for the CorosDataParser class and parsing functionality
- `test_create_training_log.py` - Tests for training log aggregation
- `test_view_training_data.py` - Tests for viewing and displaying training data

## Fixtures

Common test fixtures are defined in `conftest.py`:

- `temp_data_dir` - Temporary directory for test data
- `temp_parsed_dir` - Temporary directory for parsed data
- `sample_csv_content` - Sample CSV file content
- `sample_tcx_content` - Sample TCX file content
- `sample_metadata` - Sample metadata JSON
- `sample_activity_folder` - Complete activity folder with all files
- `sample_parsed_activity` - Sample parsed activity data

## Writing New Tests

Follow the existing patterns:

1. Create test classes that group related tests
2. Use descriptive test names that explain what is being tested
3. Use fixtures from `conftest.py` for common test data
4. Use pytest's built-in fixtures like `tmp_path`, `capsys`, `monkeypatch`
5. Test both success and error cases

Example:
```python
def test_my_feature(temp_data_dir, sample_csv_content):
    """Test description of what this tests."""
    # Arrange
    csv_file = temp_data_dir / "test.csv"
    csv_file.write_text(sample_csv_content)

    # Act
    result = my_function(csv_file)

    # Assert
    assert result is not None
    assert result["key"] == "expected_value"
```

## Test Markers

Tests can be marked with custom markers:

- `@pytest.mark.slow` - For slow-running tests
- `@pytest.mark.integration` - For integration tests
- `@pytest.mark.unit` - For unit tests

Run specific marked tests:
```bash
pytest -m unit           # Run only unit tests
pytest -m "not slow"     # Skip slow tests
```

## Continuous Integration

The tests are configured to run automatically via GitHub Actions (if `.github/workflows/tests.yml` is set up).

## Coverage Goals

Aim for:
- Overall coverage: >80%
- Critical parsing functions: >90%
- Error handling paths: >70%

## Troubleshooting

### Tests fail with "ModuleNotFoundError"
Make sure you're running pytest from the project root directory and all dependencies are installed:
```bash
cd /path/to/runlog-ai
pip install -r requirements.txt
pytest
```

### Coverage report not generated
Make sure pytest-cov is installed:
```bash
pip install pytest-cov
```

### FitFile parsing tests fail
The fitparse library needs to be installed:
```bash
pip install fitparse
```
