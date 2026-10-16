# Southbridge: evidencia específica para CUH-2115B

**Fecha de consulta:** 2026-10-16  
**Resultado:** la evidencia pública consultada refuerza que el modelo comercial por sí solo no permite seleccionar un kernel. El southbridge del equipo del laboratorio sigue **sin confirmar**.

## Hallazgo nuevo

La tabla comunitaria [PS4 Developer wiki — Hardware Info](https://www.psdevwiki.com/ps4/Hardware_Info) incluye el mismo identificador `CUH-2115B B01X` con dos valores distintos de SouthBridge SubSystem:
- `30201 (Baikal B1)` (la fila que incluye CUH-2115B aparece en la tabla actual).
- `40100 (Belize2 A0)` (otra fila también lista CUH-2115B B01X).

La página se marca a sí misma como pendiente de reestructuración y no es documentación primaria de Sony. La tabla no explica la duplicación ni permite decidir cuál corresponde a la unidad concreta de Marcos. Por eso se registra como **EVIDENCIA COMUNITARIA CONFLICTIVA**, no como identificación del hardware local.

Fuente adicional: [PS4 Developer wiki — Southbridge](https://www.psdevwiki.com/ps4/Southbridge), que relaciona revisiones de southbridge con placas y familias de chasis, pero no basta por sí sola para inferir la revisión física exacta a partir del código comercial.

## Consecuencia para la matriz

| Dato | Estado actualizado | Consecuencia |
|---|---|---|
| Modelo comunicado CUH-2115B | OBSERVADO/COMUNICADO | Se mantiene como baseline del laboratorio |
| Firmware 13.52 | OBSERVADO | Se mantiene; no actualizar |
| Southbridge de esta unidad | DESCONOCIDO | No elegir kernel |
| Evidencia pública sobre CUH-2115B | CONFLICTIVA: la wiki asocia el mismo identificador a Baikal y Belize2 | No inferir por CUH; buscar evidencia específica de placa/revisión o dejarlo bloqueado |
| Compatibilidad de loader para Belize2 | El README del loader incluye Belize(2) entre las familias objetivo | No demuestra que un kernel particular sea compatible ni que el procedimiento USB-only sea seguro |

## Siguiente paso admisible

1. Claude debe comprobar si los archivos locales del laboratorio contienen una revisión de placa, etiqueta interna o fuente primaria que no esté reflejada en el resumen.
2. Buscar una fuente técnica con evidencia de placa/modelo exactos y registrar fecha, URL y alcance. Si solo hay wikis/comentarios comunitarios contradictorios, conservar el estado DESCONOCIDO.
3. No abrir la consola, modificar firmware ni ejecutar un payload como parte de esta tarea documental.
4. Mantener la decisión **INDETERMINADO / NO-GO para selección de kernel** hasta resolver la revisión de placa y las condiciones de arranque USB-only.

## Clasificación de fuente

- **Tipo:** wiki técnica comunitaria; no fuente primaria del fabricante.
- **Contenido útil:** demuestra que la relación CUH-2115B ↔ southbridge no es unívoca en la tabla pública consultada.
- **Limitación:** la página declara que requiere reestructuración; no se verificó la procedencia de cada fila ni se inspeccionó físicamente la consola.
- **Uso permitido:** contextualizar la incertidumbre y guiar nuevas verificaciones documentales; no afirmar qué chip está instalado en la consola del laboratorio.
