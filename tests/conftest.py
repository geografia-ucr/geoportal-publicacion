"""Fixtures compartidos: un repositorio mínimo en tmp_path.

Los tests NO usan la red ni GDAL, y no dependen de config/nodos/*.yml del
repositorio real (usan sus propios fixtures); el esquema JSON sí es el real.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures"

GLOBAL_YML = """\
crs:
  destino: EPSG:8908

geoserver:
  url: https://geoserver.ejemplo.test/geoserver
  ruta_datos_host: /var/lib/docker/volumes/geoportal-gsdatadir/_data
  ruta_datos_contenedor: /geoserver_data/data
  ruta_tmp: /tmp

servidor:
  ssh_host: servidor.ejemplo.test
  ssh_usuario: usuario
  ssh_opciones: "-o PubkeyAuthentication=no"
  ruta_respaldos: /home/usuario/bak

snit:
  wfs_base: https://geoserver.ejemplo.test/geoserver
  capa_limites: eg:ICR_dist2011
"""


@pytest.fixture
def raiz(tmp_path: Path) -> Path:
    """Raíz de un repositorio mínimo, con el esquema de nodo REAL."""
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "fixture"\n', encoding="utf-8")
    dir_config = tmp_path / "config"
    (dir_config / "nodos").mkdir(parents=True)
    shutil.copy(REPO / "config" / "esquema-nodo.json", dir_config / "esquema-nodo.json")
    (dir_config / "global.yml").write_text(GLOBAL_YML, encoding="utf-8")
    shutil.copy(FIXTURES / "nodo-prueba.yml", dir_config / "nodos" / "nodo-prueba.yml")
    return tmp_path


@pytest.fixture
def env_geoserver(monkeypatch):
    """Credenciales falsas de GeoServer en el entorno."""
    monkeypatch.setenv("GEOSERVER_URL", "https://geoserver.ejemplo.test/geoserver")
    monkeypatch.setenv("GEOSERVER_USER", "admin")
    monkeypatch.setenv("GEOSERVER_PASSWORD", "secreto-falso")
