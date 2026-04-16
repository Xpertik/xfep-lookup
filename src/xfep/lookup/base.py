"""Abstract base class for lookup providers."""

from abc import ABC, abstractmethod

from xfep.lookup.models import DniInfo, RucInfo


class LookupProvider(ABC):
    """Strategy interface for RUC/DNI data sources."""

    @abstractmethod
    async def get_ruc(self, ruc: str) -> RucInfo:
        """Query RUC data. Raises NotFoundError if not found."""
        ...

    @abstractmethod
    async def get_dni(self, dni: str) -> DniInfo:
        """Query DNI data. Raises NotFoundError if not found."""
        ...
