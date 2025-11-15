# SDK Bootstrapping

SDK for interacting with Atlantis and GitHub APIs.

## Installation

Install dependencies using `uv`:

```bash
uv sync
```

## Testing

This project uses [pytest](https://docs.pytest.org/) for testing, which is one of the fastest and most popular Python testing frameworks.

### Running Tests

Run all tests:

```bash
pytest
```

Run tests with verbose output:

```bash
pytest -v
```

Run tests for a specific file:

```bash
# Test Atlantis service
pytest src/tests/test_atlantis.py

# Test GitHub service
pytest src/tests/test_github.py
```

Run a specific test class:

```bash
pytest src/tests/test_atlantis.py::TestAtlantisServiceInit
```

Run a specific test function:

```bash
pytest src/tests/test_atlantis.py::TestAtlantisServiceInit::test_init_with_token
```

### Test Coverage

Generate coverage report:

```bash
pytest --cov=src/services --cov-report=html
```

View the HTML coverage report:

```bash
open htmlcov/index.html
```

Generate terminal coverage report:

```bash
pytest --cov=src/services --cov-report=term
```

### Test Markers

Tests are organized with markers for filtering:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests

Run only unit tests:

```bash
pytest -m unit
```

Run only integration tests:

```bash
pytest -m integration
```

## Project Structure

```
src/
├── services/
│   ├── atlantis/      # Atlantis API client
│   ├── github/        # GitHub API client
│   ├── metadata/      # Metadata service
│   └── templates/     # Template management
└── tests/             # Test suite
```

## Development

### Code Quality

Format and lint code:

```bash
ruff check .
ruff format .
```

