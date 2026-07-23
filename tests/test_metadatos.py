"""Tests del motor de metadatos (generar, validar, promover) — sin red ni GDAL."""

from pathlib import Path

import pytest

from geopub import config
from geopub.metadatos import generar, promover, validar

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_reemplazar_unico():
    assert generar.reemplazar_unico("abc", "b", "X") == "aXc"
    with pytest.raises(ValueError, match="hay 0"):
        generar.reemplazar_unico("abc", "z", "X")
    with pytest.raises(ValueError, match="hay 2"):
        generar.reemplazar_unico("abab", "a", "X")


def test_aplicar_reemplazos():
    xml = "<t><a>viejo</a><b>2021</b></t>"
    assert generar.aplicar_reemplazos(xml, {"viejo": "nuevo", "2021": "2022"}) == (
        "<t><a>nuevo</a><b>2022</b></t>"
    )


def test_generar_con_plantilla_minima(raiz):
    nodo = config.cargar_nodo("nodo-prueba", raiz)
    cfg_global = config.cargar_global(raiz)
    capa = config.buscar_capa(nodo, "capa_prueba")

    salida = generar.generar_capa(
        nodo, capa, raiz, cfg_global, plantilla=FIXTURES / "plantilla-minima.xml"
    )
    assert salida == raiz / "metadatos" / "nodo-prueba" / "1-borrador" / "capa_prueba.xml"
    texto = salida.read_text(encoding="utf-8")
    assert "Capa de prueba 2021" in texto
    assert "EPSG:8908" in texto
    assert "CR_EG-UCR_PRUEBA_2021_10KVE" in texto
    assert "{{" not in texto  # sin marcadores residuales


def test_generar_con_plantilla_incluida_y_validar(raiz):
    """La plantilla del paquete produce un borrador que pasa la validación SNIT."""
    nodo = config.cargar_nodo("nodo-prueba", raiz)
    cfg_global = config.cargar_global(raiz)
    capa = config.buscar_capa(nodo, "capa_prueba")

    salida = generar.generar_capa(nodo, capa, raiz, cfg_global)
    verificaciones = validar.validar_archivo(salida, offline=True)
    fallos = [v for v in verificaciones if not v.ok]
    assert not fallos, f"Fallaron: {[(v.campo, v.detalle) for v in fallos]}"
    # Campos clave presentes
    campos = {v.campo for v in verificaciones}
    assert {"Título", "Resumen", "CRS EPSG:8908", "Punto de contacto",
            "Bbox", "Palabras clave", "Linkage de distribución"} <= campos


def test_validar_detecta_faltantes(tmp_path):
    xml = tmp_path / "vacio.xml"
    xml.write_text("<raiz/>", encoding="utf-8")
    verificaciones = validar.validar_archivo(xml, offline=True)
    por_campo = {v.campo: v for v in verificaciones}
    assert por_campo["XML bien formado"].ok
    assert not por_campo["Título"].ok
    assert not por_campo["CRS EPSG:8908"].ok
    assert not por_campo["Bbox"].ok


def test_validar_mal_formado(tmp_path):
    xml = tmp_path / "roto.xml"
    xml.write_text("<a><b></a>", encoding="utf-8")
    verificaciones = validar.validar_archivo(xml, offline=True)
    assert len(verificaciones) == 1
    assert not verificaciones[0].ok


def test_promover(raiz):
    dir_rev = raiz / "metadatos" / "nodo-prueba" / "2-revision-snit"
    dir_rev.mkdir(parents=True)
    (dir_rev / "capa_prueba-corregido.xml").write_text("<x/>", encoding="utf-8")

    movidos = promover.promover("nodo-prueba", raiz)
    assert len(movidos) == 1
    destino = raiz / "metadatos" / "nodo-prueba" / "3-actual" / "capa_prueba.xml"
    assert destino.is_file()
    assert not (dir_rev / "capa_prueba-corregido.xml").exists()


def test_promover_sin_archivos(raiz):
    (raiz / "metadatos" / "nodo-prueba" / "2-revision-snit").mkdir(parents=True)
    with pytest.raises(FileNotFoundError):
        promover.promover("nodo-prueba", raiz)
