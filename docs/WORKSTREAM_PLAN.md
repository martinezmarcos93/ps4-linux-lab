# Plan de trabajo por categorías

**Fecha de apertura:** 2026-10-16  
**Repositorio:** `martinezmarcos93/ps4-linux-lab`  
**Base de las ramas:** `main`  
**Objetivo:** completar al 100 % las cinco categorías de preparación que pueden avanzar sin una prueba física en PS4. Las categorías de prueba en hardware y caracterización GPU/gaming/LLM quedan fuera del ciclo actual.

## Método

Cada categoría tiene una rama independiente y un roadmap propio con identificadores, tareas pendientes, criterios de aceptación y registro de evidencia. El 100 % significa cumplir el alcance explícito de esa categoría; no autoriza a afirmar un arranque Linux ni compatibilidad física sin pruebas en consola.

Las ramas se crearon desde `main` y contienen únicamente su roadmap inicial. No se han integrado entre sí ni en `main`. Cada responsable debe trabajar dentro de su rama, actualizar el roadmap y aportar evidencia real. No marcar tareas completadas por inferencia o porque exista documentación previa.

## Orden de ejecución y responsables

| Orden | Categoría | Rama | Responsable | Criterio de cierre |
|---:|---|---|---|---|
| 1 | Gobernanza y documentación | `workstream/01-docs-governance` | ChatGPT | Documentación pública consistente, enlaces verificados, auditoría registrada |
| 2 | Herramientas y tests host-side | `workstream/02-tools-tests` | Claude Code | Baseline, correcciones, tests de seguridad y suite reproducible |
| 3 | Auditoría upstream y licencias | `workstream/03-upstream-audit` | Claude Code | Inventario completo, procedencia/licencias por dependencia y decisiones documentadas |
| 4 | Identificación y compatibilidad | `workstream/04-compatibility` | Claude Code; revisión cruzada de ChatGPT | Paquete de decisión previo al laboratorio, matriz reconciliada y bloqueos explícitos |
| 5 | Imagen y cadena USB-only | `workstream/05-usb-image` | Claude Code; revisión cruzada de ChatGPT | Pipeline host-side reproducible y auditado, sin escritura a dispositivos físicos |

## Dependencias

- Categoría 1 establece consistencia documental y gobernanza.
- Categoría 2 establece el estado real de las herramientas y los tests.
- Categoría 3 resuelve procedencia y licencias de componentes.
- Categoría 4 usa la auditoría para tomar una decisión técnica fundamentada sobre compatibilidad.
- Categoría 5 depende de herramientas fiables, artefactos aceptables y una decisión de compatibilidad defendible.

Las categorías 2 y 3 pueden realizar inspección inicial en paralelo, pero el cierre de la categoría 5 requiere los resultados de las categorías 2, 3 y 4. La categoría 1 no debe bloquear las pruebas técnicas por ajustes editoriales menores.

## Protocolo de trabajo

1. Leer el roadmap específico de la rama y el estado actual del repositorio.
2. Registrar baseline antes de cambiar código o documentación.
3. Trabajar en commits pequeños y coherentes.
4. Ejecutar pruebas relevantes y registrar comandos/salida reales.
5. Marcar cada tarea como completada solo con evidencia verificable.
6. Si una tarea depende de consola, permisos, configuración externa o artefactos no disponibles, marcarla `BLOQUEADA` y documentar la razón; no falsear el 100 %.
7. Actualizar el roadmap y producir un informe de cierre con cambios, tests, riesgos residuales y commit final.
8. No fusionar las ramas de trabajo entre sí ni en `main` durante su ejecución. La integración se revisará al terminar el ciclo y requerirá decisión explícita del mantenedor.

## Definición del avance

Los porcentajes se basan en tareas aceptadas y ponderadas por importancia, no en cantidad de archivos ni commits. Una tarea parcialmente resuelta no cuenta como terminada. Cada roadmap contiene el criterio de 100 % de su categoría.

## Fuera del ciclo actual

- Prueba de arranque en hardware.
- Verificación física de que el almacenamiento interno permanece intacto.
- Caracterización de GPU, audio, red, temperatura, gaming, emulación y LLM.

Estas fases se reabren después de completar la preparación documental, las herramientas, la auditoría, la compatibilidad previa al laboratorio y la imagen host-side.
