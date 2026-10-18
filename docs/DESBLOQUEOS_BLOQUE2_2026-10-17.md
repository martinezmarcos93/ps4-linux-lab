# Desbloqueos del bloque 2 — 2026-10-17

Tres bloqueos que dependen de cuentas o de la consola de Marcos. Se dejó listo todo lo que se podía hacer sin ellas.

## 1. CI de GitHub Actions — RESUELTO (`TESTS`)
Los runs recientes arrancan y pasan: `main` en `success` (run 111 y anteriores, 2026-10-16) y los PR de ChatGPT/OpenCode ejecutan el workflow. El único fallo reciente (`chatgpt/image-input-snapshot-integrity`, 2026-10-17) lo corrige el fixture UTF-8 de `opencode/image-input-snapshot-ci-fix`, ya integrado en `integracion/2026-10-17`. Se actualizaron `ROADMAP.md` y `PUBLIC_PROJECT_STATUS.md`. Queda decidir la protección de `main` (decisión de Marcos). El CI de la rama de integración solo se verá al pushearla.

## 2. Acceso al kernel Baikal (`rmuxnet/linux`) — PENDIENTE de Marcos
El repositorio existe y su metadato público (API de GitLab, 200) dice: "PlayStation 4 Strawberry Kernel. To request access, contact @dreams-of-formaldehyde. Also known as 'leg' on Discord and Fluxer." No es un botón de GitLab: el acceso se pide por contacto directo.

Borrador de mensaje (revisar antes de enviar):
> Hola, soy Marcos. Estoy auditando de forma reproducible el kernel Strawberry Baikal 7.0.8 (`bzImage-baikal-7.0.8`, sha256 `46c835f762e7b0b5400ea762b8daa1bcec638a1b769c7ec0905137bc565b1ba8`) para una PS4 Slim CUH-2115B con FW 13.52. ¿Me das acceso de lectura a `gitlab.com/rmuxnet/linux` (o al commit/tag y el `.config` de ese build)? Solo lo uso para verificar el origen del binario, sin redistribuirlo.

Sin la fuente, el kernel sigue como binario de procedencia no verificable (riesgo R-22).

## 3. R-23: versión de GoldHEN — PENDIENTE de Marcos (`OBSERVADO`)
Búsqueda hecha: no hay ninguna captura de la pantalla *About* en el disco de trabajo. Lo único con evidencia es `logs/serve-2026-10-15.log` en `PS4-Linux-artefactos`: el 2026-10-15 a las 21:15 la PS4 (192.168.1.69) descargó `/goldhen.bin`, cuyo hash es `df3f27c1b35bc7c40e3a08caab948930914dc7d0301a73b68945cf6ffe40ea12`. LAB-001 es del 2026-10-16 y no hay log de servidor de ese día, así que **no se puede afirmar** que el binario cargado en LAB-001 fuera ese. No se corrige ni se descarta v2.2.3.

Para cerrarlo, la próxima vez que se sirva el payload: guardar el log del servidor del día, hacer la captura de *About GoldHEN* y registrar su SHA-256 junto con el hash servido.
