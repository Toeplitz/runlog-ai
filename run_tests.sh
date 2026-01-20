#!/bin/bash
# Script to run tests for runlog-ai

set -e

echo "==================================="
echo "Running runlog-ai Test Suite"
echo "==================================="
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "Error: pytest is not installed"
    echo "Please run: pip install -r requirements.txt"
    exit 1
fi

# Parse command line arguments
COVERAGE=true
VERBOSE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-cov)
            COVERAGE=false
            shift
            ;;
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--no-cov] [-v|--verbose]"
            exit 1
            ;;
    esac
done

# Run tests
if [ "$COVERAGE" = true ]; then
    echo "Running tests with coverage..."
    pytest $VERBOSE --cov=. --cov-report=html --cov-report=term-missing
    echo ""
    echo "Coverage report generated in htmlcov/index.html"
else
    echo "Running tests without coverage..."
    pytest $VERBOSE --no-cov
fi

echo ""
echo "==================================="
echo "Test run complete!"
echo "==================================="
