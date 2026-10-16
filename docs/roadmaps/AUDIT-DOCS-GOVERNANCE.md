# Auditoría documental — rama workstream/01-docs-governance

**Fecha:** 2026-10-16  
**Rama:** `workstream/01-docs-governance`  
**Responsable:** ChatGPT  
**Estado:** en curso; revisión inicial, no auditoría exhaustiva.

## Alcance de esta pasada

Se inspeccionaron el README, el roadmap, la guía de contribución, el acta del proyecto, la política de licencias, el diagnóstico de CI, el script de chequeo local, el validador documental y el workflow de GitHub Actions. No se ejecutaron tests porque esta sesión no dispone de un checkout local del repositorio.

## Hallazgos confirmados

| ID | Hallazgo | Severidad | Acción / estado |
|---|---|---|---|
| DG-F01 | `docs/CI_DIAGNOSIS.md` afirmaba que el repo era privado y recomendaba hacerlo público como alternativa; la información quedó obsoleta. | Alta | Corregido en esta rama; el estado actual de CI sigue sin verificarse. |
| DG-F02 | El documento de CI describía observaciones del 15-10 como si fueran aplicables al presente. | Alta | Corregido: separado el diagnóstico histórico de las comprobaciones pendientes. |
| DG-F03 | El workflow remoto y `scripts/check.sh` cubren pasos similares, pero no son idénticos: el script local también ejecuta `compileall`; el workflow configura Python 3.11 y ejecuta unittest y check_docs. | Media | Registrar como diferencia a evaluar; no cambiar el pipeline sin baseline. |
| DG-F04 | El repositorio no mostraba un archivo de licencia en la raíz en el inventario inspeccionado. | Alta | Pendiente decidir licencia para código propio; no inferir que la documentación o el código de terceros quedan cubiertos. |
| DG-F05 | La validación documental existente cubre README y Markdown bajo docs, enlaces relativos, referencias D/Q, frases obsoletas y algunas condiciones del roadmap; no demuestra escaneo de secretos ni revisión de licencias. | Media | Pendiente ejecutar el checker y añadir controles separados si las herramientas disponibles lo permiten. |

## Pendientes de esta categoría

- [ ] DG-01 Completar inventario de documentos, scripts, manifiestos y workflows.
- [ ] DG-02 Reconciliar contradicciones de estado entre todos los documentos.
- [ ] DG-03 Ejecutar verificación de enlaces internos con resultados registrados.
- [ ] DG-04 Normalizar etiquetas de evidencia.
- [ ] DG-05 Buscar referencias obsoletas a privacidad y verificar todas las afirmaciones de arranque/compatibilidad.
- [ ] DG-06 Revisar reglas de contribución y flujo de ramas.
- [ ] DG-07 Resolver descripción, topics y propuesta de licencia del código propio.
- [ ] DG-08 Ejecutar `bash scripts/check.sh` y registrar resultado cuando se disponga de entorno local.
- [ ] DG-09 Ejecutar un escaneo de secretos con herramienta adecuada y documentar alcance.
- [ ] DG-10 Completar este informe con resultados de pruebas y enlaces verificados.
- [ ] DG-11 Revalidar enlaces tras los cambios finales.
- [ ] DG-12 Cerrar la categoría con revisión cruzada.

## Limitaciones

Esta pasada es una inspección de contenido remoto. No se ha ejecutado el repositorio, no se han descargado ni analizado todos los blobs, no se ha comprobado el historial completo de Git y no se ha ejecutado un escaneo de secretos. Por eso, esta categoría no se declara terminada ni se le asigna un 100 %.
