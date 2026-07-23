# Guía de contribución

## Preparación del entorno

```bash
git clone https://github.com/geografia-ucr/geoportal-publicacion.git
cd geoportal-publicacion
conda env create -f environment.yml   # crea el entorno "geopub" (incluye GDAL/geopandas)
conda activate geopub                 # el paquete queda instalado en modo editable
cp .env.example .env                  # completar credenciales (NUNCA se versiona)
```

Los datos no vienen con el clon: `geopub release descargar <nodo>` los restaura en
`datos/<nodo>/` verificando los checksums de `checksums/`.

> Alternativa sin crear el entorno: cualquier Python con GDAL sirve para los módulos
> geoespaciales usando `PYTHONPATH=src` (python-dotenv es opcional).

## Flujo de trabajo

1. Crear una rama desde `main` con el prefijo según el tipo de cambio:
   `feat/…`, `fix/…`, `docs/…`, `datos/…`, `metadatos/…`
   (ej. `metadatos/pastos-correcciones-snit`).
2. Commits estilo *Conventional Commits*: tipo en inglés, descripción en español —
   `feat: agrega capa de piña 2023`, `fix: corrige bbox de cobertura_pastos_cr_2021`.
3. Abrir un *pull request* hacia `main` (plantilla incluida). `main` está protegida:
   la CI debe pasar antes del *merge*.
4. La CI ejecuta: `ruff` + `pytest`, validación de `config/nodos/*.yml` contra
   `config/esquema-nodo.json`, XML de metadatos bien formados, formato de
   `checksums/*` y detección de secretos (gitleaks).

## Pruebas locales

```bash
pytest -q            # 39+ pruebas, sin red y sin GDAL
ruff check src/ tests/
geopub estado        # comparación con los servicios vivos (requiere red)
```

## Reglas importantes

- **Nunca** commitear credenciales ni archivos con datos sensibles. Las credenciales
  van en `.env` (git-ignored); la CI bloquea secretos con gitleaks.
- **Nunca** commitear datos geoespaciales grandes: `datos/` está git-ignored y los
  datos se distribuyen como assets de Releases (`geopub release crear`).
- Todo cambio de títulos, abstracts, estado de metadatos o transformaciones se
  refleja en `config/nodos/<nodo>.yml` — el YAML es la fuente de verdad declarativa.
- Toda capa publicada debe estar en EPSG:8908 (`geopub verificar`; ver `docs/crs.md`).
- Para agregar una capa o nodo nuevo, seguir `docs/flujo-publicacion.md` paso a paso.
