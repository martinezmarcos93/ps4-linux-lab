# Estado público del proyecto — 2026-10-16

## Resumen ejecutivo

El repositorio es público y contiene una base sustancial de documentación, auditorías estáticas, manifiestos, utilidades de verificación y tests host-side. El objetivo operativo —arrancar Linux desde USB en la PS4 Slim CUH-2115B con firmware 13.52 sin modificar el almacenamiento interno— **todavía no está logrado ni verificado**.

**Estimación global de avance: 25 %.** Es una estimación del progreso técnico integral, no un porcentaje de documentos escritos. La investigación y las herramientas están avanzadas; los hitos decisivos de compatibilidad, preparación de imagen y prueba real siguen pendientes o bloqueados.

## Datos de laboratorio

- Consola: PS4 Slim CUH-2115B.
- Firmware registrado: 13.52.
- Capacidad observada: 861,4 GB (clase comercial de 1 TB).
- Southbridge: desconocido.
- Arquitectura objetivo: USB-only.
- Arranque Linux propio: no verificado.
- Pruebas de GPU, periféricos y temperatura: no realizadas.

## Trabajo realizado

1. Estructura de proyecto con README, contribución, roadmap, herramientas, manifiestos y documentación especializada.
2. Acta, arquitectura, registro de decisiones, riesgos, estrategia de recuperación y plan de pruebas.
3. Auditoría de fuentes upstream y fijación de commits/artefactos consultados.
4. Inspección del código del loader y distribución, incluidos caminos de lectura y escritura de almacenamiento.
5. Auditoría estática del material relacionado con firmware 13.52, con límites explícitos y sin confundir análisis con ejecución.
6. Matriz de compatibilidad que separa firmware, modelo, southbridge, kernel y nivel de evidencia.
7. Inventario de artefactos con procedencia, hashes y estado de licencias.
8. Manifiestos y utilidades para verificar artefactos, cadena de arranque, ELF y payload.
9. Constructor/preflight de imagen con enfoque de archivos y simulación, no escritura directa en dispositivos físicos.
10. Suite de tests host-side y validación documental.
11. Compilación aislada del loader documentada con evidencias de entorno y hashes.
12. Diseño USB-only, análisis de riesgos del pipeline y diagnóstico del estado de CI.
13. Actualización de README, guía de contribución y roadmap para reflejar que el proyecto es público.
14. Registro explícito de los pendientes de publicación y metadatos de GitHub.

Estos elementos acreditan investigación y preparación, no compatibilidad funcional de la consola.

## Pendientes prioritarios

### P0 — Bloqueos técnicos
- [ ] Identificar el southbridge o encontrar una vía de compatibilidad que no dependa de asumirlo.
- [ ] Resolver compatibilidad conjunta CUH-2115B + firmware 13.52 + loader + kernel con fuentes trazables.
- [ ] Auditar procedencia y licencias de todas las dependencias candidatas.
- [ ] Revisar la procedencia del payload candidato y no ejecutarlo mientras no estén resueltas las condiciones de seguridad y autorización.
- [ ] Confirmar mediante revisión y pruebas que el flujo propuesto no requiere escritura en el almacenamiento interno.

### P1 — Preparación reproducible
- [ ] Ejecutar la suite completa en un entorno limpio y conservar la salida real.
- [ ] Reparar/verificar GitHub Actions; el diagnóstico previo indica fallo antes de ejecutar el runner por facturación/configuración.
- [ ] Elegir kernel, initramfs y rootfs compatibles.
- [ ] Completar el manifiesto de artefactos con hashes esperados obtenidos de fuentes confiables.
- [ ] Construir y auditar una imagen candidata en PC, primero en modo dry-run.
- [ ] Completar revisión de recuperación, criterios de aborto y pasos de retorno.

### P2 — Laboratorio físico
- [ ] Autorizar explícitamente la prueba en consola una vez superadas las puertas anteriores.
- [ ] Ejecutar el primer arranque externo y registrar condiciones, logs, hashes y resultado.
- [ ] Verificar retorno al sistema original y ausencia de cambios no deseados.
- [ ] Medir GPU, audio, red, temperatura y estabilidad.
- [ ] Evaluar gaming, emulación y LLM únicamente con mediciones.

### P3 — Calidad de publicación
- [ ] Revisar enlaces internos, fechas, afirmaciones obsoletas y consistencia de todos los documentos.
- [ ] Completar los metadatos del repositorio: descripción, topics, licencia visible y configuración de colaboración.
- [ ] Revisar los archivos publicados para detectar secretos, datos sensibles o artefactos redistribuidos sin permiso.
- [ ] Mantener sincronizados README, roadmap, inventario y registro de decisiones.

## Estimación por área

| Área | Avance estimado | Justificación |
|---|---:|---|
| Gobernanza y documentación | 80 % | Base amplia; falta auditoría de consistencia de todos los documentos y metadatos públicos |
| Auditoría upstream | 65 % | Loader/distribución revisados; dependencias y licencias aún incompletas |
| Identificación y compatibilidad | 35 % | CUH y firmware registrados; southbridge y selección de kernel pendientes |
| Herramientas y tests host-side | 65 % | Utilidades implementadas; falta una ejecución limpia actual y CI funcional |
| Imagen y cadena USB-only | 15 % | Diseño y preflight; imagen final y aislamiento integral no demostrados |
| Prueba en hardware | 0 % | No hay arranque Linux propio verificado |
| Caracterización GPU/gaming/LLM | 0 % | Depende de arranque funcional y mediciones |

**Estimación global orientativa: 25 %.** No es un promedio aritmético estricto: los hitos de compatibilidad y laboratorio pesan más que la cantidad de documentación, porque convierten la investigación en un resultado funcional.

## Criterio de éxito

El proyecto no se considerará funcional hasta registrar un arranque Linux externo reproducible en la consola objetivo, comprobar el retorno al sistema original y documentar evidencia suficiente de que se respetó el objetivo USB-only. Hasta entonces, la formulación pública correcta es: **“investigación y preparación en curso; arranque propio aún no verificado”**.

## Metodología de actualización

Cada cambio futuro debe registrar fecha, alcance, archivos afectados, tests realmente ejecutados, resultados, evidencia y nuevos pendientes. No marcar `VERIFIED` sin prueba de laboratorio. Los porcentajes se actualizan cuando cambian hitos técnicos, no por cantidad de commits.
