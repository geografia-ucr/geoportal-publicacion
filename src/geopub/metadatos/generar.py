"""Generación de borradores de metadatos ISO 19115-3 para el SNIT.

Dos modos de trabajo (heredados de la experiencia con mocupp-pastos):

1. **Plantilla con marcadores** (por defecto): rellena los marcadores
   ``{{TITULO}}``, ``{{RESUMEN}}``, etc. de una plantilla XML con los valores
   del YAML del nodo. La plantilla incluida en
   ``src/geopub/metadatos/plantillas/plantilla_snit.xml`` es mínima; sirve
   como punto de partida para completar en el editor del SNIT.

2. **Clonación de un XML aprobado** (el método que mejor funcionó): tomar un
   XML de ``metadatos/<nodo>/3-actual/`` y aplicar sustituciones exactas con
   ``aplicar_reemplazos`` / ``reemplazar_unico`` (cada reemplazo verifica que
   la cadena exista exactamente una vez).

El resultado se escribe en ``metadatos/<nodo>/1-borrador/<slug>.xml``.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

MARCADOR = re.compile(r"\{\{([A-Z_]+)\}\}")
PLANTILLA_INCLUIDA = Path(__file__).parent / "plantillas" / "plantilla_snit.xml"

# bbox aproximado de la parte continental de Costa Rica (EPSG:4326), usado
# cuando no se puede calcular el de la capa. Revisar antes de enviar al SNIT.
BBOX_COSTA_RICA = {"OESTE": "-85.96", "ESTE": "-82.53", "SUR": "8.03", "NORTE": "11.22"}


def reemplazar_unico(texto: str, viejo: str, nuevo: str) -> str:
    """Reemplaza una cadena verificando que exista exactamente una vez."""
    n = texto.count(viejo)
    if n != 1:
        raise ValueError(f"Se esperaba 1 ocurrencia de {viejo!r}, hay {n}")
    return texto.replace(viejo, nuevo)


def aplicar_reemplazos(xml: str, reemplazos: dict[str, str]) -> str:
    """Aplica un dict {viejo: nuevo} con reemplazar_unico (motor de clonación)."""
    for viejo, nuevo in reemplazos.items():
        xml = reemplazar_unico(xml, viejo, nuevo)
    return xml


def _bbox_capa(ruta_datos: Path) -> dict[str, str] | None:
    """Intenta calcular el bbox (EPSG:4326) de la capa con GDAL; None si no se puede."""
    try:
        from osgeo import ogr, osr

        ds = ogr.Open(str(ruta_datos))
        if ds is None:
            return None
        capa = ds.GetLayer()
        minx, maxx, miny, maxy = capa.GetExtent()
        origen = capa.GetSpatialRef()
        destino = osr.SpatialReference()
        destino.ImportFromEPSG(4326)
        destino.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
        if origen is not None:
            origen.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
            tx = osr.CoordinateTransformation(origen, destino)
            minx, miny, _ = tx.TransformPoint(minx, miny)
            maxx, maxy, _ = tx.TransformPoint(maxx, maxy)
        return {
            "OESTE": f"{minx:.5f}",
            "ESTE": f"{maxx:.5f}",
            "SUR": f"{miny:.5f}",
            "NORTE": f"{maxy:.5f}",
        }
    except Exception:
        return None


def _keywords_xml(palabras: list[str]) -> str:
    bloques = [
        "          <mri:keyword>\n"
        f"            <gco:CharacterString>{p}</gco:CharacterString>\n"
        "          </mri:keyword>"
        for p in palabras
    ]
    return "\n".join(bloques)


def valores_capa(nodo: dict, capa: dict, cfg_global: dict, raiz: Path) -> dict[str, str]:
    """Valores de los marcadores de la plantilla, a partir del YAML del nodo."""
    info_nodo = nodo["nodo"]
    workspace = info_nodo["workspace"]
    url_gs = cfg_global.get("geoserver", {}).get("url", "").rstrip("/")
    metadatos = capa.get("metadatos") or {}

    ruta_datos = raiz / "datos" / info_nodo["slug"] / capa["archivo"]
    bbox = (_bbox_capa(ruta_datos) if ruta_datos.exists() else None) or BBOX_COSTA_RICA

    return {
        "IDENTIFICADOR": metadatos.get("identificador_snit") or "",
        "TITULO": capa["titulo"],
        "RESUMEN": capa.get("abstract", ""),
        "FECHA": date.today().isoformat(),
        "CRS": capa.get("crs_destino", "EPSG:8908"),
        "ORGANIZACION": info_nodo.get(
            "responsable", "Escuela de Geografía, Universidad de Costa Rica"
        ),
        "CONTACTO": info_nodo.get("contacto", ""),
        "PALABRAS_CLAVE_XML": _keywords_xml(capa.get("palabras_clave") or []),
        "URL_SERVICIO": f"{url_gs}/{workspace}/wms",
        "NOMBRE_CAPA": capa["slug"],
        "DESCRIPCION_RECURSO": capa.get("abstract", capa["titulo"]),
        **bbox,
    }


def generar_capa(
    nodo: dict,
    capa: dict,
    raiz: Path,
    cfg_global: dict,
    plantilla: str | Path | None = None,
    reemplazos: dict[str, str] | None = None,
) -> Path:
    """Genera metadatos/<nodo>/1-borrador/<slug>.xml a partir de la plantilla.

    - Si la plantilla tiene marcadores ``{{ASI}}``, se rellenan con los
      valores del YAML (modo 1).
    - Si además (o en su lugar) se pasa `reemplazos`, se aplican con
      reemplazar_unico (modo 2, clonación de un XML aprobado).
    """
    ruta_plantilla = Path(plantilla) if plantilla else PLANTILLA_INCLUIDA
    xml = ruta_plantilla.read_text(encoding="utf-8")

    if MARCADOR.search(xml):
        valores = valores_capa(nodo, capa, cfg_global, raiz)

        def sustituir(m: re.Match) -> str:
            nombre = m.group(1)
            if nombre not in valores:
                raise ValueError(f"Marcador sin valor definido: {{{{{nombre}}}}}")
            return valores[nombre]

        xml = MARCADOR.sub(sustituir, xml)

    if reemplazos:
        xml = aplicar_reemplazos(xml, reemplazos)

    # Verificación de buena formación antes de escribir
    from lxml import etree

    etree.fromstring(xml.encode("utf-8"))

    salida = raiz / "metadatos" / nodo["nodo"]["slug"] / "1-borrador" / f"{capa['slug']}.xml"
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(xml, encoding="utf-8")
    print(f"OK -> {salida}")
    return salida


def generar_nodo(
    nodo: dict,
    raiz: Path,
    cfg_global: dict,
    capa_slug: str | None = None,
    plantilla: str | Path | None = None,
) -> list[Path]:
    """Genera los borradores de todas las capas del nodo (o de una)."""
    capas = nodo["capas"]
    if capa_slug:
        capas = [c for c in capas if c["slug"] == capa_slug]
        if not capas:
            raise KeyError(f"No existe la capa {capa_slug!r} en el nodo")
    return [
        generar_capa(nodo, capa, raiz, cfg_global, plantilla=plantilla) for capa in capas
    ]
