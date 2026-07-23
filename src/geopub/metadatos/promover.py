"""Promoción de metadatos corregidos por el SNIT a la carpeta 3-actual/.

Flujo: el XML corregido en la herramienta del SNIT se descarga a
``metadatos/<nodo>/2-revision-snit/<slug>-corregido.xml``; una vez verificado
se promueve a ``metadatos/<nodo>/3-actual/<slug>.xml`` (versión vigente).
"""

from __future__ import annotations

from pathlib import Path

SUFIJO = "-corregido"


def promover(nodo_slug: str, raiz: Path, capa_slug: str | None = None) -> list[tuple[Path, Path]]:
    """Mueve <slug>-corregido.xml de 2-revision-snit/ a 3-actual/<slug>.xml.

    Si no se indica capa, promueve todos los ``*-corregido.xml`` del nodo.
    Retorna la lista de pares (origen, destino).
    """
    dir_revision = raiz / "metadatos" / nodo_slug / "2-revision-snit"
    dir_actual = raiz / "metadatos" / nodo_slug / "3-actual"

    if capa_slug:
        candidatos = [dir_revision / f"{capa_slug}{SUFIJO}.xml"]
        if not candidatos[0].is_file():
            raise FileNotFoundError(f"No existe {candidatos[0]}")
    else:
        candidatos = sorted(dir_revision.glob(f"*{SUFIJO}.xml"))
        if not candidatos:
            raise FileNotFoundError(f"No hay *{SUFIJO}.xml en {dir_revision}")

    movidos = []
    dir_actual.mkdir(parents=True, exist_ok=True)
    for origen in candidatos:
        slug = origen.stem.removesuffix(SUFIJO)
        destino = dir_actual / f"{slug}.xml"
        origen.rename(destino)
        print(f"{origen.name} -> {destino}")
        movidos.append((origen, destino))
    return movidos
