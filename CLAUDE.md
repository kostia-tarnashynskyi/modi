# CLAUDE.md

This file provides guidance to Claude AI and other AI assistants when working with the Modi dependency injection framework.

## Project Overview

Modi is a powerful and intuitive dependency injection framework for Python, inspired by NestJS. It provides clean decorator-based syntax, type-safe dependency injection, and modular architecture for Python applications.

**Core Features:**

- 🎯 Simple & Intuitive decorator-based syntax
- 🔒 Type-Safe dependency injection with full MyPy support
- 🧩 Modular architecture with organized modules
- ⚡ Flexible scoping (singleton and transient service lifetimes)
- 🚀 Zero Dependencies core framework
- 🔧 Framework Agnostic (works with FastAPI, Flask, FastStream, etc.)

## Essential Commands

### Development Workflow

```bash
# Setup and Environment
just setup                  # Complete development environment setup
just install                # Install all dependencies
just doctor                 # Run environment diagnostics

# Testing and Quality
just test                   # Run tests
just test --coverage       # Run tests with coverage
just lint                   # Run linting (ruff + mypy)
just format                 # Format code with ruff
just check                  # Full code quality check
just security               # Run security checks

# Documentation
just docs-serve             # Serve documentation locally
just docs-build             # Build documentation
just docs-validate          # Validate documentation

# Build and Release
just build                  # Build package
just release                # Prepare for release
just publish                # Publish to PyPI

# Advanced Workflow
just dev                    # Development workflow (test + lint + build)
just ci                     # Full CI check locally
```

### Invoke Task System

Modi uses a sophisticated invoke task system with 40+ organized tasks:

```bash
# Direct invoke usage
uv run invoke --list                    # Show all tasks
uv run invoke dev-info                  # Show task categories
uv run invoke test --coverage          # Tests with coverage
uv run invoke docs.serve --port=8080   # Docs with custom port
uv run invoke examples.run basic       # Run specific example
uv run invoke full-release patch       # Complete release workflow

# Via Just integration
just inv --list                        # Show all invoke tasks
just inv test --watch                  # Advanced task usage
just inv docs.serve                    # Namespaced tasks
```

## Architecture Overview

### Project Structure

```
modi/
├── src/modi/                    # Core framework source
│   ├── __init__.py             # Public API exports
│   ├── core/                   # Core dependency injection
│   ├── decorators/             # Decorator implementations
│   ├── modules/                # Module system
│   └── exceptions/             # Custom exceptions
├── tests/                      # Test suite
├── docs/                       # Jekyll documentation
├── examples/                   # Usage examples
├── scripts/invoke/             # Organized invoke tasks
├── invokefile.py              # Main task entry point
├── tasks.py                   # Invoke integration
├── justfile                   # Quick command access
└── pyproject.toml             # Project configuration
```

### Core Components

**Dependency Injection Engine:**

- `@injectable()` - Mark classes as injectable services
- `@module()` - Define module containers with providers
- `AppFactory` - Create and configure application instances
- Type-safe injection with Python type hints

**Module System:**

- Organized provider registration
- Dependency resolution and circular dependency detection
- Scoped service lifetimes (singleton/transient)
- Module composition and imports

**Framework Integration:**

- FastAPI integration with dependency injection
- Flask integration with service containers
- FastStream integration for event-driven apps
- CLI application support

### Development Tools

- **uv** - Fast Python package manager
- **just** - Command runner for quick access
- **invoke** - Python task execution with rich organization
- **ruff** - Fast Python linter and formatter
- **mypy** - Static type checking
- **pytest** - Testing framework with coverage
- **Jekyll** - Documentation with GitHub Pages

## Development Patterns

### Code Style and Standards

```python
# Use type hints everywhere
from typing import Protocol, Optional
from modi import injectable, module, AppFactory

# Injectable services with clear interfaces
@injectable()
class UserService:
    def get_user(self, user_id: int) -> Optional[User]:
        # Implementation
        pass

# Protocol-based interfaces for flexibility
class IUserRepository(Protocol):
    def find_by_id(self, user_id: int) -> Optional[User]: ...

# Module organization
@module(providers=[UserService, UserRepository])
class UserModule:
    pass
```

### Testing Patterns

```python
# Test structure with fixtures
import pytest
from modi import AppFactory
from modi.testing import TestModule

@pytest.fixture
def app():
    return AppFactory.create(TestModule)

def test_dependency_injection(app):
    service = app.get(UserService)
    assert isinstance(service, UserService)
```

### Documentation Standards

- **Clear examples** for every feature
- **Type annotations** in all code samples
- **Integration guides** for popular frameworks
- **Best practices** and common patterns
- **API reference** with comprehensive details

## Task System Organization

### Task Modules Structure

```
scripts/invoke/
├── common.py        # Shared utilities and project paths
├── setup.py         # Environment setup and installation
├── testing.py       # Testing, linting, quality assurance
├── build.py         # Building, versioning, releases
├── maintenance.py   # Cleanup, stats, dependencies
├── docs.py          # Documentation management
└── examples.py      # Example management and execution
```

### Key Task Categories

1. **Setup & Environment** - Development environment management
2. **Testing & Quality** - Comprehensive testing and code quality
3. **Build & Release** - Package building and release automation
4. **Documentation** - Jekyll documentation system
5. **Examples** - Example management and validation
6. **Maintenance** - Project maintenance and utilities

## AI Assistant Guidelines

### When Working with Modi

1. **Follow Type Safety** - Always use proper type hints
2. **Maintain Consistency** - Follow established patterns
3. **Test Everything** - Write tests for new features
4. **Document Changes** - Update docs and examples
5. **Use Task System** - Leverage invoke tasks for workflows
6. **Check Quality** - Run lint, format, and security checks

### Code Quality Standards

- **Type hints required** for all public APIs
- **Docstrings** for all classes and public methods
- **Error handling** with custom exceptions
- **Performance considerations** for DI resolution
- **Memory efficiency** in service management
- **Thread safety** where applicable

### Framework Integration Patterns

```python
# FastAPI Integration
from fastapi import FastAPI, Depends
from modi.integrations.fastapi import ModiDependency

app = FastAPI()
modi_app = AppFactory.create(AppModule)

@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    user_service: UserService = Depends(ModiDependency(UserService))
):
    return user_service.get_user(user_id)
```

## Commit Message Format

Use conventional commits with emojis:

- ✨ `feat`: new features
- 🐛 `fix`: bug fixes
- 📚 `docs`: documentation changes
- 🎨 `style`: code formatting
- ♻️ `refactor`: code refactoring
- 🧪 `test`: adding or updating tests
- 🔧 `chore`: maintenance tasks
- 🚀 `perf`: performance improvements
- 🔒 `security`: security improvements

### Sample Commit Messages

```
✨ feat(core): add support for conditional providers
🐛 fix(decorators): resolve circular dependency detection
📚 docs(examples): add FastAPI integration example
♻️ refactor(modules): improve module resolution performance
🧪 test(core): add comprehensive dependency injection tests
```

## Key Files to Understand

- `src/modi/__init__.py` - Public API and exports
- `src/modi/core/container.py` - Dependency injection container
- `src/modi/decorators/injectable.py` - Injectable decorator
- `src/modi/modules/module.py` - Module system
- `invokefile.py` - Task system entry point
- `justfile` - Quick command access
- `pyproject.toml` - Project configuration and dependencies

## Best Practices

### Dependency Injection

1. **Use interfaces** (Protocols) for loose coupling
2. **Prefer constructor injection** over property injection
3. **Avoid circular dependencies** through proper design
4. **Use scoping appropriately** (singleton for stateless services)
5. **Test with mock implementations** using test modules

### Module Organization

1. **Group related services** in modules
2. **Use imports** for module composition
3. **Keep modules focused** on single responsibility
4. **Document module purpose** and dependencies

### Integration Development

1. **Follow framework conventions** for each integration
2. **Provide clear examples** for common use cases
3. **Handle framework-specific patterns** appropriately
4. **Maintain backwards compatibility** when possible

## Important Notes

- **Python 3.9+** minimum requirement for type hints
- **Zero external dependencies** for core framework
- **Type safety** is a primary goal
- **Performance** matters for DI resolution
- **Documentation first** approach to development
- **Testing** is mandatory for all features
