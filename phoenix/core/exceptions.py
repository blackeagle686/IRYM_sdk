class Phoenix AIError(Exception):
    """Base exception for Phoenix AI SDK."""
    pass

class ServiceNotInitializedError(Phoenix AIError):
    """Raised when a service is used before being properly initialized."""
    pass

class ConfigurationError(Phoenix AIError):
    """Raised when there is a configuration issue."""
    pass
