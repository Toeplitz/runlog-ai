# Testing Documentation for runlog-ai

## Overview

This document provides a comprehensive overview of the testing infrastructure added to the runlog-ai project.

## What Was Added

### Test Files

1. **`tests/conftest.py`** - Shared pytest fixtures and configuration
   - Fixtures for temporary directories
   - Sample CSV, TCX, and metadata content
   - Sample parsed activity data
   - Complete activity folder fixtures

2. **`tests/test_parse_coros_data.py`** - Tests for data parsing (39 tests)
   - Tests for `CorosDataParser` class initialization
   - CSV parsing tests (splits, summary data, numeric conversions)
   - TCX parsing tests (trackpoints, laps, GPS data)
   - FIT parsing tests (with and without fitparse library)
   - Activity parsing tests (metadata, error handling)
   - Batch processing tests
   - CLI/main function tests

3. **`tests/test_create_training_log.py`** - Tests for training log aggregation (13 tests)
   - Single and multiple activity aggregation
   - Statistics calculation (distance, time, calories)
   - TCX metadata inclusion
   - Date range calculation
   - Error handling (invalid data, empty directories)
   - CLI/main function tests

4. **`tests/test_view_training_data.py`** - Tests for data viewing (14 tests)
   - Time parsing utility tests
   - Pace formatting tests
   - Activity summarization with various data sources
   - CLI tests (list, view specific date, view all)
   - Error handling tests

### Configuration Files

1. **`pytest.ini`** - Pytest configuration
   - Test discovery patterns
   - Output formatting options
   - Test markers (slow, integration, unit)
   - Minimum Python version

2. **`.coveragerc`** - Coverage configuration
   - Source paths and exclusions
   - Report formatting
   - Missing line detection

3. **`.github/workflows/tests.yml`** - GitHub Actions CI/CD workflow
   - Multi-OS testing (Ubuntu, macOS, Windows)
   - Multi-Python version testing (3.8-3.12)
   - Coverage reporting to Codecov
   - Linting with flake8 and black

### Support Files

1. **`run_tests.sh`** - Convenience script for running tests
   - Automatic coverage reporting
   - Verbose mode option
   - No-coverage option for faster runs

2. **`tests/README.md`** - Detailed testing documentation
   - Installation instructions
   - Usage examples
   - Fixture documentation
   - Writing new tests guide

3. **Updated `.gitignore`** - Ignore test artifacts
   - Coverage reports
   - pytest cache
   - Test output files

4. **Updated `requirements.txt`** - Test dependencies
   - pytest>=7.4.0
   - pytest-cov>=4.1.0
   - pytest-mock>=3.11.0

5. **Updated `README.md`** - Testing section added
   - Quick start guide for running tests
   - Test structure overview
   - Links to detailed documentation

## Test Coverage

The test suite includes **56 tests** covering:

### Parse Module (39 tests)
- ✓ CSV file parsing and data extraction
- ✓ TCX file parsing with GPS and sensor data
- ✓ FIT file parsing (with graceful handling when fitparse is missing)
- ✓ Metadata loading and error handling
- ✓ Activity folder processing
- ✓ Batch processing of multiple activities
- ✓ Command-line interface

### Create Training Log Module (13 tests)
- ✓ Single and multiple activity aggregation
- ✓ Statistics calculation (totals and averages)
- ✓ Time parsing and formatting
- ✓ TCX metadata inclusion
- ✓ Date range tracking
- ✓ Error handling for missing/invalid data
- ✓ Command-line interface

### View Training Data Module (14 tests)
- ✓ Time and pace formatting utilities
- ✓ Activity summarization with all data sources
- ✓ Split-by-split display
- ✓ GPS position display
- ✓ FIT data display
- ✓ Command-line interface (list, view specific, view all)
- ✓ Error handling

## Running Tests

### Basic Usage

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific module
pytest tests/test_parse_coros_data.py

# Run specific test
pytest tests/test_parse_coros_data.py::TestCorosDataParser::test_parse_csv_splits

# Using the convenience script
./run_tests.sh              # With coverage
./run_tests.sh --no-cov     # Without coverage
./run_tests.sh -v           # Verbose mode
```

### Advanced Usage

```bash
# Run only fast tests (skip slow tests)
pytest -m "not slow"

# Run only unit tests
pytest -m unit

# Run with verbose output
pytest -v

# Run with extra verbosity (show test output)
pytest -vv -s

# Run failed tests from last run
pytest --lf

# Run tests in parallel (requires pytest-xdist)
pytest -n auto
```

## Test Quality Features

### 1. Comprehensive Fixtures
- Reusable test data in `conftest.py`
- Temporary directories for file I/O tests
- Sample data for CSV, TCX, and metadata

### 2. Edge Case Coverage
- Missing files and directories
- Invalid data formats
- Parsing errors
- Empty values
- Invalid numeric conversions

### 3. Isolation
- Each test uses temporary directories
- No side effects between tests
- Clean state for each test run

### 4. Clear Test Names
- Descriptive test names that explain what is being tested
- Organized into test classes by functionality
- Docstrings for additional context

### 5. Multiple Assertion Patterns
- Structure verification
- Value verification
- Error handling verification
- Output verification (using capsys)

## Continuous Integration

Tests automatically run on:
- Push to main or develop branches
- Pull requests to main or develop
- Multiple operating systems (Ubuntu, macOS, Windows)
- Multiple Python versions (3.8, 3.9, 3.10, 3.11, 3.12)

Results are reported to:
- GitHub Actions UI
- Codecov for coverage tracking

## Adding New Tests

When adding new features:

1. Write tests for the new functionality
2. Ensure tests cover both success and error cases
3. Use existing fixtures where possible
4. Follow the naming convention: `test_<what_is_being_tested>`
5. Add docstrings to explain complex tests
6. Run tests locally before committing

Example:
```python
def test_new_feature(temp_data_dir):
    """Test new feature does X when given Y."""
    # Arrange
    input_data = create_test_data()

    # Act
    result = new_feature(input_data)

    # Assert
    assert result.success is True
    assert result.value == expected_value
```

## Test Maintenance

### Coverage Goals
- Overall: >80%
- Critical parsing functions: >90%
- Error handling: >70%

### Regular Tasks
- Update tests when changing functionality
- Add tests for bug fixes
- Review and remove obsolete tests
- Keep fixtures up to date with data formats

## Benefits of This Test Suite

1. **Confidence in Changes** - Refactor with confidence knowing tests will catch regressions
2. **Documentation** - Tests serve as examples of how to use the code
3. **Bug Prevention** - Catch issues before they reach production
4. **Quality Assurance** - Ensure consistent behavior across platforms and Python versions
5. **Easier Onboarding** - New contributors can understand the codebase through tests

## Troubleshooting

### Common Issues

**Tests fail with "ModuleNotFoundError"**
```bash
pip install -r requirements.txt
```

**Coverage not generated**
```bash
pip install pytest-cov
```

**FIT parsing tests fail**
```bash
pip install fitparse
```

**Tests run slowly**
```bash
pytest --no-cov  # Skip coverage for faster runs
```

## Future Improvements

Potential enhancements to the test suite:

1. Add integration tests with real data files
2. Add performance benchmarking tests
3. Add property-based testing with Hypothesis
4. Add mutation testing to verify test quality
5. Add visual regression tests for output formatting
6. Add stress tests for large data files
7. Add compatibility tests for different watch brands

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Testing Best Practices](https://testdriven.io/blog/testing-best-practices/)

---

**Questions or Issues?**

If you encounter any issues with the test suite, please:
1. Check the [tests/README.md](tests/README.md) for detailed documentation
2. Review the troubleshooting section above
3. Open an issue on GitHub with details about the problem
