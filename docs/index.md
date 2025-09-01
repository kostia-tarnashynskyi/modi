# Modi

A powerful and intuitive dependency injection framework for Python

## ✨ Key Features

<div class="features-grid">
  <div class="feature-card">
    <h3>🎯 Simple & Intuitive</h3>
    <p>Clean decorator-based syntax inspired by NestJS. Easy to learn and use.</p>
  </div>
  <div class="feature-card">
    <h3>🔒 Type-Safe</h3>
    <p>Full support for Python type hints and static analysis tools like MyPy.</p>
  </div>
  <div class="feature-card">
    <h3>🧩 Modular</h3>
    <p>Organize your application into logical, reusable modules.</p>
  </div>
  <div class="feature-card">
    <h3>⚡ Flexible Scoping</h3>
    <p>Support for singleton and transient service lifetimes.</p>
  </div>
  <div class="feature-card">
    <h3>🚀 Zero Dependencies</h3>
    <p>Core framework has no external dependencies. Lightweight and fast.</p>
  </div>
  <div class="feature-card">
    <h3>🔧 Framework Agnostic</h3>
    <p>Works with FastAPI, Flask, FastStream, or any Python application.</p>
  </div>
</div>

## 🚀 Quick Example

```python
from modi import injectable, module, AppFactory

@injectable()
class UserService:
    def get_user(self, user_id: int):
        return {"id": user_id, "name": "John Doe"}

@injectable()
class UserController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def get_user_endpoint(self, user_id: int):
        return self.user_service.get_user(user_id)

@module(providers=[UserService, UserController])
class AppModule:
    pass

# Create and use the application
app = AppFactory.create(AppModule)
controller = app.get(UserController)
user = controller.get_user_endpoint(1)
print(user)  # {"id": 1, "name": "John Doe"}
```

## 📦 Installation

```bash
pip install modi
```

## 🎯 Why Modi?

Modi brings the power and elegance of dependency injection to Python applications. Inspired by NestJS, it provides:

### Clean Architecture

```python
@injectable()
class DatabaseService:
    def connect(self): ...

@injectable()
class UserRepository:
    def __init__(self, db: DatabaseService):
        self.db = db

@injectable()
class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository
```

### Modular Organization

```python
@module(
    providers=[DatabaseService, UserRepository, UserService],
    exports=[UserService]
)
class UserModule:
    pass

@module(imports=[UserModule])
class AppModule:
    pass
```

## 🔗 Framework Integration

Modi works seamlessly with your favorite frameworks:

- **[FastAPI]()** - Modern web APIs
- **[Flask]()** - Traditional web applications
- **[FastStream]()** - Event-driven applications
- **[CLI Applications]()** - Command-line tools

## 📚 Learn More

<div class="links-grid">
  ## 
    <h4>📖 Getting Started</h4>
    <p>Quick installation and first steps with Modi.</p>
  </a>
  ## 
    <h4>🧠 Core Concepts</h4>
    <p>Understanding dependency injection and modules.</p>
  </a>
  ## 
    <h4>📋 API Reference</h4>
    <p>Complete documentation of all classes and functions.</p>
  </a>
  ## 
    <h4>📁 Examples</h4>
    <p>Practical code examples and real-world patterns.</p>
  </a>
</div>

## 🤝 Contributing

We welcome contributions! Modi is open source and available on [GitHub](https://github.com/).

## 📄 License

This project is licensed under the MIT License.
