"""Generación de la imagen de vista previa (browse graphic) estilo SNIT.

Estilo de las vistas previas ya publicadas en el SNIT:
- Contorno continental de Costa Rica en negro (sin divisiones internas).
- Entidades de la capa en color (rojo por defecto) + sus centroides, para que
  los polígonos diminutos sean visibles.
- Fondo blanco con marco, encuadre a todo el país, A4 horizontal a 300 DPI.

El contorno nacional se obtiene de la capa de distritos del geoportal
(config global: snit.capa_limites) vía WFS, se disuelve al polígono
continental (excluye Isla del Coco) y se cachea en
datos/cache/limite_continental_cr.gpkg.

geopandas y matplotlib se importan dentro de las funciones para no romper el
CLI en entornos donde falten.
"""

from __future__ import annotations

import sys
from pathlib import Path

CRS_OBJETIVO = 8908  # CR-SIRGAS / CRTM05


def _url_wfs_limites(cfg_global: dict) -> str:
    snit = cfg_global.get("snit", {})
    base = snit.get("wfs_base", "https://geoportal.ucr.ac.cr/geoserver").rstrip("/")
    capa = snit.get("capa_limites", "eg:ICR_dist2011")
    workspace = capa.split(":", 1)[0]
    return (
        f"{base}/{workspace}/wfs?service=WFS&version=2.0.0&request=GetFeature"
        f"&typeNames={capa}&outputFormat=application/json&srsName=EPSG:{CRS_OBJETIVO}"
    )


def _continental(gdf):
    """Disuelve todo y se queda con el polígono de mayor área (parte continental)."""
    disuelto = gdf.dissolve()
    partes = disuelto.explode(index_parts=False).reset_index(drop=True)
    return partes.loc[[partes.geometry.area.idxmax()]]


def cargar_contorno(raiz: Path, cfg_global: dict, ruta_limites: str | None = None):
    """GeoDataFrame con el polígono continental de Costa Rica.

    Orden de preferencia: archivo indicado en `ruta_limites` > cache local >
    descarga del WFS (y se cachea para la próxima vez).
    """
    import geopandas

    if ruta_limites:
        g = geopandas.read_file(ruta_limites).to_crs(CRS_OBJETIVO)
        return _continental(g)

    cache = raiz / "datos" / "cache" / "limite_continental_cr.gpkg"
    if cache.exists():
        return geopandas.read_file(cache).to_crs(CRS_OBJETIVO)

    print("Descargando límites del WFS (solo la primera vez)...", file=sys.stderr)
    dist = geopandas.read_file(_url_wfs_limites(cfg_global)).set_crs(
        CRS_OBJETIVO, allow_override=True
    )
    cont = _continental(dist)
    try:
        cache.parent.mkdir(parents=True, exist_ok=True)
        cont.to_file(cache, driver="GPKG")
        print(f"Contorno continental cacheado en {cache}", file=sys.stderr)
    except Exception as e:  # cachear es opcional
        print(f"Aviso: no se pudo cachear el contorno ({e})", file=sys.stderr)
    return cont


def generar(
    ruta_capa: str | Path,
    salida: str | Path,
    raiz: Path,
    cfg_global: dict,
    capa_nombre: str | None = None,
    color: str = "red",
    markersize: float = 2.5,
    limites: str | None = None,
    dpi: int = 300,
) -> Path:
    """Genera la vista previa de una capa con el estilo del SNIT."""
    from .crs import _configurar_proj

    _configurar_proj()
    try:
        import geopandas
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as e:
        raise RuntimeError(
            "Falta geopandas/matplotlib. Use el entorno conda del proyecto "
            "(environment.yml)."
        ) from e

    salida = Path(salida)
    capa = geopandas.read_file(ruta_capa, layer=capa_nombre).to_crs(CRS_OBJETIVO)
    contorno = cargar_contorno(raiz, cfg_global, limites)
    print(f"Entidades: {len(capa)} | contorno listo", file=sys.stderr)

    minx, miny, maxx, maxy = contorno.total_bounds
    dx, dy, m = maxx - minx, maxy - miny, 0.03

    fig, ax = plt.subplots(figsize=(11.69, 8.27), dpi=dpi)  # A4 horizontal
    contorno.boundary.plot(ax=ax, color="black", linewidth=0.5, zorder=1)
    capa.plot(ax=ax, facecolor=color, edgecolor=color, linewidth=0.4, zorder=2)
    capa.geometry.representative_point().plot(
        ax=ax, color=color, markersize=markersize, zorder=3
    )

    ax.set_aspect("equal")
    ax.set_xlim(minx - dx * m, maxx + dx * m)
    ax.set_ylim(miny - dy * m, maxy + dy * m)
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(True)
        s.set_linewidth(0.8)
        s.set_color("black")

    salida.parent.mkdir(parents=True, exist_ok=True)
    guardar = {"dpi": dpi, "facecolor": "white"}
    if salida.suffix.lower() in (".jpg", ".jpeg"):
        guardar["pil_kwargs"] = {"quality": 92}
    fig.savefig(salida, **guardar)
    plt.close(fig)
    print(f"OK -> {salida}")
    return salida
