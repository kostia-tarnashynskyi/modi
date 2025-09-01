
# API Reference

Complete reference for all Modi classes, decorators, and functions.

## Decorators

### @injectable()

Marks a class as injectable provider that can be used as a dependency.

```python
@injectable(scope: Scope = Scope.SINGLETON)
```

**Parameters:**

- `scope` (Scope, optional): The scope for the provider instance. Defaults to `Scope.SINGLETON`.

**Returns:**

- The decorated class with injection metadata

**Example:**

```python
from modi import injectable, Scope

@injectable()  # Singleton scope (default)
class UserService:
    def get_users(self):
        return ["user1", "user2"]

@injectable(scope=Scope.TRANSIENT)  # Transient scope
class RequestHandler:
    def __init__(self):
        self.request_id = generate_id()
```


## Enums

### Scope

Defines the lifecycle scope for provider instances.

```python
class Scope(Enum):
    SINGLETON = "singleton"
    TRANSIENT = "transient"
```

**Values:**

- `SINGLETON`: One instance shared across the application
- `TRANSIENT`: New instance created for each injection

**Example:**

```python
from modi import injectable, Scope

@injectable(scope=Scope.SINGLETON)
class DatabaseService:
    pass

@injectable(scope=Scope.TRANSIENT)
class RequestProcessor:
    pass
```


### ModiApplication

Main application class that manages the dependency injection container.

#### \_\_init\_\_()

Initialize the Modi application.

```python
def __init__(self, root_module: Type)
```

**Parameters:**

- `root_module` (Type): The root module class to bootstrap

#### get()

Get an instance of a provider from the container.

```python
def get(self, cls: Type) -> Any
```

**Parameters:**

- `cls` (Type): The provider class to resolve

**Returns:**

- An instance of the requested provider

**Raises:**

- `ValueError`: If the provider is not registered
- `RuntimeError`: If circular dependency is detected

**Example:**

```python
app = AppFactory.create(AppModule)
user_service = app.get(UserService)
```

#### create()

Class method factory for creating an application (alternative to AppFactory).

```python
@classmethod
def create(cls, root_module: Type) -> 'ModiApplication'
```

**Parameters:**

- `root_module` (Type): The root module class to bootstrap

**Returns:**

- `ModiApplication`: New application instance


## Type Annotations

Modi works with Python's type hint system to automatically resolve dependencies.

### Supported Type Hints

```python
from typing import Optional, Union, List
from modi import injectable

@injectable()
class ExampleService:
    def __init__(
        self,
        required_service: UserService,              # Required dependency
        optional_service: Optional[EmailService],   # Optional dependency (not supported yet)
        union_service: Union[Service1, Service2],   # Union types (not supported yet)
        list_service: List[BaseService]             # List injection (not supported yet)
    ):
        pass
```

**Currently Supported:**

- Direct class type hints: `service: UserService`
- Forward references: `service: 'UserService'`

**Not Yet Supported:**

- Optional dependencies: `Optional[UserService]`
- Union types: `Union[Service1, Service2]`
- List injection: `List[BaseService]`
- Generic types: `Repository[User]`

### Forward References

Use string type hints for forward references:

```python
@injectable()
class ServiceA:
    def __init__(self, service_b: 'ServiceB'):  # Forward reference
        self.service_b = service_b

@injectable()
class ServiceB:
    def __init__(self, service_a: ServiceA):    # Direct reference
        self.service_a = service_a
```


## Module Metadata

When you use the `@module()` decorator, Modi adds metadata attributes to your class:

### Module Attributes

- `_is_module` (bool): Always `True` for module classes
- `_providers` (List[Type]): List of provider classes
- `_imports` (List[Type]): List of imported modules
- `_exports` (List[Type]): List of exported providers
- `_is_global` (bool): Whether the module is global

**Example:**

```python
@module(providers=[UserService], exports=[UserService])
class UserModule:
    pass

# Modi adds these attributes:
assert UserModule._is_module == True
assert UserModule._providers == [UserService]
assert UserModule._exports == [UserService]
assert UserModule._imports == []
assert UserModule._is_global == False
```

### Provider Attributes

When you use the `@injectable()` decorator, Modi adds metadata attributes:

- `_injectable` (bool): Always `True` for injectable classes
- `_scope` (Scope): The scope for this provider

**Example:**

```python
@injectable(scope=Scope.TRANSIENT)
class RequestProcessor:
    pass

# Modi adds these attributes:
assert RequestProcessor._injectable == True
assert RequestProcessor._scope == Scope.TRANSIENT
```


## Best Practices

### 1. Type Hints

Always use type hints for automatic dependency resolution:

```python
# Good
@injectable()
class UserService:
    def __init__(self, db: DatabaseService):
        self.db = db

# Bad - no type hints
@injectable()
class UserService:
    def __init__(self, db):
        self.db = db
```

### 2. Module Organization

Organize related providers into logical modules:

```python
# Feature-based modules
@module(providers=[UserService, UserRepository])
class UserModule:
    pass

@module(providers=[OrderService, PaymentService])
class OrderModule:
    pass

# Infrastructure modules
@module(
    providers=[DatabaseService, LoggerService],
    exports=[DatabaseService, LoggerService],
    global_=True
)
class InfrastructureModule:
    pass
```

### 3. Scope Selection

Choose appropriate scopes for your providers:

```python
# Singleton for shared resources
@injectable()  # Default SINGLETON
class DatabaseService:
    pass

# Transient for stateful operations
@injectable(scope=Scope.TRANSIENT)
class RequestHandler:
    def __init__(self):
        self.request_data = {}
```

### 4. Error Handling

Handle Modi-specific errors appropriately:

```python
def get_service_safely(app: ModiApplication, service_class: Type[T]) -> Optional[T]:
    try:
        return app.get(service_class)
    except ValueError:
        # Provider not registered
        return None
    except RuntimeError:
        # Circular dependency
        raise
```

### 5. Testing

Use Modi's container for testing:

```python
def test_user_service():
    app = AppFactory.create(TestModule)
    user_service = app.get(UserService)

    assert user_service is not None
    assert isinstance(user_service.db, MockDatabaseService)
```


## Performance Considerations

### Instance Creation

- **Singleton**: Created once and cached
- **Transient**: Created every time (higher memory usage)

### Resolution Performance

Modi uses a simple dependency resolution algorithm:

- O(1) for singleton lookups (cached)
- O(n) for transient creation where n is dependency depth
- Circular dependency detection adds minimal overhead

### Memory Usage

- **Singletons**: One instance per provider type
- **Transients**: Multiple instances, garbage collected when not referenced
- **Container**: Minimal metadata storage per provider

