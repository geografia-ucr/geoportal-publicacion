# Registro de la reorganización del proyecto (2026-07-22)

Este documento registra la reorganización que dio origen a este repositorio, para
que las decisiones y el mapeo desde el espacio de trabajo anterior queden trazables.

## Antecedentes

Entre 2026-02 y 2026-07 la publicación se gestionó en el repositorio privado
`mfvargas/geoportal-publicacion` (directorio local `~/geoportal/publicacion`), que
creció orgánicamente: raíz plana con scripts sueltos, recetarios de comandos
copy-paste (con la credencial de GeoServer embebida), metadatos con nomenclatura
inconsistente, datos grandes parcialmente versionados y sin README. Ese repositorio
quedó **archivado** (privado, solo lectura) como registro histórico.

## Decisiones de diseño

| Tema | Decisión |
|---|---|
| Datos grandes | Assets de GitHub Releases (un zip por capa + `SHA256SUMS.txt`), tag `<nodo>-vAAAA.MM.DD`; checksums duplicados en `checksums/` para vincular repo↔release |
| Historial git | Repositorio nuevo con historia limpia (el historial viejo contenía credenciales y binarios; `.git` de 673 MB) |
| Credenciales | Solo en `.env` local (git-ignored) + plantilla `.env.example`; CI con gitleaks |
| Reproducibilidad | CLI `geopub` + configuración declarativa YAML por nodo (`config/nodos/`, validada con JSON Schema) |
| Organización | Repo público en `geografia-ucr` como muestra de transparencia institucional |
| Idioma | Español (README con resumen en inglés); commits Conventional con tipo en inglés |

## Mapeo viejo → nuevo (resumen)

| Origen (repo viejo) | Destino |
|---|---|
| `verificar_crs.py`, `generar_vista_previa_snit.py`, `generar_excel_metadatos.py` | `src/geopub/{crs,vista_previa,metadatos/excel}.py` |
| `generar_metadatos_pastos_nacionales.py` | motor → `src/geopub/metadatos/generar.py`; su diccionario de capas → `config/nodos/mocupp-pastos.yml` |
| Recetarios `publicar_*.txt`, `mantenimiento_*.txt`, `reemplazar_*.txt` | lógica → `src/geopub/geoserver.py` y `servidor.py`; texto sanitizado → `docs/historico/*.txt`; síntesis → `docs/flujo-publicacion.md` y `docs/mantenimiento.md` |
| `metadatos/<nodo>/{actual,borrador,nacionales,revision-snit,para-enviar}` | `metadatos/<nodo>/{1-borrador,2-revision-snit,3-actual,vistas-previas}` — 98 archivos renombrados por slug de capa; tabla completa en [renombrado-metadatos.md](renombrado-metadatos.md) |
| Shapefiles/GeoPackages finales | Releases `*-v2026.07.22` (14 capas con datos locales; las 10 Brunca de pastos solo existen en el servidor y en los insumos fuente) |
| Insumos y originales (`originales/`, exportaciones, fuentes) | Fuera del repo, en el directorio local de insumos (`datos-fuente/`) |
| Documentos personales/sensibles (credenciales, correos, minutas) | Fuera de todo repositorio (directorio local privado) |
| `formulario_snit_*.txt`, formularios DOCX de subnodos | `docs/nodo-snit.md` + copias en `docs/historico/` |
| `GUIA_CORRECCIONES_SNIT_PASTOS.md` | Generalizada en `docs/correcciones-snit.md` |
| Excel de metadatos generados | No se versionan (salida regenerable de `geopub metadatos excel`) |

## Verificaciones al cierre de la migración

- Sin secretos en árbol ni historial (grep de la credencial + gitleaks): limpio.
- 39 pruebas de `pytest` y `ruff` sin errores; CI verde en todos los commits.
- Las 14 capas con datos locales verificadas en EPSG:8908 (`geopub verificar`).
- `geopub estado` contra el GeoServer vivo: 100 % de coincidencia con los YAML
  (capas publicadas/deshabilitadas y metadatos).
- Simulacro de recuperación (clon limpio → `release descargar` → checksums →
  `publicar --dry-run`): superado — detalle en
  [../recuperacion-desastres.md](../recuperacion-desastres.md).
- Hallazgo corregido durante la migración: las 4 vistas previas nacionales de pastos
  estaban duplicadas por pares (2021 = 2022); se regeneraron desde los datos.

## Pendientes al cierre

Ver [../pendientes.md](../pendientes.md).
