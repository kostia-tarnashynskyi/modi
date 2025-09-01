"""
Example of Modi DI integration with popular frameworks
"""
import sys
from pathlib import Path

# Добавляем src в Python path для примера
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modi import injectable, module, AppFactory

# === Core Services ===
@injectable()
class ConfigService:
    def get(self, key: str, default=None):
        config = {
            "database_url": "postgresql://localhost/myapp",
            "redis_url": "redis://localhost:6379",
            "jwt_secret": "secret-key",
            "debug": True
        }
        return config.get(key, default)

@injectable()
class DatabaseService:
    def __init__(self, config: ConfigService):
        self.config = config
        self.url = config.get("database_url")
    
    def get_connection(self):
        return f"Connected to {self.url}"

@injectable()
class CacheService:
    def __init__(self, config: ConfigService):
        self.config = config
        self.url = config.get("redis_url")
    
    def get(self, key: str):
        return f"Cache value for {key}"
    
    def set(self, key: str, value: str):
        return f"Cached {key}={value}"

@injectable()
class UserService:
    def __init__(self, db: DatabaseService, cache: CacheService):
        self.db = db
        self.cache = cache
    
    def get_user(self, user_id: int):
        # Сначала проверяем кеш
        cached = self.cache.get(f"user:{user_id}")
        if cached:
            return {"id": user_id, "name": "John", "source": "cache"}
        
        # Если нет в кеше, получаем из БД
        conn = self.db.get_connection()
        user = {"id": user_id, "name": "John", "source": "database"}
        
        # Кешируем результат
        self.cache.set(f"user:{user_id}", str(user))
        
        return user

@module(
    providers=[ConfigService, DatabaseService, CacheService, UserService],
    exports=[UserService]
)
class CoreModule:
    pass

# === FastAPI Integration ===
def create_fastapi_app():
    """Create FastAPI application with Modi DI"""
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.responses import JSONResponse
    except ImportError:
        print("FastAPI not installed. Install with: pip install fastapi")
        return None, None
    
    # Create Modi application
    modi_app = AppFactory.create(CoreModule)
    
    # Create FastAPI application
    app = FastAPI(
        title="Modi DI + FastAPI",
        description="Example of integrating Modi DI with FastAPI",
        version="1.0.0"
    )
    
    @app.get("/users/{user_id}")
    async def get_user(user_id: int):
        """Get user by ID"""
        user_service = modi_app.get(UserService)
        user = user_service.get_user(user_id)
        return user
    
    @app.get("/health")
    async def health():
        """Health check endpoint"""
        return {"status": "healthy", "di_framework": "Modi"}
    
    @app.get("/config")
    async def get_config():
        """Get configuration"""
        config_service = modi_app.get(ConfigService)
        return {
            "database_url": config_service.get("database_url"),
            "debug": config_service.get("debug")
        }
    
    return app, modi_app

# === Flask Integration ===
def create_flask_app():
    """Create Flask application with Modi DI"""
    try:
        from flask import Flask, jsonify
    except ImportError:
        print("Flask not installed. Install with: pip install flask")
        return None, None
    
    # Create Modi application
    modi_app = AppFactory.create(CoreModule)
    
    # Create Flask application
    app = Flask(__name__)
    
    @app.route('/users/<int:user_id>')
    def get_user(user_id):
        """Get user by ID"""
        user_service = modi_app.get(UserService)
        user = user_service.get_user(user_id)
        return jsonify(user)
    
    @app.route('/health')
    def health():
        """Health check endpoint"""
        return jsonify({"status": "healthy", "di_framework": "Modi"})
    
    @app.route('/config')
    def get_config():
        """Get configuration"""
        config_service = modi_app.get(ConfigService)
        return jsonify({
            "database_url": config_service.get("database_url"),
            "debug": config_service.get("debug")
        })
    
    return app, modi_app

# === CLI Application ===
def create_cli_app():
    """Create CLI application with Modi DI"""
    class CLIApp:
        def __init__(self):
            self.modi_app = AppFactory.create(CoreModule)
        
        def run_user_command(self, user_id: int):
            """Command to get user"""
            user_service = self.modi_app.get(UserService)
            user = user_service.get_user(user_id)
            print(f"User: {user}")
        
        def run_config_command(self):
            """Command to show configuration"""
            config_service = self.modi_app.get(ConfigService)
            print("Configuration:")
            print(f"  Database URL: {config_service.get('database_url')}")
            print(f"  Redis URL: {config_service.get('redis_url')}")
            print(f"  Debug: {config_service.get('debug')}")
        
        def run_test_command(self):
            """Command to test services"""
            print("Testing services...")
            db_service = self.modi_app.get(DatabaseService)
            cache_service = self.modi_app.get(CacheService)
            
            print(f"Database: {db_service.get_connection()}")
            print(f"Cache test: {cache_service.set('test', 'value')}")
            print("✅ All services working!")
    
    return CLIApp()

def demo_integrations():
    """Demonstrate integrations"""
    print("🚀 Modi DI Framework Integrations")
    print("=" * 50)
    
    # CLI Demo
    print("\n=== CLI Application Demo ===")
    cli_app = create_cli_app()
    cli_app.run_config_command()
    cli_app.run_user_command(123)
    cli_app.run_test_command()
    
    # FastAPI Demo
    print("\n=== FastAPI Integration Demo ===")
    fastapi_app, modi_app = create_fastapi_app()
    if fastapi_app:
        print("✅ FastAPI app created successfully")
        print("Available endpoints:")
        print("  GET /users/{user_id}")
        print("  GET /health")
        print("  GET /config")
        print("Start with: uvicorn app:app --reload")
    else:
        print("❌ FastAPI not available")
    
    # Flask Demo
    print("\n=== Flask Integration Demo ===")
    flask_app, modi_app = create_flask_app()
    if flask_app:
        print("✅ Flask app created successfully")
        print("Available endpoints:")
        print("  GET /users/<user_id>")
        print("  GET /health")
        print("  GET /config")
        print("Start with: flask run")
    else:
        print("❌ Flask not available")
    
    print("\n" + "=" * 50)
    print("🎉 Integration demos completed!")

if __name__ == "__main__":
    demo_integrations()
