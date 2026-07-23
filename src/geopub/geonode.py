"""Integración con GeoNode — PENDIENTE.

La integración con GeoNode (API v2, credenciales GEONODE_URL/GEONODE_TOKEN
en .env) está pendiente de decisión. Ver docs/geonode.md.
"""

from __future__ import annotations

_MENSAJE = (
    "La integración con GeoNode aún no está implementada. "
    "Ver docs/geonode.md para el estado y las decisiones pendientes."
)


def _pendiente(*_args, **_kwargs):
    raise NotImplementedError(_MENSAJE)


def subir_capa(*args, **kwargs):
    """Sube una capa a GeoNode. PENDIENTE (ver docs/geonode.md)."""
    _pendiente()


def actualizar_metadatos(*args, **kwargs):
    """Actualiza los metadatos de una capa en GeoNode. PENDIENTE (ver docs/geonode.md)."""
    _pendiente()


def capas_publicadas(*args, **kwargs):
    """Lista las capas publicadas en GeoNode. PENDIENTE (ver docs/geonode.md)."""
    _pendiente()
