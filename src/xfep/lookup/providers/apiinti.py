"""ApiInti provider — httpx async client for api.inti.pe."""

import httpx

from xfep.lookup.base import LookupProvider
from xfep.lookup.errors import NotFoundError, ProviderError
from xfep.lookup.models import DniInfo, RucInfo


class ApiInti(LookupProvider):
    """REST provider using https://api.inti.pe/v1."""

    BASE_URL = "https://api.inti.pe/v1"

    def __init__(self, token: str) -> None:
        self._token = token
        self._http = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={"Authorization": f"Bearer {token}"},
        )

    async def get_ruc(self, ruc: str) -> RucInfo:
        """Query SUNAT RUC via ApiInti."""
        try:
            resp = await self._http.get(f"/ruc/{ruc}")
        except httpx.HTTPError as exc:
            raise ProviderError(f"ApiInti request failed: {exc}") from exc

        if resp.status_code == 404:
            raise NotFoundError(f"RUC {ruc} not found via ApiInti")
        if resp.status_code >= 400:
            raise ProviderError(f"ApiInti error {resp.status_code}: {resp.text}")

        data = resp.json()
        return RucInfo(
            ruc=data.get("ruc", ruc),
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
        """Query RENIEC DNI via ApiInti."""
        try:
            resp = await self._http.get(f"/dni/{dni}")
        except httpx.HTTPError as exc:
            raise ProviderError(f"ApiInti request failed: {exc}") from exc

        if resp.status_code == 404:
            raise NotFoundError(f"DNI {dni} not found via ApiInti")
        if resp.status_code >= 400:
            raise ProviderError(f"ApiInti error {resp.status_code}: {resp.text}")

        data = resp.json()
        return DniInfo(
            dni=data.get("dni", dni),
            nombres=data.get("nombres", ""),
            apellido_paterno=data.get("apellidoPaterno", ""),
            apellido_materno=data.get("apellidoMaterno", ""),
        )

    async def close(self) -> None:
        """Close the underlying httpx client."""
        await self._http.aclose()
