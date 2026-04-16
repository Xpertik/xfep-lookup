"""ApisNet provider — httpx async client for apis.net.pe."""

import httpx

from xfep.lookup.base import LookupProvider
from xfep.lookup.errors import NotFoundError, ProviderError
from xfep.lookup.models import DniInfo, RucInfo


class ApisNet(LookupProvider):
    """REST provider using https://api.apis.net.pe/v2."""

    BASE_URL = "https://api.apis.net.pe/v2"

    def __init__(self, token: str) -> None:
        self._token = token
        self._http = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={"Authorization": f"Bearer {token}"},
        )

    async def get_ruc(self, ruc: str) -> RucInfo:
        """Query SUNAT RUC via ApisNet."""
        try:
            resp = await self._http.get(f"/sunat/ruc?numero={ruc}")
        except httpx.HTTPError as exc:
            raise ProviderError(f"ApisNet request failed: {exc}") from exc

        if resp.status_code == 404:
            raise NotFoundError(f"RUC {ruc} not found via ApisNet")
        if resp.status_code >= 400:
            raise ProviderError(f"ApisNet error {resp.status_code}: {resp.text}")

        data = resp.json()
        return RucInfo(
            ruc=data.get("numeroDocumento", ruc),
            razon_social=data.get("razonSocial", ""),
            estado=data.get("estado", ""),
            condicion=data.get("condicion", ""),
            direccion=data.get("direccion"),
            ubigeo=data.get("ubigeo"),
            tipo_contribuyente=data.get("tipoContribuyente"),
            departamento=data.get("departamento"),
            provincia=data.get("provincia"),
            distrito=data.get("distrito"),
        )

    async def get_dni(self, dni: str) -> DniInfo:
        """Query RENIEC DNI via ApisNet."""
        try:
            resp = await self._http.get(f"/reniec/dni?numero={dni}")
        except httpx.HTTPError as exc:
            raise ProviderError(f"ApisNet request failed: {exc}") from exc

        if resp.status_code == 404:
            raise NotFoundError(f"DNI {dni} not found via ApisNet")
        if resp.status_code >= 400:
            raise ProviderError(f"ApisNet error {resp.status_code}: {resp.text}")

        data = resp.json()
        return DniInfo(
            dni=data.get("numeroDocumento", dni),
            nombres=data.get("nombres", ""),
            apellido_paterno=data.get("apellidoPaterno", ""),
            apellido_materno=data.get("apellidoMaterno", ""),
        )

    async def close(self) -> None:
        """Close the underlying httpx client."""
        await self._http.aclose()
