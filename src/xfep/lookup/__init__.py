"""xfep-lookup — RUC/DNI lookup with pluggable providers."""

from xfep.lookup.base import LookupProvider
from xfep.lookup.dni import DniLookup
from xfep.lookup.errors import LookupError, NotFoundError, ProviderError
from xfep.lookup.models import DniInfo, RucInfo
from xfep.lookup.ruc import RucLookup

__all__ = [
    "DniInfo",
    "DniLookup",
    "LookupError",
    "LookupProvider",
    "NotFoundError",
    "ProviderError",
    "RucInfo",
    "RucLookup",
]
