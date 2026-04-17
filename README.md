# xfep-lookup

Cliente async para **consulta de RUC y DNI** con arquitectura de proveedores pluggables — Perú.

Parte del [ecosistema XFEP](https://github.com/Xpertik). Permite consultar información tributaria (RUC → SUNAT) y de identidad (DNI → RENIEC) a través de múltiples proveedores intercambiables.

## Instalación

```bash
pip install xfep-lookup
```

## Uso

```python
import asyncio
from xfep.lookup import RucLookup, DniLookup
from xfep.lookup.providers import ApisNet

async def main():
    provider = ApisNet(token="tu_token")

    # Consulta RUC
    ruc = RucLookup(provider=provider)
    info = await ruc.get("20123456789")
    print(info.razon_social, info.estado, info.condicion)

    # Consulta DNI
    dni = DniLookup(provider=provider)
    persona = await dni.get("12345678")
    print(persona.nombres, persona.apellido_paterno)

asyncio.run(main())
```

## Proveedores built-in

| Provider | Endpoint | Notas |
|----------|----------|-------|
| `ApisNet` | apis.net.pe | Token requerido |
| `ApiInti` | apiperu.dev | Token requerido |
| `PadronSunat` | CSV local | Consulta offline del padrón descargado |

## Características

- **Arquitectura pluggable** — Cambiá el proveedor sin cambiar el código cliente.
- **Proveedores built-in** — Soporte para APIs.net.pe, SUNAT directa, RENIEC directa (según proveedor).
- **Excepciones tipadas** — `NotFoundError`, `ProviderError`, `LookupError`.
- **100% async/await** — Construido sobre `httpx.AsyncClient`.
- **Context manager** — Gestión automática del ciclo de vida del cliente HTTP.

## API

### `RucLookup(provider)`

```python
from xfep.lookup import RucLookup
from xfep.lookup.providers import ApisNet

lookup = RucLookup(provider=ApisNet(token="..."))
info: RucInfo = await lookup.get("20123456789")
```

Retorna `RucInfo` con: `ruc`, `razon_social`, `nombre_comercial`, `estado`, `condicion`, `direccion`, `ubigeo`, etc.

### `DniLookup(provider)`

```python
from xfep.lookup import DniLookup
from xfep.lookup.providers import ApisNet

lookup = DniLookup(provider=ApisNet(token="..."))
info: DniInfo = await lookup.get("12345678")
```

Retorna `DniInfo` con: `dni`, `nombres`, `apellido_paterno`, `apellido_materno`, `nombre_completo`.

### Implementar un proveedor custom

```python
from xfep.lookup import LookupProvider, RucInfo

class MiProveedor(LookupProvider):
    async def query_ruc(self, ruc: str) -> RucInfo:
        # ... tu lógica
        pass
```

### Excepciones

- `NotFoundError` — Documento no existe en el registro.
- `ProviderError` — Error del proveedor externo (5xx, timeout, etc.).
- `LookupError` — Excepción base.

## Stack

- **Python** >= 3.13
- **httpx** >= 0.27
- **Build**: Hatchling
- **Tests**: pytest + pytest-asyncio

## Desarrollo

```bash
git clone https://github.com/Xpertik/xfep-lookup.git
cd xfep-lookup

python3.13 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

pytest -v
```

## Licencia

Apache License 2.0 — ver [LICENSE](LICENSE).
