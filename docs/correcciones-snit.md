# Ciclo de revisión y corrección de metadatos en el SNIT

Generalización de la experiencia con las revisiones de café (2026-06) y pastos
(2026-06/07). La guía original, específica de pastos, está en el repo viejo
(`metadatos/mocupp-pastos/revision-snit/GUIA_CORRECCIONES_SNIT_PASTOS.md`).

## Cómo funciona el ciclo

1. **Se cargan los XML** de las capas en la herramienta en línea del SNIT y se envían
   a revisión (ver [`flujo-publicacion.md`](flujo-publicacion.md), paso 7).
2. **El SNIT devuelve un DOCX por capa** (`*_rev.docx`) con las observaciones de la
   persona revisora: el texto en **rojo** (color `EE0000`) es lo corregido/insertado;
   el texto negro adyacente es lo viejo a eliminar. Puede haber además **comentarios
   al margen** (sugerencias, no obligatorias).
3. **Las correcciones se aplican en la herramienta en línea del SNIT** (su editor
   GeoNetwork), **no editando el XML local**. Editar el XML local no sirve: GeoNetwork
   es la fuente de verdad y al reimportar sobrescribe o regenera varios campos.
4. **Verificar contra el registro vivo** con la URL pública
   `…ver_xml_publico?key=<base64>` (devuelve el XML crudo, sin autenticación).
5. **Descargar el XML corregido** y guardarlo en
   `metadatos/<nodo>/2-revision-snit/<slug>-corregido.xml`. Hacer un diff contra la
   versión previa para confirmar que solo cambió lo esperado.
6. **Promover a `metadatos/<nodo>/3-actual/`** (`geopub metadatos promover <slug>`)
   cuando el diff está limpio. El archivo promovido debe ser una **descarga genuina**
   del SNIT, no un XML parchado a mano.
7. **Avisar a la persona revisora** (correo) cuando todas las capas estén corregidas,
   y dar seguimiento hasta la aprobación.

Para extraer el texto de un `.docx` de revisión sin abrir Word:

```bash
unzip -p archivo.docx word/document.xml | sed 's/<\/w:p>/\n/g; s/<[^>]*>//g'
```

## Correcciones típicas pedidas por el SNIT

(Observadas en las revisiones de café y pastos; sirven de lista de chequeo preventiva
al generar metadatos nuevos.)

- **Identificador del metadato**: patrón con guiones bajos exactos, p. ej.
  `CR_EG-UCR_<COD>_<años>_10K_VE` (el sufijo `_VE` va separado con guion bajo).
- **Título alternativo**: el código sin `CR_` y sin `VE` (`EG-UCR_<COD>_<años>_10K`).
- **Tipos de palabra clave**: "Producto" → "Tema" cuando corresponde; palabras de
  lugar ordenadas y contiguas, incluyendo siempre "Costa Rica" (más la región si
  aplica, p. ej. "Región Brunca").
- **Restricción de uso**: texto estándar "Su uso tendrá carácter libre y gratuito,
  siempre que se mencione el origen y propiedad de los datos."
- **Función del recurso en línea**: "Navegación" → "Información".
- **Clase o tipo de objeto geográfico** (scope): "Cobertura".
- **Información suplementaria**: no dejar el texto-guía de la plantilla
  ("En este campo podría colocar…"); llenar o vaciar el campo.
- **Redacción** de resumen/propósito/linaje: tildes, palabras duplicadas, años
  correctos por capa.
- Sugerencias frecuentes de la revisora: ampliar el propósito ("…la cual es relevante
  para diversos fines agropecuarios, ambientales, históricos, entre otros.") y llenar
  el crédito con la unidad que generó la capa.

**Verificar también el DOCX de la revisora**: puede arrastrar erratas (años de otra
capa copiados, `V1` escrito como `VI`, omisiones de una corrección que sí pidió en las
capas hermanas). Ante inconsistencias, aplicar el criterio consistente con el resto de
las capas y anotarlo.

## Trampas conocidas de la herramienta del SNIT / GeoNetwork

- **Advertencias PHP antepuestas al XML descargado**: el servidor del SNIT a veces
  antepone avisos de PHP (p. ej. "No space left on device") al XML. Limpiarlas antes
  de parsear o hacer diff.
- **El export puede vaciar campos que el registro vivo sí conserva**:
  - `administrativeArea` (provincia) de un contacto puede llegar vacío — re-descargar
    hasta obtener una copia completa; no parchear a mano.
  - La **URL de distribución** (`distributionInfo//linkage`) llega vacía en el export
    aunque el registro vivo la conserva (se ve en la herramienta como "URL para el
    servicio OGC"). No es un problema real: verificar en el editor/registro vivo, no
    solo en el XML descargado.
- **GeoNetwork regenera el `graphicOverview`**: la URL de la vista previa se genera
  desde la miniatura adjunta al registro; URLs pegadas a mano en el XML se pierden.
  La imagen se adjunta en el editor (sección Resumen gráfico).
- **GeoNetwork reinyecta teléfonos placeholder** `(+506) ____-____` desde su
  plantilla; se borran en el editor.
- **El borrador descargado a veces llega como `data.xml`** — renombrarlo al nombre de
  la capa antes de guardarlo en el repo.
- Otros artefactos cosméticos del export: tipo de geometría "Compuesto", descripción
  del recurso en línea igual al nombre de la capa, y el correo del autor del metadato
  inyectado como correo de la organización. El contenido sustantivo (título, CRS,
  conteo, keywords, restricciones, personas de contacto) sí persiste.

## Convención de archivos en este repo

```
metadatos/<nodo>/
├── 1-borrador/        # XML/DOCX fuente generados localmente
├── 2-revision-snit/   # DOCX de la revisora + <slug>-corregido.xml descargados
├── 3-actual/          # XML aprobados/promovidos (descargas genuinas del SNIT)
└── vistas-previas/    # imágenes de vista previa (browse graphics)
```
