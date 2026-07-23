# Publicación de capas geoespaciales — Escuela de Geografía, UCR

Herramientas, datos, metadatos y documentación para la publicación de capas geoespaciales
de la [Escuela de Geografía de la Universidad de Costa Rica](https://geografia.fcs.ucr.ac.cr/)
en el [Sistema Nacional de Información Territorial (SNIT)](https://www.snitcr.go.cr/) y en el
geoportal institucional (<https://geoportal.ucr.ac.cr/>, GeoServer/GeoNode).

Este repositorio contiene todo lo necesario para **reproducir la publicación completa**
(por ejemplo, ante un cambio o pérdida del servidor): los datos finales de cada capa
(como *assets* de [Releases](../../releases) con sumas de verificación), sus metadatos
ISO 19115-3:2018, las transformaciones aplicadas y las herramientas de publicación.

## Contenido

| Directorio | Descripción |
|---|---|
| `src/geopub/` | Paquete Python con el CLI `geopub` (verificación de CRS, publicación en GeoServer, metadatos, vistas previas, releases de datos) |
| `config/nodos/` | Configuración declarativa YAML de cada nodo y sus capas (títulos, resúmenes, CRS, transformaciones, destinos SNIT/GeoNode, estado) |
| `metadatos/<nodo>/` | Metadatos por capa: `1-borrador/` → `2-revision-snit/` → `3-actual/` (aprobados), más `vistas-previas/` |
| `datos/` | Datos geoespaciales (no versionados en git: se restauran desde Releases con `geopub release descargar`) |
| `checksums/` | Sumas SHA-256 que vinculan el repo con los assets de Releases |
| `estilos/` | Simbología (SLD) por nodo |
| `docs/` | Flujos de trabajo documentados; `docs/historico/` conserva los comandos ejecutados originalmente |

## Nodos publicados

Capas del proyecto **MOCUPP** (Monitoreo de Cambio de Uso en Paisajes Productivos):

- **mocupp-musaceas** — cultivo de musáceas 2021/2022 y pérdida-ganancia
- **mocupp-cafe** — cultivo de café 2021/2022, pérdida-ganancia y pérdida de cobertura arbórea
- **mocupp-pastos** — cobertura de pastos y cobertura arbórea en paisajes de pastos (nacional 2021/2022 y región Brunca 2019-2022)

Servicios: WFS/WMS en `https://geoportal.ucr.ac.cr/geoserver/<workspace>/wfs|wms`.

## Uso rápido

```bash
# Entorno (conda, incluye GDAL/geopandas)
conda env create -f environment.yml
conda activate geopub

# Credenciales: copiar la plantilla y completar (NUNCA se versiona .env)
cp .env.example .env

# Flujos principales
geopub verificar mocupp-pastos          # CRS EPSG:8908 y requisitos de archivos
geopub publicar mocupp-pastos --dry-run # publicación en GeoServer (ensayo)
geopub metadatos validar mocupp-pastos  # validación de XML ISO 19115-3
geopub release descargar mocupp-pastos  # restaura datos/ desde Releases
geopub estado                           # compara configuración vs servicios vivos
```

El flujo completo (incluidos los pasos manuales en GeoFence y en la herramienta del SNIT)
está en [`docs/flujo-publicacion.md`](docs/flujo-publicacion.md); el índice de toda la
documentación, en [`docs/README.md`](docs/README.md).

## Requisito de CRS

Toda capa publicada debe estar en **CR-SIRGAS / CRTM05 (EPSG:8908)**.
Ver [`docs/crs.md`](docs/crs.md) para las transformaciones desde CR05 (EPSG:5367) y las
trampas conocidas (p. ej. CR-SIRGAS UTM 16N no es CRTM05).

## Contribuir

El trabajo se gestiona mediante *pull requests* sobre `main` (protegida), con ramas
`feat/…`, `fix/…`, `docs/…`, `datos/…`, `metadatos/…` y mensajes de commit tipo
*Conventional Commits* (`feat: agrega …`). La CI valida código (ruff, pytest),
configuración (JSON Schema), metadatos (XML) y ausencia de secretos (gitleaks).
Guía completa en [CONTRIBUTING.md](CONTRIBUTING.md); estado y tareas pendientes en
[`docs/pendientes.md`](docs/pendientes.md).

## Licencia

- **Código**: [MIT](LICENSE)
- **Datos y metadatos**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.es) —
  citar como se indica en [`CITATION.cff`](CITATION.cff)

---

## About (English)

Tools, data and ISO 19115-3 metadata for publishing geospatial layers of the School of
Geography, University of Costa Rica, to Costa Rica's National Territorial Information
System (SNIT) and the institutional geoportal (GeoServer/GeoNode). The repository is
self-sufficient for full republication: final datasets are distributed as checksummed
Release assets, layer configuration is declarative (YAML), and the `geopub` CLI
reproduces the whole publication workflow. Code is MIT-licensed; data and metadata are
CC BY 4.0.
