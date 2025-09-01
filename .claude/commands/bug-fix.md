# Bug Fix Command

## Purpose

Fix bugs in the Modi dependency injection framework with systematic approach and comprehensive testing.

## Usage

When asked to fix a bug, follow this structured debugging and resolution approach:

### 1. Bug Analysis Phase

**Understand the Problem:**

- Read the bug report and reproduction steps
- Identify affected components and scope
- Determine root cause vs symptoms
- Assess impact and priority

**Reproduce the Bug:**

```bash
# Create test case that reproduces the problem
just test --watch  # Keep running while developing fix

# If needed, create minimal reproduction example
just inv examples.create bug-reproduction
```

### 2. Investigation Workflow

**Debug Information Gathering:**

```bash
# Check recent changes
git log --oneline -10

# Run diagnostics
just doctor

# Check specific component
just test tests/specific_test.py -v

# Enable debug logging if available
export MODI_DEBUG=1
just test
```

**Code Analysis:**

- Review related code paths
- Check for edge cases and boundary conditions
- Look for type safety issues
- Identify potential race conditions

### 3. Fix Implementation

**Test-Driven Fix:**

```python
def test_bug_fix_description():
    """Test that reproduces the bug and validates the fix"""
    # Arrange - Set up conditions that trigger the bug
    app = AppFactory.create(BugReproductionModule)

    # Act - Perform the action that was failing
    with pytest.raises(ExpectedError):  # If error expected
        result = app.get(ProblematicService)

    # OR for successful fix
    result = app.get(FixedService)

    # Assert - Verify the fix works correctly
    assert result is not None
    assert result.works_correctly()
```

**Implementation Guidelines:**

```python
# Example: Fixing circular dependency detection
from modi.exceptions import CircularDependencyError

def resolve_dependency(self, service_type: Type[T]) -> T:
    """Fixed version with proper circular dependency handling"""
    if service_type in self._resolution_stack:
        chain = " -> ".join([s.__name__ for s in self._resolution_stack])
        raise CircularDependencyError(
            f"Circular dependency detected: {chain} -> {service_type.__name__}"
        )

    try:
        self._resolution_stack.add(service_type)
        # Resolution logic here
        return instance
    finally:
        self._resolution_stack.discard(service_type)
```

### 4. Bug Fix Categories

**Dependency Injection Issues:**

- Circular dependency detection
- Scope resolution problems
- Type resolution failures
- Provider configuration errors

**Decorator Issues:**

- Metadata preservation
- Parameter injection
- Inheritance handling
- Generic type support

**Module System Issues:**

- Import resolution
- Provider conflicts
- Export visibility
- Module composition

**Integration Issues:**

- Framework compatibility
- Async/await support
- Thread safety
- Memory leaks

### 5. Testing Strategy

**Unit Tests:**

```python
def test_specific_bug_scenario():
    """Test the specific scenario that was failing"""
    # Test with minimal setup
    pass

def test_edge_cases():
    """Test related edge cases that might also be affected"""
    # Test boundary conditions
    pass

def test_regression_prevention():
    """Ensure the bug doesn't reoccur"""
    # Test multiple related scenarios
    pass
```

**Integration Tests:**

```python
def test_full_application_scenario():
    """Test the fix in a realistic application context"""
    app = AppFactory.create(RealWorldModule)
    # Test end-to-end functionality
```

**Performance Tests:**

```python
def test_fix_performance_impact():
    """Ensure the fix doesn't introduce performance regression"""
    import time

    start_time = time.time()
    # Perform operation multiple times
    duration = time.time() - start_time

    assert duration < acceptable_threshold
```

### 6. Fix Validation

**Quality Checklist:**

- [ ] Bug reproduction test created and passing
- [ ] Root cause identified and addressed
- [ ] Edge cases considered and tested
- [ ] No performance regression introduced
- [ ] Type safety maintained
- [ ] Error messages are clear and helpful
- [ ] Documentation updated if API changed
- [ ] Integration tests pass
- [ ] Backwards compatibility preserved
- [ ] Related components tested

**Comprehensive Testing:**

```bash
# Run specific test suite
just test tests/core/ -v

# Run full test suite
just test --coverage

# Check for any regressions
just ci

# Validate fix doesn't break integrations
just test tests/integrations/ -v
```

### 7. Common Bug Patterns

**Type Resolution Issues:**

```python
# Common issue: Generic type handling
def resolve_generic_type(self, service_type: Type[T]) -> T:
    # Get the origin type for generics
    origin = get_origin(service_type) or service_type
    args = get_args(service_type)

    # Handle Generic[T] properly
    if origin is Generic:
        # Special handling for generic types
        pass
```

**Scoping Issues:**

```python
# Common issue: Singleton not working correctly
@injectable(scope=Scope.SINGLETON)
class SingletonService:
    pass

# Fix: Ensure singleton container properly manages instances
def get_singleton_instance(self, service_type: Type[T]) -> T:
    if service_type not in self._singletons:
        self._singletons[service_type] = self._create_instance(service_type)
    return self._singletons[service_type]
```

**Async Issues:**

```python
# Common issue: Mixing sync/async contexts
async def async_provider_method(self) -> AsyncService:
    # Ensure proper async handling
    service = await create_async_service()
    return service
```

### 8. Error Handling Improvements

**Better Error Messages:**

```python
class BetterDIException(DIException):
    """Enhanced exception with more context"""

    def __init__(self, message: str, service_type: Type = None, context: dict = None):
        self.service_type = service_type
        self.context = context or {}

        enhanced_message = f"{message}"
        if service_type:
            enhanced_message += f" (Service: {service_type.__name__})"
        if context:
            enhanced_message += f" (Context: {context})"

        super().__init__(enhanced_message)
```

**Debugging Support:**

```python
def _debug_log_resolution(self, service_type: Type, result: Any):
    """Add debug logging for troubleshooting"""
    if os.getenv('MODI_DEBUG'):
        logger.debug(f"Resolved {service_type.__name__} -> {type(result).__name__}")
```

### 9. Documentation Updates

**If Bug Fix Changes Behavior:**

- Update API documentation
- Add migration guide if needed
- Update examples to show correct usage
- Add troubleshooting section

**Changelog Entry:**

```markdown
### Bug Fixes

- **core**: Fixed circular dependency detection in complex scenarios (#123)
- **decorators**: Resolved metadata preservation with inheritance (#124)
- **integrations**: Fixed FastAPI async dependency injection (#125)
```

### 10. Release Considerations

**Version Bump:**

- Patch version for bug fixes (1.0.1)
- Minor version if new functionality added
- Major version for breaking changes

**Release Process:**

```bash
# For patch release
just inv full-release patch

# Validate release
just build
just test --coverage
```

## Notes

- Always create a test that reproduces the bug first
- Consider the impact on existing users
- Document workarounds if fix isn't backwards compatible
- Review related code that might have similar issues
- Consider adding defensive programming for similar cases
