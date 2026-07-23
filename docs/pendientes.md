# Estado del proyecto y pendientes

Actualizado: 2026-07-22.

## Estado

| Nodo | Capas | Activas | Metadatos SNIT | Datos en Releases |
|---|---|---|---|---|
| mocupp-musaceas | 3 | 3 | 3 aprobados | `mocupp-musaceas-v2026.07.22` |
| mocupp-cafe | 6 | 4 | 4 aprobados (las 2 deshabilitadas no aplican) | `mocupp-cafe-v2026.07.22` |
| mocupp-pastos | 15 | 5 (nacionales) | 10 Brunca + 5 nacionales **en revisión** | `mocupp-pastos-v2026.07.22` (5 nacionales) |

## Pendientes

1. **Aprobación del SNIT (pastos)** — las 10 capas Brunca (correcciones enviadas
   2026-07-02) y las 5 nacionales (subidas 2026-07-14) siguen en revisión. Al
   aprobarse: actualizar `metadatos.estado` a `publicado` en
   `config/nodos/mocupp-pastos.yml` y promover los XML de `2-revision-snit/` a
   `3-actual/` con `geopub metadatos promover`.
2. **Vistas previas nacionales de pastos en el SNIT** — las imágenes locales estaban
   duplicadas por pares (2021 = 2022) y se regeneraron el 2026-07-22; verificar si
   las adjuntadas en el editor del SNIT tienen el mismo defecto y reemplazarlas.
3. **Integración GeoNode** — ver [geonode.md](geonode.md): decidir el backend con el
   administrador de la instancia; luego implementar `src/geopub/geonode.py`.
4. **Datos de las 10 capas Brunca** — no están en Releases (capas deshabilitadas;
   los shapefiles viven en el servidor y en los insumos fuente locales). Si se
   reactivan, empaquetarlas con `geopub release crear`.
5. **Capas futuras del export viejo de GeoNetwork** — `CR_EG-UCR_ACANTILADOSMUERTOS_500KVE`
   (escala 1:500.000, posiblemente otro workspace) y `Cobertura_Arborea_Region_Brunca_2020`.
6. **MOCUPP Piña y Palma** — insumos disponibles en los datos fuente, sin publicar.
7. **Correo de organización en `pointOfContact` (4 capas de café)** — el correo a nivel
   de organización quedó con el del autor del metadato en vez del de INISEFOR-UNA;
   corregir en el directorio de contactos de GeoNetwork cuando se retomen esas capas.
8. **Mantenimiento de credenciales** — gestionado fuera de este repositorio (requiere
   coordinación del equipo).
