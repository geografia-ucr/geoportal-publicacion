# Documentación

Índice de la documentación del proyecto. Para la visión general del repositorio,
ver el [README principal](../README.md); para contribuir, [CONTRIBUTING.md](../CONTRIBUTING.md).

## Flujos de trabajo

| Documento | Contenido |
|---|---|
| [flujo-publicacion.md](flujo-publicacion.md) | **El documento central**: publicación de una capa/nodo de principio a fin con `geopub` (verificación de CRS, GeoServer, metadatos, SNIT), incluidos los pasos manuales (GeoFence, herramienta del SNIT) |
| [mantenimiento.md](mantenimiento.md) | Habilitar/deshabilitar capas, actualizar títulos y resúmenes, reemplazar datos de una capa, respaldos |
| [correcciones-snit.md](correcciones-snit.md) | Ciclo de revisión de metadatos del SNIT: observaciones, corrección en la herramienta en línea, verificación y promoción a `3-actual/`; trampas conocidas del export de GeoNetwork |
| [nodo-snit.md](nodo-snit.md) | Alta y gestión de un subnodo del SNIT: formularios, contactos institucionales |
| [recuperacion-desastres.md](recuperacion-desastres.md) | Republicación completa desde cero (clon + Releases + `geopub publicar`); simulacro validado el 2026-07-22 |

## Referencia técnica

| Documento | Contenido |
|---|---|
| [crs.md](crs.md) | Requisito CR-SIRGAS/CRTM05 (EPSG:8908), transformación desde CR05 (EPSG:5367), diferencias con CR-SIRGAS UTM 16N |
| [geonode.md](geonode.md) | Integración con GeoNode: estado, decisiones pendientes y diseño preparado |
| [pendientes.md](pendientes.md) | Estado del proyecto y tareas pendientes |

## Registro histórico

| Documento | Contenido |
|---|---|
| [historico/reorganizacion-2026-07.md](historico/reorganizacion-2026-07.md) | Registro de la reorganización del proyecto (2026-07-22): decisiones, mapeo viejo→nuevo, verificaciones |
| [historico/renombrado-metadatos.md](historico/renombrado-metadatos.md) | Tabla de correspondencia completa de los 98 archivos de metadatos migrados a la convención por slug |
| `historico/*.txt` | Recetarios de comandos ejecutados originalmente (2026-03 a 2026-07), sanitizados; sustituidos por el CLI `geopub` |
