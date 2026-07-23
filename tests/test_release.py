"""Tests de release en dry-run: empaqueta y calcula checksums sin subir nada."""

import zipfile
from datetime import date

from geopub import config, release


def _crear_datos_falsos(raiz):
    dir_datos = raiz / "datos" / "nodo-prueba"
    dir_datos.mkdir(parents=True)
    for ext in (".shp", ".shx", ".dbf", ".prj", ".cpg"):
        (dir_datos / f"capa_prueba{ext}").write_bytes(b"contenido " + ext.encode())
    (dir_datos / "capa_gpkg.gpkg").write_bytes(b"gpkg falso")
    return dir_datos


def test_crear_dry_run(raiz, tmp_path):
    _crear_datos_falsos(raiz)
    nodo = config.cargar_nodo("nodo-prueba", raiz)
    staging = tmp_path / "staging"

    resultado = release.crear(nodo, raiz, dry_run=True, staging=staging)

    hoy = date.today().strftime("%Y.%m.%d")
    assert resultado["tag"] == f"nodo-prueba-v{hoy}"

    # El shapefile se empaqueta como zip con el juego completo
    zip_capa = staging / "capa_prueba.zip"
    assert zip_capa.is_file()
    with zipfile.ZipFile(zip_capa) as z:
        assert sorted(z.namelist()) == [
            "capa_prueba.cpg", "capa_prueba.dbf", "capa_prueba.prj",
            "capa_prueba.shp", "capa_prueba.shx",
        ]
    # El gpkg se copia tal cual
    assert (staging / "capa_gpkg.gpkg").is_file()

    # Checksums: una línea por asset, formato sha256sum
    lineas = (staging / "SHA256SUMS.txt").read_text().strip().splitlines()
    assert len(lineas) == 2
    for linea in lineas:
        suma, nombre = linea.split()
        assert len(suma) == 64
        assert nombre in ("capa_prueba.zip", "capa_gpkg.gpkg")

    # El comando gh queda armado pero NO se ejecuta ni se escribe en checksums/
    assert resultado["comando"][:4] == ["gh", "release", "create", resultado["tag"]]
    assert not (raiz / "checksums" / "SHA256SUMS-nodo-prueba.txt").exists()


def test_crear_version_explicita(raiz, tmp_path):
    _crear_datos_falsos(raiz)
    nodo = config.cargar_nodo("nodo-prueba", raiz)
    resultado = release.crear(
        nodo, raiz, version="v2026.01.15", dry_run=True, staging=tmp_path / "s"
    )
    assert resultado["tag"] == "nodo-prueba-v2026.01.15"


def test_descargar_dry_run(raiz, capsys):
    nodo = config.cargar_nodo("nodo-prueba", raiz)
    destino = release.descargar(nodo, raiz, tag="nodo-prueba-v2026.01.15", dry_run=True)
    assert destino == raiz / "datos" / "nodo-prueba"
    salida = capsys.readouterr().out
    assert "gh release download nodo-prueba-v2026.01.15" in salida
