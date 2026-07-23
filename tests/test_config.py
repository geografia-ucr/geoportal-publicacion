"""Tests de geopub.config: carga y validación contra el esquema real."""

import pytest
import yaml

from geopub import config


def test_raiz_repo_encuentra_pyproject(raiz):
    assert config.raiz_repo(raiz / "config" / "nodos") == raiz


def test_raiz_repo_falla_sin_pyproject(tmp_path):
    with pytest.raises(FileNotFoundError):
        config.raiz_repo(tmp_path)


def test_listar_nodos(raiz):
    assert config.listar_nodos(raiz) == ["nodo-prueba"]


def test_listar_nodos_excluye_plantilla(raiz):
    (raiz / "config" / "nodos" / "_plantilla.yml").write_text("nodo: {}\n", encoding="utf-8")
    assert config.listar_nodos(raiz) == ["nodo-prueba"]


def test_cargar_nodo_valida_y_aplica_defaults(raiz):
    nodo = config.cargar_nodo("nodo-prueba", raiz)
    assert nodo["nodo"]["workspace"] == "nodo_prueba"

    capa1, capa2 = nodo["capas"]
    # Defaults del nodo aplicados a la capa
    assert capa1["formato"] == "shapefile"
    assert capa1["crs_destino"] == "EPSG:8908"
    assert capa1["destinos"] == {"snit": True, "geonode": False}
    assert capa1["habilitada"] is True
    # La capa puede sobreescribir los defaults
    assert capa2["formato"] == "gpkg"
    assert capa2["habilitada"] is False
    assert capa2["destinos"] == {"snit": True, "geonode": True}


def test_cargar_nodo_inexistente(raiz):
    with pytest.raises(FileNotFoundError, match="nodo-prueba"):
        config.cargar_nodo("no-existe", raiz)


def test_nodo_invalido_no_pasa_el_esquema(raiz):
    ruta = raiz / "config" / "nodos" / "roto.yml"
    invalido = {
        "nodo": {"slug": "roto", "workspace": "roto"},  # falta datastore_tipo
        "capas": [{"slug": "x", "titulo": "X", "archivo": "x.shp", "intruso": 1}],
    }
    ruta.write_text(yaml.safe_dump(invalido), encoding="utf-8")
    with pytest.raises(ValueError, match="no cumple el esquema"):
        config.cargar_nodo("roto", raiz)


def test_buscar_capa(raiz):
    nodo = config.cargar_nodo("nodo-prueba", raiz)
    assert config.buscar_capa(nodo, "capa_gpkg")["slug"] == "capa_gpkg"
    with pytest.raises(KeyError):
        config.buscar_capa(nodo, "inexistente")


def test_cargar_global(raiz):
    cfg = config.cargar_global(raiz)
    assert cfg["geoserver"]["url"].startswith("https://")
