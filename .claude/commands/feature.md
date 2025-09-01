# Feature Development Command

## Purpose

Create new features for the Modi dependency injection framework following established patterns and best practices.

## Usage

When asked to implement a new feature, follow this structured approach:

### 1. Analysis Phase

- Review the task description and acceptance criteria
- Understand the feature requirements and constraints
- Identify affected components and modules
- Plan the implementation approach

### 2. Implementation Structure

**Core Components** (if applicable):

```python
# src/modi/core/ - Core dependency injection logic
# Focus: Container, resolution, scoping

# src/modi/decorators/ - Decorator implementations
# Focus: @injectable, @module, parameter decorators

# src/modi/modules/ - Module system
# Focus: Module definition, imports, providers

# src/modi/exceptions/ - Custom exceptions
# Focus: DI-specific error handling
```

**Integration Components** (if applicable):

```python
# src/modi/integrations/ - Framework integrations
# Focus: FastAPI, Flask, FastStream, CLI support
```

### 3. Development Workflow

```bash
# 1. Setup development environment
just setup

# 2. Create feature branch
git checkout -b feat/feature-name

# 3. Implement feature with TDD approach
just test --watch  # Run in separate terminal

# 4. Write implementation
# Follow type safety and established patterns

# 5. Run quality checks
just check

# 6. Update documentation
# Add examples, update API docs

# 7. Validate everything
just ci
```

### 4. Implementation Guidelines

**Type Safety:**

```python
from typing import TypeVar, Generic, Protocol, Optional
from modi import injectable, module

T = TypeVar('T')

class IRepository(Protocol[T]):
    def find_by_id(self, id: int) -> Optional[T]: ...

@injectable()
class UserRepository(IRepository[User]):
    def find_by_id(self, id: int) -> Optional[User]:
        # Implementation with proper type hints
        pass
```

**Error Handling:**

```python
from modi.exceptions import DIException, CircularDependencyError

class FeatureError(DIException):
    """Specific error for this feature"""
    pass

# Use custom exceptions with clear messages
if invalid_condition:
    raise FeatureError("Clear description of what went wrong")
```

**Testing Pattern:**

```python
import pytest
from modi import AppFactory
from modi.testing import TestModule

def test_feature_implementation():
    """Test the new feature functionality"""
    # Arrange
    app = AppFactory.create(TestModule)

    # Act
    result = app.get(ServiceUnderTest)

    # Assert
    assert isinstance(result, ServiceUnderTest)
    # Additional assertions
```

### 5. Documentation Requirements

**API Documentation:**

- Add docstrings with type information
- Include usage examples
- Document any exceptions

**User Documentation:**

- Update relevant sections in docs/
- Add practical examples
- Update feature comparison tables

**Example Code:**

- Create minimal example in examples/
- Ensure example is tested and works
- Include integration examples if applicable

### 6. Quality Checklist

- [ ] Implementation follows established patterns
- [ ] Full type hint coverage
- [ ] Comprehensive test coverage (>95%)
- [ ] No circular import issues
- [ ] Performance considerations addressed
- [ ] Error handling with custom exceptions
- [ ] Documentation updated (API + user docs)
- [ ] Examples created and tested
- [ ] Integration tests pass
- [ ] Security considerations reviewed
- [ ] Backwards compatibility maintained

### 7. Integration Patterns

**FastAPI Integration:**

```python
from fastapi import FastAPI, Depends
from modi.integrations.fastapi import ModiDependency

app = FastAPI()

@app.get("/endpoint")
async def endpoint(service: MyService = Depends(ModiDependency(MyService))):
    return service.method()
```

**Module Definition:**

```python
@module(
    providers=[ServiceA, ServiceB],
    imports=[OtherModule],
    exports=[ServiceA]  # If needed by other modules
)
class FeatureModule:
    """Module for the new feature functionality"""
    pass
```

### 8. Common Patterns

**Service with Dependencies:**

```python
@injectable()
class AdvancedService:
    def __init__(
        self,
        repo: IRepository,
        config: AppConfig,
        logger: Optional[ILogger] = None
    ):
        self._repo = repo
        self._config = config
        self._logger = logger or NullLogger()
```

**Conditional Providers:**

```python
@module(providers=[
    ConditionalProvider(
        provide=IService,
        use_class=ProductionService,
        condition=lambda: os.getenv('ENVIRONMENT') == 'production'
    )
])
class ConditionalModule:
    pass
```

### 9. Performance Considerations

- Lazy initialization where appropriate
- Efficient dependency resolution
- Memory usage optimization
- Thread safety if applicable
- Caching strategies for expensive operations

### 10. Final Validation

```bash
# Run full CI pipeline locally
just ci

# Check specific quality metrics
just test --coverage
just lint
just security
just docs-validate

# Validate examples work
just inv examples.run feature-example
```

## Notes

- Always prioritize type safety and clear interfaces
- Follow the existing codebase patterns
- Consider backwards compatibility impact
- Document breaking changes clearly
- Test integration scenarios thoroughly
