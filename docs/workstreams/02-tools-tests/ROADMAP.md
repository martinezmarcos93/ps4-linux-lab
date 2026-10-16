# Workstream 02 — Herramientas y tests host-side

**Responsable principal:** Claude Code  
**Revisor de diseño y resultados:** ChatGPT  
**Prioridad:** 2 de 5  
**Objetivo:** que las herramientas locales sean seguras, deterministas, comprobables y tengan una suite ejecutable en un entorno limpio.

## Alcance

Scripts de verificación de artefactos, cadena de arranque, payload/ELF, constructor/preflight de imagen, chequeos documentales, tests y CI. No incluye escribir en USB físico ni ejecutar payloads en PS4.

## Tareas hasta el 100 %

- [ ] T01 — Inventariar herramientas, dependencias, entrypoints, tests y comandos documentados.
- [ ] T02 — Ejecutar el comando de test canónico en entorno limpio y guardar la salida real, incluyendo versión de Python/Bash y dependencias.
- [ ] T03 — Clasificar cada fallo como regresión, defecto preexistente, dependencia ambiental o test obsoleto.
- [ ] T04 — Revisar tests de seguridad para entradas malformadas, rutas, symlinks, archivos ausentes, hashes erróneos y datos límite.
- [ ] T05 — Verificar que ninguna herramienta escriba en dispositivos de bloque, monte unidades ni ejecute artefactos externos de forma implícita.
- [ ] T06 — Corregir defectos reproducidos con cambios mínimos y añadir test de regresión por cada arreglo.
- [ ] T07 — Revisar manejo de errores, códigos de salida, mensajes y comportamiento idempotente.
- [ ] T08 — Validar manifiestos y reproducibilidad de hashes/outputs en fixtures ficticios.
- [ ] T09 — Diagnosticar CI y lograr un run verificable; separar problemas del workflow de bloqueos de cuenta/facturación.
- [ ] T10 — Ejecutar toda la suite después de los cambios y registrar comando, entorno, resultado y limitaciones.
- [ ] T11 — Actualizar README y documentos de tooling solo con resultados comprobados.
- [ ] T12 — Publicar informe final de tests y deuda técnica restante.

## Criterios de aceptación

- La suite completa corre localmente desde un entorno limpio o cada bloqueo externo queda documentado con evidencia.
- Los defectos corregidos tienen pruebas de regresión.
- No hay escrituras a dispositivos físicos ni ejecución de payloads como parte de tests.
- Los resultados reportados son reproducibles y no se infieren de código sin ejecutar.
- CI queda verde en GitHub o se documenta con precisión el bloqueo externo no resoluble desde el repositorio.

## Restricciones

No editar `main` directamente. No cambiar el alcance de las herramientas para escribir dispositivos reales. No afirmar que los tests host-side validan el arranque de la consola.