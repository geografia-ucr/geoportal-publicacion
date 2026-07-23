"""Ejecución de las transformaciones declaradas en el YAML de cada capa.

Tipos soportados (bloque ``transformaciones`` de la capa):

- ``ogr2ogr``: ejecuta el comando declarado, sustituyendo ``{entrada}`` y
  ``{salida}`` (p. ej. reproyección EPSG:5367 → EPSG:8908, o ``-nln`` para
  renombrar la capa interna de un GeoPackage).
- ``renombrado``: copia el archivo fuente con el nombre definitivo; para
  shapefiles copia todos los archivos hermanos (shp, shx, dbf, prj, cpg).
- ``otro``: no se ejecuta; se imprime la descripción (paso manual).

Al final se registra el sha256 del archivo resultante (para pegarlo en el
YAML de la capa).
"""

from __future__ import annotations

import hashlib
import shlex
import shutil
import subprocess
from pathlib import Path

EXTENSIONES_SHAPEFILE = (".shp", ".shx", ".dbf", ".prj", ".cpg")


def sha256_archivo(ruta: str | Path) -> str:
    """Calcula el sha256 de un archivo."""
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def _ruta_entrada(capa: dict, raiz: Path, slug_nodo: str) -> Path | None:
    """Resuelve la ruta del archivo fuente de la capa (si está declarada)."""
    fuente = capa.get("fuente") or {}
    original = fuente.get("archivo_original")
    if not original:
        return None
    ubicacion = fuente.get("ubicacion")
    if ubicacion:
        base = Path(ubicacion)
        if not base.is_absolute():
            base = raiz / base
        return base / original
    return raiz / "datos" / slug_nodo / original


def _copiar_juego(entrada: Path, salida: Path, dry_run: bool) -> None:
    """Copia entrada→salida; si es shapefile, copia todos los hermanos."""
    pares = [(entrada, salida)]
    if entrada.suffix.lower() == ".shp":
        pares = [
            (entrada.with_suffix(ext), salida.with_suffix(ext))
            for ext in EXTENSIONES_SHAPEFILE
            if entrada.with_suffix(ext).is_file()
        ]
    for origen, destino in pares:
        print(f"  cp {origen} -> {destino}")
        if not dry_run:
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(origen, destino)


def transformar_capa(nodo: dict, capa: dict, raiz: Path, dry_run: bool = False) -> dict:
    """Ejecuta las transformaciones de una capa. Retorna {'salida': ..., 'sha256': ...}."""
    slug_nodo = nodo["nodo"]["slug"]
    salida = raiz / "datos" / slug_nodo / capa["archivo"]
    entrada = _ruta_entrada(capa, raiz, slug_nodo)

    transformaciones = capa.get("transformaciones") or []
    if not transformaciones:
        print(f"[{capa['slug']}] sin transformaciones declaradas")
    for t in transformaciones:
        tipo = t["tipo"]
        print(f"[{capa['slug']}] {tipo}: {t['descripcion']}")
        if tipo == "ogr2ogr":
            comando = t["comando"].format(entrada=entrada, salida=salida)
            print(f"  $ {comando}")
            if not dry_run:
                salida.parent.mkdir(parents=True, exist_ok=True)
                subprocess.run(shlex.split(comando), check=True)
        elif tipo == "renombrado":
            if entrada is None:
                raise ValueError(
                    f"La capa {capa['slug']!r} declara 'renombrado' pero no tiene "
                    "fuente.archivo_original"
                )
            _copiar_juego(entrada, salida, dry_run)
        else:  # otro: paso manual documentado
            print("  (paso manual, no se ejecuta)")

    resultado = {"capa": capa["slug"], "salida": str(salida), "sha256": None}
    if not dry_run and salida.is_file():
        resultado["sha256"] = sha256_archivo(salida)
        print(f"  sha256: {resultado['sha256']}")
    return resultado


def transformar_nodo(
    nodo: dict, raiz: Path, capa_slug: str | None = None, dry_run: bool = False
) -> list[dict]:
    """Ejecuta las transformaciones de todas las capas del nodo (o de una)."""
    capas = nodo["capas"]
    if capa_slug:
        capas = [c for c in capas if c["slug"] == capa_slug]
        if not capas:
            raise KeyError(f"No existe la capa {capa_slug!r} en el nodo")
    return [transformar_capa(nodo, capa, raiz, dry_run=dry_run) for capa in capas]
