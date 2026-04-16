"""PadronSunat provider — reads SUNAT's padrón reducido CSV."""

import asyncio
import csv
from pathlib import Path

from xfep.lookup.base import LookupProvider
from xfep.lookup.errors import NotFoundError, ProviderError
from xfep.lookup.models import DniInfo, RucInfo


class PadronSunat(LookupProvider):
    """Reads from SUNAT's padrón reducido CSV file.

    Loads the entire CSV into a dict on first access for O(1) lookups.
    Only supports RUC lookups — DNI raises ProviderError.
    """

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._data: dict[str, dict[str, str]] = {}
        self._loaded = False

    def _load_sync(self) -> dict[str, dict[str, str]]:
        """Synchronous CSV loading — runs in executor via _load()."""
        data: dict[str, dict[str, str]] = {}
        with self._path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="|")
            for row in reader:
                ruc = row.get("RUC", "").strip()
                if ruc:
                    data[ruc] = {
                        "ruc": ruc,
                        "razon_social": row.get("NOMBRE O RAZÓN SOCIAL", "").strip(),
                        "estado": row.get("ESTADO DEL CONTRIBUYENTE", "").strip(),
                        "condicion": row.get("CONDICIÓN DE DOMICILIO", "").strip(),
                        "ubigeo": row.get("UBIGEO", "").strip() or None,
                        "direccion": row.get("DIRECCIÓN", "").strip() or None,
                        "tipo_contribuyente": row.get("TIPO CONTRIBUYENTE", "").strip() or None,
                        "departamento": row.get("DEPARTAMENTO", "").strip() or None,
                        "provincia": row.get("PROVINCIA", "").strip() or None,
                        "distrito": row.get("DISTRITO", "").strip() or None,
                    }
        return data

    async def _load(self) -> None:
        """Lazily load CSV data into memory (once)."""
        if not self._loaded:
            self._data = await asyncio.to_thread(self._load_sync)
            self._loaded = True

    async def get_ruc(self, ruc: str) -> RucInfo:
        """Look up a RUC in the padrón. Raises NotFoundError if absent."""
        await self._load()
        if ruc not in self._data:
            raise NotFoundError(f"RUC {ruc} not found in padrón")
        return RucInfo(**self._data[ruc])

    async def get_dni(self, dni: str) -> DniInfo:
        """PadronSunat does not support DNI lookup."""
        raise ProviderError("PadronSunat does not support DNI lookup")
