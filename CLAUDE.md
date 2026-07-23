# Publicación de capas geoespaciales — EG-UCR

Publicación de capas de la Escuela de Geografía (UCR) en el SNIT y el geoportal
institucional (GeoServer/GeoNode). Ver `README.md` para la visión general y
`docs/flujo-publicacion.md` para el flujo completo.

## Reglas del repositorio

- **Credenciales**: SIEMPRE en `.env` (git-ignored, plantilla en `.env.example`).
  NUNCA en código, YAML, docs ni commits. La CI corre gitleaks.
- **CRS**: toda capa publicada debe estar en CR-SIRGAS / CRTM05 (**EPSG:8908**).
  Cuidado: CR05/CRTM05 es EPSG:5367 (transformar) y CR-SIRGAS UTM 16N no es CRTM05
  (ver `docs/crs.md`).
- **Datos**: `datos/` está git-ignored; se distribuyen como assets de GitHub Releases
  con checksums en `checksums/`. No commitear binarios grandes.
- **Configuración declarativa**: cada nodo/capa se describe en `config/nodos/<slug>.yml`
  (validado contra `config/esquema-nodo.json`). Cualquier cambio de títulos, abstracts,
  estado de metadatos o transformaciones se refleja AHÍ, no solo en el servidor.
- **Metadatos**: ciclo `1-borrador/` → `2-revision-snit/` (`-enviado`, `-observaciones`,
  `-corregido`) → `3-actual/` en `metadatos/<nodo>/`. Nombre de archivo = slug de la capa.
  Las correcciones del SNIT se hacen en su herramienta en línea, no editando el XML local
  (ver `docs/correcciones-snit.md`).
- **Flujo git**: PRs sobre `main` (protegida), ramas `feat/`, `fix/`, `docs/`, `datos/`,
  `metadatos/`; commits Conventional (`feat: agrega …`, tipo en inglés, descripción en
  español).

## Herramienta principal

CLI `geopub` (paquete en `src/geopub/`, entorno conda `geopub` de `environment.yml`):

```
geopub verificar <nodo>            # CRS y requisitos de archivos
geopub transformar <nodo>          # ogr2ogr declarado en el YAML
geopub publicar <nodo> --dry-run   # publicación GeoServer (ensayo primero SIEMPRE)
geopub mantener <nodo> <capa> ...  # habilitar/deshabilitar, abstracts, reset
geopub metadatos generar|validar|excel|promover <nodo>
geopub vista-previa <nodo>         # JPG estilo SNIT
geopub release crear|descargar <nodo>
geopub estado [<nodo>]             # YAML vs servicios vivos
```

## Pasos manuales (no automatizables)

- Regla ALLOW en **GeoFence** (UI: Security > GeoFence Data Rules) — sin ella la capa
  no es pública.
- Subir XML, adjuntar imagen de vista previa y enviar a revisión en la herramienta en
  línea del **SNIT** (GeoNetwork).

## Servidor

GeoServer 2.16.2 en Docker en geoportal.ucr.ac.cr; datos del volumen en
`/var/lib/docker/volumes/geoportal-gsdatadir/_data/` (host) = `/geoserver_data/data/`
(contenedor). SSH con contraseña (`-o PubkeyAuthentication=no`); usar `-t` para sudo.
Detalles no sensibles en `config/global.yml`; credenciales en `.env`.
