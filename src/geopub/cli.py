"""CLI de geopub — publicación de capas geoespaciales de la EG-UCR.

Subcomandos principales:

  geopub nodo crear <slug>
  geopub verificar <nodo> [--capa X]
  geopub transformar <nodo> [--capa X] [--dry-run]
  geopub publicar <nodo> [--capa X] [--destino snit|geonode|todos] [--dry-run]
  geopub mantener <nodo> <capa> [--habilitar|--deshabilitar] [--abstract TEXTO]
                  [--reset-datastore] [--dry-run]
  geopub metadatos generar|validar|excel|promover <nodo> [--capa X]
  geopub vista-previa <nodo> [--capa X]
  geopub release crear <nodo> [--version vAAAA.MM.DD] [--dry-run]
  geopub release descargar <nodo> [--tag TAG]
  geopub estado [<nodo>]
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from . import config as cfg
from . import geoserver as gs

app = typer.Typer(
    help="Publicación de capas geoespaciales de la EG-UCR (GeoServer/SNIT).",
    no_args_is_help=True,
)
nodo_app = typer.Typer(help="Gestión de nodos (config/nodos/<slug>.yml).", no_args_is_help=True)
metadatos_app = typer.Typer(help="Metadatos ISO 19115-3 para el SNIT.", no_args_is_help=True)
release_app = typer.Typer(help="Releases de datos en GitHub.", no_args_is_help=True)
app.add_typer(nodo_app, name="nodo")
app.add_typer(metadatos_app, name="metadatos")
app.add_typer(release_app, name="release")

PLANTILLA_NODO = """\
# Nodo de publicación geoespacial EG-UCR.
# Generado por `geopub nodo crear`; completar y validar con `geopub estado <slug>`.
nodo:
  slug: "<slug>"
  titulo: ""
  workspace: "<workspace>"
  datastore: "<workspace>"
  datastore_tipo: shapefile_dir   # shapefile_dir | gpkg_por_capa
  responsable: "Escuela de Geografía, Universidad de Costa Rica"
  contacto: ""

defaults:
  crs_destino: EPSG:8908
  formato: shapefile              # shapefile | gpkg
  destinos:
    snit: true
    geonode: false

capas:
  - slug: capa_ejemplo
    titulo: "Título de la capa"
    archivo: capa_ejemplo.shp
"""


def _contexto() -> tuple[Path, dict]:
    """(raíz del repo, configuración global) — carga también el .env."""
    raiz = cfg.raiz_repo()
    return raiz, cfg.cargar_global(raiz)


def _cliente(cfg_global: dict, dry_run: bool = False) -> gs.GeoServer:
    """Cliente de GeoServer: GEOSERVER_URL del .env tiene prioridad sobre global.yml."""
    import os

    url = os.environ.get("GEOSERVER_URL") or cfg_global.get("geoserver", {}).get("url")
    return gs.GeoServer(url=url, dry_run=dry_run)


def _capas(nodo: dict, capa: Optional[str], solo_habilitadas: bool = False) -> list[dict]:
    capas = nodo["capas"]
    if capa:
        capas = [cfg.buscar_capa(nodo, capa)]
    elif solo_habilitadas:
        capas = [c for c in capas if c.get("habilitada", True)]
    return capas


def _archivos_capa(dir_datos: Path, capa: dict) -> list[Path]:
    """Archivos físicos de una capa (juego completo si es shapefile)."""
    from .transformar import EXTENSIONES_SHAPEFILE

    archivo = dir_datos / capa["archivo"]
    if archivo.suffix.lower() == ".shp":
        return [
            archivo.with_suffix(ext)
            for ext in EXTENSIONES_SHAPEFILE
            if archivo.with_suffix(ext).is_file()
        ]
    return [archivo] if archivo.is_file() else []


# --------------------------------------------------------------------------- #
# nodo
# --------------------------------------------------------------------------- #


@nodo_app.command("crear")
def nodo_crear(slug: str = typer.Argument(..., help="Slug del nodo nuevo (ej. mocupp-pinia)")):
    """Crea el YAML del nodo y su estructura de directorios."""
    raiz = cfg.raiz_repo()
    dir_nodos = raiz / "config" / "nodos"
    dir_nodos.mkdir(parents=True, exist_ok=True)

    plantilla = dir_nodos / "_plantilla.yml"
    if not plantilla.is_file():
        plantilla.write_text(PLANTILLA_NODO, encoding="utf-8")
        typer.echo(f"Creada plantilla: {plantilla}")

    destino = dir_nodos / f"{slug}.yml"
    if destino.exists():
        typer.echo(f"Ya existe {destino}; no se sobrescribe.", err=True)
        raise typer.Exit(1)
    workspace = slug.replace("-", "_")
    contenido = plantilla.read_text(encoding="utf-8")
    contenido = contenido.replace("<slug>", slug).replace("<workspace>", workspace)
    destino.write_text(contenido, encoding="utf-8")
    typer.echo(f"Creado {destino}")

    for sub in ("1-borrador", "2-revision-snit", "3-actual", "vistas-previas"):
        d = raiz / "metadatos" / slug / sub
        d.mkdir(parents=True, exist_ok=True)
        typer.echo(f"Creado {d}/")
    d = raiz / "estilos" / slug
    d.mkdir(parents=True, exist_ok=True)
    typer.echo(f"Creado {d}/")
    typer.echo("Complete el YAML (capas, títulos, archivos) antes de publicar.")


# --------------------------------------------------------------------------- #
# verificar / transformar
# --------------------------------------------------------------------------- #


@app.command("verificar")
def verificar(
    nodo: str = typer.Argument(..., help="Slug del nodo"),
    capa: Optional[str] = typer.Option(None, "--capa", help="Verificar solo esta capa"),
):
    """Verifica el CRS (EPSG:8908) y el juego de archivos de las capas del nodo."""
    from . import crs

    raiz, _ = _contexto()
    datos_nodo = cfg.cargar_nodo(nodo, raiz)
    dir_datos = raiz / "datos" / datos_nodo["nodo"]["slug"]

    try:
        if capa:
            rutas = [dir_datos / cfg.buscar_capa(datos_nodo, capa)["archivo"]]
            faltantes = [r for r in rutas if not r.is_file()]
            if faltantes:
                typer.echo(f"No existe: {faltantes[0]}", err=True)
                raise typer.Exit(1)
            resultados = [crs.verificar_archivo(r) for r in rutas]
        else:
            resultados = crs.verificar_directorio(dir_datos)
    except ImportError:
        typer.echo("GDAL no disponible: use el entorno conda del proyecto.", err=True)
        raise typer.Exit(2)

    if not resultados:
        typer.echo(f"No hay archivos geoespaciales en {dir_datos}")
        raise typer.Exit(1)
    totales = crs.imprimir_resultados(resultados, base=dir_datos)
    problemas = sum(totales.values()) - totales[crs.CORRECTO]
    raise typer.Exit(1 if problemas else 0)


@app.command("transformar")
def transformar_cmd(
    nodo: str = typer.Argument(..., help="Slug del nodo"),
    capa: Optional[str] = typer.Option(None, "--capa"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Solo imprime los comandos"),
):
    """Ejecuta las transformaciones declaradas en el YAML (ogr2ogr, renombrado)."""
    from . import transformar

    raiz, _ = _contexto()
    datos_nodo = cfg.cargar_nodo(nodo, raiz)
    transformar.transformar_nodo(datos_nodo, raiz, capa_slug=capa, dry_run=dry_run)


# --------------------------------------------------------------------------- #
# publicar
# --------------------------------------------------------------------------- #


@app.command("publicar")
def publicar(
    nodo: str = typer.Argument(..., help="Slug del nodo"),
    capa: Optional[str] = typer.Option(None, "--capa"),
    destino: str = typer.Option("snit", "--destino", help="snit | geonode | todos"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Publica el nodo: verificación → respaldo/subida → REST → GeoFence → verificación."""
    from . import servidor

    raiz, cfg_global = _contexto()
    datos_nodo = cfg.cargar_nodo(nodo, raiz)
    info = datos_nodo["nodo"]
    workspace = info["workspace"]
    capas = _capas(datos_nodo, capa, solo_habilitadas=True)
    dir_datos = raiz / "datos" / info["slug"]

    if destino not in ("snit", "geonode", "todos"):
        typer.echo("Destino inválido: use snit, geonode o todos.", err=True)
        raise typer.Exit(1)
    if destino in ("geonode", "todos"):
        typer.echo("GeoNode: integración pendiente (ver docs/geonode.md); se omite.")
        if destino == "geonode":
            raise typer.Exit(0)

    # 1. Verificación de CRS
    typer.echo("== 1. Verificación de CRS ==")
    try:
        from . import crs

        archivos = []
        for c in capas:
            archivos.extend(_archivos_capa(dir_datos, c))
        principales = [a for a in archivos if a.suffix.lower() in crs.EXTENSIONES]
        if not principales:
            typer.echo(f"No hay archivos de datos en {dir_datos}; aborte o transforme antes.", err=True)
            raise typer.Exit(1)
        resultados = [crs.verificar_archivo(a) for a in principales]
        totales = crs.imprimir_resultados(resultados, base=dir_datos)
        if sum(totales.values()) != totales[crs.CORRECTO]:
            typer.echo("Hay capas con CRS incorrecto; corrija antes de publicar.", err=True)
            raise typer.Exit(1)
    except ImportError:
        typer.echo("Aviso: GDAL no disponible; se omite la verificación de CRS.", err=True)
        archivos = []
        for c in capas:
            archivos.extend(_archivos_capa(dir_datos, c))

    # 2. Respaldo y subida al servidor (ssh/scp; el usuario teclea la contraseña)
    typer.echo("\n== 2. Respaldo y subida al servidor ==")
    srv = servidor.Servidor(cfg_global)
    comandos = (
        srv.comandos_respaldo(workspace)
        + srv.comandos_subida(archivos, workspace)
        + srv.comandos_md5(archivos, workspace)
        + srv.comandos_limpieza(workspace)
    )
    srv.ejecutar(comandos, dry_run=dry_run)
    if not dry_run and archivos:
        typer.echo("md5 locales (compare con la salida remota):")
        for nombre, suma in srv.md5_locales(archivos).items():
            typer.echo(f"  {suma}  {nombre}")

    # 3. REST API de GeoServer
    typer.echo("\n== 3. REST API de GeoServer ==")
    cliente = _cliente(cfg_global, dry_run=dry_run)
    ruta_contenedor = cfg_global.get("geoserver", {}).get(
        "ruta_datos_contenedor", "/geoserver_data/data"
    )
    try:
        cliente.crear_workspace(workspace)
    except gs.ErrorGeoServer as e:
        typer.echo(f"Workspace: {e} (probablemente ya existe; se continúa)")

    tipo = info["datastore_tipo"]
    datastore = info.get("datastore", workspace)
    if tipo == "shapefile_dir":
        try:
            cliente.crear_datastore_directorio(
                workspace, datastore, f"{ruta_contenedor}/{workspace}"
            )
        except gs.ErrorGeoServer as e:
            typer.echo(f"Datastore: {e} (probablemente ya existe; se continúa)")
        for c in capas:
            cliente.publicar_featuretype(workspace, datastore, c)
    else:  # gpkg_por_capa: un datastore por GeoPackage
        for c in capas:
            ds = c["slug"]
            try:
                cliente.crear_datastore_gpkg(
                    workspace, ds, f"{ruta_contenedor}/{workspace}/{Path(c['archivo']).name}"
                )
            except gs.ErrorGeoServer as e:
                typer.echo(f"Datastore {ds}: {e} (probablemente ya existe; se continúa)")
            cliente.publicar_featuretype(workspace, ds, c)

    # 4. GeoFence (paso manual)
    typer.echo("\n== 4. GeoFence ==")
    typer.echo(gs.INSTRUCCIONES_GEOFENCE.format(url=cliente.url, workspace=workspace))

    # 5. Verificación final
    typer.echo("== 5. Verificación (GetCapabilities + conteos) ==")
    if dry_run:
        typer.echo("[dry-run] se omite la verificación contra el servidor")
        return
    publicadas = {c["name"] for c in cliente.capas_publicadas(workspace)}
    for c in capas:
        if c["slug"] not in publicadas:
            typer.echo(f"  FALTA en GetCapabilities: {c['slug']} (¿regla de GeoFence?)")
            continue
        n = cliente.contar_features(workspace, c["slug"])
        typer.echo(f"  {c['slug']}: publicada, {n} entidades")


# --------------------------------------------------------------------------- #
# mantener
# --------------------------------------------------------------------------- #


@app.command("mantener")
def mantener(
    nodo: str = typer.Argument(...),
    capa: str = typer.Argument(..., help="Slug de la capa (typeName)"),
    habilitada: Optional[bool] = typer.Option(
        None, "--habilitar/--deshabilitar", help="Cambia el estado enabled de la capa"
    ),
    abstract: Optional[str] = typer.Option(None, "--abstract", help="Nuevo resumen (abstract)"),
    reset_datastore: bool = typer.Option(
        False, "--reset-datastore", help="Recarga el datastore (tras reemplazar archivos)"
    ),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Mantenimiento de una capa ya publicada (enabled, abstract, reset del datastore)."""
    raiz, cfg_global = _contexto()
    datos_nodo = cfg.cargar_nodo(nodo, raiz)
    info = datos_nodo["nodo"]
    workspace = info["workspace"]
    cliente = _cliente(cfg_global, dry_run=dry_run)

    if habilitada is None and abstract is None and not reset_datastore:
        typer.echo("Nada que hacer: use --habilitar/--deshabilitar, --abstract o --reset-datastore.")
        raise typer.Exit(1)

    if habilitada is True:
        cliente.habilitar(workspace, capa)
        typer.echo(f"{capa}: habilitada")
    elif habilitada is False:
        cliente.deshabilitar(workspace, capa)
        typer.echo(f"{capa}: deshabilitada")
    if abstract is not None:
        cliente.actualizar_abstract(workspace, capa, abstract)
        typer.echo(f"{capa}: abstract actualizado")
    if reset_datastore:
        capa_cfg = cfg.buscar_capa(datos_nodo, capa)
        ds = info.get("datastore", workspace)
        if info["datastore_tipo"] == "gpkg_por_capa":
            ds = capa_cfg["slug"]
        cliente.reset_datastore(workspace, ds)
        typer.echo(f"Datastore {ds}: reset")


# --------------------------------------------------------------------------- #
# metadatos
# --------------------------------------------------------------------------- #


@metadatos_app.command("generar")
def metadatos_generar(
    nodo: str = typer.Argument(...),
    capa: Optional[str] = typer.Option(None, "--capa"),
    plantilla: Optional[Path] = typer.Option(
        None, "--plantilla", help="XML plantilla (def: la mínima incluida en el paquete)"
    ),
):
    """Genera borradores XML ISO 19115-3 en metadatos/<nodo>/1-borrador/."""
    from .metadatos import generar

    raiz, cfg_global = _contexto()
    datos_nodo = cfg.cargar_nodo(nodo, raiz)
    generar.generar_nodo(datos_nodo, raiz, cfg_global, capa_slug=capa, plantilla=plantilla)


@metadatos_app.command("validar")
def metadatos_validar(
    nodo: str = typer.Argument(...),
    capa: Optional[str] = typer.Option(None, "--capa"),
    offline: bool = typer.Option(
        True, "--offline/--online", help="Con --online verifica también la URL de distribución"
    ),
):
    """Valida los XML de metadatos (buena formación + campos obligatorios SNIT)."""
    from .metadatos import validar

    raiz, _ = _contexto()
    base = raiz / "metadatos" / nodo
    archivos: list[Path] = []
    for sub in ("1-borrador", "2-revision-snit", "3-actual"):
        archivos.extend(sorted((base / sub).glob("*.xml")))
    if capa:
        archivos = [a for a in archivos if a.stem in (capa, f"{capa}-corregido")]
    if not archivos:
        typer.echo(f"No hay XML que validar en {base}/(1-borrador|2-revision-snit|3-actual)/")
        raise typer.Exit(1)

    todo_ok = True
    for a in archivos:
        resultado = validar.validar_archivo(a, offline=offline)
        todo_ok &= validar.imprimir_verificaciones(a.relative_to(raiz), resultado)
    raise typer.Exit(0 if todo_ok else 1)


@metadatos_app.command("excel")
def metadatos_excel(
    nodo: Optional[str] = typer.Argument(None, help="Nodo (por defecto, todos)"),
    base: Optional[Path] = typer.Option(None, "--base", help="Directorio de metadatos"),
):
    """Genera los Excel con los campos de metadatos de las capas."""
    from .metadatos import excel

    raiz, _ = _contexto()
    excel.generar_excel(base or raiz / "metadatos", nodo=nodo)


@metadatos_app.command("promover")
def metadatos_promover(
    nodo: str = typer.Argument(...),
    capa: Optional[str] = typer.Option(None, "--capa"),
):
    """Promueve XML corregidos de 2-revision-snit/ a 3-actual/."""
    from .metadatos import promover

    raiz, _ = _contexto()
    promover.promover(nodo, raiz, capa_slug=capa)


# --------------------------------------------------------------------------- #
# vista-previa
# --------------------------------------------------------------------------- #


@app.command("vista-previa")
def vista_previa_cmd(
    nodo: str = typer.Argument(...),
    capa: Optional[str] = typer.Option(None, "--capa"),
    color: Optional[str] = typer.Option(None, "--color", help="Sobrescribe el color del YAML"),
    markersize: Optional[float] = typer.Option(None, "--markersize"),
    limites: Optional[Path] = typer.Option(None, "--limites", help="Archivo de contorno propio"),
):
    """Genera las imágenes de vista previa (estilo SNIT) de las capas del nodo."""
    from . import vista_previa

    raiz, cfg_global = _contexto()
    datos_nodo = cfg.cargar_nodo(nodo, raiz)
    slug_nodo = datos_nodo["nodo"]["slug"]
    dir_salida = raiz / "metadatos" / slug_nodo / "vistas-previas"

    for c in _capas(datos_nodo, capa, solo_habilitadas=True):
        ruta_capa = raiz / "datos" / slug_nodo / c["archivo"]
        if not ruta_capa.is_file():
            typer.echo(f"Se omite {c['slug']}: no existe {ruta_capa}", err=True)
            continue
        params = (c.get("metadatos") or {}).get("vista_previa") or {}
        vista_previa.generar(
            ruta_capa,
            dir_salida / f"{c['slug']}.jpg",
            raiz,
            cfg_global,
            color=color or params.get("color", "red"),
            markersize=markersize if markersize is not None else params.get("markersize", 2.5),
            limites=str(limites) if limites else None,
        )


# --------------------------------------------------------------------------- #
# release
# --------------------------------------------------------------------------- #


@release_app.command("crear")
def release_crear(
    nodo: str = typer.Argument(...),
    version: Optional[str] = typer.Option(None, "--version", help="vAAAA.MM.DD (def: hoy)"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Empaqueta las capas del nodo y crea el release en GitHub (gh)."""
    from . import release

    raiz, _ = _contexto()
    datos_nodo = cfg.cargar_nodo(nodo, raiz)
    release.crear(datos_nodo, raiz, version=version, dry_run=dry_run)


@release_app.command("descargar")
def release_descargar(
    nodo: str = typer.Argument(...),
    tag: Optional[str] = typer.Option(None, "--tag", help="Tag del release (def: el del YAML)"),
):
    """Descarga los datos del release a datos/<nodo>/ y verifica los checksums."""
    from . import release

    raiz, _ = _contexto()
    datos_nodo = cfg.cargar_nodo(nodo, raiz)
    release.descargar(datos_nodo, raiz, tag=tag)


# --------------------------------------------------------------------------- #
# estado
# --------------------------------------------------------------------------- #


@app.command("estado")
def estado(nodo: Optional[str] = typer.Argument(None, help="Slug del nodo (def: todos)")):
    """Compara el YAML con el GeoServer vivo y el estado local de datos/metadatos."""
    raiz, cfg_global = _contexto()
    slugs = [nodo] if nodo else cfg.listar_nodos(raiz)
    if not slugs:
        typer.echo("No hay nodos en config/nodos/.")
        raise typer.Exit(1)

    for slug in slugs:
        datos_nodo = cfg.cargar_nodo(slug, raiz)
        info = datos_nodo["nodo"]
        workspace = info["workspace"]
        typer.echo(f"\n=== {slug} (workspace {workspace}) ===")

        # Estado remoto (tolerante a falta de red)
        publicadas: dict[str, dict] | None = None
        try:
            cliente = _cliente(cfg_global)
            publicadas = {c["name"]: c for c in cliente.capas_publicadas(workspace)}
        except Exception as e:
            typer.echo(f"  (sin conexión con GeoServer: {e}; se reporta solo lo local)")

        dir_datos = raiz / "datos" / slug
        dir_meta = raiz / "metadatos" / slug
        declaradas = set()
        for c in datos_nodo["capas"]:
            declaradas.add(c["slug"])
            partes = []
            partes.append("datos:OK" if (dir_datos / c["archivo"]).is_file() else "datos:FALTAN")
            xml_actual = dir_meta / "3-actual" / f"{c['slug']}.xml"
            estado_meta = (c.get("metadatos") or {}).get("estado", "?")
            partes.append(
                f"metadatos:{'OK' if xml_actual.is_file() else 'sin XML en 3-actual'}"
                f" (estado YAML: {estado_meta})"
            )
            if publicadas is not None:
                anunciada = c["slug"] in publicadas
                habilitada = c.get("habilitada", True)
                if habilitada and anunciada:
                    partes.append("geoserver:publicada")
                elif habilitada and not anunciada:
                    partes.append("geoserver:FALTA (habilitada en YAML, no anunciada)")
                elif not habilitada and anunciada:
                    partes.append("geoserver:SOBRA (deshabilitada en YAML, sigue anunciada)")
                else:
                    partes.append("geoserver:deshabilitada (coincide)")
            typer.echo(f"  {c['slug']}: " + " | ".join(partes))

        if publicadas is not None:
            extras = sorted(set(publicadas) - declaradas)
            for nombre in extras:
                typer.echo(f"  {nombre}: publicada en GeoServer pero NO declarada en el YAML")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
