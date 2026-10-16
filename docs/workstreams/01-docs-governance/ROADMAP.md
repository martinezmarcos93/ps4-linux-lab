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

## Hallazgos nuevos (esta sesión, Claude Code)

| ID | Hallazgo | Severidad | Estado |
|---|---|---|---|
| F06 | `docs/DECISION_LOG.md` (línea ~92, 2026-10-15) registra explícitamente que "hacer público el repositorio" **seguía sin autorización** en ese momento, sin entrada posterior que registrara el cambio de visibilidad. | Alta | **Cerrado.** Marcos confirmó (2026-10-16) que autorizó la publicación; se registró retroactivamente en `docs/DECISION_LOG.md` (D-022). |
| F07 | `docs/opencode/2026-10-15-docs-quality-audit/` contiene bitácora/roadmap interno de otro agente (OpenCode) para una tarea (`check_docs_links.py`, `DOCS_QUALITY_CHECKS.md`) que nunca se completó — esos archivos no existen en el repo. Es trabajo en curso de otro agente mezclado en el árbol público de `docs/`, no documentación del proyecto. | Baja/Media | **Decisión de Marcos (2026-10-16): dejarlo, solo documentar.** No se mueve ni se borra; queda como hallazgo abierto por si se decide reubicar más adelante. |
| F08 | `docs/UPSTREAM_AUDIT.md:47` describía el repositorio como "privado" pese a estar público desde la auditoría de publicación. | Media | **Corregido en este commit** (se quitó la calificación obsoleta y se referenció `PUBLICATION_AUDIT.md`). |
| F09 | `docs/WORKSTREAMS.md` enlaza a `workstreams/0N-*/ROADMAP.md` para las categorías 2-5; esos archivos solo existen en sus respectivas ramas de trabajo. Desde cualquier rama individual (incluida `main`), `tools/check_docs.py` reporta esos enlaces como rotos hasta integrar todas las ramas. | Baja | Excepción documentada (ver abajo); no se fuerza una corrección que requeriría mezclar ramas fuera de la política de coordinación. |

## Excepciones de enlaces documentadas

- `docs/WORKSTREAMS.md` → `workstreams/02-tools-tests/ROADMAP.md`, `workstreams/03-upstream-audit/ROADMAP.md`, `workstreams/04-compatibility/ROADMAP.md`, `workstreams/05-usb-image/ROADMAP.md`: rotos en cualquier checkout de una sola rama (F09). Se resuelven solo tras integrar las cinco ramas de workstream a `main`; no se simulan con archivos vacíos.

## Registro de ejecución

| ID | Estado | Evidencia / commit | Observaciones |
|---|---|---|---|
| D01 | EN CURSO | 40 Markdown inventariados (`find . -name "*.md"`) | Inventario de Markdown hecho; falta revisar scripts/manifiestos/workflows (parte de D01 original). |
| D02 | EN CURSO | F01, F02, F06, F08 | Contradicciones de CI corregidas; nueva contradicción F06 (publicación sin decisión registrada) requiere a Marcos, no se resuelve documentalmente. |
| D03 | TESTS | grep de patrones de credenciales/tokens/claves privadas + emails + IPs sobre árbol actual (`*.md/.py/.sh/.json/.yml`); verificación de nombres de archivo sensibles en todo el historial (`git log --all --name-only`, 89 commits) | Sin hallazgos. Alcance: patrones conocidos + nombres de archivo en todo el historial; **no** es un diff de contenido de cada blob histórico. |
| D04 | BLOQUEADO | F04 | Falta archivo `LICENSE` en la raíz; decisión de licencia del código propio corresponde al mantenedor. |
| D05 | EN CURSO | F08 (commit de esta sesión) | `docs/UPSTREAM_AUDIT.md` corregido; quedan F06/F07 pendientes de decisión de Marcos (no son enlaces rotos, son contenido a decidir). |
| D06 | PENDIENTE | — | Sincronizar README/ROADMAP/DECISION_LOG/RISK_REGISTER/ARTIFACT_INVENTORY. |
| D07 | TESTS | `python tools/check_docs.py` ejecutado: 4 problemas (los 4 enlaces de F09, excepción documentada); ver salida completa en el informe de cierre | Validador documental ejecutado con salida real. `scripts/check.sh` (suite completa) queda para workstream 02 por alcance. |
| D08 | PENDIENTE | — | Revisar que las afirmaciones distingan IMPLEMENTADO/TESTS/CÓDIGO/TERCEROS/LAB. |
| D09 | PENDIENTE | — | Redactar texto sugerido de About/topics para que Marcos lo aplique (no hay acceso de API en esta sesión). |
| D10 | PENDIENTE | — | Informe de cierre al terminar D01-D09. |