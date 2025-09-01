from typing import Type, List, Optional, Any
from enum import Enum

class Scope(Enum):
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    REQUEST = "request"

def injectable(scope: Scope = Scope.SINGLETON):
    """Mark a class as injectable provider, similar to NestJS @Injectable() decorator.
    
    Args:
        scope: The scope of the provider (SINGLETON, TRANSIENT, REQUEST)
        
    Returns:
        Class decorator that marks the class as injectable
    """
    def wrapper(cls):
        cls._injectable = True
        cls._scope = scope
        return cls
    return wrapper

def module(
    providers: Optional[List[Type]] = None, 
    imports: Optional[List[Type]] = None, 
    exports: Optional[List[Type]] = None,
    global_: bool = False
):
    """Create a module decorator, similar to NestJS @Module() decorator.
    
    Args:
        providers: List of providers to register in this module
        imports: List of modules to import into this module
        exports: List of providers to export from this module
        global_: Whether this module should be global (available everywhere)
        
    Returns:
        Class decorator that marks the class as a module
    """
    def wrapper(cls):
        cls._providers = providers or []
        cls._imports = imports or []
        cls._exports = exports or []
        cls._is_global = global_
        cls._is_module = True
        return cls
    return wrapper
