"""
Advanced Modi DI example with modular architecture
"""
import sys
from pathlib import Path

# Добавляем src в Python path для примера
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modi import injectable, module, AppFactory, Scope

# === Database Layer ===
@injectable()
class DatabaseConnection:
    def __init__(self):
        self.connection_string = "sqlite:///app.db"
    
    def connect(self):
        return f"Connected to {self.connection_string}"

@injectable()
class UserRepository:
    def __init__(self, db: DatabaseConnection):
        self.db = db
    
    def find_all(self):
        conn = self.db.connect()
        return [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"}
        ]
    
    def find_by_id(self, user_id: int):
        users = self.find_all()
        return next((u for u in users if u["id"] == user_id), None)

@module(
    providers=[DatabaseConnection, UserRepository],
    exports=[UserRepository]  # Экспортируем для использования в других модулях
)
class DatabaseModule:
    pass

# === Logging Layer ===
@injectable()
class Logger:
    def info(self, message: str):
        print(f"[INFO] {message}")
    
    def error(self, message: str):
        print(f"[ERROR] {message}")

@module(
    providers=[Logger],
    exports=[Logger],
    global_=True  # Global module - available everywhere
)
class LoggerModule:
    pass

# === Business Logic Layer ===
@injectable()
class UserService:
    def __init__(self, user_repo: UserRepository, logger: Logger):
        self.user_repo = user_repo
        self.logger = logger
    
    def get_all_users(self):
        self.logger.info("Fetching all users")
        users = self.user_repo.find_all()
        self.logger.info(f"Found {len(users)} users")
        return users
    
    def get_user(self, user_id: int):
        self.logger.info(f"Fetching user with ID: {user_id}")
        user = self.user_repo.find_by_id(user_id)
        if user:
            self.logger.info(f"User found: {user['name']}")
        else:
            self.logger.error(f"User with ID {user_id} not found")
        return user

@injectable()
class EmailService:
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def send_email(self, to: str, subject: str, body: str):
        self.logger.info(f"Sending email to {to}: {subject}")
        return f"Email sent to {to}"

@injectable(scope=Scope.TRANSIENT)
class NotificationBuilder:
    """Transient service - new instance every time"""
    def __init__(self):
        self.message = ""
        self.recipients = []
    
    def add_message(self, message: str):
        self.message = message
        return self
    
    def add_recipient(self, email: str):
        self.recipients.append(email)
        return self
    
    def build(self):
        return {
            "message": self.message,
            "recipients": self.recipients,
            "id": id(self)  # Show that this is a new instance
        }

@injectable()
class UserController:
    def __init__(self, user_service: UserService, email_service: EmailService):
        self.user_service = user_service
        self.email_service = email_service
    
    def list_users(self):
        return {"users": self.user_service.get_all_users()}
    
    def get_user_profile(self, user_id: int):
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
            body=f"Hello {user['name']}, welcome to our app!"
        )
        return {"result": result}

@module(
    providers=[UserService, EmailService, NotificationBuilder, UserController],
    imports=[DatabaseModule]  # Import DatabaseModule
)
class UserModule:
    pass

# === Application Module ===
@module(
    imports=[LoggerModule, UserModule]  # LoggerModule is global, so available automatically
)
class AppModule:
    pass

def demo_basic_functionality():
    """Demo basic functionality"""
    print("=== Demo: Basic Functionality ===")
    
    app = AppFactory.create(AppModule)
    controller = app.get(UserController)
    
    # User list
    users = controller.list_users()
    print(f"All users: {users}")
    
    # User profile
    profile = controller.get_user_profile(1)
    print(f"User profile: {profile}")
    
    # Send email
    email_result = controller.send_welcome_email(1)
    print(f"Email result: {email_result}")

def demo_scopes():
    """Demo scope functionality"""
    print("\n=== Demo: Scopes (Singleton vs Transient) ===")
    
    app = AppFactory.create(AppModule)
    
    # Singleton - one instance
    service1 = app.get(UserService)
    service2 = app.get(UserService)
    print(f"Singleton UserService - Same instance: {service1 is service2}")
    
    # Transient - new instance each time
    builder1 = app.get(NotificationBuilder)
    builder2 = app.get(NotificationBuilder)
    
    notification1 = builder1.add_message("Hello").add_recipient("user1@example.com").build()
    notification2 = builder2.add_message("World").add_recipient("user2@example.com").build()
    
    print(f"Transient Builder - Different instances: {builder1 is not builder2}")
    print(f"Notification 1: {notification1}")
    print(f"Notification 2: {notification2}")

def demo_global_modules():
    """Demo global modules functionality"""
    print("\n=== Demo: Global Modules ===")
    
    app = AppFactory.create(AppModule)
    
    # Logger is available everywhere thanks to is_global=True
    user_service = app.get(UserService)
    email_service = app.get(EmailService)
    logger = app.get(Logger)
    
    print(f"Logger in UserService: {user_service.logger is logger}")
    print(f"Logger in EmailService: {email_service.logger is logger}")
    print("Global modules work - same logger instance everywhere!")

def main():
    """Run all demos"""
    print("🚀 Modi DI - Advanced Example")
    print("=" * 50)
    
    try:
        demo_basic_functionality()
        demo_scopes()
        demo_global_modules()
        
        print("\n" + "=" * 50)
        print("🎉 Advanced demo completed successfully!")
        print("\nKey concepts demonstrated:")
        print("• Modular architecture with imports/exports")
        print("• Global modules (LoggerModule)")
        print("• Singleton vs Transient scopes")
        print("• Multi-layer dependency injection")
        print("• Automatic dependency resolution")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        raise

if __name__ == "__main__":
    main()
