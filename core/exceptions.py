class IRYMError(Exception):
    """Base exception for IRYM SDK."""
    pass

class ServiceNotInitializedError(IRYMError):
    """Raised when a service is used before being properly initialized."""
    pass

class ConfigurationError(IRYMError):
    """Raised when there is a configuration issue."""
    pass
