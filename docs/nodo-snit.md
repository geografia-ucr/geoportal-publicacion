# Alta y gestión de un subnodo del SNIT

Cómo se registra un nuevo subnodo (nodo temático) de la UCR en el
[Sistema Nacional de Información Territorial (SNIT)](https://www.snitcr.go.cr/).
Basado en los tres formularios enviados para los subnodos MOCUPP
(`docs/historico/formulario_snit_mocupp_{musaceas,cafe,pastos}.txt`).

## Proceso

1. **Publicar primero el workspace en GeoServer** (ver
   [`flujo-publicacion.md`](flujo-publicacion.md)): el formulario pide las URL de los
   geoservicios WMS/WFS ya funcionando, con su regla ALLOW en GeoFence.
2. **Completar el formulario de información del nodo** (plantilla abajo) y enviarlo
   al SNIT. Es un trámite manual por correo/coordinación con el SNIT; no hay API.
3. El SNIT crea el subnodo y habilita el **usuario para metadatos** con el que se
   cargan los XML en su herramienta en línea (GeoNetwork del SNIT).
4. Cargar los metadatos de cada capa y enviarlos a revisión
   (ver [`flujo-publicacion.md`](flujo-publicacion.md) paso 7 y
   [`correcciones-snit.md`](correcciones-snit.md)).

## Datos institucionales de referencia (EG-UCR)

Valores usados de forma consistente en los tres subnodos existentes:

| Campo | Valor |
|---|---|
| Institución | Universidad de Costa Rica (UCR) |
| Persona encargada del nodo | Melvin Lizano Araya |
| Correo del nodo / usuario para metadatos | geoportal@ucr.ac.cr |
| Teléfono del nodo (formulario) | 25116402 |
| Sitio web | https://www.geografia.fcs.ucr.ac.cr/ |
| Visor de la institución | https://geoportal.ucr.ac.cr/ |
| Geoservicios | `https://geoportal.ucr.ac.cr/geoserver/<workspace>/wms` y `…/wfs` |

Contactos usados en los **metadatos** de las capas (pueden diferir de los del
formulario del nodo):

- **Punto de contacto**: Melvin Lizano Araya — melvin.lizanoaraya@ucr.ac.cr,
  Escuela de Geografía UCR, tel. (+506) 2511-4592.
- **Autor del metadato**: Manuel Vargas Del Valle — manuel.vargas_d@ucr.ac.cr,
  Escuela de Geografía UCR, tel. (+506) 2511-4592.

## Plantilla del formulario

```
FORMULARIO: Información para la publicación de un nodo en el SNIT
Subnodo: <nombre>
===========================================================================

Nombre del nodo:                <nombre>
Nombre de la institución:       Universidad de Costa Rica (UCR)
Descripción del nodo:           <párrafo: qué capas contiene, proyecto, temática,
                                 periodicidad, atributos principales>
Nombre de la persona encargada: Melvin Lizano Araya
Correo electrónico:             geoportal@ucr.ac.cr
Teléfono:                       25116402
Sitio web:                      https://www.geografia.fcs.ucr.ac.cr/
Geoservicios (URL) WMS:         https://geoportal.ucr.ac.cr/geoserver/<workspace>/wms
Geoservicios (URL) WFS:         https://geoportal.ucr.ac.cr/geoserver/<workspace>/wfs
Usuario para metadatos:         geoportal@ucr.ac.cr
Visor de la institución:        https://geoportal.ucr.ac.cr/

---------------------------------------------------------------------------
Capas incluidas en el geoservicio
---------------------------------------------------------------------------

Nombre de la capa                  | Capa oficial? | Fundamento legal
-----------------------------------|---------------|------------------
<typeName de cada capa>            | No            |
```

La tabla lista los `typeName` técnicos de las capas del workspace. En los tres
subnodos MOCUPP ninguna capa es "oficial" (sin fundamento legal); si alguna capa
futura lo fuera, indicar el fundamento en la última columna.

## Formularios enviados (referencia)

### MOCUPP - Musáceas (`mocupp_musaceas`)

- Descripción: "Capas generadas por el proyecto MOCUPP (Monitoreo del Cambio de Uso y
  Cobertura de la Tierra en Paisajes Productivos) sobre áreas de cultivo de musáceas
  (banano y plátano) en Costa Rica. Incluye información anual de cobertura con detalle
  de clase de cultivo, región y área en hectáreas."
- Capas listadas: `musaceas_cr_2021`, `musaceas_cr_2022`.

### MOCUPP - Café (`mocupp_cafe`)

- Descripción: "Capas generadas por el proyecto MOCUPP (…) sobre áreas de cultivo de
  café y cobertura arbórea en paisajes productivos de café en Costa Rica. Incluye
  información anual de cobertura y análisis de pérdida y ganancia de cultivo de café y
  cobertura arbórea entre periodos, con detalle de uso, categoría y área en hectáreas."
- Capas listadas: `cultivo_cafe_2021`, `cultivo_cafe_2022`, `cobertura_arborea_2021`,
  `cobertura_arborea_2022`, `perdida_cobertura_arborea`,
  `perdida_ganancia_cultivo_cafe`.

### MOCUPP - Pastos (`mocupp_pastos`)

- Descripción: "Capas generadas por el proyecto MOCUPP (…) sobre cobertura de pastos y
  cobertura arbórea en paisajes productivos de pastos en Costa Rica. Incluye
  información anual de cobertura y análisis de pérdida y ganancia de cobertura arbórea
  entre periodos, con detalle de uso, categoría y área en hectáreas."
- Capas listadas (las 10 regionales Brunca originales): `Paisaje_cobertura_arborea_2020/2021/2022`,
  `Paisaje_cobertura_pastos_2020/2021/2022` y las 4
  `Perdida_ganancia_cobertura_arborea_sobre_paisaje_productivo_de_pastos_*`.
  (Posteriormente se agregaron las 5 capas nacionales `*_cr_*` al mismo workspace y
  las 10 regionales fueron deshabilitadas en GeoServer.)

## Gestión posterior

- Si se agregan capas a un workspace ya registrado como subnodo, no se rellena un
  formulario nuevo: se cargan los metadatos de las capas nuevas con el usuario para
  metadatos del subnodo (así se hizo con las 5 capas nacionales de pastos).
- Los cambios de capas (deshabilitar, renombrar títulos) pueden dejar desactualizados
  los metadatos ya publicados en el SNIT que apuntan al WFS/WMS — coordinar con el
  SNIT cuando aplique.
