"""Response models for RUC and DNI lookups."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RucInfo:
    """Immutable RUC (taxpayer) information."""

    ruc: str
    razon_social: str
    estado: str
    condicion: str
    direccion: str | None = None
    ubigeo: str | None = None
    tipo_contribuyente: str | None = None
    departamento: str | None = None
    provincia: str | None = None
    distrito: str | None = None


@dataclass(frozen=True)
class DniInfo:
    """Immutable DNI (citizen identity) information."""

    dni: str
    nombres: str
    apellido_paterno: str
    apellido_materno: str
