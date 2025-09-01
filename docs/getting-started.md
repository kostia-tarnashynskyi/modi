
# Getting Started

## Installation

Install Modi using your preferred package manager:

### Using pip

```bash
pip install modi
```

### Using uv

```bash
uv add modi
```

### Using poetry

```bash
poetry add modi
```

## Requirements

- Python 3.9 or higher
- No additional dependencies required

## Quick Start

Let's build a simple application to demonstrate Modi's core concepts:

### 1. Define Services

```python
from modi import injectable

@injectable()
class DatabaseService:
    def get_connection(self):
        return "database_connection"

@injectable()
class UserService:
    def __init__(self, db: DatabaseService):
        self.db = db

    def get_users(self):
        conn = self.db.get_connection()
        return [{"id": 1, "name": "John"}]
```

### 2. Create a Module

```python
from modi import module

@module(providers=[DatabaseService, UserService])
class UserModule:
    pass
```

### 3. Bootstrap the Application

```python
from modi import AppFactory

app = AppFactory.create(UserModule)
user_service = app.get(UserService)
users = user_service.get_users()
print(users)  # [{"id": 1, "name": "John"}]
```

### Complete Example

```python
from modi import injectable, module, AppFactory

# Services
@injectable()
class DatabaseService:
    def get_connection(self):
        return "database_connection"

@injectable()
class UserService:
    def __init__(self, db: DatabaseService):
        self.db = db

    def get_users(self):
        conn = self.db.get_connection()
        return [{"id": 1, "name": "John"}]

# Module
@module(providers=[DatabaseService, UserService])
class UserModule:
    pass

# Application
if __name__ == "__main__":
    app = AppFactory.create(UserModule)
    user_service = app.get(UserService)
    print(user_service.get_users())
```

## Key Concepts at a Glance

### Providers

Classes marked with `@injectable()` that can be injected as dependencies:

```python
@injectable()
class MyService:
    def do_something(self):
        return "done"
```

### Modules

Classes marked with `@module()` that organize providers:

```python
@module(providers=[MyService])
class MyModule:
    pass
```

### Dependency Injection

Dependencies are automatically resolved through constructor parameters:

```python
@injectable()
class UserController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service  # Automatically injected
```

### Application Bootstrap

Create and configure your application:

```python
app = AppFactory.create(RootModule)
controller = app.get(UserController)
```

## Scopes

Modi supports different instance scopes:

### Singleton (Default)

One instance shared across the application:

```python
@injectable()  # Default scope is SINGLETON
class DatabaseService:
    pass
```

### Transient

New instance created for each injection:

```python
from modi import Scope

@injectable(scope=Scope.TRANSIENT)
class RequestService:
    pass
```

## Module Imports and Exports

Organize your application into logical modules:

```python
# Shared module
@module(
    providers=[DatabaseService],
    exports=[DatabaseService]  # Make available to importing modules
)
class DatabaseModule:
    pass

# Feature module
@module(
    imports=[DatabaseModule],  # Import DatabaseModule
    providers=[UserService]
)
class UserModule:
    pass
```

## Type Hints

Modi fully supports Python type hints for automatic dependency resolution:

```python
from typing import Protocol

class Logger(Protocol):
    def log(self, message: str) -> None: ...

@injectable()
class ConsoleLogger:
    def log(self, message: str) -> None:
        print(f"[LOG] {message}")

@injectable()
class UserService:
    def __init__(self, logger: ConsoleLogger):  # Type hint enables auto-resolution
        self.logger = logger
```

## Error Handling

Modi provides clear error messages for common issues:

```python
# Missing provider registration
app = AppFactory.create(EmptyModule)
try:
    service = app.get(UnregisteredService)
except ValueError as e:
    print(e)  # "Provider UnregisteredService not registered"

# Circular dependency
@injectable()
class ServiceA:
    def __init__(self, service_b: 'ServiceB'): pass

@injectable()
class ServiceB:
    def __init__(self, service_a: ServiceA): pass

try:
    app = AppFactory.create(CircularModule)
    service = app.get(ServiceA)
except RuntimeError as e:
    print(e)  # "Circular dependency detected: ServiceA"
```

## Next Steps

Now that you understand the basics:

1. **Learn the details** - Read about [core concepts](core-concepts.md)
2. **Choose your framework** - Check out [integration guides](integrations/)
3. **See examples** - Browse [practical examples](examples/)
4. **Best practices** - Learn [recommended patterns](best-practices.md)

## Common Patterns

### Configuration Service

```python
@injectable()
class ConfigService:
    def __init__(self):
        self.config = {
            "database_url": "postgresql://localhost/myapp",
            "debug": True
        }

    def get(self, key: str):
        return self.config.get(key)
```

### Factory Pattern

```python
@injectable()
class DatabaseFactory:
    def __init__(self, config: ConfigService):
        self.config = config

    def create_connection(self):
        url = self.config.get("database_url")
        return create_engine(url)
```

### Interface-based Design

```python
from abc import ABC, abstractmethod

class IUserRepository(ABC):
    @abstractmethod
    def get_user(self, user_id: int) -> dict: ...

@injectable()
class DatabaseUserRepository(IUserRepository):
    def get_user(self, user_id: int) -> dict:
        return {"id": user_id, "name": "John"}

@injectable()
class UserService:
    def __init__(self, repo: DatabaseUserRepository):  # Can be easily swapped
        self.repo = repo
```
