# Mantenimiento de capas publicadas

Operaciones sobre capas ya publicadas en GeoServer, destiladas de los registros
históricos `docs/historico/mantenimiento_mocupp_pastos_20260720.txt` y
`docs/historico/reemplazar_capa_musaceas.txt`. El estado deseado de cada capa
(habilitada, título, resumen) se declara en `config/nodos/<slug>.yml` y se aplica con:

```bash
geopub mantener <slug> --dry-run   # muestra las diferencias config vs. servidor
geopub mantener <slug>             # aplica los cambios (PUT a los featureTypes)
geopub estado                      # verificación general config vs. servicios vivos
```

En los ejemplos, `$GEOSERVER_PASSWORD` es la contraseña del `admin` de GeoServer
(en `.env`, nunca en el repo).

## Habilitar / deshabilitar capas (PUT enabled)

Deshabilitar una capa (`enabled: false`) la saca del GetCapabilities y deja de servirse
por WFS/WMS, pero **el featureType y el datastore quedan configurados**: reactivarla es
solo otro `PUT` con `enabled: true`. Es el mecanismo usado con las 2 capas de café
(2026) y las 10 capas regionales Brunca de pastos (2026-07-20).

Equivalente manual (el href del recurso se obtiene del layer):

```bash
url=$(curl -s -u admin:$GEOSERVER_PASSWORD \
  "https://geoportal.ucr.ac.cr/geoserver/rest/layers/<workspace>:<capa>.json" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['layer']['resource']['href'])")

curl -s -u admin:$GEOSERVER_PASSWORD -XPUT \
  -H "Content-type: application/json" \
  -d '{"featureType":{"enabled":false}}' "$url"     # o true para reactivar
```

Verificación: el GetCapabilities del WFS público ya no debe anunciar la capa
(o debe volver a anunciarla al reactivar).

**Ojo:** si los metadatos SNIT de la capa apuntan a la distribución WFS/WMS del
workspace, deshabilitarla rompe ese enlace para los usuarios del SNIT. Decidirlo
conscientemente (caso Brunca 2026-07-20: se deshabilitaron de todos modos, a pedido
del responsable).

## Actualizar título o resumen (abstract) de una capa

El campo "Resumen" de la interfaz de GeoServer es el `abstract` del featureType.
Mismo mecanismo de `PUT`:

```bash
curl -s -u admin:$GEOSERVER_PASSWORD -XPUT \
  -H "Content-type: application/json; charset=utf-8" \
  -d '{"featureType":{"abstract":"<descripción>"}}' "$url"
```

Patrón de redacción usado (solicitud del SNIT, 2026-07-20):
"*\<Título\> para el año/período X, generada por el proyecto MOCUPP (Monitoreo del
Cambio de Uso y Cobertura de la Tierra en Paisajes Productivos). La capa contiene
polígonos con información de \<atributos reales\>.*" Los atributos se verifican con
`DescribeFeatureType` del WFS, no de memoria.

Verificación: `GetCapabilities` del WFS debe mostrar cada capa con su `wfs:Abstract`.

## Reemplazar los archivos de una capa existente

**No hay que recrear nada** (ni workspace, ni datastore, ni featureType). Basta con
copiar los archivos nuevos encima y recargar el datastore (caso real: corrección de
CRS de `perdida_ganancia_musaceas_2021_2022`, que estaba en UTM 16N):

1. **Respaldar** el directorio del workspace en el servidor:

   ```bash
   ssh -t -o PubkeyAuthentication=no geoportal@geoportal.ucr.ac.cr \
     "sudo zip -r /home/geoportal/bak/geoserver-data-<workspace>-$(date +%Y%m%d).zip \
      /var/lib/docker/volumes/geoportal-gsdatadir/_data/<workspace>"
   ```

2. **Subir** los archivos corregidos (`scp` a `/tmp/…` del servidor) y **copiarlos**
   sobre los existentes (`sudo cp` al directorio de datos). Para un shapefile,
   reemplazar el juego completo: `.shp .shx .dbf .prj .cpg`.

3. **Recargar el datastore**:

   ```bash
   curl -s -u admin:$GEOSERVER_PASSWORD -XPUT \
     "https://geoportal.ucr.ac.cr/geoserver/rest/workspaces/<workspace>/datastores/<datastore>/reset"
   ```

4. **Verificar** en Layer Preview / WFS que la capa se sirve con los datos nuevos.

## Respaldos

- Antes de cualquier operación que toque los datos del servidor, respaldar con
  `sudo zip` a `/home/geoportal/bak/` (patrón `geoserver-data-<nodo>-<fecha>.zip`).
- Opcionalmente descargar el zip a la estación local con `scp`.
- Los cambios puramente de configuración vía REST (enabled, abstract) no tocan los
  datos, pero conviene anotar en el YAML del nodo qué se cambió y cuándo.
