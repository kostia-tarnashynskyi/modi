from typing import Type, Dict, Any, get_type_hints, Optional, Set
import inspect
from .decorators import Scope

class ModuleContainer:
    """Central DI container, similar to NestJS ModuleContainer.
    
    This class manages the registration and resolution of modules and providers,
    handles dependency injection, and maintains the application's dependency graph.
    """
    
    def __init__(self):
        self._providers: Dict[Type, Any] = {}
        self._singletons: Dict[Type, Any] = {}
        self._provider_configs: Dict[Type, dict] = {}
        self._modules: Dict[Type, Any] = {}
        self._global_exports: Set[Type] = set()
        self._resolving_stack: Set[Type] = set()  # Protection against circular dependencies

    def register_module(self, module_cls: Type):
        """Register a module and all its providers.
        
        Args:
            module_cls: The module class to register
            
        Raises:
            ValueError: If the class is not a valid module
        """
        if not hasattr(module_cls, '_is_module'):
            raise ValueError(f"{module_cls.__name__} is not a module")
        
        # Store the module instance
        self._modules[module_cls] = module_cls()
        
        # Register module providers
        for provider in getattr(module_cls, '_providers', []):
            scope = getattr(provider, '_scope', Scope.SINGLETON)
            self._register_provider(provider, scope, module_cls)
            
            # If module is global, add to global exports
            if getattr(module_cls, '_is_global', False):
                self._global_exports.add(provider)

        # Recursively register imported modules
        for imported_module in getattr(module_cls, '_imports', []):
            self.register_module(imported_module)

    def _register_provider(self, cls: Type, scope: Scope, module_cls: Type):
        """Register a provider with its scope and module.
        
        Args:
            cls: The provider class
            scope: The scope of the provider
            module_cls: The module that owns this provider
        """
        self._provider_configs[cls] = {
            "scope": scope,
            "module": module_cls
        }

    def resolve(self, cls: Type, context_module: Optional[Type] = None) -> Any:
        """Resolve a dependency with automatic instance creation.
        
        Args:
            cls: The class type to resolve
            context_module: Optional module context for resolution
            
        Returns:
            Instance of the requested class with dependencies injected
            
        Raises:
            RuntimeError: If circular dependency is detected
            ValueError: If provider is not registered
        """
        
        # Protection against circular dependencies
        if cls in self._resolving_stack:
            class_name = cls.__name__ if hasattr(cls, '__name__') else str(cls)
            raise RuntimeError(f"Circular dependency detected: {class_name}")
        
        self._resolving_stack.add(cls)
        
        try:
            config = self._provider_configs.get(cls)
            if not config:
                class_name = cls.__name__ if hasattr(cls, '__name__') else str(cls)
                raise ValueError(f"Provider {class_name} not registered")
            
            scope = config.get("scope", Scope.SINGLETON)

            # For singleton, return existing instance
            if scope == Scope.SINGLETON and cls in self._singletons:
                return self._singletons[cls]

            # Create new instance
            instance = self._create_instance(cls)

            # Store singleton
            if scope == Scope.SINGLETON:
                self._singletons[cls] = instance

            return instance
            
        finally:
            self._resolving_stack.discard(cls)

    def _create_instance(self, cls: Type) -> Any:
        """Create an instance with automatic dependency injection.
        
        Args:
            cls: The class to instantiate
            
        Returns:
            New instance with all dependencies injected
        """
        # Get constructor
        constructor = cls.__init__
        sig = inspect.signature(constructor)
        
        # Collect constructor arguments
        kwargs = {}
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
                
            param_type = param.annotation
            if param_type != inspect.Parameter.empty:
                # Handle forward references (strings)
                if isinstance(param_type, str):
                    # Try to find the class in the registered providers
                    param_type = self._resolve_forward_reference(param_type)
                
                # Recursively resolve dependency
                kwargs[param_name] = self.resolve(param_type)

        return cls(**kwargs)
    
    def _resolve_forward_reference(self, ref_string: str):
        """Resolve forward reference string to actual class.
        
        Args:
            ref_string: String name of the class
            
        Returns:
            The resolved class type
            
        Raises:
            ValueError: If the forward reference cannot be resolved
        """
        # Remove quotes if present
        class_name = ref_string.strip("'\"")
        
        # Search in registered providers
        for cls in self._provider_configs.keys():
            if cls.__name__ == class_name:
                return cls
        
        raise ValueError(f"Cannot resolve forward reference: {class_name}")
