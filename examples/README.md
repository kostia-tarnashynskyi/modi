# Modi DI Examples

This directory contains various examples demonstrating how to use Modi DI framework.

## Examples

### 1. `simple_test.py` - Basic Usage

**Demonstrates:**

- Basic dependency injection
- Singleton vs Transient scopes
- Configuration injection
- Multiple dependencies

**Run:**

```bash
python examples/simple_test.py
```

### 2. `fastapi_example.py` - FastAPI Integration

**Demonstrates:**

- Integration with FastAPI
- Service layer architecture
- REST API endpoints with DI
- Graceful fallback when FastAPI is not installed

**Run:**

```bash
# Install FastAPI first
pip install fastapi uvicorn

# Run the example
python examples/fastapi_example.py
```

Visit: http://localhost:8000 and http://localhost:8000/docs

### 3. `advanced_example.py` - Modular Architecture

**Demonstrates:**

- Multi-layer architecture (Database, Business Logic, Controllers)
- Module imports and exports
- Global modules
- Complex dependency graphs
- Repository pattern

**Run:**

```bash
python examples/advanced_example.py
```

### 4. `framework_integration.py` - Framework Integrations

**Demonstrates:**

- FastAPI integration
- Flask integration
- CLI application
- Configuration management
- Caching layer

**Run:**

```bash
python examples/framework_integration.py
```

## Key Concepts Demonstrated

### Dependency Injection

```python
@injectable()
class UserService:
    def __init__(self, db: DatabaseService, logger: Logger):
        self.db = db
        self.logger = logger
```

### Modules

```python
@module(
    providers=[DatabaseService, UserService],
    imports=[LoggerModule],
    exports=[UserService],
    is_global=False
)
class UserModule:
    pass
```

### Scopes

```python
@injectable(scope=Scope.SINGLETON)  # Default - one instance
class ConfigService:
    pass

@injectable(scope=Scope.TRANSIENT)  # New instance each time
class RequestHandler:
    pass
```

### Application Bootstrap

```python
app = AppFactory.create(AppModule)
user_service = app.get(UserService)
```

## Installation for Examples

```bash
# Basic examples (no additional dependencies)
python examples/simple_test.py
python examples/advanced_example.py

# Web framework examples
pip install fastapi uvicorn  # For FastAPI
pip install flask           # For Flask

python examples/fastapi_example.py
python examples/framework_integration.py
```

## Integration Patterns

### With FastAPI

```python
# Create Modi app
modi_app = AppFactory.create(AppModule)

# Create FastAPI app
app = FastAPI()

@app.get("/users")
def get_users():
    user_service = modi_app.get(UserService)
    return user_service.get_all()
```

### With Flask

```python
# Create Modi app
modi_app = AppFactory.create(AppModule)

# Create Flask app
app = Flask(__name__)

@app.route('/users')
def get_users():
    user_service = modi_app.get(UserService)
    return jsonify(user_service.get_all())
```

### CLI Applications

```python
class CLIApp:
    def __init__(self):
        self.modi_app = AppFactory.create(AppModule)

    def run_command(self):
        service = self.modi_app.get(SomeService)
        service.do_work()
```

## Tips

1. **Start Simple**: Begin with `simple_test.py` to understand basics
2. **Layer by Layer**: Use `advanced_example.py` to see modular architecture
3. **Real Integration**: Check `framework_integration.py` for production patterns
4. **Path Setup**: Examples include path setup for importing from `src/`
5. **Graceful Degradation**: Examples handle missing optional dependencies
