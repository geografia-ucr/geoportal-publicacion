"""Cliente REST de GeoServer para publicación y mantenimiento de capas.

Las credenciales se leen SIEMPRE de variables de entorno (.env):
GEOSERVER_URL, GEOSERVER_USER, GEOSERVER_PASSWORD.

Notas heredadas de los recetarios:
- Los POST exitosos de la REST API devuelven texto plano, no JSON.
- El estado enabled de una capa se cambia con GET /rest/layers/<ws>:<capa>.json
  → resource.href → PUT {"featureType": {"enabled": ...}} a ese href.
- El conteo real de una capa se obtiene del WFS con resultType=hits.

En modo ``dry_run`` las operaciones de escritura solo imprimen el método,
la URL y el payload (y quedan en ``self.registro`` para inspección).
"""

from __future__ import annotations

import json
import os
import re

import requests

TIMEOUT = 60


class ErrorGeoServer(RuntimeError):
    """Error devuelto por la REST API de GeoServer."""


class GeoServer:
    """Cliente de la REST API de GeoServer (y de su WFS público)."""

    def __init__(
        self,
        url: str | None = None,
        usuario: str | None = None,
        password: str | None = None,
        dry_run: bool = False,
    ):
        self.url = (url or os.environ.get("GEOSERVER_URL", "")).rstrip("/")
        if not self.url:
            raise ErrorGeoServer("Defina GEOSERVER_URL en .env (o pase url=...)")
        self.usuario = usuario or os.environ.get("GEOSERVER_USER", "admin")
        self.password = password if password is not None else os.environ.get("GEOSERVER_PASSWORD")
        self.dry_run = dry_run
        # Registro de operaciones de escritura: [(método, url, payload), ...]
        self.registro: list[tuple[str, str, dict | None]] = []

    # ------------------------------------------------------------------ #
    # Infraestructura HTTP
    # ------------------------------------------------------------------ #

    @property
    def _auth(self) -> tuple[str, str]:
        if not self.password:
            raise ErrorGeoServer("Defina GEOSERVER_PASSWORD en .env")
        return (self.usuario, self.password)

    def _url(self, ruta: str) -> str:
        return ruta if ruta.startswith("http") else self.url + ruta

    def _escribir(self, metodo: str, ruta: str, payload: dict | None = None) -> str | None:
        """POST/PUT/DELETE. En dry_run imprime y registra sin ejecutar."""
        url = self._url(ruta)
        self.registro.append((metodo, url, payload))
        if self.dry_run:
            print(f"[dry-run] {metodo} {url}")
            if payload is not None:
                print(f"          {json.dumps(payload, ensure_ascii=False)}")
            return None
        r = requests.request(
            metodo,
            url,
            auth=self._auth,
            json=payload,
            headers={"Content-type": "application/json; charset=utf-8"},
            timeout=TIMEOUT,
        )
        if not r.ok:
            raise ErrorGeoServer(f"{metodo} {url} -> HTTP {r.status_code}: {r.text[:500]}")
        return r.text  # los POST exitosos devuelven texto plano

    def _get_json(self, ruta: str) -> dict:
        r = requests.get(self._url(ruta), auth=self._auth, timeout=TIMEOUT)
        if not r.ok:
            raise ErrorGeoServer(f"GET {ruta} -> HTTP {r.status_code}: {r.text[:500]}")
        return r.json()

    # ------------------------------------------------------------------ #
    # Workspace y datastores
    # ------------------------------------------------------------------ #

    def crear_workspace(self, workspace: str) -> None:
        """Crea un workspace (POST /rest/workspaces)."""
        self._escribir("POST", "/rest/workspaces", {"workspace": {"name": workspace}})

    def crear_datastore_directorio(
        self, workspace: str, nombre: str, ruta_contenedor: str
    ) -> None:
        """Crea un datastore tipo 'Directory of spatial files (shapefiles)'.

        `ruta_contenedor` es la ruta del directorio vista desde DENTRO del
        contenedor de GeoServer (p. ej. /geoserver_data/data/<workspace>).
        """
        payload = {
            "dataStore": {
                "name": nombre,
                "type": "Directory of spatial files (shapefiles)",
                "connectionParameters": {
                    "entry": [
                        {"@key": "url", "$": f"file://{ruta_contenedor}"},
                        {"@key": "namespace", "$": f"http://geoserver.org/{workspace}"},
                    ]
                },
            }
        }
        self._escribir("POST", f"/rest/workspaces/{workspace}/datastores", payload)

    def crear_datastore_gpkg(self, workspace: str, nombre: str, ruta_gpkg: str) -> None:
        """Crea un datastore GeoPackage (uno por cada .gpkg; no hay tipo 'directorio')."""
        payload = {
            "dataStore": {
                "name": nombre,
                "type": "GeoPackage",
                "connectionParameters": {
                    "entry": [
                        {"@key": "database", "$": f"file://{ruta_gpkg}"},
                        {"@key": "namespace", "$": f"http://geoserver.org/{workspace}"},
                    ]
                },
            }
        }
        self._escribir("POST", f"/rest/workspaces/{workspace}/datastores", payload)

    def reset_datastore(self, workspace: str, datastore: str) -> None:
        """Recarga un datastore tras reemplazar sus archivos (PUT .../reset)."""
        self._escribir(
            "PUT", f"/rest/workspaces/{workspace}/datastores/{datastore}/reset"
        )

    # ------------------------------------------------------------------ #
    # FeatureTypes
    # ------------------------------------------------------------------ #

    def publicar_featuretype(self, workspace: str, datastore: str, capa: dict) -> None:
        """Publica una capa como featureType.

        `capa` es el dict del YAML del nodo: usa slug (name/nativeName),
        titulo, abstract y habilitada; el SRS siempre es EPSG:8908.
        """
        ft = {
            "name": capa["slug"],
            "nativeName": capa["slug"],
            "title": capa["titulo"],
            "nativeCRS": "EPSG:8908",
            "srs": "EPSG:8908",
            "enabled": capa.get("habilitada", True),
        }
        if capa.get("abstract"):
            ft["abstract"] = capa["abstract"]
        self._escribir(
            "POST",
            f"/rest/workspaces/{workspace}/datastores/{datastore}/featuretypes",
            {"featureType": ft},
        )

    def _href_featuretype(self, workspace: str, capa: str) -> str:
        """Obtiene el href del featureType de una capa (GET /rest/layers/...)."""
        if self.dry_run:
            href = f"{self.url}/rest/layers/{workspace}:{capa}.json -> resource.href"
            print(f"[dry-run] GET {self.url}/rest/layers/{workspace}:{capa}.json")
            return href
        datos = self._get_json(f"/rest/layers/{workspace}:{capa}.json")
        return datos["layer"]["resource"]["href"]

    def _put_featuretype(self, workspace: str, capa: str, cuerpo: dict) -> None:
        href = self._href_featuretype(workspace, capa)
        self._escribir("PUT", href, {"featureType": cuerpo})

    def habilitar(self, workspace: str, capa: str) -> None:
        """Habilita una capa (vuelve a servirse por WFS/WMS)."""
        self._put_featuretype(workspace, capa, {"enabled": True})

    def deshabilitar(self, workspace: str, capa: str) -> None:
        """Deshabilita una capa (deja de anunciarse y servirse; config intacta)."""
        self._put_featuretype(workspace, capa, {"enabled": False})

    def actualizar_abstract(self, workspace: str, capa: str, texto: str) -> None:
        """Actualiza la descripción (abstract) del featureType."""
        self._put_featuretype(workspace, capa, {"abstract": texto})

    # ------------------------------------------------------------------ #
    # Verificación (WFS público, sin credenciales)
    # ------------------------------------------------------------------ #

    def get_capabilities_wfs(self, workspace: str) -> str:
        """Devuelve el XML del GetCapabilities WFS del workspace."""
        url = f"{self.url}/{workspace}/wfs"
        r = requests.get(
            url, params={"service": "WFS", "request": "GetCapabilities"}, timeout=TIMEOUT
        )
        r.raise_for_status()
        return r.text

    def capas_publicadas(self, workspace: str) -> list[dict]:
        """Capas anunciadas en el GetCapabilities: [{'name', 'title', 'abstract'}].

        Solo aparecen las capas habilitadas y con acceso (GeoFence).
        """
        from lxml import etree

        raiz = etree.fromstring(self.get_capabilities_wfs(workspace).encode("utf-8"))
        capas = []
        for ft in raiz.xpath("//*[local-name()='FeatureType']"):
            def texto(etiqueta):
                nodos = ft.xpath(f"*[local-name()='{etiqueta}']/text()")
                return nodos[0].strip() if nodos else ""

            nombre = texto("Name")
            if ":" in nombre:  # quitar prefijo del workspace
                nombre = nombre.split(":", 1)[1]
            capas.append(
                {"name": nombre, "title": texto("Title"), "abstract": texto("Abstract")}
            )
        return capas

    def contar_features(self, workspace: str, capa: str) -> int:
        """Conteo real de entidades vía WFS (resultType=hits → numberMatched)."""
        url = f"{self.url}/{workspace}/wfs"
        r = requests.get(
            url,
            params={
                "service": "WFS",
                "version": "2.0.0",
                "request": "GetFeature",
                "typeNames": f"{workspace}:{capa}",
                "resultType": "hits",
            },
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        m = re.search(r'numberMatched="(\d+)"', r.text)
        if not m:
            raise ErrorGeoServer(f"Sin numberMatched en la respuesta WFS de {capa}: {r.text[:300]}")
        return int(m.group(1))


INSTRUCCIONES_GEOFENCE = """\
PASO MANUAL — Regla de GeoFence (sin ella las capas NO son públicas):
  1. Entrar a la interfaz web de GeoServer: {url}/web/
  2. Security > GeoFence Data Rules > Add new rule
  3. Configurar: Role=*, User=*, Service=*, Request=*, SubField=*,
     Workspace={workspace}, Layer=*, Access=ALLOW
  4. La regla se aplica de inmediato (no requiere reiniciar).
  Nota: si el workspace ya tenía una regla ALLOW con Layer=*, cubre las
  capas nuevas y no hay nada que hacer.
"""
