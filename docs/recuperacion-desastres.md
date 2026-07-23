# Recuperación ante desastres — republicación desde cero

**Esqueleto — se completará y validará tras el simulacro de recuperación.**

Objetivo: poder reconstruir toda la publicación (GeoServer + metadatos) partiendo solo
de este repositorio, sus Releases y las credenciales.

## Pasos

1. **Clonar el repositorio**

   ```bash
   git clone git@github.com:geografia-ucr/geoportal-publicacion.git
   cd geoportal-publicacion
   ```

2. **Crear el entorno**

   ```bash
   conda env create -f environment.yml
   conda activate geopub
   ```

3. **Credenciales**

   ```bash
   cp .env.example .env
   # completar GEOSERVER_PASSWORD (y GEONODE_TOKEN si aplica)
   ```

4. **Restaurar los datos desde Releases** (verifica las sumas SHA-256 de `checksums/`)

   ```bash
   geopub release descargar <nodo>      # por cada nodo
   ```

5. **Republicar en GeoServer**

   ```bash
   geopub verificar <nodo>
   geopub publicar <nodo> --dry-run
   geopub publicar <nodo>
   ```

6. **Metadatos**: los XML aprobados ya están en `metadatos/<nodo>/3-actual/`.
   Si el registro del SNIT sobrevivió, no hay nada que hacer; si se perdió, recargar
   los XML en la herramienta del SNIT (ver [`flujo-publicacion.md`](flujo-publicacion.md)
   paso 7 — incluye readjuntar las imágenes de `vistas-previas/`).

7. **GeoFence — paso MANUAL**: recrear la regla ALLOW de cada workspace en la interfaz
   de GeoServer (Security > GeoFence Data Rules; ver
   [`flujo-publicacion.md`](flujo-publicacion.md) paso 5). Sin esto, nada es público.

8. **Verificación**

   ```bash
   geopub estado
   ```

   Más GetCapabilities y conteos WFS (`resultType=hits`) por capa.

## Notas y limitaciones conocidas

- **Las 10 capas regionales Brunca de pastos NO están en Releases**: están
  deshabilitadas en GeoServer y sus datos fuente permanecen en el servidor y en
  `~/geografia-ucr/datos-fuente/`. Si hubiera que restaurarlas, tomar los shapefiles
  de ahí y publicarlos como featureTypes deshabilitados (`enabled: false`).
- Las capas deshabilitadas de café (`cobertura_arborea_2021/2022`) deben quedar
  igualmente con `enabled: false` tras la republicación.
- Pendiente tras el simulacro: tiempos medidos, orden óptimo de nodos, y cualquier
  paso manual no documentado que aparezca.
