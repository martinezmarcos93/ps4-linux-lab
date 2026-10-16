# Plan maestro de workstreams — PS4 Linux Lab

**Fecha:** 2026-10-16  
**Base de coordinación:** `main`  
**Política:** cada categoría avanza en su propia rama; no integrar a `main` sin revisión y autorización de Marcos.

## Orden de trabajo

El orden se define de menor a mayor complejidad. Las ramas ya existen y cada una contiene su propio roadmap de tareas con criterios de aceptación.

| Orden | Categoría | Rama | Lidera | Revisión cruzada | Roadmap |
|---:|---|---|---|---|---|
| 1 | Documentación y gobernanza | `workstream/01-docs-governance` | Claude Code | ChatGPT | [ROADMAP](workstreams/01-docs-governance/ROADMAP.md) |
| 2 | Herramientas y tests host-side | `workstream/02-tools-tests` | Claude Code | ChatGPT | [ROADMAP](workstreams/02-tools-tests/ROADMAP.md) |
| 3 | Auditoría upstream y licencias | `workstream/03-upstream-audit` | ChatGPT | Claude Code | [ROADMAP](workstreams/03-upstream-audit/ROADMAP.md) |
| 4 | Identificación y compatibilidad | `workstream/04-compatibility` | ChatGPT | Claude Code | [ROADMAP](workstreams/04-compatibility/ROADMAP.md) |
| 5 | Imagen y cadena USB-only | `workstream/05-usb-image` | Claude Code | ChatGPT | [ROADMAP](workstreams/05-usb-image/ROADMAP.md) |

## Reglas de coordinación

1. Cada agente trabaja únicamente en las ramas asignadas y no cambia de rama sin registrar el traspaso.
2. No modificar `main` directamente. Las ramas de trabajo deben abrir PR o entregar un diff revisable; Marcos autoriza la integración.
3. No trabajar en paralelo sobre el mismo archivo si eso genera conflictos. El revisor propone cambios en comentarios o en una rama separada.
4. Mantener cada roadmap actualizado: tarea, estado, evidencia, commit, tests ejecutados, bloqueos y próximo paso.
5. No marcar tareas al 100 % por haber escrito documentación. Se exige cumplir sus criterios de aceptación.
6. Estados permitidos: `PENDIENTE`, `EN CURSO`, `BLOQUEADO`, `IMPLEMENTADO`, `TESTS`, `CÓDIGO`, `TERCEROS`, `VERIFICADO` cuando corresponda.
7. Un test solo se marca como ejecutado si el comando realmente corrió; registrar salida real y entorno.
8. No ejecutar payloads, no realizar pruebas físicas y no escribir en USB o almacenamiento interno en estas cinco categorías. La validación de hardware y la caracterización GPU/gaming/LLM quedan fuera del ciclo actual.
9. Las categorías pueden alcanzar 100 % de su alcance documental/host-side aunque la compatibilidad de hardware siga indeterminada. Nunca presentar ese 100 % local como 100 % del objetivo general del proyecto.
10. Si un resultado depende de un dato que no puede obtenerse con las herramientas disponibles, documentar el bloqueo y la evidencia necesaria; no inventar certeza.

## Definición de “100 %”

Una categoría llega al 100 % cuando todas sus tareas están completadas con evidencia, se cumplen todos sus criterios de aceptación, los tests aplicables están ejecutados y no quedan bloqueos ocultos. Si una tarea está bloqueada por una dependencia externa, la categoría no se declara completa: se informa el porcentaje real y el impedimento.

## Secuencia de ejecución

- **Ciclo A:** workstream 01; Claude Code ejecuta el barrido documental completo.
- **Ciclo B:** workstream 02; Claude Code ejecuta tests, clasifica fallos y corrige defectos reproducidos.
- **Ciclo C:** workstream 03; ChatGPT lidera auditoría de fuentes/licencias y Claude reproduce verificaciones locales.
- **Ciclo D:** workstream 04; ChatGPT construye la matriz y una decisión de compatibilidad sustentada.
- **Ciclo E:** workstream 05; Claude implementa y prueba en dry-run el pipeline USB-only, ChatGPT hace revisión de seguridad independiente.

Se puede preparar trabajo posterior mientras otra rama está bloqueada, pero se respetan las dependencias y no se elige una imagen final sin compatibilidad y procedencia suficientes.
