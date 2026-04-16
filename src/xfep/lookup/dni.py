"""DniLookup facade — validates and delegates DNI queries."""

from xfep.lookup.base import LookupProvider
from xfep.lookup.models import DniInfo


class DniLookup:
    """Thin facade that validates DNI format and delegates to a provider."""

    def __init__(self, provider: LookupProvider) -> None:
        self._provider = provider

    async def get(self, dni: str) -> DniInfo:
        """Look up a DNI. Raises ValueError if format is invalid."""
        if not dni or len(dni) != 8 or not dni.isdigit():
            raise ValueError("DNI must be 8 digits")
        return await self._provider.get_dni(dni)
