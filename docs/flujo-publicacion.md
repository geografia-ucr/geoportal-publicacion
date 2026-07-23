# Flujo de publicación de una capa o nodo

Este es el documento central del proceso: describe la publicación de un nodo (workspace)
y sus capas de principio a fin, usando el CLI `geopub`. Está destilado de los cuatro
registros históricos de publicación (`docs/historico/publicar_*.txt`), donde constan los
comandos crudos (curl, ssh, scp) tal como se ejecutaron originalmente.

**Convención de este documento:** los pasos automatizables se hacen con `geopub`;
los pasos que se hacen a mano en una interfaz web están marcados como **MANUAL**.
Los dos manuales imprescindibles son:

1. **GeoFence** (interfaz web de GeoServer): sin una regla ALLOW para el workspace,
   las capas NO son accesibles públicamente ni por WFS/WMS.
2. **SNIT** (herramienta en línea): la carga de metadatos XML, la imagen de vista previa
   y el envío a revisión se hacen en su editor web; no hay API.

## Vista general

```
preparar datos → verificar CRS → (transformar) → publicar en GeoServer → GeoFence (manual)
      → generar metadatos → subir al SNIT (manual) → verificación (GetCapabilities, conteos WFS)
```

## 0. Requisitos previos

```bash
conda activate geopub          # entorno con GDAL/geopandas (environment.yml)
cp .env.example .env           # completar GEOSERVER_PASSWORD y demás credenciales
```

Las credenciales viven solo en `.env` (ignorado por git). En los ejemplos de este
documento, `$GEOSERVER_PASSWORD` representa la contraseña del usuario `admin` de la
REST API de GeoServer.

## 1. Definir el nodo (configuración declarativa)

Cada nodo se describe en `config/nodos/<slug>.yml` (validado contra
`config/esquema-nodo.json`): workspace, tipo de datastore, capas con título, resumen,
CRS de origen, transformaciones, destinos (SNIT/GeoNode) y estado.

```bash
geopub nodo crear <slug>       # crea el YAML inicial del nodo
```

Los datos de las capas van en `datos/<slug>/` (no versionados en git; se distribuyen
como assets de Releases, ver paso 8).

## 2. Preparar los datos

- Nombres de archivo definitivos, en minúscula y sin sufijos de trabajo
  (ej. histórico: `Pastos_2021_Finales` → `cobertura_pastos_cr_2021`).
- Para GeoPackage, al copiar/renombrar con `ogr2ogr` usar **`-nln`** para renombrar
  también la capa interna (sin `-nln` la tabla interna conserva el nombre original):

  ```bash
  ogr2ogr -nln cultivo_cafe_2021 cultivo_cafe_2021.gpkg cultivo_cafe_2021_fin.gpkg
  ```

- Conservar los archivos originales recibidos (no se suben al servidor); registrar
  la procedencia y transformaciones en el YAML del nodo (`fuente`, `transformaciones`).

## 3. Verificar el CRS (y transformar si hace falta)

Toda capa publicada debe estar en **CR-SIRGAS / CRTM05 (EPSG:8908)**. Ver
[`crs.md`](crs.md) para el detalle (diferencias con EPSG:5367 y con UTM 16N).

```bash
geopub verificar <slug>        # comprueba EPSG:8908 y requisitos de archivos
geopub transformar <slug>      # aplica las transformaciones declaradas en el YAML
                               # (ej. EPSG:5367 → EPSG:8908 con ogr2ogr)
geopub verificar <slug>        # volver a verificar tras transformar
```

Caso real (pastos nacionales, 2026-07-14): dos capas llegaron en CR05/CRTM05
(EPSG:5367) y se transformaron con la transformación oficial de EPSG
"CR05 to CR-SIRGAS (1)" (Helmert, exactitud 0.5 m).

## 4. Publicar en GeoServer

```bash
geopub publicar <slug> --dry-run   # ensayo: muestra lo que haría, sin tocar el servidor
geopub publicar <slug>             # ejecuta la publicación completa
```

Internamente el flujo reproduce lo que antes se hacía a mano (ver históricos):

1. **Respaldo** del directorio de datos en el servidor:
   `sudo zip -r /home/geoportal/bak/geoserver-data-<nodo>-<fecha>.zip <ruta datos>`
   (opcionalmente descargar el zip a la estación local con `scp`).
2. **Subida** de archivos: `scp` a un directorio temporal del servidor (`/tmp/…`) y
   luego `sudo cp` a `/var/lib/docker/volumes/geoportal-gsdatadir/_data/<workspace>/`
   (esa ruta se ve como `/geoserver_data/data/<workspace>` dentro del contenedor).
   Verificar la integridad (md5sum local vs. servidor) y limpiar el temporal.
3. **Workspace** vía REST API:
   `POST https://geoportal.ucr.ac.cr/geoserver/rest/workspaces`
   con `{"workspace":{"name":"<workspace>"}}`.
4. **Datastore(s)** — según el formato (ver diferencias abajo).
5. **featureTypes** — un `POST …/datastores/<ds>/featuretypes` por capa, con
   `name` (typeName técnico), `title` (nombre de despliegue), `abstract` (resumen),
   `nativeCRS`/`srs` = `EPSG:8908` y `enabled: true`.

Notas operativas heredadas de los históricos:

- Los `POST` exitosos de la REST API pueden devolver texto plano, no JSON
  (no encadenar `| jq` a ciegas).
- No es necesario reiniciar GeoServer para agregar datos nuevos.
- El SSH del servidor requiere `-o PubkeyAuthentication=no` (autenticación por
  contraseña) y `-t` para comandos con `sudo`.
- Si el nombre de despliegue debe diferir del técnico (ej. "…en la región Brunca…"),
  se cambia el `title` del featureType, nunca el `typeName`.

### Diferencias por formato

| | Shapefile | GeoPackage |
|---|---|---|
| Datastore | **Uno solo por directorio**: tipo `Directory of spatial files (Shapefiles)`, parámetros `url` (`file:///geoserver_data/data/<workspace>`) y `charset: UTF-8` | **Uno por cada .gpkg** — no existe datastore tipo "directorio de GeoPackage". Tipo `GeoPackage`, parámetros `database` (`file:///geoserver_data/data/<ws>/<capa>.gpkg`) y `namespace` |
| Capas nuevas en un nodo existente | El datastore de directorio detecta los shapefiles nuevos: basta copiar los archivos y publicar los featureTypes | Hay que crear un datastore nuevo por cada .gpkg adicional |
| En `config/nodos/*.yml` | `datastore_tipo: shapefile_dir` | `datastore_tipo: gpkg_por_capa` |

## 5. Regla ALLOW en GeoFence — paso MANUAL

**Sin este paso las capas no son públicas** (ni Layer Preview anónimo, ni WFS/WMS).

En la interfaz web de GeoServer (`https://geoportal.ucr.ac.cr/geoserver/web/`):

> **Security > GeoFence Data Rules > Add new rule**
> Role=`*`, User=`*`, Service=`*`, Request=`*`, SubField=`*`,
> Workspace=`<workspace>`, Layer=`*`, Access=**ALLOW**

- La regla se aplica de inmediato; no requiere reiniciar.
- Si el workspace ya tiene una regla con Layer=`*`, las capas nuevas quedan cubiertas
  automáticamente (así ocurrió con las 5 capas nacionales de pastos).

## 6. Generar metadatos (ISO 19115-3:2018)

Un XML por capa, UTF-8, raíz `mdb:MD_Metadata`, CRS `EPSG:8908`. El ciclo de vida en
el repo es `metadatos/<nodo>/1-borrador/` → `2-revision-snit/` → `3-actual/`
(aprobados), más `vistas-previas/`.

```bash
geopub metadatos generar <slug>    # genera/actualiza los XML por capa
geopub metadatos validar <slug>    # valida estructura y valores
geopub vista-previa <slug>         # imagen de vista previa estilo SNIT
                                   # (contorno de CR + entidades en rojo, A4 horizontal, 300 DPI)
geopub metadatos promover <slug>   # mueve XML verificados a 3-actual/
```

El conteo real de entidades para el metadato se toma del WFS (ver paso 9), no del
archivo local, para confirmar que coinciden.

## 7. Subir al SNIT — pasos MANUALES

Todo el trabajo en el SNIT se hace en su **herramienta en línea** (GeoNetwork del SNIT);
no hay API. Con la sesión del usuario de metadatos del nodo:

1. **Subir el XML** de cada capa en la herramienta en línea del SNIT.
2. **Adjuntar la imagen de vista previa** en el editor, sección **Resumen gráfico**
   ("subir archivo"). No basta con el `fileName` del XML: la URL del `graphicOverview`
   la regenera GeoNetwork a partir de la miniatura adjunta al registro.
3. **Enviar a revisión**. El SNIT devuelve observaciones en DOCX; el ciclo de
   corrección está documentado en [`correcciones-snit.md`](correcciones-snit.md).
4. Al aprobarse, descargar el XML final y promoverlo a `metadatos/<nodo>/3-actual/`.

Si el nodo (subnodo del SNIT) aún no existe, primero hay que darlo de alta con el
formulario de información del nodo: ver [`nodo-snit.md`](nodo-snit.md).

## 8. Release de datos (reproducibilidad)

Los datos finales publicados se suben como assets de un Release de GitHub, con sumas
SHA-256 en `checksums/`:

```bash
geopub release crear <slug>       # empaqueta datos/<slug>/ y sube el Release
geopub release descargar <slug>   # restaura datos/<slug>/ verificando checksums
```

## 9. Verificación final

```bash
geopub estado                     # compara configuración local vs. servicios vivos
```

Comprobaciones manuales equivalentes (las de los históricos):

```bash
# Capas y títulos anunciados por el WFS público
curl -s "https://geoportal.ucr.ac.cr/geoserver/<workspace>/wfs?service=WFS&request=GetCapabilities" \
  | grep -E "<(Name|Title|Abstract)>"

# Conteo de entidades de una capa (atributo numberMatched) — debe coincidir con el archivo local
curl -s "https://geoportal.ucr.ac.cr/geoserver/<workspace>/wfs?service=WFS&version=2.0.0&request=GetFeature&typeNames=<workspace>:<capa>&resultType=hits"

# Listar capas del workspace por la REST API
curl -s -u admin:$GEOSERVER_PASSWORD \
  "https://geoportal.ucr.ac.cr/geoserver/rest/workspaces/<workspace>/layers.json" | jq
```

Además: Layer Preview en la interfaz web de GeoServer y conexión WFS desde QGIS,
**sin credenciales** (para confirmar que la regla de GeoFence funciona).

## Mantenimiento posterior

Habilitar/deshabilitar capas, actualizar resúmenes, reemplazar archivos de una capa y
respaldos: ver [`mantenimiento.md`](mantenimiento.md) (`geopub mantener`).
