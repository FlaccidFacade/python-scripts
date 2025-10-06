# GitHub Actions CI/CD

This repository uses GitHub Actions for continuous integration and testing.

## Workflow Overview

The CI workflow (`.github/workflows/ci.yml`) automatically:

1. **Runs on every push and pull request** to the `main` branch
2. **Tests across multiple Python versions**: 3.9, 3.10, 3.11, and 3.12
3. **Executes the test suite** using pytest
4. **Generates coverage reports** and uploads to Codecov

## Test Coverage

Coverage reports are automatically uploaded to [Codecov](https://codecov.io/gh/FlaccidFacade/python-scripts) after each test run.

### Setting Up Codecov

To enable Codecov integration, you need to:

1. Sign up at [codecov.io](https://codecov.io) using your GitHub account
2. Enable the repository in Codecov
3. Add the `CODECOV_TOKEN` as a repository secret in GitHub:
   - Go to repository Settings → Secrets and variables → Actions
   - Add a new repository secret named `CODECOV_TOKEN`
   - Paste the token from Codecov

> **Note**: The workflow will continue to run even if Codecov upload fails (`fail_ci_if_error: false`), so tests will still pass while you're setting this up.

## Badges

The following badges are displayed in the README files:

- **CI Status**: Shows whether the latest build passed or failed
- **Codecov**: Shows the current test coverage percentage
- **Python Version**: Shows which Python versions are supported

## Running Tests Locally

To run the tests locally before pushing:

```bash
cd merge
pip install -r requirements.txt
pytest tests/ -v --cov=merge --cov-report=term-missing
```

## Codecov Configuration

The `codecov.yml` file in the repository root configures:

- Coverage precision and acceptable ranges
- Status checks for project and patch coverage
- Comment behavior on pull requests
