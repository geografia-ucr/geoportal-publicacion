"""Tests de geopub.crs que no requieren GDAL (juego de shapefile, .cpg)."""

from geopub import crs


def _juego(tmp_path, extensiones, cpg_texto=None):
    for ext in extensiones:
        (tmp_path / f"capa{ext}").write_bytes(b"x")
    if cpg_texto is not None:
        (tmp_path / "capa.cpg").write_text(cpg_texto, encoding="ascii")
    return tmp_path / "capa.shp"


def test_juego_completo_utf8(tmp_path):
    shp = _juego(tmp_path, [".shp", ".shx", ".dbf", ".prj"], cpg_texto="UTF-8")
    assert crs.verificar_juego_shapefile(shp) == []


def test_juego_incompleto(tmp_path):
    shp = _juego(tmp_path, [".shp", ".dbf"], cpg_texto="UTF-8")
    avisos = crs.verificar_juego_shapefile(shp)
    assert any(".shx" in a for a in avisos)
    assert any(".prj" in a for a in avisos)
    assert not any(".dbf" in a for a in avisos)


def test_cpg_ausente(tmp_path):
    shp = _juego(tmp_path, [".shp", ".shx", ".dbf", ".prj"])
    avisos = crs.verificar_juego_shapefile(shp)
    assert avisos == ["falta .cpg (codificación no declarada)"]


def test_cpg_no_utf8(tmp_path):
    shp = _juego(tmp_path, [".shp", ".shx", ".dbf", ".prj"], cpg_texto="ISO-8859-1")
    avisos = crs.verificar_juego_shapefile(shp)
    assert any("ISO-8859-1" in a for a in avisos)
