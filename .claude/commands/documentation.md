# Documentation Command

## Purpose

Create, update, and maintain comprehensive documentation for the Modi dependency injection framework.

## Usage

When asked to work on documentation, follow this structured approach for different types of documentation tasks.

### 1. Documentation Types

**API Documentation:**

- Docstrings for classes, methods, and functions
- Type annotations and parameter descriptions
- Usage examples within docstrings
- Exception documentation

**User Guide Documentation:**

- Jekyll documentation in `docs/` directory
- Getting started guides and tutorials
- Integration guides for different frameworks
- Best practices and patterns

**Example Documentation:**

- Practical code examples in `examples/` directory
- Framework integration examples
- Real-world use case demonstrations
- Testing examples

### 2. Documentation Workflow

```bash
# Start documentation development
just docs-serve  # Start local Jekyll server at http://localhost:4000

# Validate documentation
just docs-validate

# Build production documentation
just docs-build

# Check documentation quality
just inv docs.check-links    # Check for broken links
just inv docs.validate      # Validate markdown and structure
```

### 3. Jekyll Documentation Structure

**File Organization:**

```
docs/
├── _config.yml           # Jekyll configuration
├── _includes/           # Reusable components
├── _layouts/            # Page layouts
├── _sass/              # Styling
├── assets/             # Images, CSS, JS
├── api/                # API reference
├── guides/             # User guides
├── examples/           # Example documentation
├── integrations/       # Framework integrations
└── index.md           # Homepage
```

**Writing Style Guidelines:**

- Clear, concise explanations
- Progressive complexity (basic → advanced)
- Practical examples for every concept
- Code samples with explanations
- Visual aids where helpful

### 4. API Documentation Standards

**Class Documentation:**

```python
class DependencyContainer:
    """Container for managing dependency injection and service resolution.

    The DependencyContainer is the core component that handles service
    registration, dependency resolution, and lifecycle management.

    Example:
        Basic usage with service registration:

        >>> container = DependencyContainer()
        >>> container.register(IUserService, UserService)
        >>> service = container.get(IUserService)
        >>> isinstance(service, UserService)
        True

    Args:
        auto_register: Whether to automatically register services
        scope: Default scope for registered services

    Raises:
        DIException: When dependency resolution fails
        CircularDependencyError: When circular dependencies detected

    Note:
        The container uses type hints for automatic dependency resolution.
        Ensure all services have proper type annotations.
    """
```

**Method Documentation:**

```python
def register(
    self,
    service_type: Type[T],
    implementation: Union[Type[T], Callable[[], T]],
    scope: Scope = Scope.TRANSIENT
) -> None:
    """Register a service implementation for dependency injection.

    Args:
        service_type: The interface or base class type
        implementation: The concrete implementation class or factory
        scope: Service lifetime scope (SINGLETON or TRANSIENT)

    Raises:
        ServiceRegistrationError: If service is already registered
        TypeError: If implementation doesn't match service_type

    Example:
        Register a singleton service:

        >>> container.register(ILogger, ConsoleLogger, Scope.SINGLETON)
        >>> logger1 = container.get(ILogger)
        >>> logger2 = container.get(ILogger)
        >>> logger1 is logger2
        True
    """
```

### 5. User Guide Documentation

**Getting Started Template:**

````markdown
# Getting Started with Modi

Modi makes dependency injection in Python simple and type-safe. This guide will get you up and running in minutes.

## Installation

```bash
pip install modi
```
````

## Basic Usage

### 1. Define Your Services

Create your service classes with the `@injectable` decorator:

```python
from modi import injectable

@injectable()
class UserService:
    def get_user(self, user_id: int) -> str:
        return f"User {user_id}"
```

### 2. Create a Module

Organize your services into modules:

```python
from modi import module

@module(providers=[UserService])
class AppModule:
    pass
```

### 3. Create Application

Use the AppFactory to create your application:

```python
from modi import AppFactory

app = AppFactory.create(AppModule)
user_service = app.get(UserService)
print(user_service.get_user(1))  # Output: User 1
```

## Next Steps

- [Dependency Injection Basics](./guides/dependency-injection.md)
- [Module System](./guides/modules.md)
- [Framework Integrations](./integrations/)

````

**Advanced Guide Template:**
```markdown
# Advanced Dependency Injection

Learn advanced patterns and techniques for complex applications.

## Table of Contents

- [Circular Dependencies](#circular-dependencies)
- [Custom Providers](#custom-providers)
- [Conditional Registration](#conditional-registration)
- [Performance Optimization](#performance-optimization)

## Circular Dependencies

Modi automatically detects and prevents circular dependencies:

```python
@injectable()
class ServiceA:
    def __init__(self, service_b: 'ServiceB'):
        self.service_b = service_b

@injectable()
class ServiceB:
    def __init__(self, service_a: ServiceA):
        self.service_a = service_a

# This will raise CircularDependencyError
app = AppFactory.create(module(providers=[ServiceA, ServiceB]))
````

### Solutions

1. **Interface Segregation**: Break dependencies using interfaces
2. **Event-Driven**: Use events instead of direct dependencies
3. **Factory Pattern**: Use factories to break cycles

[Continue with detailed examples...]

````

### 6. Integration Documentation

**Framework Integration Template:**
```markdown
# FastAPI Integration

Modi provides seamless integration with FastAPI for dependency injection.

## Installation

```bash
pip install modi[fastapi]
````

## Setup

```python
from fastapi import FastAPI, Depends
from modi import AppFactory, module, injectable
from modi.integrations.fastapi import ModiDependency

# Define your services
@injectable()
class UserService:
    def get_user(self, user_id: int) -> dict:
        return {"id": user_id, "name": f"User {user_id}"}

# Create module
@module(providers=[UserService])
class AppModule:
    pass

# Create FastAPI app
app = FastAPI()
modi_app = AppFactory.create(AppModule)

# Use dependency injection in routes
@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    user_service: UserService = Depends(ModiDependency(UserService))
):
    return user_service.get_user(user_id)
```

## Advanced Patterns

### Scoped Services

[Continue with detailed patterns...]

```

### 7. Example Documentation

**Example Structure:**
```

examples/
├── basic/ # Basic usage examples
├── fastapi/ # FastAPI integration
├── flask/ # Flask integration
├── advanced/ # Advanced patterns
└── testing/ # Testing examples

````

**Example Template:**
```python
"""
Modi Example: Basic Dependency Injection

This example demonstrates the fundamental concepts of dependency injection
using Modi framework. It shows how to:

1. Define injectable services
2. Create modules
3. Build applications
4. Retrieve services

Run this example:
    python examples/basic/main.py
"""

from modi import injectable, module, AppFactory

# Step 1: Define services
@injectable()
class Logger:
    """Simple logging service"""
    def log(self, message: str) -> None:
        print(f"[LOG] {message}")

@injectable()
class UserService:
    """User management service with logger dependency"""
    def __init__(self, logger: Logger):
        self._logger = logger

    def create_user(self, name: str) -> str:
        self._logger.log(f"Creating user: {name}")
        return f"User '{name}' created successfully"

# Step 2: Create module
@module(providers=[Logger, UserService])
class AppModule:
    """Application module containing all services"""
    pass

# Step 3: Create and use application
def main():
    # Create application
    app = AppFactory.create(AppModule)

    # Get service instance
    user_service = app.get(UserService)

    # Use the service
    result = user_service.create_user("John Doe")
    print(result)

if __name__ == "__main__":
    main()
````

### 8. Documentation Quality Checklist

**Content Quality:**

- [ ] Clear explanations with examples
- [ ] Progressive complexity
- [ ] All code examples tested and working
- [ ] Proper grammar and spelling
- [ ] Consistent terminology
- [ ] Up-to-date with current API

**Technical Quality:**

- [ ] All links working
- [ ] Code syntax highlighted correctly
- [ ] Examples can be copy-pasted and run
- [ ] API documentation matches implementation
- [ ] Cross-references are accurate

**User Experience:**

- [ ] Good navigation structure
- [ ] Search functionality works
- [ ] Mobile-friendly layout
- [ ] Fast loading times
- [ ] Accessible design

### 9. Documentation Maintenance

**Regular Updates:**

```bash
# Check for outdated content
just inv docs.check-outdated

# Update API documentation
just inv docs.update-api

# Validate all examples still work
just inv examples.validate-all

# Check documentation metrics
just inv docs.stats
```

**Version Management:**

- Update documentation with each release
- Maintain backwards compatibility notes
- Archive old version documentation
- Update migration guides

### 10. Common Documentation Tasks

**Adding New Feature Documentation:**

1. Write API documentation (docstrings)
2. Create user guide section
3. Add practical examples
4. Update integration guides if needed
5. Add to changelog

**Improving Existing Documentation:**

1. Review user feedback and issues
2. Identify unclear sections
3. Add more examples where needed
4. Improve navigation and structure
5. Update outdated information

**Documentation Review Process:**

1. Technical accuracy review
2. Language and clarity review
3. Example validation
4. Link checking
5. User testing with real scenarios

## Notes

- Always include working code examples
- Keep documentation in sync with code changes
- Consider different user skill levels
- Use visual aids where helpful
- Maintain consistent style and terminology
