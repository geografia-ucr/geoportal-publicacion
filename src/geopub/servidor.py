"""Pasos ssh/scp de la publicación, como generador de comandos.

El servidor exige autenticación por contraseña (PubkeyAuthentication=no) y
sudo interactivo, así que en modo normal los comandos se ejecutan con
subprocess y el usuario teclea la contraseña; con dry-run solo se imprimen
los comandos exactos.

Secuencia típica: respaldo remoto (sudo zip) → scp a /tmp → sudo cp al
volumen de datos de GeoServer → verificación md5sum → limpieza de /tmp.
"""

from __future__ import annotations

import os
import subprocess
from datetime import date
from pathlib import Path


class Servidor:
    """Genera (y opcionalmente ejecuta) los comandos ssh/scp de publicación."""

    def __init__(self, cfg_global: dict | None = None):
        cfg = cfg_global or {}
        srv = cfg.get("servidor", {})
        gs = cfg.get("geoserver", {})
        self.host = os.environ.get("GEOPORTAL_SSH_HOST") or srv.get("ssh_host", "")
        self.usuario = os.environ.get("GEOPORTAL_SSH_USER") or srv.get("ssh_usuario", "")
        self.opciones = srv.get("ssh_opciones", "-o PubkeyAuthentication=no")
        self.ruta_datos = gs.get(
            "ruta_datos_host", "/var/lib/docker/volumes/geoportal-gsdatadir/_data"
        )
        self.ruta_tmp = gs.get("ruta_tmp", "/tmp")
        self.ruta_respaldos = srv.get("ruta_respaldos", "/home/geoportal/bak")

    @property
    def destino(self) -> str:
        if not (self.host and self.usuario):
            raise RuntimeError(
                "Defina GEOPORTAL_SSH_HOST y GEOPORTAL_SSH_USER en .env "
                "(o servidor.* en config/global.yml)"
            )
        return f"{self.usuario}@{self.host}"

    def _ssh(self, comando_remoto: str, tty: bool = False) -> str:
        # -t es necesario para comandos remotos con sudo
        t = "-t " if tty else ""
        return f'ssh {t}{self.opciones} {self.destino} "{comando_remoto}"'

    # ------------------------------------------------------------------ #
    # Generadores de comandos
    # ------------------------------------------------------------------ #

    def comandos_respaldo(self, workspace: str, fecha: str | None = None) -> list[str]:
        """Respalda el directorio del workspace en el servidor (sudo zip)."""
        fecha = fecha or date.today().strftime("%Y%m%d")
        zip_remoto = f"{self.ruta_respaldos}/geoserver-data-{workspace}-{fecha}.zip"
        return [
            self._ssh(
                f"sudo mkdir -p {self.ruta_respaldos} && "
                f"sudo zip -rq {zip_remoto} {self.ruta_datos}/{workspace}",
                tty=True,
            )
        ]

    def comandos_subida(self, archivos: list[str | Path], workspace: str) -> list[str]:
        """Sube los archivos por scp a /tmp y los copia (sudo) al volumen de datos."""
        tmp = f"{self.ruta_tmp}/geopub-{workspace}"
        locales = " ".join(str(a) for a in archivos)
        nombres = " ".join(f"{tmp}/{Path(a).name}" for a in archivos)
        return [
            self._ssh(f"mkdir -p {tmp}"),
            f"scp {self.opciones} {locales} {self.destino}:{tmp}/",
            self._ssh(
                f"sudo mkdir -p {self.ruta_datos}/{workspace} && "
                f"sudo cp {nombres} {self.ruta_datos}/{workspace}/",
                tty=True,
            ),
        ]

    def comandos_md5(self, archivos: list[str | Path], workspace: str) -> list[str]:
        """md5sum remoto de los archivos copiados (para comparar con el local)."""
        nombres = " ".join(f"{self.ruta_datos}/{workspace}/{Path(a).name}" for a in archivos)
        return [self._ssh(f"sudo md5sum {nombres}", tty=True)]

    def comandos_limpieza(self, workspace: str) -> list[str]:
        """Elimina el directorio temporal de subida en el servidor."""
        return [self._ssh(f"rm -rf {self.ruta_tmp}/geopub-{workspace}")]

    # ------------------------------------------------------------------ #
    # Ejecución
    # ------------------------------------------------------------------ #

    @staticmethod
    def md5_locales(archivos: list[str | Path]) -> dict[str, str]:
        """md5 de los archivos locales, para comparar con la salida remota."""
        import hashlib

        resultado = {}
        for a in archivos:
            h = hashlib.md5()
            with open(a, "rb") as f:
                for bloque in iter(lambda: f.read(1 << 20), b""):
                    h.update(bloque)
            resultado[Path(a).name] = h.hexdigest()
        return resultado

    def ejecutar(self, comandos: list[str], dry_run: bool = False) -> None:
        """Ejecuta los comandos (el usuario teclea la contraseña ssh/sudo).

        Con dry_run imprime los comandos exactos sin ejecutarlos.
        """
        for cmd in comandos:
            prefijo = "[dry-run] " if dry_run else "$ "
            print(f"{prefijo}{cmd}")
            if not dry_run:
                subprocess.run(cmd, shell=True, check=True)
