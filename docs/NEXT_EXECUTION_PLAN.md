# Plan de ejecución siguiente

**Actualizado:** 2026-10-15  
**Estado global:** investigación offline y herramientas de PC; no ejecutar payload en la PS4 todavía.

## Decisiones de trabajo
- Prioridad de arranque: USB-only. No escribir en `/data/linux/boot/` por defecto.
- `goldhen.bin`: no ejecutar en hardware hasta completar análisis estático reproducible y revisar procedencia.
- REA: diferido. Primero comprobar si ya existe Rizin/objdump; no instalar un MCP adicional ni ejecutar `npx rea-agents setup` todavía.
- Herramientas: desarrollar y probar en PC con archivos temporales e imágenes virtuales; ninguna escritura a dispositivos físicos.
- Red: no probar el exploit mientras la consola tenga salida a Internet/PSN. La desconexión efectiva aún no está verificada.
- CUH/southbridge: seguir como desconocidos; no inferirlos por familia Slim ni capacidad del disco.

## Tarea A — Auditar el payload nativo sin ejecutarlo
**Responsable sugerido:** Claude Code en el equipo local.  
**Estado:** PENDIENTE.

1. Confirmar que el checkout local está limpio y que `main` incluye el commit publicado `bdf7bb7d6f510dd33d6c26a52e2d21c69fe482e3`.
2. Verificar qué herramientas existen (`rizin`, `rz-bin`, `objdump`, `llvm-objdump`, `strings`, `sha256sum`). No instalar nada sin necesidad demostrada.
3. Descargar el archivo de la revisión exacta `raw13g/raw13g.github.io@9ba2f07` a un directorio temporal fuera del repo. No ejecutar ni servir el archivo.
4. Calcular SHA-256 y comprobar que coincide con `df3f27c1b35bc7c40e3a08caab948930914dc7d0301a73b68945cf6ffe40ea12`. Si no coincide, parar y explicar la discrepancia.
5. Analizar el blob como x86-64 crudo con herramienta estática, documentando dirección base asumida, límites de decodificación, saltos, regiones no decodificables y referencias a estructuras/offsets. No presentar un desensamblado lineal como prueba de comprensión completa.
6. Comparar, si se obtiene una referencia oficial legítima y verificable, hashes y diferencias con la versión oficial más cercana. No llamar “oficial” a un binario solo por su nombre o cadenas.
7. Revisar los datos de entrada y los artefactos auxiliares usados por el exploit, manteniendo todo offline.
8. Escribir `docs/EXPLOIT_AUDIT_13.52.md` con método, comandos, versiones de herramientas, hashes, observaciones, limitaciones y conclusión. Si no se puede concluir qué hace el payload, el estado sigue siendo **NO VERIFICADO**.
9. No ejecutar el binario, no lanzarlo contra la consola y no instalar REA como atajo.

**Salida exigida:** auditoría reproducible, con afirmaciones clasificadas como observación/inferencia/hipótesis y una lista explícita de preguntas sin resolver.

## Tarea B — Utilidades de PC no destructivas
**Estado:** PENDIENTE; puede avanzar en paralelo.

1. [x] Implementar verificador de manifiestos SHA-256 de solo lectura en `tools/verify_artifacts.py`.
2. [x] Añadir 11 tests para hash correcto/incorrecto, tamaño, archivo ausente/vacío, manifiesto malformado, rutas inseguras y symlinks.
3. [x] Ejecutar la suite en sandbox local: 11/11 PASS.
4. [ ] Diagnosticar el workflow GitHub Actions: los runs observados terminaron en FAIL con runner_id=0, sin pasos ni logs disponibles; no asumir que la suite falló ni que pasó.
5. [ ] Confirmar en CI que se ejecuta `python -m unittest discover -v` y que los tests pasan.
6. [ ] Implementar inspección de imagen en modo solo lectura; no abrir block devices ni escribir medios.
7. [ ] Añadir un `doctor` que informe dependencias y sistema operativo sin instalar ni cambiar nada.
8. [ ] No implementar aún la escritura física de USB. Mantenerla fuera del código ejecutable hasta revisar y aprobar los tests.

**Salida exigida:** código, tests, comandos reproducibles y resultados reales. No marcar pruebas como PASS si no se ejecutaron.

## Tarea C — Compatibilidad y hardware
**Estado:** PARCIAL/BLOCKED.

- Mantener en la matriz: Slim inferida por foto, firmware 13.52 observado, capacidad 861,4 GB (clase nominal de 1 TB), CUH desconocido, southbridge desconocido, ningún arranque propio.
- No abrir la consola ni retirar sellos para buscar el CUH como primera opción.
- Si se obtiene una lectura fiable de la etiqueta/caja, actualizar el registro; si no, mantener desconocido hasta que exista un método de identificación seguro.
- La identificación de southbridge en runtime solo será posible después de un método de ejecución aprobado; no usarla como justificación para ejecutar un payload sin revisar.

## Tarea D — Red y precondiciones de una futura prueba
**Estado:** NO COMPLETADA.

- Confirmar que las actualizaciones automáticas de sistema están desactivadas en la PS4.
- Antes de cualquier ejecución futura, establecer y verificar una regla reversible que impida salida a Internet/PSN sin bloquear la conexión local necesaria para el laboratorio.
- No afirmar que DNS manual o un bloqueo de MAC aísla la consola hasta comprobarlo.
- Una eventual prueba de exploit/payload requiere un consentimiento específico posterior; esta planificación no lo autoriza.

## Puertas de decisión
- **Gate 1:** hash del payload verificado y análisis estático realizado.
- **Gate 2:** artefactos, licencias y método de arranque revisados; USB-only probado con imagen virtual.
- **Gate 3:** red aislada de forma comprobable, actualización automática desactivada y procedimiento de aborto documentado.
- **Gate 4:** consentimiento explícito antes de cualquier ejecución del exploit en la PS4.
- **Gate 5:** primer arranque externo solo después de identificar la combinación de hardware/firmware con la mejor evidencia disponible.

## Regla de reporte
Cada ejecución de Claude Code debe terminar con: archivos cambiados, commit SHA, pruebas ejecutadas y resultado, comandos usados, riesgos residuales y siguiente paso recomendado. Si no pudo verificar algo, debe decirlo explícitamente.
