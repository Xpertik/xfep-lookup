"""RucLookup facade — validates and delegates RUC queries."""

from xfep.lookup.base import LookupProvider
from xfep.lookup.models import RucInfo


class RucLookup:
    """Thin facade that validates RUC format and delegates to a provider."""

    def __init__(self, provider: LookupProvider) -> None:
        self._provider = provider

    async def get(self, ruc: str) -> RucInfo:
        """Look up a RUC. Raises ValueError if format is invalid."""
        if not ruc or len(ruc) != 11 or not ruc.isdigit():
            raise ValueError("RUC must be 11 digits")
        return await self._provider.get_ruc(ruc)
