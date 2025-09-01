
# FastAPI Integration

Modi integrates seamlessly with FastAPI, allowing you to use dependency injection for your API endpoints while maintaining FastAPI's native dependency injection for request-specific dependencies.

## Installation

```bash
pip install modi fastapi uvicorn
```

## Basic Integration

### 1. Define Your Services

```python
from modi import injectable

@injectable()
class DatabaseService:
    def get_connection(self):
        return "postgresql://localhost/myapp"

@injectable()
class UserService:
    def __init__(self, db: DatabaseService):
        self.db = db

    def get_all_users(self):
        return [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"}
        ]

    def get_user(self, user_id: int):
        users = self.get_all_users()
        return next((u for u in users if u["id"] == user_id), None)

@injectable()
class EmailService:
    def __init__(self, db: DatabaseService):
        self.db = db

    def send_email(self, to: str, subject: str, body: str):
        return {"status": "sent", "to": to, "subject": subject}
```

### 2. Create Controllers

```python
@injectable()
class UserController:
    def __init__(self, user_service: UserService, email_service: EmailService):
        self.user_service = user_service
        self.email_service = email_service

    def get_users(self):
        return {"users": self.user_service.get_all_users()}

    def get_user(self, user_id: int):
        user = self.user_service.get_user(user_id)
        if not user:
            return {"error": "User not found"}
        return {"user": user}

    def send_welcome_email(self, user_id: int):
        user = self.user_service.get_user(user_id)
        if not user:
            return {"error": "User not found"}

        result = self.email_service.send_email(
            to=user["email"],
            subject="Welcome!",
            body=f"Welcome {user['name']}!"
        )
        return {"message": "Email sent", "result": result}
```

### 3. Define Modules

```python
from modi import module

@module(providers=[DatabaseService, UserService, EmailService, UserController])
class AppModule:
    pass
```

### 4. Create FastAPI App

```python
from fastapi import FastAPI
from modi import AppFactory

# Create Modi application
modi_app = AppFactory.create(AppModule)

# Create FastAPI application
app = FastAPI(title="Modi + FastAPI Demo", version="1.0.0")

@app.get("/")
def root():
    return {"message": "Modi + FastAPI Integration"}

@app.get("/users")
def get_users():
    controller = modi_app.get(UserController)
    return controller.get_users()

@app.get("/users/{user_id}")
def get_user(user_id: int):
    controller = modi_app.get(UserController)
    return controller.get_user(user_id)

@app.post("/users/{user_id}/welcome-email")
def send_welcome_email(user_id: int):
    controller = modi_app.get(UserController)
    return controller.send_welcome_email(user_id)

@app.get("/health")
def health_check():
    return {"status": "healthy", "framework": "Modi + FastAPI"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Advanced Patterns

### Request Scoped Dependencies

Combine Modi's application-scoped services with FastAPI's request-scoped dependencies:

```python
from fastapi import Depends, Request
from modi import injectable, Scope

@injectable(scope=Scope.SINGLETON)
class UserService:
    def get_current_user(self, token: str):
        # Validate token and return user
        return {"id": 1, "name": "John", "token": token}

@injectable()
class AuthController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

# FastAPI dependency for request-scoped auth
def get_current_user_from_token(request: Request, token: str = Depends(get_auth_token)):
    modi_app = request.app.state.modi_app
    auth_controller = modi_app.get(AuthController)
    return auth_controller.user_service.get_current_user(token)

@app.get("/protected")
def protected_endpoint(current_user = Depends(get_current_user_from_token)):
    return {"message": f"Hello {current_user['name']}!"}
```

### Configuration Management

```python
@injectable()
class ConfigService:
    def __init__(self):
        self.config = {
            "database_url": os.getenv("DATABASE_URL", "sqlite:///./app.db"),
            "secret_key": os.getenv("SECRET_KEY", "dev-secret"),
            "debug": os.getenv("DEBUG", "false").lower() == "true"
        }

    def get(self, key: str):
        return self.config.get(key)

@app.get("/config")
def get_config():
    config_service = modi_app.get(ConfigService)
    return {
        "database_url": config_service.get("database_url"),
        "debug": config_service.get("debug")
        # Don't expose secret_key in production!
    }
```

### Database Integration with SQLAlchemy

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@injectable()
class DatabaseService:
    def __init__(self, config: ConfigService):
        self.config = config
        self.engine = None
        self.SessionLocal = None
        self._initialize()

    def _initialize(self):
        database_url = self.config.get("database_url")
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.SessionLocal()

@injectable()
class UserRepository:
    def __init__(self, db: DatabaseService):
        self.db = db

    def get_user(self, user_id: int):
        with self.db.get_session() as session:
            # Your SQLAlchemy query here
            return {"id": user_id, "name": "John"}

# FastAPI dependency for database session
def get_db_session():
    db_service = modi_app.get(DatabaseService)
    session = db_service.get_session()
    try:
        yield session
    finally:
        session.close()

@app.get("/users/{user_id}")
def get_user_with_session(user_id: int, db: Session = Depends(get_db_session)):
    # You can use both Modi DI and FastAPI dependencies
    user_repo = modi_app.get(UserRepository)
    return user_repo.get_user(user_id)
```

### Background Tasks

```python
from fastapi import BackgroundTasks

@injectable()
class NotificationService:
    def __init__(self, email_service: EmailService):
        self.email_service = email_service

    def send_notification(self, user_email: str, message: str):
        # Simulate async notification
        return self.email_service.send_email(
            to=user_email,
            subject="Notification",
            body=message
        )

@app.post("/notify/{user_id}")
def send_notification(
    user_id: int,
    message: str,
    background_tasks: BackgroundTasks
):
    user_controller = modi_app.get(UserController)
    notification_service = modi_app.get(NotificationService)

    user = user_controller.get_user(user_id)
    if user.get("error"):
        return user

    background_tasks.add_task(
        notification_service.send_notification,
        user["user"]["email"],
        message
    )

    return {"message": "Notification queued"}
```

## Complete Example

Here's a complete working example combining all the concepts:

```python
import os
from fastapi import FastAPI, HTTPException, Depends
from modi import injectable, module, AppFactory, Scope
import uvicorn

# Configuration
@injectable()
class ConfigService:
    def __init__(self):
        self.config = {
            "database_url": os.getenv("DATABASE_URL", "sqlite:///./app.db"),
            "debug": os.getenv("DEBUG", "false").lower() == "true",
            "app_name": "Modi FastAPI Demo"
        }

    def get(self, key: str):
        return self.config.get(key)

# Services
@injectable()
class DatabaseService:
    def __init__(self, config: ConfigService):
        self.config = config
        self.url = config.get("database_url")

    def get_connection(self):
        return f"Connected to {self.url}"

@injectable()
class UserService:
    def __init__(self, db: DatabaseService):
        self.db = db
        self.users = [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"}
        ]

    def get_all_users(self):
        return self.users

    def get_user(self, user_id: int):
        return next((u for u in self.users if u["id"] == user_id), None)

    def create_user(self, name: str, email: str):
        new_id = max(u["id"] for u in self.users) + 1
        user = {"id": new_id, "name": name, "email": email}
        self.users.append(user)
        return user

@injectable()
class EmailService:
    def send_email(self, to: str, subject: str, body: str):
        return {
            "status": "sent",
            "to": to,
            "subject": subject,
            "body": body[:50] + "..." if len(body) > 50 else body
        }

# Controllers
@injectable()
class UserController:
    def __init__(self, user_service: UserService, email_service: EmailService):
        self.user_service = user_service
        self.email_service = email_service

    def list_users(self):
        return {"users": self.user_service.get_all_users()}

    def get_user(self, user_id: int):
        user = self.user_service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"user": user}

    def create_user(self, name: str, email: str):
        user = self.user_service.create_user(name, email)

        # Send welcome email
        self.email_service.send_email(
            to=email,
            subject="Welcome!",
            body=f"Welcome to our platform, {name}!"
        )

        return {"user": user, "message": "User created and welcome email sent"}

# Module
@module(providers=[
    ConfigService,
    DatabaseService,
    UserService,
    EmailService,
    UserController
])
class AppModule:
    pass

# Create Modi app
modi_app = AppFactory.create(AppModule)

# Create FastAPI app
app = FastAPI(
    title="Modi + FastAPI Integration",
    description="A demo of Modi DI framework with FastAPI",
    version="1.0.0"
)

# Store Modi app in FastAPI state for access in dependencies
app.state.modi_app = modi_app

# Routes
@app.get("/")
def root():
    config = modi_app.get(ConfigService)
    return {
        "message": "Welcome to Modi + FastAPI!",
        "app_name": config.get("app_name"),
        "debug": config.get("debug")
    }

@app.get("/users")
def get_users():
    controller = modi_app.get(UserController)
    return controller.list_users()

@app.get("/users/{user_id}")
def get_user(user_id: int):
    controller = modi_app.get(UserController)
    return controller.get_user(user_id)

@app.post("/users")
def create_user(name: str, email: str):
    controller = modi_app.get(UserController)
    return controller.create_user(name, email)

@app.get("/health")
def health_check():
    db_service = modi_app.get(DatabaseService)
    return {
        "status": "healthy",
        "database": db_service.get_connection(),
        "framework": "Modi + FastAPI"
    }

@app.get("/di-info")
def di_info():
    """Endpoint to show what services are available"""
    return {
        "available_services": [
            "ConfigService",
            "DatabaseService",
            "UserService",
            "EmailService",
            "UserController"
        ],
        "pattern": "Modi Dependency Injection"
    }

if __name__ == "__main__":
    config_service = modi_app.get(ConfigService)
    debug = config_service.get("debug")

    uvicorn.run(
        "main:app",  # Replace with your module name
        host="0.0.0.0",
        port=8000,
        reload=debug
    )
```

## Running the Application

1. Save the code as `main.py`
2. Install dependencies: `pip install modi fastapi uvicorn`
3. Run the server: `python main.py`
4. Visit `http://localhost:8000/docs` for interactive API documentation

## Testing

```python
import pytest
from fastapi.testclient import TestClient
from main import app, modi_app

@pytest.fixture
def client():
    return TestClient(app)

def test_get_users(client):
    response = client.get("/users")
    assert response.status_code == 200
    assert "users" in response.json()

def test_dependency_injection():
    # Test Modi DI directly
    user_service = modi_app.get(UserService)
    users = user_service.get_all_users()
    assert len(users) >= 2
    assert users[0]["name"] == "Alice"

def test_create_user(client):
    response = client.post("/users?name=Charlie&email=charlie@example.com")
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["name"] == "Charlie"
    assert "message" in data
```

## Best Practices

1. **Keep Modi services stateless** when possible for better testability
2. **Use FastAPI dependencies for request-scoped data** (auth, sessions)
3. **Use Modi for application-scoped services** (database, configuration)
4. **Store Modi app in FastAPI state** for access in complex dependencies
5. **Separate business logic** in Modi services from HTTP concerns in FastAPI routes
6. **Use type hints consistently** for both Modi and FastAPI
