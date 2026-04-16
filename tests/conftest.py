"""Shared fixtures for xfep-lookup tests."""

import textwrap
from pathlib import Path

import pytest

from xfep.lookup.base import LookupProvider
from xfep.lookup.errors import NotFoundError
from xfep.lookup.models import DniInfo, RucInfo


class MockProvider(LookupProvider):
    """In-memory mock provider for testing facades."""

    def __init__(self) -> None:
        self.ruc_data: dict[str, RucInfo] = {}
        self.dni_data: dict[str, DniInfo] = {}

    async def get_ruc(self, ruc: str) -> RucInfo:
        if ruc not in self.ruc_data:
            raise NotFoundError(f"RUC {ruc} not found")
        return self.ruc_data[ruc]

    async def get_dni(self, dni: str) -> DniInfo:
        if dni not in self.dni_data:
            raise NotFoundError(f"DNI {dni} not found")
        return self.dni_data[dni]


SAMPLE_RUC_INFO = RucInfo(
    ruc="20100017491",
    razon_social="SUNAT",
    estado="ACTIVO",
    condicion="HABIDO",
    direccion="AV. GARCILASO DE LA VEGA 1472",
    ubigeo="150101",
)

SAMPLE_DNI_INFO = DniInfo(
    dni="12345678",
    nombres="JUAN",
    apellido_paterno="PEREZ",
    apellido_materno="GARCIA",
)


@pytest.fixture
def mock_provider() -> MockProvider:
    """Return a MockProvider pre-loaded with sample data."""
    provider = MockProvider()
    provider.ruc_data["20100017491"] = SAMPLE_RUC_INFO
    provider.dni_data["12345678"] = SAMPLE_DNI_INFO
    return provider


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    """Create a small padrón reducido CSV fixture."""
    csv_content = textwrap.dedent("""\
        RUC|NOMBRE O RAZÓN SOCIAL|ESTADO DEL CONTRIBUYENTE|CONDICIÓN DE DOMICILIO|UBIGEO|DIRECCIÓN|TIPO CONTRIBUYENTE|DEPARTAMENTO|PROVINCIA|DISTRITO
        20100017491|SUNAT|ACTIVO|HABIDO|150101|AV. GARCILASO DE LA VEGA 1472|06|LIMA|LIMA|LIMA
        20123456789|EMPRESA TEST SAC|ACTIVO|HABIDO|150102|JR. EJEMPLO 123|02|LIMA|LIMA|ANCON
        20999999999|EMPRESA BAJA SRL|BAJA DE OFICIO|NO HABIDO|||01|LIMA|LIMA|LIMA
    """)
    csv_file = tmp_path / "padron_reducido.csv"
    csv_file.write_text(csv_content, encoding="utf-8")
    return csv_file
