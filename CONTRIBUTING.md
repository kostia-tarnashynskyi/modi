# Contributing to Modi

We love your input! We want to make contributing to Modi as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

## Pull Requests

Pull requests are the best way to propose changes to the codebase. We actively welcome your pull requests:

1. Fork the repo and create your branch from `master`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Development Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/kostia-tarnashynskyi/modi.git
   cd modi
   ```

2. **Install dependencies:**

   ```bash
   pip install -e ".[dev]"
   ```

3. **Install pre-commit hooks:**

   ```bash
   pre-commit install
   ```

4. **Run tests:**

   ```bash
   pytest
   ```

5. **Run linting:**
   ```bash
   ruff check src tests
   black --check src tests
   mypy src
   ```

## Code Style

We use several tools to maintain code quality:

- **Black** for code formatting
- **Ruff** for linting
- **MyPy** for type checking
- **Pre-commit** for automated checks

Run formatting:

```bash
black src tests
ruff check --fix src tests
```

## Testing

- Write tests for any new functionality
- Ensure all tests pass before submitting PR
- Aim for high test coverage
- Use descriptive test names

Run tests with coverage:

```bash
pytest --cov=src/modi --cov-report=html
```

## Documentation

- Update README.md for significant changes
- Add docstrings to new functions/classes
- Update examples if API changes

## Reporting Bugs

We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/kostia-tarnashynskyi/modi/issues).

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## Feature Requests

We welcome feature requests! Please:

1. Check if the feature already exists
2. Open an issue with detailed description
3. Explain the use case and benefits
4. Consider if it fits the project's goals

## Coding Conventions

- Follow PEP 8 style guide
- Use type hints for all functions
- Write descriptive docstrings
- Keep functions small and focused
- Use meaningful variable names

## Inspiration from NestJS

Modi is inspired by NestJS, so when adding features:

- Check how it's implemented in NestJS
- Maintain similar API when possible
- Document differences if any
- Ensure Python-idiomatic implementation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Feel free to open an issue for any questions about contributing!
