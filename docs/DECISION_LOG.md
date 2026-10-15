# Registro de decisiones

## D-001 — Priorizar arranque externo
- **Fecha:** 2026-10-15
- **Estado:** ACEPTADA como estrategia inicial.
- **Decisión:** probar Linux desde USB y mantener el almacenamiento interno de la consola intacto.
- **Motivo:** reduce riesgo y facilita volver al sistema original.
- **Revisión:** si el loader requiere persistir archivos en el almacenamiento interno, evaluar ese requisito antes de ejecutarlo.

## D-002 — No asumir compatibilidad por categoría de consola
- **Fecha:** 2026-10-15
- **Estado:** ACEPTADA.
- **Decisión:** identificar CUH, firmware y southbridge/revisión; tratar las tablas comunitarias como evidencia de distinto nivel.
- **Motivo:** modelos Slim/Pro pueden variar internamente.

## D-003 — Separar arranque, gráficos y LLM
- **Fecha:** 2026-10-15
- **Estado:** ACEPTADA.
- **Decisión:** no instalar frameworks de IA hasta validar kernel, driver y API de cómputo.
- **Motivo:** evita invertir tiempo en una aceleración que quizá no esté disponible.

## D-004 — No copiar payloads/binarios por defecto
- **Fecha:** 2026-10-15
- **Estado:** ACEPTADA.
- **Decisión:** consumir releases upstream con manifiestos de hash; copiar código solo tras revisar licencia.
- **Motivo:** procedencia, seguridad y obligaciones legales.

## D-005 — Nombre propuesto del repo
- **Fecha:** 2026-10-15
- **Estado:** RESUELTA — repositorio creado y disponible en `https://github.com/martinezmarcos93/ps4-linux-lab` (privado).
- **Decisión:** `martinezmarcos93/ps4-linux-lab`, privado.

## D-006 — Ubicación del kernel/initramfs: ¿almacenamiento interno (FTP) o USB-only? **[BLOQUEANTE, PENDIENTE]**
- **Fecha:** 2026-10-15 (abierta por la auditoría de código de upstream).
- **Estado:** PENDIENTE — requiere decisión explícita de Marcos antes de ejecutar la Fase 3/5 del roadmap.
- **Contexto (HECHO DOCUMENTADO + OBSERVACIÓN DE CÓDIGO):** el procedimiento oficial de `X-F1REBALL-X/PS4-Linux` (README) instruye subir por FTP el `bzImage` y `initramfs.cpio.gz` a `/data/linux/boot/` en el almacenamiento interno de la consola; el USB solo lleva el rootfs. El código del loader (`main-aio.c`, ver `docs/UPSTREAM_CODE_MAP.md` §1.3 y `docs/BOOT_FLOW.md` Fase 2) sí soporta leer ambos archivos desde el USB con prioridad sobre el almacenamiento interno — un flujo 100% externo es técnicamente posible pero no es el que documenta ni prueba la distribución elegida.
- **Opciones:**
  - **A.** Seguir el procedimiento oficial (escribir en `/data/linux/boot/`). Modificación acotada y reversible (borrar una carpeta), pero contradice literalmente el Hito A del `PROJECT_CHARTER.md` ("ninguna modificación del disco interno") y el principio "el almacenamiento interno se considera solo lectura" de `ARCHITECTURE.md`.
  - **B.** Adaptar `tools/build-img.sh` para colocar el `bzImage` correcto en la partición de arranque del USB (hoy el script lo evita deliberadamente, renombrándolo, para permitir compartir un USB entre consolas de southbridge distinto). Mantiene el principio original pero no tiene ningún reporte de terceros que la haya probado así.
- **Motivo de que esté bloqueando:** no se puede ejecutar TP-05/TP-06 de `docs/TEST_PLAN.md` sin esta decisión. No es una pregunta retórica — cambia qué script se ejecuta y qué se le pide a Marcos que autorice.
- **Revisión:** se resuelve antes de la Fase 1 real sobre hardware, aunque puede decidirse antes de tener la consola identificada.

## D-007 — Numeración de versión del kernel "7.1.7"/"7.0.8": aclarar antes de citarla como versión de Linux
- **Fecha:** 2026-10-15.
- **Estado:** PENDIENTE DE VERIFICACIÓN, no bloqueante para avanzar el roadmap, pero sí para cualquier documento que cite una versión de kernel Linux real.
- **Contexto:** ver discrepancia D-B en `docs/EVIDENCE_SOURCES.md` §4. El archivo de configuración de la distribución se autodenomina "Linux/x86_64 7.1.7"; un reporte de comunidad (issue #10 del loader) describe "Kernel 5.4.247". Ambos no pueden ser literalmente la misma cifra de versión de Linux mainline.
- **Hipótesis de trabajo:** "7.1.7"/"7.0.8" son la numeración propia del fork "Strawberry" (rmuxnet), no la versión de Linux. No confirmada — el repositorio de ese kernel no fue identificado ni auditado en esta sesión.
- **Acción pendiente:** localizar el repositorio del kernel "Strawberry" (o la fuente que rmuxnet use) y confirmar la versión real de Linux mainline sobre la que está basado, antes de redactar cualquier documento que dependa de esa versión (por ejemplo, para evaluar compatibilidad de drivers o de un backend de cómputo).

## Preguntas abiertas que bloquean decisiones futuras (no son tareas, son preguntas a Marcos o a evidencia externa)

1. **¿Se autoriza, en principio, la Opción A de D-006 (escritura acotada en `/data/linux/boot/`) si no hay otra forma documentada y probada de lograr un primer arranque exitoso?** Sin esta respuesta, la Fase 3 no puede ejecutarse aunque todo lo demás esté listo.
2. **¿Existe tolerancia a repetir el ciclo de jailbreak varias veces en la misma sesión de prueba?** El propio upstream documenta que 2-3 intentos son normales (ver `docs/TROUBLESHOOTING.md` caso 2) — esto afecta cuánto tiempo de sesión planificar para TP-06, no es una decisión técnica sino de expectativas.
3. **¿Vale la pena, antes de tener la consola, investigar específicamente soporte ROCm/Vulkan-compute para GCN1-GCN4** (vacío identificado en `docs/GPU_AND_LLM_RESEARCH.md` §5) **para no descubrir un descarte evitable recién en la Fase 8?** Es una pregunta de priorización de tiempo, no de autorización.
