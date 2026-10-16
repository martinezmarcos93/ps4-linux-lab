# Plan maestro de workstreams — PS4 Linux Lab

**Fecha:** 2026-10-16  
**Base de coordinación:** `main`  
**Política:** cada categoría avanza en su propia rama; no integrar a `main` sin revisión y autorización de Marcos.

## Orden de trabajo

Cada rama contiene su propio roadmap. Los enlaces apuntan directamente a la rama correspondiente porque esos archivos todavía no están integrados en `main`.

| Orden | Categoría | Rama | Lidera | Revisión cruzada | Roadmap |
|---:|---|---|---|---|---|
| 1 | Documentación y gobernanza | `workstream/01-docs-governance` | Codex CLI 1 | ChatGPT | [ROADMAP](https://github.com/martinezmarcos93/ps4-linux-lab/blob/workstream/01-docs-governance/docs/workstreams/01-docs-governance/ROADMAP.md) |
| 2 | Herramientas y tests host-side | `workstream/02-tools-tests` | Codex CLI 1 | ChatGPT | [ROADMAP](https://github.com/martinezmarcos93/ps4-linux-lab/blob/workstream/02-tools-tests/docs/workstreams/02-tools-tests/ROADMAP.md) |
| 3 | Auditoría upstream y licencias | `workstream/03-upstream-audit` | Codex CLI 2 | ChatGPT | [ROADMAP](https://github.com/martinezmarcos93/ps4-linux-lab/blob/workstream/03-upstream-audit/docs/workstreams/03-upstream-audit/ROADMAP.md) |
| 4 | Identificación y compatibilidad | `workstream/04-compatibility` | ChatGPT | Codex CLI 2 | [ROADMAP](https://github.com/martinezmarcos93/ps4-linux-lab/blob/workstream/04-compatibility/docs/workstreams/04-compatibility/ROADMAP.md) |
| 5 | Imagen y cadena USB-only | `workstream/05-usb-image` | Codex CLI 1 | ChatGPT | [ROADMAP](https://github.com/martinezmarcos93/ps4-linux-lab/blob/workstream/05-usb-image/docs/workstreams/05-usb-image/ROADMAP.md) |

## Reglas de coordinación

1. Codex CLI 1 es el agente principal de implementación; Codex CLI 2 realiza la auditoría independiente asignada. ChatGPT revisa y mantiene las tareas explícitamente asignadas.
2. Cada agente trabaja únicamente en las ramas asignadas y no cambia de rama sin registrar el traspaso.
3. No modificar `main` directamente. Las ramas de trabajo deben abrir PR o entregar un diff revisable; Marcos autoriza la integración.
4. No trabajar en paralelo sobre el mismo archivo si eso genera conflictos. El revisor propone cambios en comentarios o en una rama separada.
5. Mantener cada roadmap actualizado: tarea, estado, evidencia, commit, tests ejecutados, bloqueos y próximo paso.
6. No marcar tareas al 100 % por haber escrito documentación. Se exige cumplir sus criterios de aceptación.
7. Estados permitidos: `PENDIENTE`, `EN CURSO`, `BLOQUEADO`, `IMPLEMENTADO`, `TESTS`, `CÓDIGO`, `TERCEROS`, `VERIFICADO` cuando corresponda.
8. Un test solo se marca como ejecutado si el comando realmente corrió; registrar salida real y entorno.
9. No ejecutar payloads, no realizar pruebas físicas y no escribir en USB o almacenamiento interno en estas cinco categorías. La validación de hardware y la caracterización GPU/gaming/LLM quedan fuera del ciclo actual.
10. Las categorías pueden alcanzar 100 % de su alcance documental/host-side aunque la compatibilidad de hardware siga indeterminada. Nunca presentar ese 100 % local como 100 % del objetivo general del proyecto.
11. Si un resultado depende de un dato que no puede obtenerse con las herramientas disponibles, documentar el bloqueo y la evidencia necesaria; no inventar certeza.

## Definición de “100 %”

Una categoría llega al 100 % cuando todas sus tareas están completadas con evidencia, se cumplen todos sus criterios de aceptación, los tests aplicables están ejecutados y no quedan bloqueos ocultos. Si una tarea está bloqueada por una dependencia externa, la categoría no se declara completa: se informa el porcentaje real y el impedimento.

## Secuencia de ejecución

- **Ciclo A:** workstream 01; Codex CLI 1 ejecuta el barrido documental completo.
- **Ciclo B:** workstream 02; Codex CLI 1 ejecuta tests, clasifica fallos y corrige defectos reproducidos.
- **Ciclo C:** workstream 03; Codex CLI 2 lidera la auditoría de fuentes/licencias y ChatGPT revisa la evidencia.
- **Ciclo D:** workstream 04; ChatGPT mantiene la matriz y la decisión de compatibilidad sustentada, con revisión de Codex CLI 2.
- **Ciclo E:** workstream 05; Codex CLI 1 implementa y prueba en dry-run el pipeline USB-only, ChatGPT hace revisión de seguridad independiente.

Se puede preparar trabajo posterior mientras otra rama está bloqueada, pero se respetan las dependencias y no se elige una imagen final sin compatibilidad y procedencia suficientes.
