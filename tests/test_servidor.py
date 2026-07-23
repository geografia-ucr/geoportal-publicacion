"""Tests del generador de comandos ssh/scp (sin ejecutar nada)."""

from geopub import servidor

CFG = {
    "servidor": {
        "ssh_host": "servidor.ejemplo.test",
        "ssh_usuario": "usuario",
        "ssh_opciones": "-o PubkeyAuthentication=no",
        "ruta_respaldos": "/home/usuario/bak",
    },
    "geoserver": {
        "ruta_datos_host": "/var/lib/docker/volumes/geoportal-gsdatadir/_data",
        "ruta_tmp": "/tmp",
    },
}


def _srv(monkeypatch):
    monkeypatch.delenv("GEOPORTAL_SSH_HOST", raising=False)
    monkeypatch.delenv("GEOPORTAL_SSH_USER", raising=False)
    return servidor.Servidor(CFG)


def test_destino_desde_config(monkeypatch):
    srv = _srv(monkeypatch)
    assert srv.destino == "usuario@servidor.ejemplo.test"


def test_entorno_sobreescribe_config(monkeypatch):
    monkeypatch.setenv("GEOPORTAL_SSH_HOST", "otro.host")
    monkeypatch.setenv("GEOPORTAL_SSH_USER", "otra")
    srv = servidor.Servidor(CFG)
    assert srv.destino == "otra@otro.host"


def test_comandos_respaldo(monkeypatch):
    (cmd,) = _srv(monkeypatch).comandos_respaldo("ws", fecha="20260722")
    assert cmd.startswith("ssh -t -o PubkeyAuthentication=no usuario@servidor.ejemplo.test")
    assert "sudo zip -rq /home/usuario/bak/geoserver-data-ws-20260722.zip" in cmd
    assert "/var/lib/docker/volumes/geoportal-gsdatadir/_data/ws" in cmd


def test_comandos_subida(monkeypatch):
    comandos = _srv(monkeypatch).comandos_subida(["/datos/a.shp", "/datos/a.dbf"], "ws")
    assert len(comandos) == 3
    assert "mkdir -p /tmp/geopub-ws" in comandos[0]
    assert comandos[1].startswith("scp -o PubkeyAuthentication=no /datos/a.shp /datos/a.dbf")
    assert "sudo cp /tmp/geopub-ws/a.shp /tmp/geopub-ws/a.dbf" in comandos[2]
    assert comandos[2].split()[1] == "-t"  # sudo requiere tty


def test_ejecutar_dry_run_no_ejecuta(monkeypatch, capsys):
    srv = _srv(monkeypatch)
    import subprocess

    def explota(*a, **k):
        raise AssertionError("dry_run ejecutó un comando")

    monkeypatch.setattr(subprocess, "run", explota)
    srv.ejecutar(["echo hola"], dry_run=True)
    assert "[dry-run] echo hola" in capsys.readouterr().out
