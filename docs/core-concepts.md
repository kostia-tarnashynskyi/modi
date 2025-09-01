
# Core Concepts

This guide explains the fundamental concepts of Modi's dependency injection framework and how they work together to create modular, maintainable applications.

## Dependency Injection Overview

Dependency injection (DI) is a design pattern where objects receive their dependencies from external sources rather than creating them internally. This promotes loose coupling, easier testing, and better code organization.

### Without DI

```python
class UserService:
    def __init__(self):
        self.db = DatabaseService()  # Tight coupling
        self.logger = LoggerService()  # Hard to test

    def get_user(self, user_id):
        self.logger.info(f"Getting user {user_id}")
        return self.db.find_user(user_id)
```

### With Modi DI

```python
@injectable()
class UserService:
    def __init__(self, db: DatabaseService, logger: LoggerService):
        self.db = db      # Injected dependency
        self.logger = logger  # Easy to mock for testing

    def get_user(self, user_id):
        self.logger.info(f"Getting user {user_id}")
        return self.db.find_user(user_id)
```

## Providers

Providers are classes that can be injected as dependencies. In Modi, you mark a class as a provider using the `@injectable()` decorator.

### Basic Provider

```python
from modi import injectable

@injectable()
class EmailService:
    def send_email(self, to: str, subject: str, body: str):
        print(f"Sending email to {to}: {subject}")
        return {"status": "sent", "to": to}
```

### Provider with Dependencies

```python
@injectable()
class NotificationService:
    def __init__(self, email_service: EmailService, sms_service: SMSService):
        self.email_service = email_service
        self.sms_service = sms_service

    def notify(self, user: dict, message: str):
        # Send both email and SMS
        self.email_service.send_email(user["email"], "Notification", message)
        self.sms_service.send_sms(user["phone"], message)
```

### Constructor Injection

Modi uses constructor injection, resolving dependencies through type hints in the `__init__` method:

```python
@injectable()
class OrderService:
    def __init__(
        self,
        payment_service: PaymentService,    # Required dependency
        email_service: EmailService,        # Required dependency
        logger: LoggerService               # Required dependency
    ):
        self.payment_service = payment_service
        self.email_service = email_service
        self.logger = logger

    def process_order(self, order_data: dict):
        self.logger.info("Processing order")

        # Use injected dependencies
        payment_result = self.payment_service.charge(order_data["amount"])
        if payment_result["success"]:
            self.email_service.send_confirmation(order_data["customer_email"])
            return {"status": "success", "order_id": order_data["id"]}

        return {"status": "failed", "error": "Payment failed"}
```

## Scopes

Scopes control the lifetime of provider instances. Modi supports two main scopes:

### Singleton Scope (Default)

One instance is created and shared throughout the application:

```python
from modi import injectable, Scope

@injectable()  # Default scope is SINGLETON
class DatabaseService:
    def __init__(self):
        self.connection = self._create_connection()
        print(f"Database connection created: {id(self.connection)}")

    def _create_connection(self):
        return "db_connection_12345"

# Usage
app = AppFactory.create(MyModule)
db1 = app.get(DatabaseService)  # Creates new instance
db2 = app.get(DatabaseService)  # Returns same instance
assert db1 is db2  # True - same instance
```

### Transient Scope

A new instance is created every time it's requested:

```python
@injectable(scope=Scope.TRANSIENT)
class RequestProcessor:
    def __init__(self):
        self.request_id = self._generate_id()
        print(f"New request processor: {self.request_id}")

    def _generate_id(self):
        import uuid
        return str(uuid.uuid4())

# Usage
app = AppFactory.create(MyModule)
processor1 = app.get(RequestProcessor)  # Creates new instance
processor2 = app.get(RequestProcessor)  # Creates another new instance
assert processor1 is not processor2  # True - different instances
```

### Scope Best Practices

- **Singleton**: Use for stateless services, database connections, configuration
- **Transient**: Use for stateful processing, request handlers, builders

```python
# Good singleton candidates
@injectable()  # Singleton by default
class ConfigService: pass

@injectable()  # Singleton by default
class DatabaseConnectionPool: pass

@injectable()  # Singleton by default
class EmailService: pass

# Good transient candidates
@injectable(scope=Scope.TRANSIENT)
class RequestHandler:
    def __init__(self):
        self.request_data = {}

@injectable(scope=Scope.TRANSIENT)
class ReportGenerator:
    def __init__(self):
        self.temp_files = []

@injectable(scope=Scope.TRANSIENT)
class DataProcessor:
    def __init__(self):
        self.processing_state = {}
```

## Modules

Modules organize related providers and manage their dependencies. They define which providers are available and how they can be shared.

### Basic Module

```python
from modi import module

@module(providers=[EmailService, UserService, OrderService])
class BusinessModule:
    pass
```

### Module Properties

- **providers**: Classes that this module makes available
- **imports**: Other modules to import
- **exports**: Providers to make available to importing modules
- **global\_**: Whether this module should be globally available

```python
@module(
    providers=[EmailService, SMSService, NotificationService],
    exports=[NotificationService],  # Only NotificationService is exported
    global_=False  # Not global, must be explicitly imported
)
class NotificationModule:
    pass

@module(
    imports=[NotificationModule],  # Import NotificationModule
    providers=[UserService, OrderService]
)
class BusinessModule:
    pass
```

### Module Imports and Exports

Modules can import other modules to access their exported providers:

```python
# Core module with shared services
@module(
    providers=[DatabaseService, LoggerService, ConfigService],
    exports=[DatabaseService, LoggerService, ConfigService],  # Export all
    global_=False
)
class CoreModule:
    pass

# User module
@module(
    imports=[CoreModule],  # Import core services
    providers=[UserService, UserRepository],
    exports=[UserService]  # Only export UserService
)
class UserModule:
    pass

# Order module
@module(
    imports=[CoreModule, UserModule],  # Import both modules
    providers=[OrderService, PaymentService]
)
class OrderModule:
    pass

# Application module
@module(
    imports=[OrderModule]  # OrderModule brings in UserModule and CoreModule
)
class AppModule:
    pass
```

### Global Modules

Global modules are automatically available to all other modules without explicit imports:

```python
@module(
    providers=[LoggerService, ConfigService],
    exports=[LoggerService, ConfigService],
    global_=True  # Available everywhere
)
class GlobalModule:
    pass

# This module can use LoggerService without importing GlobalModule
@module(providers=[UserService])  # LoggerService available automatically
class UserModule:
    pass

@injectable()
class UserService:
    def __init__(self, logger: LoggerService):  # Works because LoggerService is global
        self.logger = logger
```

## Dependency Resolution

Modi automatically resolves dependencies by analyzing type hints in constructor parameters.

### Type Hint Resolution

```python
@injectable()
class UserService:
    def __init__(
        self,
        db: DatabaseService,        # Type hint enables automatic resolution
        email: EmailService,        # Modi finds EmailService provider
        config: ConfigService       # Modi finds ConfigService provider
    ):
        self.db = db
        self.email = email
        self.config = config
```

### Forward References

When you have circular imports or forward references, use string type hints:

```python
@injectable()
class UserService:
    def __init__(self, order_service: 'OrderService'):  # String type hint
        self.order_service = order_service

@injectable()
class OrderService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

# Modi resolves forward references automatically
```

### Resolution Process

1. **Type Analysis**: Modi examines constructor parameters and their type hints
2. **Provider Lookup**: Finds registered providers that match the required types
3. **Dependency Resolution**: Recursively resolves dependencies of dependencies
4. **Instance Creation**: Creates instances with proper dependency injection
5. **Scope Management**: Manages instance lifecycle according to scope rules

```python
# Resolution example
@injectable()
class A:
    def __init__(self, b: 'B'):
        self.b = b

@injectable()
class B:
    def __init__(self, c: 'C'):
        self.c = c

@injectable()
class C:
    def __init__(self):
        pass

# When app.get(A) is called:
# 1. Modi sees A needs B
# 2. Modi sees B needs C
# 3. Modi creates C (no dependencies)
# 4. Modi creates B with C injected
# 5. Modi creates A with B injected
# 6. Returns A instance
```

## Circular Dependency Detection

Modi detects circular dependencies and throws helpful error messages:

```python
@injectable()
class ServiceA:
    def __init__(self, service_b: 'ServiceB'):
        self.service_b = service_b

@injectable()
class ServiceB:
    def __init__(self, service_a: ServiceA):
        self.service_a = service_a

@module(providers=[ServiceA, ServiceB])
class CircularModule:
    pass

app = AppFactory.create(CircularModule)
try:
    service = app.get(ServiceA)
except RuntimeError as e:
    print(e)  # "Circular dependency detected: ServiceA"
```

### Breaking Circular Dependencies

Use the factory pattern or interfaces to break circular dependencies:

```python
# Option 1: Factory pattern
@injectable()
class ServiceBFactory:
    def create_service_b(self) -> 'ServiceB':
        return ServiceB()

@injectable()
class ServiceA:
    def __init__(self, service_b_factory: ServiceBFactory):
        self.service_b_factory = service_b_factory

    def get_service_b(self):
        return self.service_b_factory.create_service_b()

# Option 2: Interface-based
from abc import ABC, abstractmethod

class IServiceB(ABC):
    @abstractmethod
    def do_something(self): pass

@injectable()
class ServiceA:
    def __init__(self, service_b: IServiceB):
        self.service_b = service_b

@injectable()
class ServiceB(IServiceB):
    def __init__(self, config: ConfigService):  # No circular dependency
        self.config = config

    def do_something(self):
        return "done"
```

## Application Bootstrap

The `AppFactory` creates and configures your application:

### Basic Bootstrap

```python
from modi import AppFactory

@module(providers=[UserService, OrderService])
class AppModule:
    pass

# Create application
app = AppFactory.create(AppModule)

# Get services
user_service = app.get(UserService)
order_service = app.get(OrderService)
```

### Application Lifecycle

```python
# Create application with root module
app = AppFactory.create(RootModule)

# Application processes the module tree:
# 1. Register providers from RootModule
# 2. Process imported modules recursively
# 3. Register their providers
# 4. Build dependency graph
# 5. Prepare for instance resolution

# Get services as needed
service = app.get(SomeService)  # Lazy instantiation
```

## Error Handling

Modi provides clear error messages for common issues:

### Provider Not Registered

```python
@injectable()
class UnregisteredService:
    pass

@module(providers=[])  # Empty providers list
class EmptyModule:
    pass

app = AppFactory.create(EmptyModule)
try:
    service = app.get(UnregisteredService)
except ValueError as e:
    print(e)  # "Provider UnregisteredService not registered"
```

### Missing Type Hints

```python
@injectable()
class BadService:
    def __init__(self, dependency):  # No type hint!
        self.dependency = dependency

# Modi cannot resolve dependencies without type hints
# The dependency parameter will be ignored
```

### Forward Reference Resolution Failure

```python
@injectable()
class ServiceA:
    def __init__(self, unknown: 'UnknownService'):  # UnknownService doesn't exist
        self.unknown = unknown

@module(providers=[ServiceA])
class BadModule:
    pass

app = AppFactory.create(BadModule)
try:
    service = app.get(ServiceA)
except ValueError as e:
    print(e)  # "Cannot resolve forward reference: UnknownService"
```

## Best Practices

### 1. Use Clear Type Hints

```python
# Good
@injectable()
class UserService:
    def __init__(self, db: DatabaseService, logger: LoggerService):
        self.db = db
        self.logger = logger

# Bad
@injectable()
class UserService:
    def __init__(self, db, logger):  # No type hints
        self.db = db
        self.logger = logger
```

### 2. Organize with Modules

```python
# Group related functionality
@module(providers=[UserService, UserRepository])
class UserModule:
    pass

@module(providers=[OrderService, PaymentService])
class OrderModule:
    pass

@module(imports=[UserModule, OrderModule])
class AppModule:
    pass
```

### 3. Use Appropriate Scopes

```python
# Singleton for stateless services
@injectable()  # Default SINGLETON
class EmailService:
    pass

# Transient for stateful processing
@injectable(scope=Scope.TRANSIENT)
class RequestProcessor:
    def __init__(self):
        self.state = {}
```

### 4. Export Minimally

```python
# Only export what other modules need
@module(
    providers=[InternalService, PublicService, AnotherInternalService],
    exports=[PublicService]  # Only export what's needed
)
class FeatureModule:
    pass
```

### 5. Use Global Modules Sparingly

```python
# Good candidates for global modules
@module(
    providers=[LoggerService, ConfigService],
    exports=[LoggerService, ConfigService],
    global_=True  # These are needed everywhere
)
class InfrastructureModule:
    pass

# Don't make business logic global
@module(
    providers=[UserService, OrderService],
    global_=False  # Keep business logic modular
)
class BusinessModule:
    pass
```

## Advanced Patterns

### Factory Pattern

```python
@injectable()
class DatabaseConnectionFactory:
    def __init__(self, config: ConfigService):
        self.config = config

    def create_connection(self, database_name: str):
        url = f"{self.config.get('db_url')}/{database_name}"
        return DatabaseConnection(url)

@injectable()
class UserRepository:
    def __init__(self, db_factory: DatabaseConnectionFactory):
        self.db = db_factory.create_connection("users")
```

### Repository Pattern

```python
from abc import ABC, abstractmethod

class IUserRepository(ABC):
    @abstractmethod
    def get_user(self, user_id: int) -> dict: pass

@injectable()
class DatabaseUserRepository(IUserRepository):
    def __init__(self, db: DatabaseService):
        self.db = db

    def get_user(self, user_id: int) -> dict:
        return self.db.query(f"SELECT * FROM users WHERE id = {user_id}")

@injectable()
class UserService:
    def __init__(self, repository: DatabaseUserRepository):  # Can be easily swapped
        self.repository = repository
```

### Configuration Pattern

```python
@injectable()
class DatabaseConfig:
    def __init__(self):
        self.host = "localhost"
        self.port = 5432
        self.database = "myapp"

@injectable()
class DatabaseService:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.connection = self._connect()

    def _connect(self):
        return f"postgresql://{self.config.host}:{self.config.port}/{self.config.database}"
```

This covers all the core concepts of Modi's dependency injection framework. Understanding these concepts will help you build maintainable, testable, and modular Python applications.
