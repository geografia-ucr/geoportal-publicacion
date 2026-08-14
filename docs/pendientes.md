# Estado del proyecto y pendientes

Actualizado: 2026-08-14.

## Estado

| Nodo | Capas | Activas | Metadatos SNIT | Datos en Releases |
|---|---|---|---|---|
| mocupp-musaceas | 3 | 3 | 3 aprobados | `mocupp-musaceas-v2026.07.22` |
| mocupp-cafe | 6 | 4 | 4 aprobados (las 2 deshabilitadas no aplican) | `mocupp-cafe-v2026.07.22` |
| mocupp-pastos | 15 | 5 (nacionales) | 10 Brunca + 5 nacionales **en revisión** | `mocupp-pastos-v2026.07.22` (5 nacionales) |
| eg | 2 | 2 | ICR **en revisión** (enviado 2026-08-11); acantilados sin metadatos | `eg-v2026.08.11` (solo ICR) |

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
5. **Nodo `eg` (UCR - Escuela de Geografía)** — declarado en `config/nodos/eg.yml`
   el 2026-08-11 con las 2 capas del workspace `eg`, ya publicadas en GeoServer y
   registradas en el SNIT sin metadatos:
   - `ICR_dist2011` (Índice Combinado de Ruralidad, CEPAL 2023): datos originales
     (EPSG:5367), transformación publicada (EPSG:8908) y metadato ISO de CEPAL
     consolidados en `~/geografia-ucr/datos-fuente/icr-indice-combinado-ruralidad/`,
     con release `eg-v2026.08.11` verificado. Metadato adaptado y **enviado a
     revisión del SNIT el 2026-08-11** con su vista previa (coropleta); registro
     vivo:
     <https://www.snitcr.go.cr/Tramites/ver_xml_publico?key=dHJhbWl0ZV9zbml0OjoyMzQ3NDE2ODU2YTdiNWI0ZjIxMWY3OTA1OTM3MzAzNg==>.
     El **2026-08-14 se aplicaron por adelantado en el editor** las correcciones
     que se habían diferido a la llegada de observaciones: autor del metadato →
     Marco Martínez (CEPAL, Consultor, con teléfono real, correo suministrado
     por él —gmail—, horario, dirección San José y código postal 10101);
     teléfonos placeholder eliminados; fechas de creación y edición →
     04/08/2023 (entrega definitiva de CEPAL, antes 01/06/2020 heredada del
     original y edición vacía); fecha de mantenimiento corregida (11/08/2026,
     estaba con día/mes volteados). Verificado contra el registro vivo:
     conteo de 491 objetos = 491 features por WFS, y la URL del WMS
     (`https://geoportal.ucr.ac.cr/geoserver/eg/wms`) declarada en el editor y
     respondiendo (GetCapabilities y GetMap); recordar que el export XML nunca
     incluye esa URL. Copia del registro corregido en
     `metadatos/eg/2-revision-snit/ICR_dist2011-corregido.xml` (junto a la
     enviada). Quedan solo artefactos cosméticos del editor (bloque de
     individuo vacío y entradas de teléfono sin número); **pendiente:
     observaciones/aprobación de la revisora**. Confirmado (correo UCR de CEPAL del
     2025-09-08): el "1er envío_correcciones" fue la entrega definitiva, no hubo
     envíos posteriores de datos; el drive original ya no está disponible, la
     copia local de `datos-fuente/` es la única.
   - `AcantiladosMuertosSirgas` (`CR_EG-UCR_ACANTILADOSMUERTOS_500KVE`, escala
     1:500.000): sin datos locales ni metadatos; el shapefile solo existe en el
     servidor. Si se retoma: descargarlo, generar metadatos y empaquetar.

   También del export viejo de GeoNetwork: `Cobertura_Arborea_Region_Brunca_2020`
   (sin publicar).
6. **MOCUPP Piña y Palma** — insumos disponibles en los datos fuente, sin publicar.
7. **Correo de organización en `pointOfContact` (4 capas de café)** — el correo a nivel
   de organización quedó con el del autor del metadato en vez del de INISEFOR-UNA;
   corregir en el directorio de contactos de GeoNetwork cuando se retomen esas capas.
8. **Mantenimiento de credenciales** — gestionado fuera de este repositorio (requiere
   coordinación del equipo).
