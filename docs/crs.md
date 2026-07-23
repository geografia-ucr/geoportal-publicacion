# Sistema de referencia de coordenadas (CRS)

## Requisito

Toda capa publicada debe estar en **CR-SIRGAS / CRTM05 — EPSG:8908**, el CRS oficial
vigente de Costa Rica. La verificación es parte del flujo:

```bash
geopub verificar <slug>     # comprueba que cada capa esté en EPSG:8908
```

## CRS que se confunden con EPSG:8908

| CRS | EPSG | Datum | Proyección | Nota |
|---|---|---|---|---|
| CR-SIRGAS / CRTM05 | **8908** | CR-SIRGAS | TM, meridiano central −84°, escala 0.9999 | **El requerido** |
| CR05 / CRTM05 | 5367 | CR05 | TM, meridiano central −84°, escala 0.9999 | CRS anterior; **requiere transformación de datum** (no basta reetiquetar) |
| CR-SIRGAS / UTM 16N | — | CR-SIRGAS | UTM, meridiano central −87°, escala 0.9996 | **Mismo datum, proyección distinta**: las coordenadas no coinciden con CRTM05 |

**¡Verificar siempre el `.prj`!** Un shapefile en CR-SIRGAS / UTM 16N tiene el mismo
datum que EPSG:8908 pero otra proyección (meridiano −87° y factor de escala 0.9996 en
vez de −84° y 0.9999); si se publica como CRTM05 la capa aparece desplazada. Ocurrió
con `perdida_ganancia_musaceas_2021_2022` y hubo que reemplazar la capa
(ver `docs/historico/reemplazar_capa_musaceas.txt`).

## Transformación desde CR05 (EPSG:5367)

Transformación oficial de EPSG **"CR05 to CR-SIRGAS (1)"** (Helmert, exactitud
declarada 0.5 m). Los parámetros coinciden con el WKT publicado por el SNIT en
<https://www.snitcr.go.cr/pdfs/utilidades/WKT_CRSIRGAS_WGS84.txt>.

Comando usado en la publicación de las capas nacionales de pastos (2026-07-14):

```bash
ogr2ogr -f "ESRI Shapefile" -s_srs EPSG:5367 -t_srs EPSG:8908 -lco ENCODING=UTF-8 \
  capa_epsg8908.shp capa_original_epsg5367.shp
```

Con `geopub`, la transformación se declara en `config/nodos/<slug>.yml`
(bloque `transformaciones` de la capa, con el comando y la fecha) y se aplica con:

```bash
geopub transformar <slug>
geopub verificar <slug>     # confirmar EPSG:8908 tras transformar
```

Conservar siempre el archivo original recibido (no se sube al servidor) y registrar su
CRS de origen en el bloque `fuente` del YAML.

## Referencia

La guía oficial en PDF sobre los sistemas de referencia de Costa Rica (CR05, CR-SIRGAS
y sus transformaciones) **quedó fuera de este repositorio por ser material de
terceros**; consultar las utilidades del SNIT (<https://www.snitcr.go.cr/>) para la
versión vigente.
