"""Tests del cliente GeoServer en modo dry_run (sin red, credenciales falsas)."""

import pytest

from geopub import geoserver

BASE = "https://geoserver.ejemplo.test/geoserver"


@pytest.fixture
def cliente(env_geoserver):
    return geoserver.GeoServer(dry_run=True)


def test_url_desde_entorno(cliente):
    assert cliente.url == BASE
    assert cliente.usuario == "admin"
    assert cliente.password == "secreto-falso"


def test_sin_url_falla(monkeypatch):
    monkeypatch.delenv("GEOSERVER_URL", raising=False)
    with pytest.raises(geoserver.ErrorGeoServer, match="GEOSERVER_URL"):
        geoserver.GeoServer()


def test_crear_workspace(cliente):
    cliente.crear_workspace("mocupp_prueba")
    metodo, url, payload = cliente.registro[-1]
    assert metodo == "POST"
    assert url == f"{BASE}/rest/workspaces"
    assert payload == {"workspace": {"name": "mocupp_prueba"}}


def test_crear_datastore_directorio(cliente):
    cliente.crear_datastore_directorio("ws", "ds", "/geoserver_data/data/ws")
    metodo, url, payload = cliente.registro[-1]
    assert (metodo, url) == ("POST", f"{BASE}/rest/workspaces/ws/datastores")
    entradas = {e["@key"]: e["$"] for e in payload["dataStore"]["connectionParameters"]["entry"]}
    assert entradas["url"] == "file:///geoserver_data/data/ws"
    assert entradas["namespace"] == "http://geoserver.org/ws"
    assert payload["dataStore"]["type"] == "Directory of spatial files (shapefiles)"


def test_crear_datastore_gpkg(cliente):
    cliente.crear_datastore_gpkg("ws", "capa", "/geoserver_data/data/ws/capa.gpkg")
    _, url, payload = cliente.registro[-1]
    assert url == f"{BASE}/rest/workspaces/ws/datastores"
    entradas = {e["@key"]: e["$"] for e in payload["dataStore"]["connectionParameters"]["entry"]}
    assert entradas["database"] == "file:///geoserver_data/data/ws/capa.gpkg"
    assert payload["dataStore"]["type"] == "GeoPackage"


def test_publicar_featuretype(cliente):
    capa = {
        "slug": "capa_prueba",
        "titulo": "Capa de prueba 2021",
        "abstract": "Resumen corto.",
        "habilitada": True,
    }
    cliente.publicar_featuretype("ws", "ds", capa)
    metodo, url, payload = cliente.registro[-1]
    assert metodo == "POST"
    assert url == f"{BASE}/rest/workspaces/ws/datastores/ds/featuretypes"
    ft = payload["featureType"]
    assert ft["name"] == ft["nativeName"] == "capa_prueba"
    assert ft["title"] == "Capa de prueba 2021"
    assert ft["abstract"] == "Resumen corto."
    assert ft["srs"] == ft["nativeCRS"] == "EPSG:8908"
    assert ft["enabled"] is True


def test_habilitar_deshabilitar(cliente):
    cliente.deshabilitar("ws", "capa")
    metodo, url, payload = cliente.registro[-1]
    assert metodo == "PUT"
    assert "rest/layers/ws:capa" in url  # href simulado en dry-run
    assert payload == {"featureType": {"enabled": False}}

    cliente.habilitar("ws", "capa")
    assert cliente.registro[-1][2] == {"featureType": {"enabled": True}}


def test_actualizar_abstract(cliente):
    cliente.actualizar_abstract("ws", "capa", "Nuevo resumen")
    assert cliente.registro[-1][2] == {"featureType": {"abstract": "Nuevo resumen"}}


def test_reset_datastore(cliente):
    cliente.reset_datastore("ws", "ds")
    metodo, url, payload = cliente.registro[-1]
    assert (metodo, payload) == ("PUT", None)
    assert url == f"{BASE}/rest/workspaces/ws/datastores/ds/reset"


def test_dry_run_no_toca_la_red(cliente):
    """En dry_run ninguna operación de escritura debe usar requests."""
    import geopub.geoserver as mod

    class Explota:
        def __getattr__(self, nombre):
            raise AssertionError("dry_run intentó usar la red")

    original = mod.requests
    mod.requests = Explota()
    try:
        cliente.crear_workspace("ws")
        cliente.publicar_featuretype("ws", "ds", {"slug": "a", "titulo": "A"})
        cliente.deshabilitar("ws", "a")
    finally:
        mod.requests = original
