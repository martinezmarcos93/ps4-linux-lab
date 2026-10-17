# Coordinación de trabajo — PS4 Linux Lab

**Actualizado:** 2026-10-16  
**Base integrada:** `main`  
**Estado:** las cinco ramas `workstream/01..05` y las ramas temporales de auditoría se integraron en `main` durante la consolidación del 2026-10-16. No deben tratarse como ramas activas ni como roadmaps pendientes de integrar.

## Estado de coordinación

La consolidación y el traspaso están documentados en [HANDOFF_LINUX_2026-10-16.md](HANDOFF_LINUX_2026-10-16.md) y [INTEGRACION_RAMAS_2026-10-16.md](INTEGRACION_RAMAS_2026-10-16.md). Los roadmaps por categoría que se integraron son documentación histórica y de referencia; sus enlaces a ramas eliminadas no son el mecanismo de coordinación vigente.

| Área | Estado actual | Responsable operativo | Próximo resultado verificable |
|---|---|---|---|
| Documentación y gobernanza | Integrada; quedan inconsistencias históricas por corregir | ChatGPT revisa; OpenCode puede aplicar cambios locales acotados | Documentación coherente con el estado real de `main` |
| Herramientas y tests host-side | Suite Linux reportada como 321 tests, 0 fallos, 0 errores y 2 omitidos; CI reciente en verde | OpenCode ejecuta; ChatGPT revisa hallazgos | Reproducción en el entorno local y cobertura de regresiones |
| Auditoría upstream y licencias | Parcial; faltan fuentes y permisos de algunos componentes | ChatGPT investiga evidencia pública; OpenCode inspecciona artefactos locales | Inventario por artefacto con procedencia, hash, licencia y límites |
| Identificación y compatibilidad | CUH-2115B, FW 13.52 y Baikal B1 observados; kernel no aprobado | ChatGPT consolida la decisión con evidencia | Decisión de kernel sustentada y bloqueos explícitos |
| Imagen y cadena USB-only | Diseño y herramientas existentes; imagen final no validada | OpenCode compila/prueba en PC; ChatGPT realiza revisión de seguridad | Loader reproducido y construcción virtual auditada |

## Reglas vigentes

1. `main` es la base integrada. No trabajar directamente sobre ella para tareas nuevas.
2. Crear una rama de trabajo por unidad coherente y pequeña. No recrear las antiguas ramas `workstream/01..05` solo para continuar la misma planificación.
3. No fusionar ramas ni publicar cambios en `main` sin autorización explícita de Marcos.
4. OpenCode ejecuta operaciones locales y pruebas que necesitan el entorno de Marcos; ChatGPT realiza revisión de código, coherencia documental, análisis de evidencia y revisión cruzada.
5. No hacer que dos agentes modifiquen simultáneamente los mismos archivos. Registrar el SHA base y entregar diffs/commits verificables.
6. Cada informe debe separar comandos ejecutados, resultados reales, afirmaciones de terceros, inferencias y tareas bloqueadas.
7. No ejecutar payloads ni realizar pruebas físicas como parte del ciclo de trabajo en PC. La escritura de un USB físico, la ejecución de payloads y el arranque en hardware requieren autorización específica.
8. USB-only sigue siendo la arquitectura objetivo, no una propiedad demostrada en runtime. Nunca usar el almacenamiento interno como fallback.
9. No declarar el kernel compatible ni la consola arrancada por tener tests host-side en verde.
10. Los porcentajes de preparación no representan el porcentaje de éxito del objetivo final.

## Próxima secuencia

1. **Reproducción local:** OpenCode ejecuta `bash scripts/check.sh` y reproduce la compilación del loader original y del parcheado USB-only.
2. **Revisión independiente:** ChatGPT audita las inconsistencias documentales y revisa los puntos críticos del constructor de imagen y la cadena de arranque.
3. **Procedencia:** resolver acceso a las fuentes de Strawberry y completar la auditoría de kernel, initramfs y rootfs reales.
4. **Imagen virtual:** construir solo cuando las entradas exactas estén catalogadas y aceptadas; comprobar la imagen como archivo regular.
5. **Decisión de laboratorio:** preparar una revisión de riesgos y criterios de aborto. Ninguna de estas tareas autoriza por sí sola a escribir el USB físico ni a arrancar la consola.
