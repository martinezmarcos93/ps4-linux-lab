# Roadmap de categoría 2 — Herramientas y tests host-side

**Rama:** `workstream/02-tools-tests`  
**Responsable de ejecución:** Claude Code  
**Orden:** 2 de 5 — complejidad baja/media  
**Objetivo:** dejar las herramientas locales y la suite host-side reproducibles, seguras y verificadas en un entorno limpio. No demuestra funcionamiento en PS4.

## Criterio de 100 %

El 100 % significa que todas las herramientas incluidas en el alcance tienen uso documentado, validación de entradas, pruebas automatizadas adecuadas, resultados reproducibles y un informe de ejecución limpio. No significa que la consola sea compatible.

## Tareas

- [ ] TT-01 Inspeccionar estructura real de herramientas, scripts, tests, dependencias y comandos del README.
- [ ] TT-02 Ejecutar `bash scripts/check.sh` en el estado inicial y guardar salida exacta, duración y entorno.
- [ ] TT-03 Clasificar fallos en preexistentes, regresiones, defectos de entorno y falsos positivos; no modificar código antes de tener baseline.
- [ ] TT-04 Auditar seguridad de herramientas que leen manifiestos, procesan payloads/ELF y construyen imágenes.
- [ ] TT-05 Confirmar que las rutas host-side no escriben en dispositivos de bloque ni ejecutan artefactos externos.
- [ ] TT-06 Añadir tests para entradas inválidas, rutas inexistentes, hashes incorrectos, archivos truncados, formatos malformados y rutas con espacios.
- [ ] TT-07 Verificar idempotencia y no modificación de archivos fuente en comandos de inspección y dry-run.
- [ ] TT-08 Revisar mensajes de error, códigos de salida y comportamiento ante interrupciones cuando corresponda.
- [ ] TT-09 Revisar cobertura funcional por herramienta; priorizar casos de seguridad y regresión, no perseguir un porcentaje artificial.
- [ ] TT-10 Ejecutar tests focalizados y suite completa en entorno limpio; registrar resultados reales.
- [ ] TT-11 Corregir workflow CI si el problema está dentro del repositorio; si es facturación/configuración de cuenta, documentar bloqueo y pasos externos sin fingir solución.
- [ ] TT-12 Actualizar documentación de comandos, requisitos y resultados de tests.
- [ ] TT-13 Generar informe de calidad con riesgos residuales y decisión de aceptación.

## Fuera de alcance

No ejecutar pruebas en la consola, no escribir a USB físico, no validar compatibilidad del kernel y no redistribuir payloads de terceros.

## Criterios de aceptación

1. Baseline anterior a los cambios y resultados posteriores registrados.
2. Tests reproducibles; ningún test reportado como aprobado si no se ejecutó.
3. Tests de seguridad cubren entradas adversariales razonables.
4. Los comandos documentados coinciden con la implementación actual.
5. CI queda verde o el bloqueo externo queda demostrado y documentado.
6. No se hace merge a `main` ni a una rama de integración sin autorización del mantenedor.

## Registro de ejecución

| ID | Estado | Evidencia / commit | Observaciones |
|---|---|---|---|
| TT-01…TT-13 | PENDIENTE | — | Completar al ejecutar |

**Dependencia:** recibir del responsable de categoría 1 la nomenclatura y reglas documentales; no bloquear el baseline de tests por tareas cosméticas.