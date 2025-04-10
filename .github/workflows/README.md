# GitHub Actions Workflows

This directory contains GitHub Actions workflows for the PromptLab project.

## PromptLab Tests

The `tests.yml` workflow runs tests for the PromptLab project. It runs on every push to the `main` and `feature/async-support` branches, as well as on pull requests to the `main` branch.

### Workflow Structure

The workflow is divided into three jobs:

1. **Unit Tests**: Run unit tests for all components of PromptLab
2. **Integration Tests**: Run integration tests that test the interaction between components
3. **Performance Tests**: Run performance tests to ensure performance requirements are met

### What it tests

#### Unit Tests
- Model classes and their methods
- Experiment class and its methods
- Studio class and its methods
- Core PromptLab functionality
- Async functionality

#### Integration Tests
- End-to-end tests for PromptLab
- Tests that involve multiple components working together

#### Performance Tests
- Tests that measure the performance of async vs sync operations
- Tests that ensure performance requirements are met

### How to run locally

You can run the tests locally using the `run_tests.sh` script:

```bash
./run_tests.sh
```

This script will:
1. Create a virtual environment
2. Install the required dependencies
3. Run all the tests (unit, integration, and performance)
4. Clean up the virtual environment

### Test Organization

Tests are organized into the following directories:

- `tests/unit/`: Unit tests for individual components
- `tests/integration/`: Tests that involve multiple components working together
- `tests/performance/`: Tests that measure performance
- `tests/fixtures/`: Common test fixtures and utilities

### CI Environment

The tests run on Ubuntu with Python 3.9, 3.10, and 3.11 for unit tests, and Python 3.9 for integration and performance tests.
