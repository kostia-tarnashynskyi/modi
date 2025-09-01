"""
Example of using Modi DI with FastAPI in NestJS style
"""
import sys
from pathlib import Path

# Добавляем src в Python path для примера
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from fastapi import FastAPI
    from uvicorn import run
    FASTAPI_AVAILABLE = True
except ImportError:
    print("FastAPI and uvicorn not installed. Install with: pip install fastapi uvicorn")
    FASTAPI_AVAILABLE = False

from modi import injectable, module, AppFactory

# Services with automatic dependency injection
@injectable()
class DatabaseService:
    def get_connection(self):
        return "database_connection"

@injectable()
class UserService:
    def __init__(self, db: DatabaseService):
        self.db = db
    
    def get_users(self):
        conn = self.db.get_connection()
        return [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]

@injectable()
class UserController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service
    
    def get_all_users(self):
        return {"users": self.user_service.get_users()}

# Modules in NestJS style
@module(providers=[DatabaseService, UserService, UserController])
class UserModule:
    pass

@module(imports=[UserModule])
class AppModule:
    pass

def create_app():
    """Create and return the Modi and FastAPI applications"""
    # Create Modi application
    modi_app = AppFactory.create(AppModule)
    
    if not FASTAPI_AVAILABLE:
        # If FastAPI is not available, just test DI
        print("Testing Modi DI without FastAPI...")
        controller = modi_app.get(UserController)
        result = controller.get_all_users()
        print(f"Result: {result}")
        return None, modi_app
    
    # Create FastAPI application
    app = FastAPI(title="Modi DI Example", description="Example using Modi DI with FastAPI")
    
    @app.get("/", summary="Get all users")
    def root():
        controller = modi_app.get(UserController)
        return controller.get_all_users()

    @app.get("/users", summary="Get users via service")
    def get_users():
        user_service = modi_app.get(UserService)
        return {"users": user_service.get_users()}
    
    @app.get("/health", summary="Health check")
    def health():
        return {"status": "ok", "framework": "Modi DI"}
    
    return app, modi_app

if __name__ == "__main__":
    fastapi_app, modi_app = create_app()
    
    if fastapi_app and FASTAPI_AVAILABLE:
        print("Starting FastAPI server with Modi DI...")
        print("Visit: http://localhost:8000")
        print("API docs: http://localhost:8000/docs")
        run(fastapi_app, host="0.0.0.0", port=8000)
    else:
        print("✅ Modi DI working correctly!")
        print("Install FastAPI to run the web server: pip install fastapi uvicorn")
