"""Validación de metadatos ISO 19115-3 antes de enviarlos al SNIT.

Comprueba buena formación (lxml) y la presencia de los campos obligatorios:
título, resumen, CRS EPSG:8908, punto de contacto, bbox, palabras clave y
linkage de distribución. En modo offline (por defecto) no toca la red; en
modo online verifica además que la URL de distribución responda.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Verificacion:
    campo: str
    ok: bool
    detalle: str = ""


def _xp(raiz, camino: str) -> list[str]:
    """xpath por local-name(); devuelve textos limpios no vacíos."""
    partes = "/".join(f"*[local-name()='{p}']" for p in camino.split("/"))
    valores = []
    for v in raiz.xpath(f"//{partes}/text()"):
        v = " ".join(str(v).split())
        if v:
            valores.append(v)
    return valores


def validar_archivo(ruta: str | Path, offline: bool = True) -> list[Verificacion]:
    """Valida un XML de metadatos. Retorna la lista de verificaciones."""
    from lxml import etree

    ruta = Path(ruta)
    try:
        raiz = etree.parse(str(ruta)).getroot()
    except etree.XMLSyntaxError as e:
        return [Verificacion("XML bien formado", False, str(e))]

    v = [Verificacion("XML bien formado", True)]

    titulo = _xp(raiz, "identificationInfo/MD_DataIdentification/citation/CI_Citation/title/CharacterString")
    v.append(Verificacion("Título", bool(titulo), titulo[0] if titulo else "ausente o vacío"))

    resumen = _xp(raiz, "abstract/CharacterString")
    v.append(
        Verificacion(
            "Resumen", bool(resumen), f"{len(resumen[0])} caracteres" if resumen else "ausente o vacío"
        )
    )

    crs = _xp(raiz, "referenceSystemInfo/MD_ReferenceSystem/referenceSystemIdentifier/MD_Identifier/code/CharacterString")
    ok_crs = any("8908" in c for c in crs)
    v.append(
        Verificacion(
            "CRS EPSG:8908", ok_crs, "; ".join(crs) if crs else "sin sistema de referencia"
        )
    )

    contacto = raiz.xpath(
        "//*[local-name()='identificationInfo']//*[local-name()='pointOfContact']"
        "//*[local-name()='name']/*[local-name()='CharacterString']/text()"
    )
    contacto = [c for c in ("".join(x.split()) for x in contacto) if c]
    v.append(
        Verificacion(
            "Punto de contacto", bool(contacto), "presente" if contacto else "ausente o vacío"
        )
    )

    lados = {
        "oeste": _xp(raiz, "westBoundLongitude/Decimal"),
        "este": _xp(raiz, "eastBoundLongitude/Decimal"),
        "sur": _xp(raiz, "southBoundLatitude/Decimal"),
        "norte": _xp(raiz, "northBoundLatitude/Decimal"),
    }
    faltantes = [lado for lado, val in lados.items() if not val]
    if faltantes:
        v.append(Verificacion("Bbox", False, f"faltan: {', '.join(faltantes)}"))
    else:
        try:
            o, e = float(lados["oeste"][0]), float(lados["este"][0])
            s, n = float(lados["sur"][0]), float(lados["norte"][0])
            ok_orden = o < e and s < n
            detalle = "" if ok_orden else f"orden inválido (O={o} E={e} S={s} N={n})"
            v.append(Verificacion("Bbox", ok_orden, detalle))
        except ValueError:
            v.append(Verificacion("Bbox", False, "valores no numéricos"))

    keywords = _xp(raiz, "descriptiveKeywords/MD_Keywords/keyword/CharacterString")
    v.append(
        Verificacion(
            "Palabras clave", bool(keywords), f"{len(keywords)} encontradas" if keywords else "ninguna"
        )
    )

    linkage = _xp(raiz, "distributionInfo/MD_Distribution/transferOptions/MD_DigitalTransferOptions/onLine/CI_OnlineResource/linkage/CharacterString")
    v.append(
        Verificacion(
            "Linkage de distribución",
            bool(linkage),
            linkage[0] if linkage else "ausente o vacío (OJO: GeoNetwork lo vacía al exportar; "
            "verificar en el registro vivo del SNIT)",
        )
    )

    if not offline and linkage:
        import requests

        try:
            r = requests.head(linkage[0], timeout=15, allow_redirects=True)
            v.append(
                Verificacion(
                    "URL de distribución accesible", r.ok, f"HTTP {r.status_code}"
                )
            )
        except requests.RequestException as e:
            v.append(Verificacion("URL de distribución accesible", False, str(e)))

    return v


def imprimir_verificaciones(ruta: str | Path, verificaciones: list[Verificacion]) -> bool:
    """Imprime el resultado de un archivo. Retorna True si todo pasó."""
    todo_ok = all(x.ok for x in verificaciones)
    print(f"\n{ruta}")
    for x in verificaciones:
        marca = "OK " if x.ok else "FALLA"
        detalle = f" — {x.detalle}" if x.detalle else ""
        print(f"  [{marca}] {x.campo}{detalle}")
    return todo_ok
