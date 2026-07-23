"""Carga y validación de la configuración del proyecto.

- ``config/global.yml``: parámetros globales (GeoServer, servidor, SNIT...).
- ``config/nodos/<slug>.yml``: definición de cada nodo (workspace + capas),
  validada contra ``config/esquema-nodo.json``.
- ``.env``: credenciales (nunca van en los YAML).
"""

from __future__ import annotations

import copy
import json
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv
from jsonschema import Draft202012Validator

# Defaults aplicados a cada capa cuando ni la capa ni el bloque `defaults`
# del nodo los definen.
DEFAULTS_BASE = {
    "crs_destino": "EPSG:8908",
    "formato": "shapefile",
    "destinos": {"snit": True, "geonode": False},
}


def raiz_repo(inicio: str | os.PathLike | None = None) -> Path:
    """Busca el directorio raíz del repositorio (el que contiene pyproject.toml).

    Sube desde `inicio` (o el directorio actual); como último recurso sube
    desde la ubicación de este archivo (instalación editable).
    """
    puntos_de_partida = []
    if inicio is not None:
        puntos_de_partida.append(Path(inicio).resolve())
    else:
        puntos_de_partida.append(Path.cwd())
        puntos_de_partida.append(Path(__file__).resolve().parent)
    for base in puntos_de_partida:
        for directorio in (base, *base.parents):
            if (directorio / "pyproject.toml").is_file():
                return directorio
    raise FileNotFoundError(
        "No se encontró pyproject.toml hacia arriba; ejecute geopub desde el repositorio."
    )


def cargar_env(raiz: Path | None = None) -> None:
    """Carga las variables de entorno del archivo .env de la raíz del repo."""
    raiz = Path(raiz) if raiz else raiz_repo()
    load_dotenv(raiz / ".env")


def cargar_global(raiz: Path | None = None) -> dict:
    """Carga config/global.yml (y el .env asociado)."""
    raiz = Path(raiz) if raiz else raiz_repo()
    cargar_env(raiz)
    with open(raiz / "config" / "global.yml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def cargar_esquema_nodo(raiz: Path | None = None) -> dict:
    """Carga config/esquema-nodo.json."""
    raiz = Path(raiz) if raiz else raiz_repo()
    with open(raiz / "config" / "esquema-nodo.json", encoding="utf-8") as f:
        return json.load(f)


def validar_nodo(datos: dict, raiz: Path | None = None) -> None:
    """Valida un nodo contra el esquema JSON; lanza ValueError con los errores."""
    esquema = cargar_esquema_nodo(raiz)
    validador = Draft202012Validator(esquema)
    errores = sorted(validador.iter_errors(datos), key=lambda e: list(e.absolute_path))
    if errores:
        detalles = "; ".join(
            f"{'/'.join(str(p) for p in e.absolute_path) or '(raíz)'}: {e.message}"
            for e in errores
        )
        raise ValueError(f"El nodo no cumple el esquema: {detalles}")


def _aplicar_defaults(datos: dict) -> dict:
    """Aplica los defaults del nodo (destinos, formato, crs_destino) a cada capa."""
    base = copy.deepcopy(DEFAULTS_BASE)
    defaults_nodo = datos.get("defaults") or {}
    for clave in ("crs_destino", "formato", "licencia"):
        if clave in defaults_nodo:
            base[clave] = defaults_nodo[clave]
    base["destinos"].update(defaults_nodo.get("destinos") or {})

    slug_nodo = datos.get("nodo", {}).get("slug", "")
    for capa in datos.get("capas", []):
        # `archivo` es un nombre relativo a datos/<nodo>/; se tolera la forma
        # con el prefijo completo y se normaliza aquí.
        prefijo = f"datos/{slug_nodo}/"
        if capa.get("archivo", "").startswith(prefijo):
            capa["archivo"] = capa["archivo"][len(prefijo):]
        capa.setdefault("formato", base["formato"])
        capa.setdefault("crs_destino", base["crs_destino"])
        if "licencia" in base:
            capa.setdefault("licencia", base["licencia"])
        destinos = copy.deepcopy(base["destinos"])
        destinos.update(capa.get("destinos") or {})
        capa["destinos"] = destinos
        capa.setdefault("habilitada", True)
    return datos


def cargar_nodo(slug: str, raiz: Path | None = None) -> dict:
    """Carga y valida config/nodos/<slug>.yml, con los defaults aplicados a cada capa."""
    raiz = Path(raiz) if raiz else raiz_repo()
    ruta = raiz / "config" / "nodos" / f"{slug}.yml"
    if not ruta.is_file():
        disponibles = ", ".join(listar_nodos(raiz)) or "(ninguno)"
        raise FileNotFoundError(f"No existe {ruta}. Nodos disponibles: {disponibles}")
    with open(ruta, encoding="utf-8") as f:
        datos = yaml.safe_load(f)
    validar_nodo(datos, raiz)
    return _aplicar_defaults(datos)


def listar_nodos(raiz: Path | None = None) -> list[str]:
    """Lista los slugs de los nodos definidos en config/nodos/ (excluye _plantilla)."""
    raiz = Path(raiz) if raiz else raiz_repo()
    directorio = raiz / "config" / "nodos"
    if not directorio.is_dir():
        return []
    return sorted(p.stem for p in directorio.glob("*.yml") if not p.name.startswith("_"))


def buscar_capa(nodo: dict, capa_slug: str) -> dict:
    """Devuelve la capa con ese slug o lanza KeyError con las disponibles."""
    for capa in nodo["capas"]:
        if capa["slug"] == capa_slug:
            return capa
    disponibles = ", ".join(c["slug"] for c in nodo["capas"])
    raise KeyError(f"No existe la capa {capa_slug!r}. Disponibles: {disponibles}")
