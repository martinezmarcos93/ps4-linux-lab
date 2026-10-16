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