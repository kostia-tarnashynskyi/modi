import pytest
from modi import injectable, module, AppFactory, Scope


def test_injectable_decorator():
    """Test that @injectable decorator marks classes correctly."""
    
    @injectable()
    class TestService:
        def get_data(self):
            return "test"
    
    assert hasattr(TestService, '_injectable')
    assert TestService._injectable is True
    assert TestService._scope == Scope.SINGLETON


def test_injectable_with_scope():
    """Test @injectable decorator with custom scope."""
    
    @injectable(scope=Scope.TRANSIENT)
    class TestService:
        pass
    
    assert TestService._scope == Scope.TRANSIENT


def test_module_decorator():
    """Test that @module decorator sets metadata correctly."""
    
    @injectable()
    class ServiceA:
        pass
    
    @injectable()
    class ServiceB:
        pass
    
    @module(providers=[ServiceA], exports=[ServiceA])
    class TestModule:
        pass
    
    assert hasattr(TestModule, '_is_module')
    assert TestModule._is_module is True
    assert TestModule._providers == [ServiceA]
    assert TestModule._exports == [ServiceA]
    assert TestModule._imports == []
    assert TestModule._is_global is False


def test_dependency_injection():
    """Test basic dependency injection."""
    
    @injectable()
    class DatabaseService:
        def get_connection(self):
            return "db_connection"
    
    @injectable()
    class UserService:
        def __init__(self, db: DatabaseService):
            self.db = db
        
        def get_users(self):
            return f"users from {self.db.get_connection()}"
    
    @module(providers=[DatabaseService, UserService])
    class TestModule:
        pass
    
    app = AppFactory.create(TestModule)
    user_service = app.get(UserService)
    
    assert user_service.get_users() == "users from db_connection"
    assert isinstance(user_service.db, DatabaseService)


def test_singleton_scope():
    """Test that singleton scope returns same instance."""
    
    @injectable(scope=Scope.SINGLETON)
    class SingletonService:
        def __init__(self):
            self.value = id(self)
    
    @module(providers=[SingletonService])
    class TestModule:
        pass
    
    app = AppFactory.create(TestModule)
    
    service1 = app.get(SingletonService)
    service2 = app.get(SingletonService)
    
    assert service1 is service2
    assert service1.value == service2.value


def test_transient_scope():
    """Test that transient scope returns new instances."""
    
    @injectable(scope=Scope.TRANSIENT)
    class TransientService:
        def __init__(self):
            self.value = id(self)
    
    @module(providers=[TransientService])
    class TestModule:
        pass
    
    app = AppFactory.create(TestModule)
    
    service1 = app.get(TransientService)
    service2 = app.get(TransientService)
    
    assert service1 is not service2
    assert service1.value != service2.value


def test_module_imports():
    """Test module imports functionality."""
    
    @injectable()
    class SharedService:
        def get_data(self):
            return "shared"
    
    @injectable()
    class UserService:
        def __init__(self, shared: SharedService):
            self.shared = shared
    
    @module(providers=[SharedService], exports=[SharedService])
    class SharedModule:
        pass
    
    @module(imports=[SharedModule], providers=[UserService])
    class UserModule:
        pass
    
    app = AppFactory.create(UserModule)
    user_service = app.get(UserService)
    
    assert user_service.shared.get_data() == "shared"


def test_circular_dependency_detection():
    """Test that circular dependencies are detected."""
    
    @injectable()
    class ServiceA:
        def __init__(self, service_b: 'ServiceB'):
            self.service_b = service_b
    
    @injectable()
    class ServiceB:
        def __init__(self, service_a: ServiceA):
            self.service_a = service_a
    
    @module(providers=[ServiceA, ServiceB])
    class TestModule:
        pass
    
    app = AppFactory.create(TestModule)
    
    with pytest.raises(RuntimeError, match="Circular dependency detected"):
        app.get(ServiceA)


def test_provider_not_registered():
    """Test error when trying to resolve unregistered provider."""
    
    @injectable()
    class UnregisteredService:
        pass
    
    @module(providers=[])
    class EmptyModule:
        pass
    
    app = AppFactory.create(EmptyModule)
    
    with pytest.raises(ValueError, match="Provider UnregisteredService not registered"):
        app.get(UnregisteredService)
