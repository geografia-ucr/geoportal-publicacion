# Tabla de correspondencia: migración de `metadatos/` al repositorio nuevo

Migración (2026-07-22) de `metadatos/` del repositorio viejo (`~/geoportal/publicacion`)
a la estructura nueva de este repositorio.

## Convención

- El nombre de archivo es el **slug de la capa** = `typeName` de GeoServer
  (ej. `cobertura_pastos_cr_2021.xml`). Los títulos largos con espacios, tildes y
  paréntesis desaparecen de los nombres de archivo.
- Estructura por nodo (`mocupp-musaceas`, `mocupp-cafe`, `mocupp-pastos`):
  - `1-borrador/` — borradores no enviados al SNIT (`<slug>.xml`, `<slug>.docx`).
  - `2-revision-snit/` — ciclo de revisión: `<slug>-enviado.xml` (y `-enviado.docx` de respaldo),
    `<slug>-observaciones.docx` (devuelto por el SNIT), `<slug>-corregido.xml`.
  - `3-actual/` — SOLO la versión aprobada/vigente: `<slug>.xml` + `<slug>.docx` (o `.pdf`) de respaldo.
  - `vistas-previas/` — `<slug>.jpg`.
- Sufijos viejos → nuevos: `_sincorregir`/`-sincorregir` → `-enviado`;
  `_corregida`/`-corregido` → `-corregido`; `_rev`/`_REV` (DOCX del SNIT) → `-observaciones`;
  los DOCX de `para-enviar/` son los respaldos de la versión enviada/actual.
- Las 5 capas nacionales de pastos (antes en `nacionales/`) son capas normales del nodo
  `mocupp-pastos`; como están en revisión del SNIT (sin aprobar), sus XML quedan en
  `2-revision-snit/<slug>-enviado.xml` y aún no tienen entrada en `3-actual/`.
- Se copiaron los archivos preservando fechas de modificación (`cp -p`). Cuatro XML
  descargados del SNIT traían advertencias PHP antepuestas a la raíz XML (disco lleno en el
  servidor del SNIT); se migraron limpios (se eliminó el prefijo, marcados abajo con "(limpiado)").
- Rutas viejas relativas a `metadatos/` del repo viejo; rutas nuevas relativas a `metadatos/` de este repo.

## mocupp-musaceas

| Archivo viejo | Archivo nuevo |
|---|---|
| `mocupp-musaceas/actual/Cultivo de musáceas en Costa Rica 2021.xml` | `mocupp-musaceas/3-actual/musaceas_cr_2021.xml` |
| `mocupp-musaceas/actual/Cultivo de musáceas en Costa Rica 2022.xml` | `mocupp-musaceas/3-actual/musaceas_cr_2022.xml` |
| `mocupp-musaceas/actual/Pérdida y ganancia de cultivo de musáceas en Costa Rica 2021-2022.xml` | `mocupp-musaceas/3-actual/perdida_ganancia_musaceas_2021_2022.xml` |

## mocupp-cafe

| Archivo viejo | Archivo nuevo |
|---|---|
| `mocupp-cafe/borrador/metadato_cambio_cobertura_arborea_cafe_2021_2022_final.docx` | `mocupp-cafe/1-borrador/perdida_cobertura_arborea.docx` |
| `mocupp-cafe/revision-snit/Pérdida de cobertura arbórea en paisaje de café de Costa Rica 2021-2022-corregido.xml` | `mocupp-cafe/2-revision-snit/perdida_cobertura_arborea-corregido.xml` |
| `mocupp-cafe/revision-snit/Pérdida de cobertura arbórea en paisaje de café de Costa Rica 2021-2022-sincorregir.xml` | `mocupp-cafe/2-revision-snit/perdida_cobertura_arborea-enviado.xml` |
| `mocupp-cafe/revision-snit/Pérdida de cobertura arbórea en paisaje de café de Costa Rica 2021-2022_rev.docx` | `mocupp-cafe/2-revision-snit/perdida_cobertura_arborea-observaciones.docx` |
| `mocupp-cafe/actual/Cultivo de café en Costa Rica 2021.xml` | `mocupp-cafe/3-actual/cultivo_cafe_2021.xml` |
| `mocupp-cafe/actual/Cultivo de café en Costa Rica 2022.xml` | `mocupp-cafe/3-actual/cultivo_cafe_2022.xml` |
| `mocupp-cafe/revision-snit/para-enviar/Pérdida de cobertura arbórea en paisaje de café de Costa Rica 2021-2022.docx` | `mocupp-cafe/3-actual/perdida_cobertura_arborea.docx` |
| `mocupp-cafe/actual/Pérdida de cobertura arbórea en paisaje de café de Costa Rica 2021-2022.xml` | `mocupp-cafe/3-actual/perdida_cobertura_arborea.xml` |
| `mocupp-cafe/actual/Pérdida y ganancia de cultivo de café en Costa Rica 2021-2022.xml` | `mocupp-cafe/3-actual/perdida_ganancia_cultivo_cafe.xml` |
| `mocupp-cafe/borrador/vista_previa_perdida_cobertura_arborea_estilo_snit.jpg` | `mocupp-cafe/vistas-previas/perdida_cobertura_arborea.jpg` |

## mocupp-pastos

| Archivo viejo | Archivo nuevo |
|---|---|
| `mocupp-pastos/borrador/Cobertura arbórea en paisaje productivo de pastos en Costa Rica 2020.xml` | `mocupp-pastos/1-borrador/Paisaje_cobertura_arborea_2020.xml` |
| `mocupp-pastos/borrador/Cobertura arbórea en paisaje productivo de pastos en Costa Rica 2021.xml` | `mocupp-pastos/1-borrador/Paisaje_cobertura_arborea_2021.xml` |
| `mocupp-pastos/borrador/Cobertura arbórea en paisaje productivo de pastos en Costa Rica 2022.xml` | `mocupp-pastos/1-borrador/Paisaje_cobertura_arborea_2022.xml` |
| `mocupp-pastos/borrador/Cobertura de pastos en Costa Rica 2020.xml` | `mocupp-pastos/1-borrador/Paisaje_cobertura_pastos_2020.xml` |
| `mocupp-pastos/borrador/Cobertura de pastos en Costa Rica 2021.xml` | `mocupp-pastos/1-borrador/Paisaje_cobertura_pastos_2021.xml` |
| `mocupp-pastos/borrador/Cobertura de pastos en Costa Rica 2022.xml` | `mocupp-pastos/1-borrador/Paisaje_cobertura_pastos_2022.xml` |
| `mocupp-pastos/borrador/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos 2019-2020 (V1).xml` | `mocupp-pastos/1-borrador/Perdida_ganancia_cobertura_arborea_sobre_paisaje_productivo_de_pastos_2019-2020_V1.xml` |
| `mocupp-pastos/borrador/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos 2019-2020 (V2).xml` | `mocupp-pastos/1-borrador/Perdida_ganancia_cobertura_arborea_sobre_paisaje_productivo_de_pastos_2019-2020_V2.xml` |
| `mocupp-pastos/borrador/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos 2020-2021.xml` | `mocupp-pastos/1-borrador/Perdida_ganancia_cobertura_arborea_sobre_paisaje_productivo_de_pastos_2020-2021.xml` |
| `mocupp-pastos/borrador/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos 2021-2022.xml` | `mocupp-pastos/1-borrador/Perdida_ganancia_cobertura_arborea_sobre_paisaje_productivo_de_pastos_2021-2022.xml` |
| `mocupp-pastos/revision-snit/Cobertura arbórea en paisaje productivo de pastos en la región Brunca de Costa Rica 2020_corregida.xml` | `mocupp-pastos/2-revision-snit/Paisaje_cobertura_arborea_2020-corregido.xml` |
| `mocupp-pastos/revision-snit/Cobertura arbórea en paisaje productivo de pastos en la región Brunca de Costa Rica 2020_sincorregir.xml` | `mocupp-pastos/2-revision-snit/Paisaje_cobertura_arborea_2020-enviado.xml` |
| `mocupp-pastos/revision-snit/Cobertura arbórea en paisaje productivo de pastos en la región Brunca de Costa Rica 2020_rev.docx` | `mocupp-pastos/2-revision-snit/Paisaje_cobertura_arborea_2020-observaciones.docx` |
| `mocupp-pastos/revision-snit/Cobertura arbórea en paisaje productivo de pastos en la región Brunca de Costa Rica 2021_corregida.xml` | `mocupp-pastos/2-revision-snit/Paisaje_cobertura_arborea_2021-corregido.xml` |
| `mocupp-pastos/revision-snit/Cobertura arbórea en paisaje productivo de pastos en la región Brunca de Costa Rica 2021_sincorregir.xml` | `mocupp-pastos/2-revision-snit/Paisaje_cobertura_arborea_2021-enviado.xml` (limpiado) |
| `mocupp-pastos/revision-snit/Cobertura arbórea en paisaje productivo de pastos en la región Brunca de Costa Rica 2021_rev.docx` | `mocupp-pastos/2-revision-snit/Paisaje_cobertura_arborea_2021-observaciones.docx` |
| `mocupp-pastos/revision-snit/Cobertura arbórea en paisaje productivo de pastos en la región Brunca de Costa Rica 2022_corregida.xml` | `mocupp-pastos/2-revision-snit/Paisaje_cobertura_arborea_2022-corregido.xml` |
| `mocupp-pastos/revision-snit/Cobertura arbórea en paisaje productivo de pastos en la región Brunca de Costa Rica 2022_sincorregir.xml` | `mocupp-pastos/2-revision-snit/Paisaje_cobertura_arborea_2022-enviado.xml` (limpiado) |
| `mocupp-pastos/revision-snit/Cobertura arbórea en paisaje productivo de pastos en la región Brunca de Costa Rica 2022_rev.docx` | `mocupp-pastos/2-revision-snit/Paisaje_cobertura_arborea_2022-observaciones.docx` |
| `mocupp-pastos/revision-snit/Cobertura de pastos en la región Brunca de Costa Rica 2020_corregida.xml` | `mocupp-pastos/2-revision-snit/Paisaje_cobertura_pastos_2020-corregido.xml` |
| `mocupp-pastos/revision-snit/Cobertura de pastos en la región Brunca de Costa Rica 2020_sincorregir.xml` | `mocupp-pastos/2-revision-snit/Paisaje_cobertura_pastos_2020-enviado.xml` |
| `mocupp-pastos/revision-snit/Cobertura de pastos en la región Brunca de Costa Rica 2020_rev.docx` | `mocupp-pastos/2-revision-snit/Paisaje_cobertura_pastos_2020-observaciones.docx` |
| `mocupp-pastos/revision-snit/Cobertura de pastos en la región Brunca de Costa Rica 2021_corregida.xml` | `mocupp-pastos/2-revision-snit/Paisaje_cobertura_pastos_2021-corregido.xml` |
| `mocupp-pastos/revision-snit/Cobertura de pastos en la región Brunca de Costa Rica 2021_sincorregir.xml` | `mocupp-pastos/2-revision-snit/Paisaje_cobertura_pastos_2021-enviado.xml` |
| `mocupp-pastos/revision-snit/Cobertura de pastos en la región Brunca de Costa Rica 2021_rev.docx` | `mocupp-pastos/2-revision-snit/Paisaje_cobertura_pastos_2021-observaciones.docx` |
| `mocupp-pastos/revision-snit/Cobertura de pastos en la región Brunca de Costa Rica 2022_corregida.xml` | `mocupp-pastos/2-revision-snit/Paisaje_cobertura_pastos_2022-corregido.xml` |
| `mocupp-pastos/revision-snit/Cobertura de pastos en la región Brunca de Costa Rica 2022_sincorregir.xml` | `mocupp-pastos/2-revision-snit/Paisaje_cobertura_pastos_2022-enviado.xml` |
| `mocupp-pastos/revision-snit/Cobertura de pastos en la región Brunca de Costa Rica 2022_rev.docx` | `mocupp-pastos/2-revision-snit/Paisaje_cobertura_pastos_2022-observaciones.docx` |
| `mocupp-pastos/revision-snit/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos en la región Brunca de Costa Rica 2019-2020 (V1)_corregida.xml` | `mocupp-pastos/2-revision-snit/Perdida_ganancia_cobertura_arborea_sobre_paisaje_productivo_de_pastos_2019-2020_V1-corregido.xml` |
| `mocupp-pastos/revision-snit/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos en la región Brunca de Costa Rica 2019-2020 (V1)_sincorregir.xml` | `mocupp-pastos/2-revision-snit/Perdida_ganancia_cobertura_arborea_sobre_paisaje_productivo_de_pastos_2019-2020_V1-enviado.xml` |
| `mocupp-pastos/revision-snit/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos en la región Brunca de Costa Rica 2019-2020 (V1)_REV.docx` | `mocupp-pastos/2-revision-snit/Perdida_ganancia_cobertura_arborea_sobre_paisaje_productivo_de_pastos_2019-2020_V1-observaciones.docx` |
| `mocupp-pastos/revision-snit/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos en la región Brunca de Costa Rica 2019-2020 (V2)_corregida.xml` | `mocupp-pastos/2-revision-snit/Perdida_ganancia_cobertura_arborea_sobre_paisaje_productivo_de_pastos_2019-2020_V2-corregido.xml` |
| `mocupp-pastos/revision-snit/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos en la región Brunca de Costa Rica 2019-2020 (V2)_sincorregir.xml` | `mocupp-pastos/2-revision-snit/Perdida_ganancia_cobertura_arborea_sobre_paisaje_productivo_de_pastos_2019-2020_V2-enviado.xml` |
| `mocupp-pastos/revision-snit/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos en la región Brunca de Costa Rica 2019-2020 (V2)_rev.docx` | `mocupp-pastos/2-revision-snit/Perdida_ganancia_cobertura_arborea_sobre_paisaje_productivo_de_pastos_2019-2020_V2-observaciones.docx` |
| `mocupp-pastos/revision-snit/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos en la región Brunca de Costa Rica 2020-2021_corregida.xml` | `mocupp-pastos/2-revision-snit/Perdida_ganancia_cobertura_arborea_sobre_paisaje_productivo_de_pastos_2020-2021-corregido.xml` |
| `mocupp-pastos/revision-snit/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos en la región Brunca de Costa Rica 2020-2021_sincorregir.xml` | `mocupp-pastos/2-revision-snit/Perdida_ganancia_cobertura_arborea_sobre_paisaje_productivo_de_pastos_2020-2021-enviado.xml` (limpiado) |
| `mocupp-pastos/revision-snit/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos en la región Brunca de Costa Rica 2020-2021_rev.docx` | `mocupp-pastos/2-revision-snit/Perdida_ganancia_cobertura_arborea_sobre_paisaje_productivo_de_pastos_2020-2021-observaciones.docx` |
| `mocupp-pastos/revision-snit/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos en la región Brunca de Costa Rica 2021-2022_corregida.xml` | `mocupp-pastos/2-revision-snit/Perdida_ganancia_cobertura_arborea_sobre_paisaje_productivo_de_pastos_2021-2022-corregido.xml` (limpiado) |
| `mocupp-pastos/revision-snit/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos en la región Brunca de Costa Rica 2021-2022_sincorregir.xml` | `mocupp-pastos/2-revision-snit/Perdida_ganancia_cobertura_arborea_sobre_paisaje_productivo_de_pastos_2021-2022-enviado.xml` |
| `mocupp-pastos/revision-snit/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos en la región Brunca de Costa Rica 2021-2022_rev.docx` | `mocupp-pastos/2-revision-snit/Perdida_ganancia_cobertura_arborea_sobre_paisaje_productivo_de_pastos_2021-2022-observaciones.docx` |
| `mocupp-pastos/nacionales/para-enviar/Cobertura arbórea en paisaje productivo de pastos en Costa Rica 2021.docx` | `mocupp-pastos/2-revision-snit/cobertura_arborea_pastos_cr_2021-enviado.docx` |
| `mocupp-pastos/nacionales/Cobertura arbórea en paisaje productivo de pastos en Costa Rica 2021.xml` | `mocupp-pastos/2-revision-snit/cobertura_arborea_pastos_cr_2021-enviado.xml` |
| `mocupp-pastos/nacionales/para-enviar/Cobertura arbórea en paisaje productivo de pastos en Costa Rica 2022.docx` | `mocupp-pastos/2-revision-snit/cobertura_arborea_pastos_cr_2022-enviado.docx` |
| `mocupp-pastos/nacionales/Cobertura arbórea en paisaje productivo de pastos en Costa Rica 2022.xml` | `mocupp-pastos/2-revision-snit/cobertura_arborea_pastos_cr_2022-enviado.xml` |
| `mocupp-pastos/nacionales/para-enviar/Cobertura de pastos Costa Rica 2021.docx` | `mocupp-pastos/2-revision-snit/cobertura_pastos_cr_2021-enviado.docx` |
| `mocupp-pastos/nacionales/Cobertura de pastos en Costa Rica 2021.xml` | `mocupp-pastos/2-revision-snit/cobertura_pastos_cr_2021-enviado.xml` |
| `mocupp-pastos/nacionales/para-enviar/Cobertura de pastos Costa Rica 2022.docx` | `mocupp-pastos/2-revision-snit/cobertura_pastos_cr_2022-enviado.docx` |
| `mocupp-pastos/nacionales/Cobertura de pastos en Costa Rica 2022.xml` | `mocupp-pastos/2-revision-snit/cobertura_pastos_cr_2022-enviado.xml` |
| `mocupp-pastos/nacionales/para-enviar/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos en Costa Rica 2021-2022.docx` | `mocupp-pastos/2-revision-snit/perdida_ganancia_cobertura_arborea_pastos_cr_2021_2022-enviado.docx` |
| `mocupp-pastos/nacionales/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos en Costa Rica 2021-2022.xml` | `mocupp-pastos/2-revision-snit/perdida_ganancia_cobertura_arborea_pastos_cr_2021_2022-enviado.xml` |
| `mocupp-pastos/revision-snit/para-enviar/Cobertura arbórea en paisaje productivo de pastos en la región Brunca de Costa Rica 2020.docx` | `mocupp-pastos/3-actual/Paisaje_cobertura_arborea_2020.docx` |
| `mocupp-pastos/actual/Cobertura arbórea en paisaje productivo de pastos en la región Brunca de Costa Rica 2020.xml` | `mocupp-pastos/3-actual/Paisaje_cobertura_arborea_2020.xml` |
| `mocupp-pastos/revision-snit/para-enviar/Cobertura arbórea en paisaje productivo de pastos en la región Brunca de Costa Rica 2021.docx` | `mocupp-pastos/3-actual/Paisaje_cobertura_arborea_2021.docx` |
| `mocupp-pastos/actual/Cobertura arbórea en paisaje productivo de pastos en la región Brunca de Costa Rica 2021.xml` | `mocupp-pastos/3-actual/Paisaje_cobertura_arborea_2021.xml` |
| `mocupp-pastos/revision-snit/para-enviar/Cobertura arbórea en paisaje productivo de pastos en la región Brunca de Costa Rica 2022.docx` | `mocupp-pastos/3-actual/Paisaje_cobertura_arborea_2022.docx` |
| `mocupp-pastos/actual/Cobertura arbórea en paisaje productivo de pastos en la región Brunca de Costa Rica 2022.xml` | `mocupp-pastos/3-actual/Paisaje_cobertura_arborea_2022.xml` |
| `mocupp-pastos/revision-snit/para-enviar/Cobertura de pastos en la región Brunca de Costa Rica 2020.docx` | `mocupp-pastos/3-actual/Paisaje_cobertura_pastos_2020.docx` |
| `mocupp-pastos/actual/Cobertura de pastos en la región Brunca de Costa Rica 2020.xml` | `mocupp-pastos/3-actual/Paisaje_cobertura_pastos_2020.xml` |
| `mocupp-pastos/revision-snit/para-enviar/Cobertura de pastos en la región Brunca de Costa Rica 2021.docx` | `mocupp-pastos/3-actual/Paisaje_cobertura_pastos_2021.docx` |
| `mocupp-pastos/actual/Cobertura de pastos en la región Brunca de Costa Rica 2021.xml` | `mocupp-pastos/3-actual/Paisaje_cobertura_pastos_2021.xml` |
| `mocupp-pastos/revision-snit/para-enviar/Cobertura de pastos en la región Brunca de Costa Rica 2022.docx` | `mocupp-pastos/3-actual/Paisaje_cobertura_pastos_2022.docx` |
| `mocupp-pastos/actual/Cobertura de pastos en la región Brunca de Costa Rica 2022.xml` | `mocupp-pastos/3-actual/Paisaje_cobertura_pastos_2022.xml` |
| `mocupp-pastos/revision-snit/para-enviar/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos en la región Brunca de Costa Rica 2019-2020 (V1).docx` | `mocupp-pastos/3-actual/Perdida_ganancia_cobertura_arborea_sobre_paisaje_productivo_de_pastos_2019-2020_V1.docx` |
| `mocupp-pastos/actual/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos en la región Brunca de Costa Rica 2019-2020 (V1).xml` | `mocupp-pastos/3-actual/Perdida_ganancia_cobertura_arborea_sobre_paisaje_productivo_de_pastos_2019-2020_V1.xml` |
| `mocupp-pastos/revision-snit/para-enviar/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos en la región Brunca de Costa Rica 2019-2020 (V2).pdf` | `mocupp-pastos/3-actual/Perdida_ganancia_cobertura_arborea_sobre_paisaje_productivo_de_pastos_2019-2020_V2.pdf` |
| `mocupp-pastos/actual/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos en la región Brunca de Costa Rica 2019-2020 (V2).xml` | `mocupp-pastos/3-actual/Perdida_ganancia_cobertura_arborea_sobre_paisaje_productivo_de_pastos_2019-2020_V2.xml` |
| `mocupp-pastos/revision-snit/para-enviar/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos en la región Brunca de Costa Rica 2020-2021.docx` | `mocupp-pastos/3-actual/Perdida_ganancia_cobertura_arborea_sobre_paisaje_productivo_de_pastos_2020-2021.docx` |
| `mocupp-pastos/actual/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos en la región Brunca de Costa Rica 2020-2021.xml` | `mocupp-pastos/3-actual/Perdida_ganancia_cobertura_arborea_sobre_paisaje_productivo_de_pastos_2020-2021.xml` |
| `mocupp-pastos/revision-snit/para-enviar/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos en la región Brunca de Costa Rica 2021-2022.docx` | `mocupp-pastos/3-actual/Perdida_ganancia_cobertura_arborea_sobre_paisaje_productivo_de_pastos_2021-2022.docx` |
| `mocupp-pastos/actual/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos en la región Brunca de Costa Rica 2021-2022.xml` | `mocupp-pastos/3-actual/Perdida_ganancia_cobertura_arborea_sobre_paisaje_productivo_de_pastos_2021-2022.xml` |
| `mocupp-pastos/borrador/Cobertura arbórea en paisaje productivo de pastos en Costa Rica 2020.jpg` | `mocupp-pastos/vistas-previas/Paisaje_cobertura_arborea_2020.jpg` |
| `mocupp-pastos/borrador/Cobertura arbórea en paisaje productivo de pastos en Costa Rica 2021.jpg` | `mocupp-pastos/vistas-previas/Paisaje_cobertura_arborea_2021.jpg` |
| `mocupp-pastos/borrador/Cobertura arbórea en paisaje productivo de pastos en Costa Rica 2022.jpg` | `mocupp-pastos/vistas-previas/Paisaje_cobertura_arborea_2022.jpg` |
| `mocupp-pastos/borrador/Cobertura de pastos en Costa Rica 2020.jpg` | `mocupp-pastos/vistas-previas/Paisaje_cobertura_pastos_2020.jpg` |
| `mocupp-pastos/borrador/Cobertura de pastos en Costa Rica 2021.jpg` | `mocupp-pastos/vistas-previas/Paisaje_cobertura_pastos_2021.jpg` |
| `mocupp-pastos/borrador/Cobertura de pastos en Costa Rica 2022.jpg` | `mocupp-pastos/vistas-previas/Paisaje_cobertura_pastos_2022.jpg` |
| `mocupp-pastos/borrador/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos 2019-2020 (V1).jpg` | `mocupp-pastos/vistas-previas/Perdida_ganancia_cobertura_arborea_sobre_paisaje_productivo_de_pastos_2019-2020_V1.jpg` |
| `mocupp-pastos/borrador/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos 2019-2020 (V2).jpg` | `mocupp-pastos/vistas-previas/Perdida_ganancia_cobertura_arborea_sobre_paisaje_productivo_de_pastos_2019-2020_V2.jpg` |
| `mocupp-pastos/borrador/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos 2020-2021.jpg` | `mocupp-pastos/vistas-previas/Perdida_ganancia_cobertura_arborea_sobre_paisaje_productivo_de_pastos_2020-2021.jpg` |
| `mocupp-pastos/borrador/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos 2021-2022.jpg` | `mocupp-pastos/vistas-previas/Perdida_ganancia_cobertura_arborea_sobre_paisaje_productivo_de_pastos_2021-2022.jpg` |
| `mocupp-pastos/nacionales/Cobertura arbórea en paisaje productivo de pastos en Costa Rica 2021.jpg` | `mocupp-pastos/vistas-previas/cobertura_arborea_pastos_cr_2021.jpg` |
| `mocupp-pastos/nacionales/Cobertura arbórea en paisaje productivo de pastos en Costa Rica 2022.jpg` | `mocupp-pastos/vistas-previas/cobertura_arborea_pastos_cr_2022.jpg` |
| `mocupp-pastos/nacionales/Cobertura de pastos en Costa Rica 2021.jpg` | `mocupp-pastos/vistas-previas/cobertura_pastos_cr_2021.jpg` |
| `mocupp-pastos/nacionales/Cobertura de pastos en Costa Rica 2022.jpg` | `mocupp-pastos/vistas-previas/cobertura_pastos_cr_2022.jpg` |
| `mocupp-pastos/nacionales/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos 2021-2022.jpg` | `mocupp-pastos/vistas-previas/perdida_ganancia_cobertura_arborea_pastos_cr_2021_2022.jpg` |

## Archivos no migrados (omisiones deliberadas)

### mocupp-cafe

- `mocupp-cafe/actual/Pérdida de cobertura arbórea en paisaje de café de Costa Rica 2021-2022.docx` — omitido: versión del 2026-06-08, reemplazada por la de `revision-snit/para-enviar/` (2026-06-23), que es la migrada a `3-actual/`

### mocupp-pastos

- `mocupp-pastos/actual/Cobertura de pastos en la región Brunca de Costa Rica 2020.docx` — omitido: versión antigua (2026-06-08), reemplazada por la de `revision-snit/para-enviar/` migrada a `3-actual/`
- `mocupp-pastos/actual/Cobertura de pastos en la región Brunca de Costa Rica 2021.docx` — omitido: versión antigua (2026-06-08), reemplazada por la de `revision-snit/para-enviar/` migrada a `3-actual/`
- `mocupp-pastos/actual/Cobertura de pastos en la región Brunca de Costa Rica 2022.docx` — omitido: versión antigua (2026-06-08), reemplazada por la de `revision-snit/para-enviar/` migrada a `3-actual/`
- `mocupp-pastos/actual/Cobertura arbórea en paisaje productivo de pastos en la región Brunca de Costa Rica 2020.docx` — omitido: versión antigua (2026-06-08), reemplazada por la de `revision-snit/para-enviar/` migrada a `3-actual/`
- `mocupp-pastos/actual/Cobertura arbórea en paisaje productivo de pastos en la región Brunca de Costa Rica 2021.docx` — omitido: duplicado exacto (md5 idéntico) del de `revision-snit/para-enviar/` migrado a `3-actual/`
- `mocupp-pastos/actual/Cobertura arbórea en paisaje productivo de pastos en la región Brunca de Costa Rica 2022.docx` — omitido: duplicado exacto (md5 idéntico) del de `revision-snit/para-enviar/` migrado a `3-actual/`
- `mocupp-pastos/actual/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos en la región Brunca de Costa Rica 2019-2020 (V1).docx` — omitido: duplicado exacto (md5 idéntico) del de `revision-snit/para-enviar/` migrado a `3-actual/`
- `mocupp-pastos/actual/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos en la región Brunca de Costa Rica 2019-2020 (V2).docx` — omitido: archivo DOCX dañado (ZIP corrupto); el respaldo vigente es el PDF de `revision-snit/para-enviar/` migrado a `3-actual/`
- `mocupp-pastos/actual/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos en la región Brunca de Costa Rica 2020-2021.docx` — omitido: duplicado exacto (md5 idéntico) del de `revision-snit/para-enviar/` migrado a `3-actual/`
- `mocupp-pastos/actual/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos en la región Brunca de Costa Rica 2021-2022.docx` — omitido: archivo DOCX dañado (ZIP corrupto); el respaldo vigente es el DOCX de `revision-snit/para-enviar/` (2026-07-02 18:56) migrado a `3-actual/`
- `mocupp-pastos/nacionales/Cobertura de pastos Costa Rica 2021.docx` — omitido: versión anterior, reemplazada por la de `nacionales/para-enviar/` migrada a `2-revision-snit/`
- `mocupp-pastos/nacionales/Cobertura de pastos Costa Rica 2022.docx` — omitido: versión anterior, reemplazada por la de `nacionales/para-enviar/` migrada a `2-revision-snit/`
- `mocupp-pastos/nacionales/Cobertura arbórea en paisaje productivo de pastos en Costa Rica 2021.docx` — omitido: versión anterior, reemplazada por la de `nacionales/para-enviar/` migrada a `2-revision-snit/`
- `mocupp-pastos/nacionales/Cobertura arbórea en paisaje productivo de pastos en Costa Rica 2022.docx` — omitido: versión anterior, reemplazada por la de `nacionales/para-enviar/` migrada a `2-revision-snit/`
- `mocupp-pastos/nacionales/Pérdida y ganancia de cobertura arbórea sobre paisaje productivo de pastos en Costa Rica 2021-2022.docx` — omitido: versión anterior, reemplazada por la de `nacionales/para-enviar/` migrada a `2-revision-snit/`
- `mocupp-pastos/revision-snit/GUIA_CORRECCIONES_SNIT_PASTOS.md` — omitido de `metadatos/`: se migra aparte a `docs/` (a cargo de otro proceso)

### (raíz de metadatos/)

- `metadatos_capas_mocupp_campos_en_filas.xlsx` — omitido: artefacto generado por `generar_excel_metadatos.py`, regenerable
- `metadatos_capas_mocupp_campos_en_columnas.xlsx` — omitido: artefacto generado por `generar_excel_metadatos.py`, regenerable

No existían archivos `bak*.xml` al momento de la migración; ningún archivo quedó sin clasificar.
