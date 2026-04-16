"""Error hierarchy for xfep-lookup."""


class LookupError(Exception):
    """Base error for all lookup operations."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class NotFoundError(LookupError):
    """Raised when a RUC or DNI is not found by the provider."""


class ProviderError(LookupError):
    """Raised when a provider encounters a network or server error."""
