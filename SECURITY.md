# Política de seguridad

## Reporte de vulnerabilidades

Si encuentra una vulnerabilidad en este repositorio o en los servicios asociados
(geoportal.ucr.ac.cr), por favor **no abra un issue público**. Repórtela de forma
privada a la Escuela de Geografía de la Universidad de Costa Rica:

- Correo: geografia@ucr.ac.cr
- O mediante un *security advisory* privado de GitHub (pestaña *Security* → *Advisories*).

## Alcance

- Este repositorio no contiene credenciales: se gestionan localmente vía `.env`
  (git-ignored) y la CI ejecuta detección de secretos (gitleaks) en cada cambio.
- Los datos y metadatos publicados aquí son públicos por diseño (licencia CC BY 4.0)
  y se sirven también por WFS/WMS en el geoportal institucional y el SNIT.
