
# Best Practices

This guide outlines recommended patterns and practices for building maintainable applications with Modi.

## Project Structure

### Recommended Directory Layout

```
my_project/
├── src/
│   └── my_project/
│       ├── __init__.py
│       ├── main.py                 # Application entry point
│       ├── config/
│       │   ├── __init__.py
│       │   └── settings.py         # Configuration services
│       ├── core/                   # Core/shared modules
│       │   ├── __init__.py
│       │   ├── database.py
│       │   ├── logging.py
│       │   └── module.py
│       ├── users/                  # Feature modules
│       │   ├── __init__.py
│       │   ├── services.py
│       │   ├── repositories.py
│       │   └── module.py
│       ├── orders/
│       │   ├── __init__.py
│       │   ├── services.py
│       │   ├── repositories.py
│       │   └── module.py
│       └── app/
│           ├── __init__.py
│           └── module.py           # Root application module
├── tests/
├── requirements.txt
└── pyproject.toml
```

### Module Organization Example

```python
# src/my_project/core/module.py
from modi import module
from .database import DatabaseService
from .logging import LoggerService
from .config import ConfigService

@module(
    providers=[DatabaseService, LoggerService, ConfigService],
    exports=[DatabaseService, LoggerService, ConfigService],
    global_=True  # Core services available everywhere
)
class CoreModule:
    pass

# src/my_project/users/module.py
from modi import module
from .services import UserService
from .repositories import UserRepository

@module(
    providers=[UserService, UserRepository],
    exports=[UserService]  # Only export the service, hide repository
)
class UserModule:
    pass

# src/my_project/app/module.py
from modi import module
from ..core.module import CoreModule
from ..users.module import UserModule
from ..orders.module import OrderModule

@module(
    imports=[CoreModule, UserModule, OrderModule]
)
class AppModule:
    pass
```

## Service Design Patterns

### 1. Single Responsibility Principle

Each service should have one clear responsibility:

```python
# Good: Single responsibility
@injectable()
class EmailService:
    def send_email(self, to: str, subject: str, body: str) -> bool:
        # Only handles email sending
        pass

@injectable()
class UserNotificationService:
    def __init__(self, email_service: EmailService):
        self.email_service = email_service

    def notify_user_created(self, user: dict) -> bool:
        # Only handles user notifications
        return self.email_service.send_email(
            user["email"],
            "Welcome!",
            "Welcome to our platform!"
        )

# Bad: Multiple responsibilities
@injectable()
class UserService:
    def create_user(self, user_data: dict) -> dict:
        # Creates user AND sends email AND logs AND updates cache
        user = self._save_to_database(user_data)
        self._send_welcome_email(user)
        self._log_user_creation(user)
        self._update_cache(user)
        return user
```

### 2. Dependency Inversion

Depend on abstractions, not concretions:

```python
from abc import ABC, abstractmethod

# Define abstractions
class IUserRepository(ABC):
    @abstractmethod
    def save_user(self, user: dict) -> dict: pass

    @abstractmethod
    def get_user(self, user_id: int) -> dict: pass

class IEmailService(ABC):
    @abstractmethod
    def send_email(self, to: str, subject: str, body: str) -> bool: pass

# Implement abstractions
@injectable()
class DatabaseUserRepository(IUserRepository):
    def __init__(self, db: DatabaseService):
        self.db = db

    def save_user(self, user: dict) -> dict:
        return self.db.save("users", user)

    def get_user(self, user_id: int) -> dict:
        return self.db.find("users", user_id)

@injectable()
class SMTPEmailService(IEmailService):
    def send_email(self, to: str, subject: str, body: str) -> bool:
        # SMTP implementation
        pass

# Depend on abstractions
@injectable()
class UserService:
    def __init__(
        self,
        repository: DatabaseUserRepository,  # Use concrete type for Modi DI
        email_service: SMTPEmailService     # Use concrete type for Modi DI
    ):
        self.repository = repository
        self.email_service = email_service

    def create_user(self, user_data: dict) -> dict:
        user = self.repository.save_user(user_data)
        self.email_service.send_email(user["email"], "Welcome!", "Welcome!")
        return user
```

### 3. Configuration Management

Centralize configuration with proper separation:

```python
# config/settings.py
@injectable()
class DatabaseConfig:
    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = int(os.getenv("DB_PORT", "5432"))
        self.database = os.getenv("DB_NAME", "myapp")
        self.username = os.getenv("DB_USER", "user")
        self.password = os.getenv("DB_PASS", "password")

    @property
    def url(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

@injectable()
class EmailConfig:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "localhost")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.username = os.getenv("SMTP_USER")
        self.password = os.getenv("SMTP_PASS")

@injectable()
class AppConfig:
    def __init__(self):
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.secret_key = os.getenv("SECRET_KEY")
        self.environment = os.getenv("ENVIRONMENT", "development")

# Usage in services
@injectable()
class DatabaseService:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.connection = self._create_connection()

    def _create_connection(self):
        return create_engine(self.config.url)
```

## Scope Management

### When to Use Singleton vs Transient

#### Singleton (Default) - Use for:

- **Stateless services**: Services that don't maintain state between calls
- **Shared resources**: Database connections, configuration, caches
- **Expensive-to-create objects**: Heavy initialization costs

```python
# Good singleton candidates
@injectable()  # Singleton by default
class DatabaseService:
    def __init__(self, config: DatabaseConfig):
        self.engine = create_engine(config.url)  # Expensive to create

@injectable()
class CacheService:
    def __init__(self):
        self.redis = Redis()  # Shared resource

@injectable()
class ConfigService:
    def __init__(self):
        self.config = load_config()  # Stateless
```

#### Transient - Use for:

- **Stateful processing**: Objects that maintain request-specific state
- **Short-lived operations**: Request handlers, temporary processors
- **Unique instances**: When each usage needs a fresh instance

```python
# Good transient candidates
@injectable(scope=Scope.TRANSIENT)
class RequestProcessor:
    def __init__(self):
        self.request_id = generate_id()
        self.processing_state = {}

@injectable(scope=Scope.TRANSIENT)
class ReportGenerator:
    def __init__(self, template_service: TemplateService):
        self.template_service = template_service
        self.temp_files = []

    def __del__(self):
        # Clean up temporary files
        for file in self.temp_files:
            os.remove(file)

@injectable(scope=Scope.TRANSIENT)
class DataImporter:
    def __init__(self):
        self.imported_records = []
        self.errors = []
```

## Error Handling Patterns

### Graceful Service Resolution

```python
@injectable()
class NotificationService:
    def __init__(
        self,
        email_service: EmailService,
        sms_service: Optional[SMSService] = None  # Optional dependency
    ):
        self.email_service = email_service
        self.sms_service = sms_service

    def send_notification(self, user: dict, message: str):
        # Always send email
        self.email_service.send_email(user["email"], "Notification", message)

        # Send SMS only if service is available
        if self.sms_service and user.get("phone"):
            try:
                self.sms_service.send_sms(user["phone"], message)
            except Exception as e:
                # Log error but don't fail the whole operation
                logger.error(f"SMS sending failed: {e}")

# Note: Modi doesn't yet support Optional[Type] injection,
# so you need to handle this at the application level:

@injectable()
class NotificationService:
    def __init__(self, email_service: EmailService):
        self.email_service = email_service
        self.sms_service = None  # Set externally if available

# In your application bootstrap:
app = AppFactory.create(AppModule)
notification_service = app.get(NotificationService)

try:
    sms_service = app.get(SMSService)
    notification_service.sms_service = sms_service
except ValueError:
    # SMS service not available, continue without it
    pass
```

### Circuit Breaker Pattern

```python
@injectable()
class ExternalAPIService:
    def __init__(self, config: AppConfig):
        self.config = config
        self.failure_count = 0
        self.last_failure = None
        self.circuit_open = False

    def call_external_api(self, data: dict) -> dict:
        if self._is_circuit_open():
            raise Exception("Circuit breaker is open")

        try:
            result = self._make_api_call(data)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _is_circuit_open(self) -> bool:
        if not self.circuit_open:
            return False

        # Reset circuit after timeout
        if time.time() - self.last_failure > 60:  # 1 minute timeout
            self.circuit_open = False
            self.failure_count = 0

        return self.circuit_open

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure = time.time()

        if self.failure_count >= 5:  # Open circuit after 5 failures
            self.circuit_open = True

    def _on_success(self):
        self.failure_count = 0
        self.circuit_open = False
```

## Testing Strategies

### Unit Testing Services

```python
# test_user_service.py
import pytest
from unittest.mock import Mock
from modi import AppFactory, injectable, module
from myapp.users.services import UserService
from myapp.users.repositories import UserRepository

# Create test doubles
@injectable()
class MockUserRepository:
    def __init__(self):
        self.users = {}
        self.next_id = 1

    def save_user(self, user_data: dict) -> dict:
        user = {**user_data, "id": self.next_id}
        self.users[self.next_id] = user
        self.next_id += 1
        return user

    def get_user(self, user_id: int) -> dict:
        return self.users.get(user_id)

@injectable()
class MockEmailService:
    def __init__(self):
        self.sent_emails = []

    def send_email(self, to: str, subject: str, body: str) -> bool:
        self.sent_emails.append({"to": to, "subject": subject, "body": body})
        return True

# Test module
@module(providers=[MockUserRepository, MockEmailService, UserService])
class TestUserModule:
    pass

# Tests
@pytest.fixture
def app():
    return AppFactory.create(TestUserModule)

def test_user_creation(app):
    user_service = app.get(UserService)

    user_data = {"name": "John Doe", "email": "john@example.com"}
    user = user_service.create_user(user_data)

    assert user["id"] is not None
    assert user["name"] == "John Doe"
    assert user["email"] == "john@example.com"

def test_welcome_email_sent(app):
    user_service = app.get(UserService)
    email_service = app.get(MockEmailService)

    user_data = {"name": "John Doe", "email": "john@example.com"}
    user_service.create_user(user_data)

    assert len(email_service.sent_emails) == 1
    assert email_service.sent_emails[0]["to"] == "john@example.com"
    assert "Welcome" in email_service.sent_emails[0]["subject"]
```

### Integration Testing

```python
# test_integration.py
import pytest
from modi import AppFactory
from myapp.app.module import AppModule

@pytest.fixture
def app():
    return AppFactory.create(AppModule)

def test_full_user_flow(app):
    user_service = app.get(UserService)

    # Create user
    user = user_service.create_user({
        "name": "Integration Test User",
        "email": "integration@example.com"
    })

    # Verify user exists
    retrieved_user = user_service.get_user(user["id"])
    assert retrieved_user is not None
    assert retrieved_user["email"] == "integration@example.com"

def test_service_dependencies(app):
    # Test that all dependencies are properly injected
    user_service = app.get(UserService)

    assert user_service.repository is not None
    assert user_service.email_service is not None
    assert hasattr(user_service.repository, 'db')
```

### Test Configuration

```python
# test_config.py
@injectable()
class TestDatabaseConfig:
    def __init__(self):
        self.host = "localhost"
        self.port = 5432
        self.database = "test_db"
        self.username = "test_user"
        self.password = "test_pass"

    @property
    def url(self) -> str:
        return f"sqlite:///:memory:"  # Use in-memory database for tests

@injectable()
class TestEmailConfig:
    def __init__(self):
        self.smtp_host = "localhost"
        self.smtp_port = 1025  # Test SMTP server
        self.username = None
        self.password = None

@module(
    providers=[TestDatabaseConfig, TestEmailConfig],
    exports=[TestDatabaseConfig, TestEmailConfig],
    global_=True
)
class TestConfigModule:
    pass
```

## Performance Optimization

### Lazy Loading

```python
@injectable()
class HeavyService:
    def __init__(self):
        self._expensive_resource = None

    @property
    def expensive_resource(self):
        if self._expensive_resource is None:
            self._expensive_resource = self._create_expensive_resource()
        return self._expensive_resource

    def _create_expensive_resource(self):
        # Expensive initialization
        return SomeExpensiveResource()

@injectable()
class UserService:
    def __init__(self, heavy_service: HeavyService):
        self.heavy_service = heavy_service

    def get_users(self):
        # Expensive resource only created when actually used
        return self.heavy_service.expensive_resource.get_data()
```

### Connection Pooling

```python
@injectable()
class DatabaseService:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._pool = None

    @property
    def pool(self):
        if self._pool is None:
            self._pool = create_engine(
                self.config.url,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True
            )
        return self._pool

    def get_connection(self):
        return self.pool.connect()

@injectable()
class UserRepository:
    def __init__(self, db: DatabaseService):
        self.db = db

    def get_user(self, user_id: int):
        with self.db.get_connection() as conn:
            result = conn.execute("SELECT * FROM users WHERE id = %s", user_id)
            return result.fetchone()
```

## Security Considerations

### Secure Configuration

```python
@injectable()
class SecureConfigService:
    def __init__(self):
        self._secrets = {}
        self._load_secrets()

    def _load_secrets(self):
        # Load from secure storage (vault, environment, etc.)
        self._secrets["api_key"] = os.getenv("API_KEY")
        self._secrets["database_password"] = os.getenv("DB_PASSWORD")

    def get_secret(self, key: str) -> str:
        if key not in self._secrets:
            raise ValueError(f"Secret {key} not found")
        return self._secrets[key]

    def get_public_config(self) -> dict:
        # Return only non-sensitive configuration
        return {
            "app_name": "MyApp",
            "version": "1.0.0",
            "environment": os.getenv("ENVIRONMENT", "development")
        }
```

### Input Validation

```python
from typing import Dict, Any
import re

@injectable()
class ValidationService:
    def validate_email(self, email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def validate_user_data(self, data: Dict[str, Any]) -> Dict[str, str]:
        errors = {}

        if not data.get("name"):
            errors["name"] = "Name is required"
        elif len(data["name"]) < 2:
            errors["name"] = "Name must be at least 2 characters"

        if not data.get("email"):
            errors["email"] = "Email is required"
        elif not self.validate_email(data["email"]):
            errors["email"] = "Invalid email format"

        return errors

@injectable()
class UserService:
    def __init__(self, repository: UserRepository, validator: ValidationService):
        self.repository = repository
        self.validator = validator

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        # Validate input
        errors = self.validator.validate_user_data(user_data)
        if errors:
            raise ValueError(f"Validation errors: {errors}")

        # Sanitize input
        sanitized_data = {
            "name": user_data["name"].strip(),
            "email": user_data["email"].lower().strip()
        }

        return self.repository.save_user(sanitized_data)
```

## Logging and Monitoring

### Structured Logging

```python
import logging
import json
from datetime import datetime

@injectable()
class StructuredLogger:
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._setup_logger()

    def _setup_logger(self):
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def info(self, message: str, **kwargs):
        self._log("INFO", message, **kwargs)

    def error(self, message: str, **kwargs):
        self._log("ERROR", message, **kwargs)

    def _log(self, level: str, message: str, **kwargs):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "environment": self.config.environment,
            **kwargs
        }
        self.logger.info(json.dumps(log_entry))

@injectable()
class UserService:
    def __init__(self, repository: UserRepository, logger: StructuredLogger):
        self.repository = repository
        self.logger = logger

    def create_user(self, user_data: dict) -> dict:
        self.logger.info(
            "Creating user",
            operation="user_creation",
            user_email=user_data.get("email")
        )

        try:
            user = self.repository.save_user(user_data)
            self.logger.info(
                "User created successfully",
                operation="user_creation",
                user_id=user["id"],
                user_email=user["email"]
            )
            return user
        except Exception as e:
            self.logger.error(
                "Failed to create user",
                operation="user_creation",
                error=str(e),
                user_email=user_data.get("email")
            )
            raise
```

## Documentation

### Service Documentation

```python
@injectable()
class UserService:
    """Service for managing user operations.

    This service handles user creation, retrieval, and updates.
    It coordinates between the repository layer and external services
    like email notifications.

    Dependencies:
        repository: UserRepository for data persistence
        email_service: EmailService for sending notifications
        validator: ValidationService for input validation
    """

    def __init__(
        self,
        repository: UserRepository,
        email_service: EmailService,
        validator: ValidationService
    ):
        self.repository = repository
        self.email_service = email_service
        self.validator = validator

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user with validation and email notification.

        Args:
            user_data: Dictionary containing user information.
                      Must include 'name' and 'email' fields.

        Returns:
            Dictionary containing the created user with assigned ID.

        Raises:
            ValueError: If validation fails or required fields are missing.
            EmailError: If welcome email cannot be sent.

        Example:
            user = user_service.create_user({
                "name": "John Doe",
                "email": "john@example.com"
            })
        """
        # Implementation...
```

These best practices will help you build maintainable, testable, and scalable applications with Modi. Remember to adapt these patterns to your specific use case and requirements.
