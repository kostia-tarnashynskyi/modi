
# Troubleshooting

This guide helps you diagnose and resolve common issues when working with Modi.

## Common Issues

### 1. Circular Dependency Errors

**Problem**: Services depend on each other creating a circular dependency.

```python
# ❌ Circular dependency
@injectable()
class UserService:
    def __init__(self, order_service: 'OrderService'):
        self.order_service = order_service

@injectable()
class OrderService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service
```

**Solutions**:

#### Option 1: Redesign the Dependencies

Extract common logic into a shared service:

```python
# ✅ Extract shared logic
@injectable()
class UserOrderManager:
    def __init__(self, user_repo: UserRepository, order_repo: OrderRepository):
        self.user_repo = user_repo
        self.order_repo = order_repo

    def create_user_order(self, user_id: int, order_data: dict):
        user = self.user_repo.get_user(user_id)
        return self.order_repo.create_order(user, order_data)

@injectable()
class UserService:
    def __init__(self, manager: UserOrderManager):
        self.manager = manager

@injectable()
class OrderService:
    def __init__(self, manager: UserOrderManager):
        self.manager = manager
```

#### Option 2: Use Events/Mediator Pattern

```python
@injectable()
class EventBus:
    def __init__(self):
        self.handlers = {}

    def subscribe(self, event_type: str, handler):
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

    def publish(self, event_type: str, data):
        for handler in self.handlers.get(event_type, []):
            handler(data)

@injectable()
class UserService:
    def __init__(self, user_repo: UserRepository, event_bus: EventBus):
        self.user_repo = user_repo
        self.event_bus = event_bus

    def create_user(self, user_data: dict):
        user = self.user_repo.save_user(user_data)
        self.event_bus.publish("user_created", user)
        return user

@injectable()
class OrderService:
    def __init__(self, order_repo: OrderRepository, event_bus: EventBus):
        self.order_repo = order_repo
        self.event_bus = event_bus
        self.event_bus.subscribe("user_created", self.on_user_created)

    def on_user_created(self, user: dict):
        # React to user creation
        pass
```

### 2. Provider Not Found Errors

**Problem**: `ValueError: Provider not found for type: <class 'MyService'>`

**Causes & Solutions**:

#### Cause 1: Service Not Registered in Module

```python
# ❌ Service not included in module
@injectable()
class MyService:
    pass

@module(
    providers=[],  # MyService missing here
)
class MyModule:
    pass
```

```python
# ✅ Include service in module
@module(
    providers=[MyService],  # Add the service
)
class MyModule:
    pass
```

#### Cause 2: Importing Wrong Module

```python
# ❌ Using module that doesn't have the service
app = AppFactory.create(WrongModule)  # MyService not in WrongModule
service = app.get(MyService)  # Error!
```

```python
# ✅ Use correct module or ensure import chain
@module(
    imports=[ModuleWithMyService],  # Import module that has MyService
    providers=[]
)
class AppModule:
    pass

app = AppFactory.create(AppModule)
service = app.get(MyService)  # Works!
```

#### Cause 3: Service Not Exported

```python
# ❌ Service not exported from its module
@module(
    providers=[MyService],
    exports=[]  # MyService not exported
)
class ServiceModule:
    pass

@module(
    imports=[ServiceModule],
    providers=[OtherService]  # OtherService depends on MyService
)
class AppModule:
    pass
```

```python
# ✅ Export the service
@module(
    providers=[MyService],
    exports=[MyService]  # Export MyService
)
class ServiceModule:
    pass
```

### 3. Wrong Service Instance Issues

**Problem**: Getting unexpected instances or shared state issues.

#### Issue 1: Transient Service Sharing State

```python
# ❌ Transient service with class-level state
@injectable(scope=Scope.TRANSIENT)
class ProcessorService:
    processed_items = []  # Class-level variable - shared across instances!

    def process(self, item):
        self.processed_items.append(item)  # All instances share this list
```

```python
# ✅ Use instance-level state
@injectable(scope=Scope.TRANSIENT)
class ProcessorService:
    def __init__(self):
        self.processed_items = []  # Instance-level variable

    def process(self, item):
        self.processed_items.append(item)
```

#### Issue 2: Singleton Service with Request State

```python
# ❌ Singleton service storing request-specific data
@injectable()  # Singleton by default
class RequestProcessor:
    def __init__(self):
        self.current_request_id = None  # Shared across all requests!

    def process_request(self, request_id: str):
        self.current_request_id = request_id  # Overwrites previous requests!
```

```python
# ✅ Use transient scope for request-specific state
@injectable(scope=Scope.TRANSIENT)
class RequestProcessor:
    def __init__(self):
        self.current_request_id = None  # Each request gets own instance

    def process_request(self, request_id: str):
        self.current_request_id = request_id
```

### 4. Module Import Issues

**Problem**: Services from imported modules not available.

#### Issue 1: Circular Module Imports

```python
# ❌ Circular module imports
# user_module.py
from .order_module import OrderModule

@module(
    imports=[OrderModule],
    providers=[UserService]
)
class UserModule:
    pass

# order_module.py
from .user_module import UserModule  # Circular import!

@module(
    imports=[UserModule],
    providers=[OrderService]
)
class OrderModule:
    pass
```

```python
# ✅ Create shared module or reorganize
# shared_module.py
@module(
    providers=[SharedService],
    exports=[SharedService],
    global_=True
)
class SharedModule:
    pass

# user_module.py
@module(
    imports=[SharedModule],
    providers=[UserService]
)
class UserModule:
    pass

# order_module.py
@module(
    imports=[SharedModule],
    providers=[OrderService]
)
class OrderModule:
    pass

# app_module.py
@module(
    imports=[SharedModule, UserModule, OrderModule]
)
class AppModule:
    pass
```

### 5. Type Annotation Issues

**Problem**: Modi cannot resolve dependencies due to incorrect type hints.

#### Issue 1: String Forward References

```python
# ❌ String forward references without proper import
@injectable()
class UserService:
    def __init__(self, repository: 'UserRepository'):  # String reference
        self.repository = repository
```

```python
# ✅ Use proper imports or TYPE_CHECKING
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .repositories import UserRepository

@injectable()
class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository
```

#### Issue 2: Generic Types

```python
# ❌ Using generic types directly
from typing import List

@injectable()
class DataService:
    def __init__(self, processors: List[DataProcessor]):  # Modi can't resolve List
        self.processors = processors
```

```python
# ✅ Inject individual services or use factory pattern
@injectable()
class DataService:
    def __init__(
        self,
        json_processor: JsonDataProcessor,
        xml_processor: XmlDataProcessor
    ):
        self.processors = [json_processor, xml_processor]

# Or use a factory
@injectable()
class ProcessorFactory:
    def __init__(
        self,
        json_processor: JsonDataProcessor,
        xml_processor: XmlDataProcessor
    ):
        self.json_processor = json_processor
        self.xml_processor = xml_processor

    def get_processors(self) -> List[DataProcessor]:
        return [self.json_processor, self.xml_processor]

@injectable()
class DataService:
    def __init__(self, factory: ProcessorFactory):
        self.processors = factory.get_processors()
```

## Debugging Tips

### 1. Enable Debug Logging

```python
import logging

# Enable debug logging to see dependency resolution
logging.basicConfig(level=logging.DEBUG)

# This will show you what Modi is doing internally
app = AppFactory.create(AppModule)
```

### 2. Inspect the Container

```python
# Check what services are registered
app = AppFactory.create(AppModule)

# Print all registered providers (this would need to be added to Modi)
# For now, you can add debug prints in your modules:

@module(
    providers=[UserService, OrderService],
    imports=[DatabaseModule]
)
class AppModule:
    def __init__(self):
        print(f"AppModule providers: {[UserService.__name__, OrderService.__name__]}")
        print(f"AppModule imports: {[DatabaseModule.__name__]}")
```

### 3. Test Individual Services

```python
# Test service creation in isolation
from modi.container import Container

container = Container()
container.register_provider(DatabaseService)
container.register_provider(UserRepository)
container.register_provider(UserService)

# Try to resolve the service
try:
    user_service = container.resolve(UserService)
    print("Service resolved successfully")
except Exception as e:
    print(f"Failed to resolve service: {e}")
```

### 4. Check Dependency Chain

```python
# Manually trace dependency chain
print("UserService depends on:")
print("- UserRepository")
print("- EmailService")

print("UserRepository depends on:")
print("- DatabaseService")

print("EmailService depends on:")
print("- EmailConfig")

# Make sure each dependency is registered in the right module
```

## Performance Issues

### 1. Slow Application Startup

**Problem**: Application takes long time to start.

**Diagnosis**:

```python
import time

@injectable()
class SlowService:
    def __init__(self):
        print(f"SlowService init started at {time.time()}")
        time.sleep(5)  # Simulate slow initialization
        print(f"SlowService init finished at {time.time()}")

# Time the application startup
start_time = time.time()
app = AppFactory.create(AppModule)
print(f"App created in {time.time() - start_time} seconds")
```

**Solutions**:

1. Use lazy initialization
2. Move expensive operations out of `__init__`
3. Use background initialization

```python
@injectable()
class OptimizedService:
    def __init__(self):
        self._expensive_resource = None

    @property
    def expensive_resource(self):
        if self._expensive_resource is None:
            self._expensive_resource = self._create_expensive_resource()
        return self._expensive_resource

    def _create_expensive_resource(self):
        # Expensive initialization only when needed
        return ExpensiveResource()
```

### 2. Memory Leaks

**Problem**: Application memory usage keeps growing.

**Common Causes**:

1. Circular references in singletons
2. Not cleaning up resources
3. Storing references to transient services

**Solutions**:

```python
@injectable()
class ResourceManager:
    def __init__(self):
        self.connections = []

    def get_connection(self):
        connection = create_connection()
        self.connections.append(connection)
        return connection

    def cleanup(self):
        for conn in self.connections:
            conn.close()
        self.connections.clear()

    def __del__(self):
        self.cleanup()
```

## Testing Issues

### 1. Cannot Mock Dependencies

**Problem**: Mocking injected dependencies for testing.

```python
# ❌ Trying to mock after injection
def test_user_service():
    app = AppFactory.create(AppModule)
    user_service = app.get(UserService)

    # Can't easily mock user_service.repository now
    with patch.object(user_service, 'repository') as mock_repo:
        # This works but feels awkward
        pass
```

```python
# ✅ Create test module with mocks
@injectable()
class MockUserRepository:
    def save_user(self, user_data):
        return {"id": 1, **user_data}

@module(
    providers=[MockUserRepository, UserService],
    # Replace real repository with mock
)
class TestUserModule:
    pass

def test_user_service():
    app = AppFactory.create(TestUserModule)
    user_service = app.get(UserService)
    # user_service now uses MockUserRepository
```

### 2. Test Isolation Issues

**Problem**: Tests affecting each other due to shared singleton instances.

```python
# ❌ Tests affecting each other
@injectable()
class CounterService:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1

def test_counter_first():
    app = AppFactory.create(AppModule)
    counter = app.get(CounterService)
    counter.increment()
    assert counter.count == 1

def test_counter_second():
    app = AppFactory.create(AppModule)
    counter = app.get(CounterService)  # Same instance as previous test!
    assert counter.count == 0  # Fails! count is 1
```

```python
# ✅ Reset state between tests or use transient scope
import pytest

@pytest.fixture
def fresh_app():
    # Create fresh container for each test
    return AppFactory.create(AppModule)

def test_counter_first(fresh_app):
    counter = fresh_app.get(CounterService)
    counter.increment()
    assert counter.count == 1

def test_counter_second(fresh_app):
    counter = fresh_app.get(CounterService)  # Fresh instance
    assert counter.count == 0  # Passes!

# Or make the service transient for tests
@injectable(scope=Scope.TRANSIENT)
class CounterService:
    # Each test gets fresh instance
    pass
```

## Getting Help

If you're still experiencing issues:

1. **Check the examples**: Look at the integration examples in the `docs/integrations/` directory
2. **Review best practices**: Make sure you're following the patterns in `docs/best-practices.md`
3. **Create minimal reproduction**: Strip down your code to the minimum that reproduces the issue
4. **Check types**: Ensure all your type annotations are correct and imports are available

### Creating a Minimal Reproduction

```python
# minimal_repro.py
from modi import injectable, module, AppFactory

@injectable()
class SimpleService:
    def __init__(self):
        self.value = "Hello"

@module(providers=[SimpleService])
class SimpleModule:
    pass

def main():
    app = AppFactory.create(SimpleModule)
    service = app.get(SimpleService)
    print(service.value)

if __name__ == "__main__":
    main()
```

This minimal example should work. If it doesn't, there's likely an installation or environment issue. If it works but your code doesn't, gradually add complexity until you find the issue.
