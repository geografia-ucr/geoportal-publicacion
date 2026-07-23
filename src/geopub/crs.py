"""Verificación de CRS de archivos geoespaciales.

Toda capa publicada debe usar CR-SIRGAS / CRTM05 (EPSG:8908). Este módulo
clasifica cada archivo en CORRECTO / REQUIERE TRANSFORMACIÓN / REVISAR /
SIN CRS y, para shapefiles, verifica además que el juego de archivos esté
completo (shp+shx+dbf+prj) y que declare su codificación (.cpg).

GDAL se importa dentro de las funciones que lo necesitan, para que el resto
del paquete funcione en entornos sin GDAL.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

EXTENSIONES_VECTORIALES = {".shp", ".geojson", ".gpkg", ".kml", ".gml"}
EXTENSIONES_RASTER = {".tif", ".tiff"}
EXTENSIONES = EXTENSIONES_VECTORIALES | EXTENSIONES_RASTER

# Categorías de CRS
CORRECTO = "CORRECTO"
REQUIERE_TRANSFORMACION = "REQUIERE TRANSFORMACIÓN"
REVISAR = "REVISAR"
SIN_CRS = "SIN CRS"
CATEGORIAS = (CORRECTO, REQUIERE_TRANSFORMACION, REVISAR, SIN_CRS)


@dataclass
class Resultado:
    """Resultado de la verificación de un archivo."""

    ruta: str
    categoria: str
    crs: str
    avisos: list[str] = field(default_factory=list)


def clasificar_crs(srs) -> tuple[str, str]:
    """Clasifica un osgeo.osr.SpatialReference. Retorna (categoría, descripción)."""
    if srs is None:
        return SIN_CRS, "No definido"

    srs.AutoIdentifyEPSG()
    codigo_epsg = srs.GetAuthorityCode(None)

    if codigo_epsg == "8908":
        return CORRECTO, "CR-SIRGAS / CRTM05 (EPSG:8908)"
    if codigo_epsg == "5367":
        return REQUIERE_TRANSFORMACION, "CR05 / CRTM05 (EPSG:5367)"

    nombre_crs = srs.GetName() or ""
    nombre_datum = srs.GetAttrValue("DATUM") or ""
    texto = (nombre_crs + " " + nombre_datum).upper()

    if "CR-SIRGAS" in texto or "CR_SIRGAS" in texto or "CRSIRGAS" in texto:
        return CORRECTO, f"CR-SIRGAS / CRTM05 ({nombre_crs})"
    if "CR05" in texto or "CR_05" in texto:
        return REQUIERE_TRANSFORMACION, f"CR05 / CRTM05 ({nombre_crs})"

    desc = nombre_crs
    if codigo_epsg:
        desc += f" (EPSG:{codigo_epsg})"
    return REVISAR, desc or "Desconocido"


def verificar_juego_shapefile(ruta_shp: str | os.PathLike) -> list[str]:
    """Verifica que un shapefile tenga el juego completo de archivos.

    Retorna una lista de avisos: componentes obligatorios faltantes
    (shx, dbf, prj) y .cpg ausente (codificación no declarada).
    """
    ruta = Path(ruta_shp)
    avisos = []
    for ext, descripcion in ((".shx", "índice"), (".dbf", "atributos"), (".prj", "CRS")):
        if not ruta.with_suffix(ext).is_file():
            avisos.append(f"falta {ruta.stem}{ext} ({descripcion})")
    cpg = ruta.with_suffix(".cpg")
    if cpg.is_file():
        codificacion = cpg.read_text(encoding="ascii", errors="replace").strip()
        if codificacion.upper() not in {"UTF-8", "UTF8"}:
            avisos.append(f"codificación declarada en .cpg: {codificacion} (se recomienda UTF-8)")
    else:
        avisos.append("falta .cpg (codificación no declarada)")
    return avisos


def _configurar_proj() -> None:
    """Apunta PROJ a sus datos si el entorno conda no fue activado formalmente."""
    import sys

    if "PROJ_DATA" not in os.environ and "PROJ_LIB" not in os.environ:
        candidato = Path(sys.prefix) / "share" / "proj"
        if (candidato / "proj.db").is_file():
            os.environ["PROJ_DATA"] = str(candidato)


def _obtener_crs_vectorial(ruta: str):
    from osgeo import ogr

    ds = ogr.Open(ruta)
    if ds is None:
        return None
    capa = ds.GetLayer()
    if capa is None:
        return None
    return capa.GetSpatialRef()


def _obtener_crs_raster(ruta: str):
    from osgeo import gdal, osr

    ds = gdal.Open(ruta)
    if ds is None:
        return None
    wkt = ds.GetProjection()
    if not wkt:
        return None
    srs = osr.SpatialReference()
    srs.ImportFromWkt(wkt)
    return srs


def verificar_archivo(ruta: str | os.PathLike) -> Resultado:
    """Verifica el CRS (y extras) de un archivo geoespacial."""
    _configurar_proj()
    from osgeo import gdal

    gdal.UseExceptions()
    ruta = str(ruta)
    ext = os.path.splitext(ruta)[1].lower()
    try:
        if ext in EXTENSIONES_VECTORIALES:
            srs = _obtener_crs_vectorial(ruta)
        else:
            srs = _obtener_crs_raster(ruta)
        categoria, descripcion = clasificar_crs(srs)
    except Exception as e:
        categoria, descripcion = REVISAR, f"Error al leer: {e}"

    avisos = verificar_juego_shapefile(ruta) if ext == ".shp" else []
    return Resultado(ruta=ruta, categoria=categoria, crs=descripcion, avisos=avisos)


def buscar_archivos(directorio: str | os.PathLike) -> list[str]:
    """Busca archivos geoespaciales (recursivamente) en un directorio."""
    encontrados = []
    for raiz, _dirs, nombres in os.walk(directorio):
        for nombre in sorted(nombres):
            if os.path.splitext(nombre)[1].lower() in EXTENSIONES:
                encontrados.append(os.path.join(raiz, nombre))
    return sorted(encontrados)


def verificar_directorio(directorio: str | os.PathLike) -> list[Resultado]:
    """Verifica todos los archivos geoespaciales de un directorio."""
    return [verificar_archivo(ruta) for ruta in buscar_archivos(directorio)]


def imprimir_resultados(resultados: list[Resultado], base: str | os.PathLike = ".") -> dict:
    """Imprime los resultados y un resumen. Retorna los totales por categoría."""
    totales = {c: 0 for c in CATEGORIAS}
    for r in resultados:
        totales[r.categoria] += 1
        nombre = os.path.relpath(r.ruta, base)
        print(f"  [{r.categoria}] {nombre}")
        print(f"           CRS: {r.crs}")
        for aviso in r.avisos:
            print(f"           Aviso: {aviso}")

    print("=" * 70)
    print("RESUMEN")
    print(f"  Total de archivos: {sum(totales.values())}")
    print(f"  Correctos (CR-SIRGAS / CRTM05):      {totales[CORRECTO]}")
    print(f"  Requieren transformación (CR05):     {totales[REQUIERE_TRANSFORMACION]}")
    print(f"  Requieren revisión (otro CRS):       {totales[REVISAR]}")
    print(f"  Sin CRS definido:                    {totales[SIN_CRS]}")
    return totales
