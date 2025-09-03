from typing import Type
from .container import ModuleContainer

class ModiApplication:
    """Main application class, similar to NestJS NestFactory.
    
    This class bootstraps the Modi application by creating and configuring
    the dependency injection container with the provided root module.
    """
    
    def __init__(self, root_module: Type):
        self.container = ModuleContainer()
        self._root_module = root_module
        self._initialize()
    
    def _initialize(self):
        """Initialize the application and all modules."""
        self.container.register_module(self._root_module)
    
    def get(self, cls: Type):
        """Get an instance from the container.
        
        Args:
            cls: The class type to resolve
            
        Returns:
            Instance of the requested class
        """
        return self.container.resolve(cls)
    
    @classmethod
    def create(cls, root_module: Type) -> 'ModiApplication':
        """Factory method for creating an application, similar to NestFactory.create().
        
        Args:
            root_module: The root module class to bootstrap
            
        Returns:
            New ModiApplication instance
        """
        return cls(root_module)


class AppFactory:
    """Factory class for creating Modi applications, similar to NestJS NestFactory."""
    
    @classmethod
    def create(cls, root_module: Type) -> ModiApplication:
        """Create a new Modi application.
        
        Args:
            root_module: The root module class that defines the application structure
            
        Returns:
            A new ModiApplication instance
        """
        return ModiApplication.create(root_module)
