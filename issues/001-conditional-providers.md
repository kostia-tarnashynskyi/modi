# Add Support for Conditional Providers

**Issue #001** | **Type:** Feature | **Priority:** Medium | **Component:** Core

## Description

Add support for conditional providers that allow services to be registered based on runtime conditions (environment variables, configuration settings, etc.).

## Business Value

This feature would enable:

- Environment-specific service implementations (production vs development)
- Feature flag-based service selection
- Configuration-driven dependency injection
- A/B testing support at the service level

## Use Cases

### 1. Environment-Specific Services

```python
@module(providers=[
    ConditionalProvider(
        provide=ILogger,
        use_class=ProductionLogger,
        condition=lambda: os.getenv('ENV') == 'production'
    ),
    ConditionalProvider(
        provide=ILogger,
        use_class=ConsoleLogger,
        condition=lambda: os.getenv('ENV') != 'production'
    )
])
class LoggingModule:
    pass
```

### 2. Feature Flag Support

```python
@module(providers=[
    ConditionalProvider(
        provide=IPaymentProcessor,
        use_class=NewPaymentProcessor,
        condition=lambda: feature_flags.is_enabled('new_payment_system')
    ),
    ConditionalProvider(
        provide=IPaymentProcessor,
        use_class=LegacyPaymentProcessor,
        condition=lambda: not feature_flags.is_enabled('new_payment_system')
    )
])
class PaymentModule:
    pass
```

### 3. Configuration-Based Selection

```python
@module(providers=[
    ConditionalProvider(
        provide=IDatabase,
        use_class=PostgreSQLDatabase,
        condition=lambda: config.database_type == 'postgresql'
    ),
    ConditionalProvider(
        provide=IDatabase,
        use_class=MySQLDatabase,
        condition=lambda: config.database_type == 'mysql'
    )
])
class DatabaseModule:
    pass
```

## Technical Requirements

### API Design

```python
from typing import Callable, Type, TypeVar, Any
from modi import Provider

T = TypeVar('T')

class ConditionalProvider(Provider[T]):
    """Provider that registers a service based on a runtime condition."""

    def __init__(
        self,
        provide: Type[T],
        use_class: Type[T] = None,
        use_factory: Callable[[], T] = None,
        use_value: T = None,
        condition: Callable[[], bool] = None,
        scope: Scope = Scope.TRANSIENT
    ):
        """
        Args:
            provide: The service type to provide
            use_class: The implementation class (mutually exclusive with use_factory/use_value)
            use_factory: Factory function to create the service
            use_value: Constant value to provide
            condition: Function that returns True if this provider should be used
            scope: Service lifetime scope
        """

# Alternative syntax using decorator
@conditional_provider(
    provide=ILogger,
    condition=lambda: os.getenv('ENV') == 'production'
)
class ProductionLogger:
    pass
```

### Core Implementation

1. **Provider Resolution Logic**

   - Evaluate conditions during container building
   - Cache condition results for performance
   - Handle condition evaluation errors gracefully
   - Support dynamic re-evaluation if needed

2. **Error Handling**

   - Clear error messages when no conditional provider matches
   - Validation that at least one provider can be satisfied
   - Detection of conflicting conditions

3. **Performance Considerations**
   - Lazy condition evaluation
   - Condition result caching
   - Minimal runtime overhead

## Acceptance Criteria

### Core Functionality

- [ ] `ConditionalProvider` class implemented with full API
- [ ] Integration with existing module system
- [ ] Support for all provider types (class, factory, value)
- [ ] Proper scope handling (singleton, transient)
- [ ] Thread-safe condition evaluation

### Error Handling

- [ ] Clear error when no conditional provider matches
- [ ] Validation of provider configuration
- [ ] Graceful handling of condition evaluation errors
- [ ] Helpful error messages with debugging information

### Performance

- [ ] Condition evaluation only during container building
- [ ] No significant impact on service resolution performance
- [ ] Memory efficient implementation
- [ ] Benchmark tests showing performance impact

### Documentation

- [ ] Comprehensive API documentation
- [ ] User guide with practical examples
- [ ] Integration examples with popular frameworks
- [ ] Best practices and common patterns

### Testing

- [ ] Unit tests for all functionality (>95% coverage)
- [ ] Integration tests with real conditions
- [ ] Performance tests and benchmarks
- [ ] Error scenario tests
- [ ] Thread safety tests

### Examples

- [ ] Environment-specific service example
- [ ] Feature flag integration example
- [ ] Configuration-driven selection example
- [ ] FastAPI integration with conditional providers

## Implementation Plan

### Phase 1: Core Implementation

1. Design and implement `ConditionalProvider` class
2. Integrate with existing container resolution logic
3. Add basic error handling and validation
4. Write comprehensive unit tests

### Phase 2: Advanced Features

1. Add condition caching and optimization
2. Implement decorator syntax
3. Add debugging and inspection tools
4. Comprehensive error handling

### Phase 3: Integration and Documentation

1. Framework integration examples
2. Performance optimization
3. User guide and documentation
4. Real-world usage examples

## Technical Considerations

### Design Decisions

1. **Condition Evaluation Timing**

   - **Option A:** Evaluate during container building (chosen)
   - **Option B:** Evaluate during service resolution
   - **Rationale:** Better performance and clearer semantics

2. **Multiple Matching Providers**

   - **Option A:** First match wins
   - **Option B:** Error on multiple matches (chosen)
   - **Rationale:** Explicit and predictable behavior

3. **No Matching Providers**
   - **Option A:** Return None/raise error (chosen)
   - **Option B:** Use default provider
   - **Rationale:** Fail fast principle

### Breaking Changes

This is a new feature with no breaking changes to existing APIs.

### Dependencies

- No new external dependencies required
- Compatible with Python 3.9+ type hints
- Integrates with existing provider system

## Testing Strategy

### Unit Tests

```python
def test_conditional_provider_matches_condition():
    """Test provider is used when condition is True"""
    pass

def test_conditional_provider_skips_when_condition_false():
    """Test provider is skipped when condition is False"""
    pass

def test_multiple_conditional_providers_first_match():
    """Test behavior with multiple providers"""
    pass

def test_no_matching_conditional_provider_raises_error():
    """Test error when no provider matches"""
    pass

def test_condition_evaluation_error_handling():
    """Test graceful handling of condition errors"""
    pass
```

### Integration Tests

```python
def test_conditional_provider_with_fastapi():
    """Test integration with FastAPI dependency injection"""
    pass

def test_conditional_provider_performance():
    """Test performance impact of conditional providers"""
    pass

def test_conditional_provider_thread_safety():
    """Test thread safety of condition evaluation"""
    pass
```

## Success Metrics

### Functionality

- All acceptance criteria met
- Zero critical bugs in initial release
- Full backward compatibility maintained

### Performance

- Less than 5% overhead in container building
- No measurable impact on service resolution
- Memory usage increase less than 10%

### Developer Experience

- Clear and intuitive API
- Comprehensive documentation
- Easy integration with existing code
- Positive community feedback

## Risk Assessment

### Technical Risks

- **Medium:** Condition evaluation performance impact
  - **Mitigation:** Lazy evaluation and caching
- **Low:** Thread safety issues
  - **Mitigation:** Immutable condition results
- **Low:** Memory usage increase
  - **Mitigation:** Efficient caching strategy

### User Experience Risks

- **Medium:** API complexity
  - **Mitigation:** Clear documentation and examples
- **Low:** Breaking existing patterns
  - **Mitigation:** Additive feature only

## Related Issues

- Issue #002: Environment-specific configuration system
- Issue #003: Feature flag integration
- Issue #004: Dynamic service replacement

## Labels

`feature` `component: core` `priority: medium` `status: approved` `good first issue`

---

**Assignee:** @ai-assistant  
**Milestone:** v0.2.0  
**Created:** 2024-01-15  
**Updated:** 2024-01-15

**Estimated Effort:** 2-3 weeks  
**Complexity:** Medium
