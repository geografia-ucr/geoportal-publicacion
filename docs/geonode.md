# Integración con GeoNode — PENDIENTE

**Estado: la integración con GeoNode NO está implementada.** Este documento registra
las preguntas abiertas y el diseño ya preparado en el repo para cuando se decida.

## Contexto

El geoportal institucional (<https://geoportal.ucr.ac.cr/>) es una instancia de
GeoNode. Las capas de este repositorio hoy se publican directamente en el GeoServer
institucional (workspaces `mocupp_*`), no en GeoNode.

## Preguntas abiertas (decidir antes de implementar)

1. **¿Qué GeoServer usará la instancia GeoNode?**
   - **Opción A — el GeoServer institucional existente como backend**: las capas ya
     publicadas se registrarían en GeoNode con
     `python manage.py updatelayers -w <workspace>` (comando de gestión de GeoNode,
     ejecutado en el servidor).
   - **Opción B — GeoNode con su propio GeoServer**: habría que subir las capas vía la
     API REST v2 de GeoNode (`/api/v2/uploads`) o con el comando `importlayers`.
2. **¿Qué versión de GeoNode corre en el geoportal?** (condiciona la API disponible y
   los comandos de gestión).
3. **¿Cómo se emiten los tokens de la API?** (usuario de servicio, alcances, caducidad).

## Diseño ya preparado en el repo

- **`config/nodos/*.yml`**: cada nodo/capa declara sus destinos con el campo
  `destinos: {snit: true/false, geonode: true/false}` (ver
  `config/esquema-nodo.json`). Hoy `geonode` está en `false`.
- **`config/global.yml`**: bloque `geonode` con `url` y `habilitado: false`.
- **`src/geopub/geonode.py`**: módulo *stub* reservado para la implementación
  (registro/subida de capas según la opción que se elija).
- **`.env`**: variables `GEONODE_URL` y `GEONODE_TOKEN` ya previstas en
  `.env.example`.

Cuando se resuelvan las preguntas, la implementación debería encajar en el flujo como
un paso más de `geopub publicar` (o un subcomando propio) condicionado por
`destinos.geonode`.
