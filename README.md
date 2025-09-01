# Modi

[![Documentation](https://img.shields.io/badge/docs-github--pages-blue)](https://kostia-tarnashynskyi.github.io/modi/)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![AI-Powered](https://img.shields.io/badge/AI--Powered-🤖-purple.svg)](CLAUDE.md)

A powerful and intuitive dependency injection framework for Python, inspired by NestJS.

> **🤖 AI-Generated Project**: This project is heavily integrated with AI development workflows. Most of the codebase, documentation, and project structure has been generated and refined through AI-assisted development using Claude and GitHub Copilot. See [CLAUDE.md](CLAUDE.md) for details about our AI integration.

## 🚀 Quick Start

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

## 📚 Core Concepts

### Dependency Injection

```python
@injectable()
class DatabaseService:
    def connect(self):
        return "Connected to database"

@injectable()
class UserService:
    def __init__(self, db: DatabaseService):  # Automatic injection
        self.db = db

    def create_user(self, name: str):
        connection = self.db.connect()
        return f"User {name} created with {connection}"
```

### Module System

```python
@module(providers=[DatabaseService, UserService])
class AppModule:
    pass

# Bootstrap your application
app = AppFactory.create(AppModule)
user_service = app.get(UserService)
```

## ✨ Features

- **🚀 Simple & Intuitive** - Easy decorators and patterns
- **💉 Automatic Injection** - Dependencies resolved automatically
- **🔄 Module System** - Organize code into reusable modules
- **🏭 Clean Bootstrap** - Simple application factory
- **🔧 Framework Agnostic** - Works with any Python app

## ��️ Installation

```bash
pip install modi
```

## 🎯 Framework Examples

### FastAPI Integration

```python
from fastapi import FastAPI
from modi import injectable, module, AppFactory

@injectable()
class UserService:
    def get_users(self):
        return [{"id": 1, "name": "John"}]

@injectable()
class UserController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

@module(providers=[UserService, UserController])
class AppModule:
    pass

# Setup
app_container = AppFactory.create(AppModule)
fastapi_app = FastAPI()
user_controller = app_container.get(UserController)

@fastapi_app.get("/users")
def get_users():
    return user_controller.user_service.get_users()
```

## 🏗️ Development

Simple development workflow:

```bash
# Install dependencies
just install

# Run tests
just test

# Format and lint
just format
just lint

# Build package
just build

# View all commands
just
```

## 🤖 AI-Powered Development

Modi is built with AI-first development practices:

- **🧠 AI-Generated Codebase** - Core framework generated through AI pair programming
- **📚 AI-Written Documentation** - Guides and API docs created with AI assistance
- **�� AI-Optimized Workflows** - Simple task management via TASKS.md
- **✨ Continuous AI Integration** - Ongoing development with AI code review

See [CLAUDE.md](CLAUDE.md) for technical details about our AI integration.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Documentation**: [https://kostia-tarnashynskyi.github.io/modi/](https://kostia-tarnashynskyi.github.io/modi/)
- **GitHub**: [https://github.com/kostia-tarnashynskyi/modi](https://github.com/kostia-tarnashynskyi/modi)
