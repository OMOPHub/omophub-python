# Contributing to OMOPHub Python SDK

First off, thank you for considering contributing to OMOPHub!

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the [existing issues](https://github.com/OMOPHub/omophub-python/issues) to avoid duplicates.

When creating a bug report, please include:

- **Python version** (`python --version`)
- **SDK version** (`pip show omophub`)
- **Operating system**
- **Minimal code example** that reproduces the issue
- **Full error traceback**
- **Expected vs actual behavior**

### Suggesting Features

Feature requests are welcome! Please open an issue with:

- Clear description of the feature
- Use case: why would this be useful?
- Possible implementation approach (optional)

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Install development dependencies:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/omophub-python.git
   cd omophub-python
   pip install -e ".[dev]"
   ```
3. **Make your changes** with clear, descriptive commits
4. **Add tests** for new functionality
5. **Run the test suite:**
   ```bash
   pytest
   ```
6. **Ensure code style compliance:**
   ```bash
   ruff check .
   ruff format .
   mypy src/
   ```
7. **Update documentation** if needed
8. **Submit a pull request** with a clear description

## Development Setup

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/omophub-python.git
cd omophub-python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=omophub --cov-report=html

# Run specific test file
pytest tests/test_concepts.py

# Run tests matching a pattern
pytest -k "test_search"
```

### Code Style

We use:
- **Ruff** for linting and formatting
- **mypy** for type checking

```bash
# Check linting
ruff check .

# Auto-format code
ruff format .

# Type checking
mypy src/
```

## Project Structure

```
omophub-python/
├── src/omophub/
│   ├── __init__.py       # Public API exports
│   ├── client.py         # OMOPHub client class
│   ├── resources/        # API resource classes
│   │   ├── concepts.py
│   │   ├── search.py
│   │   ├── hierarchy.py
│   │   └── ...
│   ├── types.py          # TypedDict definitions
│   └── exceptions.py     # Custom exceptions
├── tests/
│   ├── test_concepts.py
│   ├── test_search.py
│   └── ...
├── examples/
│   └── ...
└── pyproject.toml
```

## Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Adding or updating tests
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

Examples:
```
feat: add semantic search endpoint
fix: handle rate limit errors correctly
docs: update README with new examples
test: add tests for batch concept lookup
```

## Questions?

- Open a [GitHub Discussion](https://github.com/OMOPHub/omophub-python/discussions)
- Email: support@omophub.com

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping make OMOPHub better!
