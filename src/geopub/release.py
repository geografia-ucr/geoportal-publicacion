"""Distribución de los datos como assets de GitHub Releases.

Los datos geoespaciales no se versionan en git (ver .gitignore); cada nodo se
publica como un release con un zip por capa shapefile (shp+shx+dbf+prj+cpg)
o el .gpkg directo, más un SHA256SUMS.txt. El archivo de checksums también se
copia a checksums/SHA256SUMS-<nodo>.txt (este SÍ va en git).

Tag: <slug-del-nodo>-v<AAAA.MM.DD>. Requiere el CLI `gh` autenticado.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import zipfile
from datetime import date
from pathlib import Path

from .transformar import EXTENSIONES_SHAPEFILE, sha256_archivo


def _empaquetar_capa(capa: dict, dir_datos: Path, staging: Path) -> Path:
    """Empaqueta una capa en el staging: zip del shapefile o copia del .gpkg."""
    archivo = dir_datos / capa["archivo"]
    if not archivo.is_file():
        raise FileNotFoundError(f"No existe {archivo} (¿falta transformar/descargar?)")

    if archivo.suffix.lower() == ".shp":
        destino = staging / f"{capa['slug']}.zip"
        with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
            for ext in EXTENSIONES_SHAPEFILE:
                parte = archivo.with_suffix(ext)
                if parte.is_file():
                    z.write(parte, parte.name)
    else:  # gpkg u otro archivo único
        destino = staging / archivo.name
        shutil.copy2(archivo, destino)
    return destino


def crear(
    nodo: dict,
    raiz: Path,
    version: str | None = None,
    dry_run: bool = False,
    staging: Path | None = None,
) -> dict:
    """Empaqueta las capas del nodo y crea el release con `gh`.

    Con dry_run construye el staging y los checksums pero solo imprime el
    comando `gh` (no sube nada ni escribe en checksums/).
    """
    slug = nodo["nodo"]["slug"]
    version = version or date.today().strftime("%Y.%m.%d")
    tag = f"{slug}-v{version.lstrip('v')}"

    dir_datos = raiz / "datos" / slug
    staging = Path(staging) if staging else Path(tempfile.mkdtemp(prefix=f"geopub-{tag}-"))
    staging.mkdir(parents=True, exist_ok=True)

    assets = [_empaquetar_capa(capa, dir_datos, staging) for capa in nodo["capas"]]

    sumas = staging / "SHA256SUMS.txt"
    lineas = [f"{sha256_archivo(a)}  {a.name}" for a in sorted(assets)]
    sumas.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    assets.append(sumas)

    titulo = nodo["nodo"].get("titulo", slug)
    comando = [
        "gh", "release", "create", tag,
        *[str(a) for a in assets],
        "--title", f"{titulo} — {version}",
        "--notes", f"Datos del nodo {slug} empaquetados el {date.today().isoformat()}.",
    ]

    print(f"Staging: {staging}")
    for linea in lineas:
        print(f"  {linea}")
    if dry_run:
        print(f"[dry-run] {' '.join(comando)}")
    else:
        subprocess.run(comando, check=True, cwd=raiz)
        destino_sumas = raiz / "checksums" / f"SHA256SUMS-{slug}.txt"
        destino_sumas.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(sumas, destino_sumas)
        print(f"Checksums -> {destino_sumas}")

    return {"tag": tag, "staging": staging, "assets": assets, "comando": comando}


def descargar(nodo: dict, raiz: Path, tag: str | None = None, dry_run: bool = False) -> Path:
    """Descarga los assets del release a datos/<nodo>/ y verifica los checksums.

    Si no se indica tag, usa el declarado en las capas del YAML (release.tag).
    Los zips de shapefile se descomprimen tras la verificación.
    """
    slug = nodo["nodo"]["slug"]
    if tag is None:
        tags = {c.get("release", {}).get("tag") for c in nodo["capas"]}
        tags.discard(None)
        if len(tags) != 1:
            raise ValueError(
                f"Indique --tag: el YAML declara {len(tags)} tags distintos ({tags or 'ninguno'})"
            )
        tag = tags.pop()

    destino = raiz / "datos" / slug
    comando = ["gh", "release", "download", tag, "-D", str(destino), "--clobber"]
    if dry_run:
        print(f"[dry-run] {' '.join(comando)}")
        return destino

    destino.mkdir(parents=True, exist_ok=True)
    subprocess.run(comando, check=True, cwd=raiz)

    # Verificación contra los checksums versionados en el repo
    ruta_sumas = raiz / "checksums" / f"SHA256SUMS-{slug}.txt"
    if not ruta_sumas.is_file():
        ruta_sumas = destino / "SHA256SUMS.txt"  # retroceso: el del propio release
    errores = []
    for linea in ruta_sumas.read_text(encoding="utf-8").splitlines():
        if not linea.strip():
            continue
        esperado, nombre = linea.split(None, 1)
        archivo = destino / nombre.strip()
        if not archivo.is_file():
            errores.append(f"falta {nombre.strip()}")
        elif sha256_archivo(archivo) != esperado:
            errores.append(f"sha256 no coincide: {nombre.strip()}")
    if errores:
        raise RuntimeError("Verificación de checksums FALLIDA: " + "; ".join(errores))
    print(f"Checksums verificados contra {ruta_sumas}")

    # Descomprimir los zips de shapefiles
    for z in sorted(destino.glob("*.zip")):
        with zipfile.ZipFile(z) as zf:
            zf.extractall(destino)
        print(f"Descomprimido {z.name}")
    return destino
