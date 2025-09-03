# Modi Documentation

Modi is a powerful and intuitive dependency injection framework for Python, inspired by NestJS.

## 📚 Documentation

- **[Getting Started](getting-started.md)** - Quick setup and first steps
- **[Core Concepts](core-concepts.md)** - Understand how Modi works
- **[API Reference](api-reference.md)** - Complete API documentation
- **[Best Practices](best-practices.md)** - Tips and recommendations
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions

## 🚀 Integrations

- **[FastAPI](integrations/fastapi.md)** - Modern web APIs
- **[Flask](integrations/flask.md)** - Traditional web applications  
- **[FastStream](integrations/faststream.md)** - Event-driven applications
- **[Simple Apps](integrations/simple-apps.md)** - Command-line tools

## 💡 Examples

Check out the **[examples/](../examples/)** directory for working code examples:

- `simple_test.py` - Basic dependency injection
- `advanced_example.py` - Modular architecture 
- `fastapi_example.py` - FastAPI integration
- `framework_integration.py` - Multiple framework examples

## ✨ Key Features

- 🎯 **Simple & Intuitive** - Clean decorator-based syntax inspired by NestJS
- 🔒 **Type-Safe** - Full support for Python type hints and static analysis
- 🧩 **Modular** - Organize your application into logical, reusable modules
- ⚡ **Flexible Scoping** - Support for singleton and transient service lifetimes
- 🚀 **Zero Dependencies** - Core framework has no external dependencies
- 🔧 **Framework Agnostic** - Works with any Python application

## 📦 Installation

```bash
pip install modi
```

## 🔧 Quick Example

```python
from modi import injectable, module, AppFactory

@injectable()
class DatabaseService:
    def get_data(self): return "data"

@injectable()
class UserService:
    def __init__(self, db: DatabaseService):
        self.db = db
    
    def get_users(self): return self.db.get_data()

@module(providers=[DatabaseService, UserService])
class AppModule: pass

# Use in your application
app = AppFactory.create(AppModule)
user_service = app.get(UserService)
```

## 🤝 Contributing

We welcome contributions! Modi is open source and available on [GitHub](https://github.com/kostia-tarnashynskyi/modi).

## 📄 License

Modi is released under the MIT License.
