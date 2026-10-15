# Plan inmediato (2026-10-15)

Objetivo: llegar a un primer arranque de Linux desde USB **sin escribir en el disco interno**, avanzando por etapas con puertas claras. Decisiones tomadas: D-008 a D-013 en `DECISION_LOG.md`.

## Etapa 0 — Preparación (sin tocar la consola) — HECHO en lo posible
- [x] Auditoría estática del exploit y de su host (`EXPLOIT_AUDIT_13.52.md`).
- [x] Manifiesto con SHA-256 fijados (`manifests/raw13g-9ba2f07.json`).
- [x] `tools/ps4lab.py`: `verify` y `serve` (solo lectura, lista blanca, solo IP privada) con tests (`tests/test_ps4lab.py`, 8 OK).
- [ ] **Marcos (en la PS4, 2 minutos):** desactivar *Descargar automáticamente archivos de actualización* y la actualización en reposo; rechazar toda actualización.
- [ ] **Marcos:** buscar el CUH en parte trasera/caja/factura (no bloquea).

## Etapa 1 — Descargar los artefactos del kernel/rootfs (PC, sin consola)
- [ ] Clonar `X-F1REBALL-X/PS4-Linux` y `ps4-linux/ps4-linux-loader` en carpeta externa al repo (no se incorporan binarios de terceros al repo, `LICENSE_POLICY.md`).
- [ ] Generar manifiestos para `bzImage-baikal-7.0.8`, `bzImage-belize-7.1.7`, initramfs y rootfs; guardar SHA-256.
- [ ] Construir la imagen USB **a un archivo** (no a un dispositivo) con `tools/build-img.sh` revisado, y verificarla. Aún sin escribir en ningún pendrive.
- **Puerta:** hashes registrados y la imagen virtual verificada.

## Etapa 2 — Escribir el USB (decisión puntual de Marcos)
- [ ] `write-usb-image` aún no existe; se construye con tests sobre imágenes virtuales (Fase 4 del roadmap). Hasta entonces, escritura manual con el pendrive **identificado por modelo/tamaño/serie**, nunca por `/dev/sdX`, y con confirmación tuya.

## Etapa 3 — Primer intento real (requiere el "go" de Marcos, D-011)
Preflight, en orden:
1. `python3 tools/ps4lab.py verify --dir <copia> --manifiesto manifests/raw13g-9ba2f07.json` → OK.
2. PS4: DNS manual `127.0.0.1`, sin sesión de PSN.
3. `python3 tools/ps4lab.py serve --dir <copia> --manifiesto manifests/raw13g-9ba2f07.json --ip 192.168.1.69 --log logs/serve.log`.
4. En el navegador de la PS4: `http://192.168.1.69:8080/`.
5. Registrar todo en `docs/lab-logs/LAB-001-*.md`. Capturar el log del payload (**southbridge**: da el dato que falta).
- **Abortar si:** cuelgue repetido, mensajes de error de disco, o cualquier solicitud de red inesperada en `logs/serve.log`. Un reinicio limpia el estado (no persistente).
- **Puerta:** southbridge identificado y estado de GoldHEN cargado, o fallo documentado.

## Etapa 4 — Primer arranque de Linux (solo-USB)
Con el southbridge conocido se elige `baikal` o `belize` y se prueba el flujo solo-USB. Si falla de forma reproducible, se propone la Opción A y se pide tu confirmación (D-008).

## En paralelo
- HDMI contra el monitor: probar otra entrada/cable o modo seguro → *Cambiar resolución*; no bloquea nada (la TV sirve).
- Sin etiqueta: si el southbridge sale en Etapa 3, el CUH deja de ser necesario para elegir kernel.
