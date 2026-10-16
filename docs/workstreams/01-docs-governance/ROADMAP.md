# Workstream 01 — Documentación y gobernanza

**Responsable principal:** Claude Code  
**Revisor independiente:** ChatGPT  
**Prioridad:** 1 de 5 — menor complejidad  
**Objetivo:** documentación pública coherente, verificable, navegable y sin afirmaciones superiores a la evidencia disponible.

## Alcance

Incluye README, contribución, documentación técnica, enlaces, fechas, consistencia entre roadmap/decisiones/riesgos/inventario, licencias declaradas y revisión de publicación. No incluye cambiar licencias ni afirmar compatibilidad sin evidencia.

## Tareas hasta el 100 %

- [ ] D01 — Inventariar todos los Markdown, enlaces locales, referencias a rutas y archivos que faltan.
- [ ] D02 — Detectar afirmaciones contradictorias sobre estado, modelo, firmware, USB-only, CI y nivel de evidencia.
- [ ] D03 — Buscar secretos, tokens, datos personales y logs sensibles en el historial y árbol actual; no imprimir secretos en reportes. Si se encuentra alguno, informar ruta y tipo redactados y recomendar rotación/remediación.
- [ ] D04 — Revisar avisos de copyright/licencia y referencias a binarios/artefactos de terceros; no agregar una licencia global por suposición.
- [ ] D05 — Corregir enlaces rotos y contradicciones documentales con cambios acotados.
- [ ] D06 — Sincronizar README, ROADMAP, DECISION_LOG, RISK_REGISTER, ARTIFACT_INVENTORY y estado público.
- [ ] D07 — Ejecutar las validaciones documentales disponibles y registrar salida real.
- [ ] D08 — Verificar que las afirmaciones funcionales distingan IMPLEMENTADO, TESTS, CÓDIGO, TERCEROS y LAB.
- [ ] D09 — Revisar metadatos sugeridos de About/topics y dejar texto exacto listo para el mantenedor si no se pueden cambiar por API.
- [ ] D10 — Publicar informe de cierre con archivos modificados, checks ejecutados, resultados, riesgos residuales y tareas bloqueadas.

## Criterios de aceptación

- Todos los enlaces internos comprobables funcionan o tienen una excepción documentada.
- No quedan contradicciones conocidas sin registrar.
- No se afirma que Linux arrancó ni que USB-only está demostrado.
- El barrido de secretos indica claramente alcance y límites; un escaneo del árbol actual no equivale a limpiar el historial.
- Los checks documentales se ejecutan y sus resultados quedan registrados.
- Roadmap al 100 % solo si cada tarea está completada o tiene una exclusión explícita aceptada por el mantenedor; no esconder bloqueos.

## Restricciones

No editar `main` directamente. Trabajar en esta rama, no reescribir cambios de otros workstreams, no hacer pruebas físicas, no subir artefactos de terceros sin licencia revisada.

## Nota de consolidación (2026-10-16)

Esta rama contenía dos roadmaps paralelos para la misma categoría: este archivo (asignado a Claude Code, acorde a `docs/WORKSTREAMS.md`) y `docs/roadmaps/ROADMAP-DOCS-GOVERNANCE.md` + `docs/roadmaps/AUDIT-DOCS-GOVERNANCE.md` (registrados por ChatGPT antes de que `main` definiera la asignación final). Se consolidan en este archivo, que queda como fuente única. Los hallazgos ya registrados por ChatGPT se incorporan abajo como `F01…F05`; los dos documentos duplicados se retiran en el mismo commit (su contenido queda en el historial de Git).

## Hallazgos heredados (registrados originalmente por ChatGPT)

| ID | Hallazgo | Severidad | Estado |
|---|---|---|---|
| F01 | `docs/CI_DIAGNOSIS.md` afirmaba que el repositorio era privado y lo recomendaba como alternativa; dato obsoleto (el repo es público). | Alta | Corregido (commit previo en esta rama: separa el diagnóstico histórico del estado actual). |
| F02 | El mismo documento presentaba observaciones del 2026-10-15 como si describieran el estado presente. | Alta | Corregido junto con F01. |
| F03 | El workflow remoto (`.github/workflows/tests.yml`) y `scripts/check.sh` cubren pasos similares pero no idénticos (Python 3.11 + unittest + check_docs vs. compileall + unittest + check_docs local). | Media | Pendiente (D07): registrar la diferencia sin cambiar el pipeline sin baseline. |
| F04 | No hay archivo `LICENSE` en la raíz del repositorio. | Alta | Confirmado en este checkout (`LICENSE*` solo resuelve `docs/LICENSE_POLICY.md`). Pendiente (D04): es una decisión del mantenedor, no se infiere ni se agrega una licencia por suposición. |
| F05 | El validador documental disponible (`tools/check_docs.py`) no escanea secretos ni licencias; solo cubre Markdown, enlaces y frases obsoletas. | Media | Confirmado tras leer el script (D07/D03 pendientes: ejecutar y, por separado, barrer secretos con otra herramienta). |

## Registro de ejecución

| ID | Estado | Evidencia / commit | Observaciones |
|---|---|---|---|
| D01 | EN CURSO | — | Inventario de Markdown y enlaces en curso en esta sesión. |
| D02 | EN CURSO | F01, F02 | Contradicciones de CI ya corregidas; se sigue revisando el resto del árbol. |
| D03 | PENDIENTE | — | Barrido de secretos en árbol actual, sin imprimir contenido sensible. |
| D04 | BLOQUEADO | F04 | Falta archivo `LICENSE` en la raíz; decisión de licencia del código propio corresponde al mantenedor. |
| D05 | PENDIENTE | — | Corrección de enlaces rotos y contradicciones restantes. |
| D06 | PENDIENTE | — | Sincronizar README/ROADMAP/DECISION_LOG/RISK_REGISTER/ARTIFACT_INVENTORY. |
| D07 | PENDIENTE | F03, F05 | Ejecutar `scripts/check.sh` / `tools/check_docs.py` y registrar salida real. |
| D08 | PENDIENTE | — | Revisar que las afirmaciones distingan IMPLEMENTADO/TESTS/CÓDIGO/TERCEROS/LAB. |
| D09 | PENDIENTE | — | Redactar texto sugerido de About/topics para que Marcos lo aplique (no hay acceso de API en esta sesión). |
| D10 | PENDIENTE | — | Informe de cierre al terminar D01-D09. |