# Revisión cruzada de rama Claude — 2026-10-16

**Rama revisada:** `claude/2026-10-16-inventario-imagen`  
**Método:** inspección estática de archivos publicados en GitHub; no se ejecutaron los tests ni se accedió al disco local.  
**Estado de la rama al revisar inicialmente:** divergida respecto de `main` (3 commits por delante, 1 por detrás). En la actualización posterior de Claude, la rama quedó en 6 commits por delante y 0 por detrás de `main`; ese problema de base quedó resuelto.

## Hallazgos

### CR-001 — El manifiesto local expone una ruta personal absoluta

`manifests/inventario-local-2026-10-16.json` contiene una ruta absoluta que incluye el nombre del usuario, el UUID/etiqueta del volumen y la estructura local de carpetas.

**Estado actualizado:** Claude regeneró el manifiesto y su respuesta indica que ya no contiene rutas absolutas. Este punto queda pendiente de confirmar con una inspección directa de la versión más reciente de ese archivo; no debe tratarse como bloqueo vigente si la ruta personal efectivamente desapareció.

**Impacto:** privacidad y portabilidad. No invalida por sí mismo los hashes de los artefactos.

### CR-002 — El constructor ahora trata informe e imagen como una publicación conjunta

La versión inspeccionada prepara el informe antes de publicar, publica primero el informe y después la imagen; si la segunda publicación falla, retira los archivos finales creados por esa ejecución. También usa publicación sin sobrescritura y registra las verificaciones de filesystem realmente ejecutadas.

**Evaluación estática:** corrige el riesgo previo de dejar una imagen final sin informe cuando falla la generación del informe. La recuperación depende de que las operaciones de limpieza puedan completarse; no debe describirse como una transacción atómica del filesystem en sentido estricto.

**Verificación pendiente:** ejecutar la suite del repositorio y confirmar pruebas de fallo de publicación, informe preexistente, fallo de FAT/ext4 y rollback de ambos nombres finales. Esta revisión no ejecutó esas pruebas.

### CR-003 — La verificación de filesystem no equivale a compatibilidad de arranque

El informe generado distingue FAT/ext4 verificados de comprobaciones omitidas. Esto es útil, pero el campo `totalmente_verificada` solo describe las verificaciones declaradas por el constructor: no acredita compatibilidad del kernel con el southbridge, procedencia independiente, seguridad del payload ni arranque real.

La documentación y el CLI deben mantener esta distinción y evitar usar el resultado como autorización para escribir un USB físico.

### CR-004 — La rama ya no está divergida de main, pero hay solapamientos entre ramas de trabajo

En la revisión inicial la rama estaba divergida; la actualización posterior de Claude la dejó 6 commits por delante y 0 por detrás de `main`. No hay necesidad de reconciliarla con `main` por divergencia. Sin embargo, las ramas `claude/2026-10-16-inventario-imagen` y `chatgpt/ps4-audit-roadmap` modifican en paralelo documentos comunes (`README.md`, `ROADMAP.md`, `DECISION_LOG.md`, `TEST_PLAN.md`). La integración debe preservar ambos conjuntos de cambios mediante una revisión deliberada; no hacer merge automático entre ramas de agentes.

## Resultado

- **Bloqueante previo a integrar:** anonimizar la ruta absoluta del manifiesto.
- **Prometedor, pendiente de ejecución independiente:** manejo de informe, verificación de filesystem y rollback del constructor.
- **No demostrado:** suite completa, compatibilidad de kernel, aislamiento en runtime, arranque real y seguridad de cualquier acción física.
- **Acción tomada por esta revisión:** solo documentación en la rama de auditoría; no se modificó la rama de Claude ni `main`.

### CR-005 — El README de Claude quedó desactualizado respecto del CUH confirmado

La versión actual de `docs/KERNEL_SELECTION.md` y `docs/COMPATIBILITY_MATRIX.md` ya registra el modelo **CUH-2115B confirmado**, pero el primer párrafo del `README.md` de la rama de Claude aún dice que el CUH es desconocido y el checklist habla de completar la identificación del CUH. Es una inconsistencia documental; el bloqueo real es el southbridge.

**Corrección aplicada solo en `chatgpt/ps4-audit-roadmap`:** el README de esa rama ahora refleja CUH-2115B confirmado y southbridge desconocido. No modifiqué la rama de Claude ni `main`.
