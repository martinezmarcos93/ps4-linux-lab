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
- **Estado:** PENDIENTE de creación.
- **Decisión propuesta:** `martinezmarcos93/ps4-linux-lab`, privado.
