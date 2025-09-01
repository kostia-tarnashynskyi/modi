"""
Simple example of testing Modi DI
"""
import sys
from pathlib import Path

# Добавляем src в Python path для примера
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modi import injectable, module, AppFactory, Scope

@injectable()
class LoggerService:
    def log(self, message: str):
        print(f"[LOG] {message}")
        return f"Logged: {message}"

@injectable()
class ConfigService:
    def get_config(self, key: str):
        configs = {
            "database_url": "sqlite:///example.db",
            "log_level": "INFO",
            "debug": True
        }
        return configs.get(key, "Not found")

@injectable()
class NotificationService:
    def __init__(self, logger: LoggerService, config: ConfigService):
        self.logger = logger
        self.config = config
    
    def send_notification(self, message: str):
        log_level = self.config.get_config("log_level")
        log_msg = f"[{log_level}] Sending notification: {message}"
        self.logger.log(log_msg)
        return f"Notification sent: {message}"

@injectable(scope=Scope.TRANSIENT)
class TransientService:
    def __init__(self):
        self.id = id(self)
    
    def get_id(self):
        return self.id

@module(providers=[LoggerService, ConfigService, NotificationService, TransientService])
class NotificationModule:
    pass

def test_basic_di():
    """Test basic DI functionality"""
    print("=== Testing Basic DI ===")
    
    app = AppFactory.create(NotificationModule)
    
    # Get service from container
    notification_service = app.get(NotificationService)
    
    # Test functionality
    result = notification_service.send_notification("Hello World!")
    print(f"Result: {result}")
    
    # Check that dependencies were injected
    assert notification_service.logger is not None
    assert notification_service.config is not None
    
    print("✅ Basic DI working correctly!")

def test_singleton_vs_transient():
    """Test singleton vs transient scopes"""
    print("\n=== Testing Scopes ===")
    
    app = AppFactory.create(NotificationModule)
    
    # Test Singleton (default)
    logger1 = app.get(LoggerService)
    logger2 = app.get(LoggerService)
    
    print(f"Singleton - Logger1 ID: {id(logger1)}")
    print(f"Singleton - Logger2 ID: {id(logger2)}")
    assert logger1 is logger2, "Singleton services should be the same instance"
    print("✅ Singleton scope working correctly!")
    
    # Test Transient
    transient1 = app.get(TransientService)
    transient2 = app.get(TransientService)
    
    print(f"Transient - Service1 ID: {transient1.get_id()}")
    print(f"Transient - Service2 ID: {transient2.get_id()}")
    assert transient1 is not transient2, "Transient services should be different instances"
    print("✅ Transient scope working correctly!")

def test_config_injection():
    """Test configuration injection"""
    print("\n=== Testing Config Injection ===")
    
    app = AppFactory.create(NotificationModule)
    config = app.get(ConfigService)
    
    db_url = config.get_config("database_url")
    debug = config.get_config("debug")
    
    print(f"Database URL: {db_url}")
    print(f"Debug mode: {debug}")
    
    assert db_url == "sqlite:///example.db"
    assert debug is True
    
    print("✅ Config injection working correctly!")

def main():
    """Run all tests"""
    print("🚀 Testing Modi Dependency Injection Framework")
    print("=" * 50)
    
    try:
        test_basic_di()
        test_singleton_vs_transient()
        test_config_injection()
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed! Modi DI is working correctly!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    main()
