"""Tests for concrete providers: PadronSunat, ApisNet, ApiInti."""

import json

import httpx
import pytest

from xfep.lookup.errors import NotFoundError, ProviderError
from xfep.lookup.models import DniInfo, RucInfo
from xfep.lookup.providers.apisnet import ApisNet
from xfep.lookup.providers.apiinti import ApiInti
from xfep.lookup.providers.padron import PadronSunat


# ---------------------------------------------------------------------------
# PadronSunat
# ---------------------------------------------------------------------------


class TestPadronSunat:
    async def test_get_ruc_found(self, sample_csv):
        provider = PadronSunat(path=sample_csv)
        result = await provider.get_ruc("20100017491")
        assert isinstance(result, RucInfo)
        assert result.ruc == "20100017491"
        assert result.razon_social == "SUNAT"
        assert result.estado == "ACTIVO"
        assert result.condicion == "HABIDO"

    async def test_get_ruc_not_found(self, sample_csv):
        provider = PadronSunat(path=sample_csv)
        with pytest.raises(NotFoundError, match="not found in padrón"):
            await provider.get_ruc("00000000000")

    async def test_get_dni_raises_provider_error(self, sample_csv):
        provider = PadronSunat(path=sample_csv)
        with pytest.raises(ProviderError, match="does not support DNI"):
            await provider.get_dni("12345678")

    async def test_lazy_loading(self, sample_csv):
        provider = PadronSunat(path=sample_csv)
        assert provider._loaded is False
        await provider.get_ruc("20100017491")
        assert provider._loaded is True

    async def test_multiple_ruc_entries(self, sample_csv):
        provider = PadronSunat(path=sample_csv)
        r1 = await provider.get_ruc("20100017491")
        r2 = await provider.get_ruc("20123456789")
        assert r1.razon_social == "SUNAT"
        assert r2.razon_social == "EMPRESA TEST SAC"


# ---------------------------------------------------------------------------
# ApisNet (mocked via httpx MockTransport)
# ---------------------------------------------------------------------------


def _apisnet_transport(request: httpx.Request) -> httpx.Response:
    """Mock transport for ApisNet API."""
    url = str(request.url)

    if "/sunat/ruc" in url and "numero=20100017491" in url:
        return httpx.Response(200, json={
            "numeroDocumento": "20100017491",
            "razonSocial": "SUNAT",
            "estado": "ACTIVO",
            "condicion": "HABIDO",
            "direccion": "AV. GARCILASO DE LA VEGA 1472",
            "ubigeo": "150101",
        })

    if "/sunat/ruc" in url and "numero=99999999999" in url:
        return httpx.Response(404, json={"message": "not found"})

    if "/sunat/ruc" in url and "numero=50000000000" in url:
        return httpx.Response(500, text="Internal Server Error")

    if "/reniec/dni" in url and "numero=12345678" in url:
        return httpx.Response(200, json={
            "numeroDocumento": "12345678",
            "nombres": "JUAN",
            "apellidoPaterno": "PEREZ",
            "apellidoMaterno": "GARCIA",
        })

    if "/reniec/dni" in url and "numero=99999999" in url:
        return httpx.Response(404, json={"message": "not found"})

    return httpx.Response(400, text="Bad Request")


class TestApisNet:
    @pytest.fixture
    def provider(self) -> ApisNet:
        p = ApisNet(token="test-token")
        p._http = httpx.AsyncClient(
            transport=httpx.MockTransport(_apisnet_transport),
            base_url=ApisNet.BASE_URL,
            headers={"Authorization": "Bearer test-token"},
        )
        return p

    async def test_get_ruc_success(self, provider):
        result = await provider.get_ruc("20100017491")
        assert isinstance(result, RucInfo)
        assert result.ruc == "20100017491"
        assert result.razon_social == "SUNAT"

    async def test_get_ruc_not_found(self, provider):
        with pytest.raises(NotFoundError):
            await provider.get_ruc("99999999999")

    async def test_get_ruc_server_error(self, provider):
        with pytest.raises(ProviderError, match="ApisNet error 500"):
            await provider.get_ruc("50000000000")

    async def test_get_dni_success(self, provider):
        result = await provider.get_dni("12345678")
        assert isinstance(result, DniInfo)
        assert result.dni == "12345678"
        assert result.nombres == "JUAN"

    async def test_get_dni_not_found(self, provider):
        with pytest.raises(NotFoundError):
            await provider.get_dni("99999999")


# ---------------------------------------------------------------------------
# ApiInti (mocked via httpx MockTransport)
# ---------------------------------------------------------------------------


def _apiinti_transport(request: httpx.Request) -> httpx.Response:
    """Mock transport for ApiInti API."""
    path = request.url.path

    if path == "/v1/ruc/20100017491":
        return httpx.Response(200, json={
            "ruc": "20100017491",
            "razonSocial": "SUNAT",
            "estado": "ACTIVO",
            "condicion": "HABIDO",
            "direccion": "AV. GARCILASO DE LA VEGA 1472",
            "ubigeo": "150101",
        })

    if path == "/v1/ruc/99999999999":
        return httpx.Response(404, json={"message": "not found"})

    if path == "/v1/ruc/50000000000":
        return httpx.Response(500, text="Internal Server Error")

    if path == "/v1/dni/12345678":
        return httpx.Response(200, json={
            "dni": "12345678",
            "nombres": "JUAN",
            "apellidoPaterno": "PEREZ",
            "apellidoMaterno": "GARCIA",
        })

    if path == "/v1/dni/99999999":
        return httpx.Response(404, json={"message": "not found"})

    return httpx.Response(400, text="Bad Request")


class TestApiInti:
    @pytest.fixture
    def provider(self) -> ApiInti:
        p = ApiInti(token="test-token")
        p._http = httpx.AsyncClient(
            transport=httpx.MockTransport(_apiinti_transport),
            base_url=ApiInti.BASE_URL,
            headers={"Authorization": "Bearer test-token"},
        )
        return p

    async def test_get_ruc_success(self, provider):
        result = await provider.get_ruc("20100017491")
        assert isinstance(result, RucInfo)
        assert result.ruc == "20100017491"

    async def test_get_ruc_not_found(self, provider):
        with pytest.raises(NotFoundError):
            await provider.get_ruc("99999999999")

    async def test_get_ruc_server_error(self, provider):
        with pytest.raises(ProviderError, match="ApiInti error 500"):
            await provider.get_ruc("50000000000")

    async def test_get_dni_success(self, provider):
        result = await provider.get_dni("12345678")
        assert isinstance(result, DniInfo)
        assert result.dni == "12345678"

    async def test_get_dni_not_found(self, provider):
        with pytest.raises(NotFoundError):
            await provider.get_dni("99999999")
