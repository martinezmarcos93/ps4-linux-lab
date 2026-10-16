# Registro de fuentes y evidencia

Toda fuente usada en esta auditoría (sesión del 2026-10-15), con URL, versión/commit, fecha de consulta y nivel de confiabilidad. Ver `docs/COMPATIBILITY_MATRIX.md` para la escala de niveles de evidencia aplicada a afirmaciones de compatibilidad específicamente.

## 1. Repositorios de código (fuente primaria)

| # | Fuente | Commit/tag consultado | Fecha de consulta | Método | Confiabilidad |
|---|---|---|---|---|---|
| S-01 | [X-F1REBALL-X/PS4-Linux](https://github.com/X-F1REBALL-X/PS4-Linux) | `66e21cb8c15f20189254e2608c6e9bf957eb8078` (rama `main`) | 2026-10-15 | Clon superficial local + lectura directa de archivos | Alta — código/binarios propios, verificado de primera mano |
| S-02 | [ps4-linux/ps4-linux-loader](https://github.com/ps4-linux/ps4-linux-loader) | `f70f43a60a973b3662daeb29c1f115d95408db93` (rama `master`) | 2026-10-15 | Clon superficial local + lectura directa de archivos | Alta — código fuente completo, verificado de primera mano |

## 2. Releases publicados (metadata vía API de GitHub, no se descargaron los binarios de Release)

| # | Repo | Tag | Fecha de publicación | Notas |
|---|---|---|---|---|
| S-03 | PS4-Linux | `v1.0` | 2026-09-28 | Único release del repositorio de distribución |
| S-04 | ps4-linux-loader | `v25.1` | 2026-09-25 | Release más reciente a la fecha de consulta |
| S-05 | ps4-linux-loader | `v25` | 2026-07-25 | Incluye, según changelog del README, "FW 13.52 + Edid fix" |
| S-06 | ps4-linux-loader | `v24b.1` | 2026-05-11 | — |
| S-07 | ps4-linux-loader | `v24b` | 2026-04-03 | Según README: detección en runtime de Pro/southbridge/firmware, payload único para todos los firmwares soportados |
| S-08 | ps4-linux-loader | `v24` | 2026-04-02 | — |
| S-09 | ps4-linux-loader | `v23` | 2026-03-28 | Según README: añade fallback a `/user/system/boot/` (confirmado por `2769dd6`, 2026-03-28) y cita "Automatic boot files placement" (la frase del README es de 2025-09-26, **anterior** a v23; sin código) — **ver D-A** |
| S-10 | ps4-linux-loader | `v22`, `v21.5`, `v21`, `v20` | 2026-03-23 a 2025-12-24 | Historial de soporte incremental de firmwares, no auditado en detalle |

## 3. Issues y pull requests (evidencia de comunidad — nivel de confianza explícito en cada uno)

| # | Fuente | Tipo | Estado | Fecha | Resumen | Nivel de confianza |
|---|---|---|---|---|---|---|
| S-11 | [ps4-linux-loader#10](https://github.com/ps4-linux/ps4-linux-loader/issues/10) | Issue | Abierto | reporte 2026-09-22, ack 2026-09-23 | CUH-2208B (Baikal) FW 13.52 funcionando con detalle extenso (Wi-Fi, audio HDMI, KDE, RADV/Vulkan, Steam/Proton/DXVK) | **ACEPTADO-MANTENEDOR** — el mantenedor `ArabPixel` agradeció el reporte sin refutarlo; no es verificación independiente nuestra ni de un tercero distinto |
| S-12 | Comentario en S-11 | Comentario | — | 2026-09-26 | `EnderPanel`: "tengo un CUH-7216B y no funciona", sin detalle de síntoma ni diagnóstico | **REPORTADO-TERCEROS sin seguimiento** — no se registró causa ni se reabrió como issue propio |
| S-13 | [ps4-linux-loader#11](https://github.com/ps4-linux/ps4-linux-loader/issues/11) | Issue | Cerrado (resuelto) | abierto 2026-09-23, cerrado por el autor 2026-09-26 | PS4 Slim/Belize, FW 13.52, GoldHEN v2.4 + Loader v25: LED blanca fija ("no kexec handoff"), HDMI sin señal; otro usuario sugirió payload de 1024 MB, enviarlo por red y arrancar desde el pendrive ("instalar desde el disco de la PS4 no funciona"); el autor confirmó que funcionó "al arrancar desde USB" | **REPORTADO-TERCEROS, con solución empírica confirmada por el propio reportante** — no es una causa raíz confirmada por el mantenedor, es una solución que funcionó una vez |
| S-14 | [ps4-linux-loader#9](https://github.com/ps4-linux/ps4-linux-loader/pull/9) | Pull Request (mergeado) | Cerrado/mergeado | 2026-07-18 | `firmware: fix EDID buffer overflow and truncated extension blocks` — commit `3b5e038e88f7a88d39408d960a0a798b1bac56a7` sobre base `142f55ff42eaa5a494c14d096ce35170c6edbbbc` | **ALTA — cambio de código verificado línea por línea, confirmado presente en el commit auditado (S-02)** |
| S-15 | [ps4-linux-loader#8](https://github.com/ps4-linux/ps4-linux-loader/issues/8) | Issue (cerrado) | Cerrado | 2026-05-05 | "Dump current edid to be reused in linux" — contexto de por qué existe la extracción de EDID en runtime | Mención, cuerpo no leído en detalle en esta sesión |
| S-16 | [ps4-linux-loader#1](https://github.com/ps4-linux/ps4-linux-loader/issues/1) | Issue (cerrado) | Cerrado | 2026-02-14 | "master: Add fixed offset for gpu_devid_is_9924 for 12.50 FW" — evidencia histórica de que la detección Pro/no-Pro requirió offsets específicos por firmware | Título solamente, cuerpo no auditado |
| — | Issues de PS4-Linux (S-01) | — | — | — | Se consultó la API; **no hay issues registrados** en ese repositorio a la fecha de consulta | N/A |

## 4. Discrepancias encontradas (requieren resolución antes de citar como hecho firme)

### D-A — "Automatic boot files placement" del changelog vs. código y artefactos inspeccionados
**RESUELTA PARCIALMENTE (2026-10-15).** La frase del README entra en `8a1468f` (2025-09-26, solo README) y su matiz "from the external fat32 partition" en `7280a37` (2026-04-02, solo README); ningún commit de las 71 del historial añade código que escriba archivos (ver `UPSTREAM_CODE_MAP.md` §1.8 y D-017). Tampoco hay copia en el `init`/`functions.sh` del initramfs v0.9.1 ni literales de escritura en el ELF distribuido. La hipótesis anterior (a) "existió en v23 y se eliminó" queda **refutada** para las instantáneas revisadas; quedan las explicaciones (b) rama/repositorio distinto del que se publican los *releases* y (c) imprecisión del changelog, **sin confirmar**. La afirmación hermana "RTC time passed to initramfs (`time=CURRENTTIME`)" tampoco tiene código ni procesamiento en el initramfs. **No usar estas funciones en ningún procedimiento.**

### D-B — Numeración de versión del kernel: "7.1.7"/"7.0.8" (S-01) vs. "5.4.247" (S-11)
**RESUELTA (2026-10-15, D-009).** La cabecera de arranque de cada `bzImage` trae la cadena de versión: `7.0.8-Strawberry-FullLTO-Baikal-+ … 2026-09-08` y `7.1.7-Strawberry-General-FullLTO+ … 2026-08-25`. Son versiones reales de Linux. El "Kernel 5.4.247" del issue #10 es otra compilación y no respalda los kernels del catálogo. Pendiente (no bloqueante): identificar el repositorio fuente del kernel "Strawberry".

### D-C — Existencia de un jailbreak público para 13.52 (consultado 2026-10-15)

Fuentes **de comunidad y blogs, no oficiales, no verificadas contra el código**: PSXHax (portada y búsqueda interna, sin cobertura de 13.52; GoldHEN publicado allí llega a 11.00), GitHub `GoldHEN/GoldHEN` (solo se ven binarios v2.3 para 5.05/6.72/9.00), y varios blogs/tutoriales/vídeos (p. ej. tgames.fr, se7ensins, onejailbreak, gaminglikeaboss) que afirman un exploit de navegador (WebKit) para 13.02/13.04/13.50/13.52 desde ~mediados de septiembre de 2026.

- **Discrepancia:** las fuentes no coinciden en si GoldHEN funciona completo en 13.52 o solo HEN; un reporte menciona GoldHEN 2.4b18.11 y otros advierten que no se asuma.
- **Estabilidad reportada:** resultados inconsistentes; una consola no completó, una Pro tuvo éxito tras reintentar.
- **Riesgos reportados:** ban de consola/cuenta si se conecta a PSN; con firmware 14.00 el exploit no funciona (por eso no actualizar).
- **Estado:** SIN VERIFICAR. No promueve ninguna fila de `COMPATIBILITY_MATRIX.md`. Pendiente: leer la fuente primaria del exploit y del GoldHEN usado, y los avisos de seguridad, antes de cualquier ejecución (ver `SAFETY_AND_TOOLING.md`).

**Actualización D-C (2026-10-15, metadatos vía `gh api`, solo lectura; no se descargó ni ejecutó nada):**
- Host público del exploit: `raw13g/raw13g.github.io` (creado 2026-09-19, último push 2026-09-25, 212 estrellas). Commits: "Deploy RAW GAME (PS4 13.02/13.04/13.50/13.52)" (09-19), "added goldhen for 13.52" (09-20), "added goldhen 13.02 - 13.52" (09-21), "aio fix thanks to MODDED_WARFARE and Al-Azif" (09-22), "Improve stability" y "Add MIT license" (09-25). Contiene `jb.js`, `core.js`, `mem.js`, `ps4_offsets.js` y dos binarios idénticos en tamaño: `goldhen.bin` y `payload2.bin` (293 120 bytes).
- **GoldHEN oficial (`GoldHEN/GoldHEN`)**: su último release es v2.4b18 (2024-10-28) y **no** lista 13.52. El "GoldHEN 2.4b18.11" citado por blogs **no figura en los releases oficiales**: el binario que se serviría es el `goldhen.bin` de raw13g, de procedencia no verificada y sin código fuente asociado en ese repo.
- Forks/mirrors (`boomerf90777`, `WhiteShadow8500`, `L00naria`) y `OptiTronOffical/bd-j-usr-1352` ("probs fake" según su propia descripción): **no usar**.
- Conclusión provisoria: el exploit parece real y público, pero el payload que habilita GoldHEN en 13.52 es un binario sin auditar. Cualquier ejecución requiere antes revisar `jb.js`/`ps4_offsets.js`, comparar hashes de los `.bin` con el binario oficial más cercano y decidir el aislamiento de PSN.

### D-D — Descargas descritas en el README de la distribución vs. assets del release (consultado 2026-10-15 vía API)
El README de `X-F1REBALL-X/PS4-Linux` (`66e21cb`) describe `psxitarch.tar.xz` (2,8 GB), `kernel.zip`, `payloads.zip` y `tools.zip`. El único release (`v1.0`, 2026-09-28) publica en cambio `psxitarch-usb.img.xz.part1/.part2` (2 × 1 088 315 226 B), `bzImage-*`, `initramfs.cpio.gz`, `linux-*.elf`, `SHA256SUMS`, `build-img.sh` y `write-img.ps1`; el commit "Release v1.0.0" es del 2026-10-01, posterior al release. Las cifras del README no corresponden a lo que se descarga. El proyecto trabaja con los assets sueltos del release (hashes en `manifests/distro-66e21cb.json`); `psxitarch.tar.xz` no se ha visto.

### D-D2 — El tag `v1.0` de la distribución se movió después de publicar el release
La API (consulta 2026-10-15) da para `refs/tags/v1.0` el commit `26a6451817c35d02021b838235ed0463fb09b241` (2026-09-29 00:23 +03), mientras el release se publicó el 2026-09-28 21:24 UTC. Entre ese commit y `66e21cb` (HEAD) cambian el README, las imágenes y `tools/write-img.ps1` (28 líneas añadidas); `boot/`, `payload/` y `tools/build-img.sh` son idénticos. El asset `write-img.ps1` del release coincide con la versión de HEAD (`893dc5ac…`). Consecuencia: un tag no es una referencia inmutable; este proyecto fija **commits y hashes**, no tags.

### D-E — Procedencia de los releases del loader
(1) El README del loader enlaza a `ArabPixel/ps4-linux-payloads` (releases y "How to Compile"); la API devuelve para ese nombre el repositorio `ps4-linux/ps4-linux-loader` (renombre/transferencia; creado 2025-12-19 con historial desde 2022). (2) El workflow `.github/workflows/build.yml` sube artefactos de Actions pero **no crea releases**; los zips de *Releases* (con `sha256` que publica GitHub, p. ej. v25.1 `7ee03018…da74`) no quedan ligados a un build verificable. (3) `lib/syscalls.py` descarga `syscalls.master` de GitHub y una página de `web.archive.org` en cada compilación y `lib/Makefile` exige `yasm`. Consecuencia: ningún binario del loader es reproducible con lo que tenemos (`USB_ONLY_DESIGN.md` §4).

### D-F — Exploit y video
El video de referencia (`https://www.youtube.com/watch?v=Juf2IOxOQcY`) no pudo leerse más allá de su título ("¡POR FIN! Jailbreak PS4 hasta 13.52 con GoldHEN | Tutorial Paso a Paso"): sin canal, fecha, descripción ni transcripción. No se atribuye ningún paso al video. Hay una disputa pública de crédito del exploit (acusaciones de que el núcleo JS copia a OOMfie) citada por blogs, **sin confirmar ni refutar**.

## 5. Fuentes mencionadas por upstream pero NO auditadas en esta sesión (dependencias de hecho, pendientes)

Cada una aparece citada en los créditos de S-01 o en comentarios de código de S-02. Ninguna se clonó ni se leyó en esta sesión — listarlas aquí es parte de la auditoría, no una afirmación sobre su contenido.

| Dependencia mencionada | Dónde se menciona | Rol declarado |
|---|---|---|
| `Al-Azif/ps4-skeleton` | Comentario en `linux/fw_detect.c` (S-02) | Origen (MIT) del método de detección de firmware vía SCE header |
| `ArabPixel/ps4-linux-payloads` | README de S-02, línea de instrucción de clonado | Upstream real del que S-02 parece ser mirror/fork funcional |
| Kernel "Strawberry" (rmuxnet) | Créditos README de S-01 | Fuente del kernel 7.1.7 (Aeolia/Belize) y su port a 7.0.8 (Baikal) — repositorio no identificado |
| Psxitarch / "better-initramfs" (PSXITA Team, Piotr Karbowski) | Créditos README de S-01 | Initramfs y scripts de instalación del rootfs |
| Rootfs "Arch Linux KDE v1.1.1" (Erkkola) | Créditos README de S-01 | Distribución base del escritorio |
| Paquetes Mesa/video parcheados (centi07, DionKill) | Créditos README de S-01 | Driver gráfico parcheado para PS4 |
| GoldHEN (SiSTR0) | Créditos README de S-01, README de `ps4-kexec-common` (S-02) | Jailbreak + servidor FTP + PayLoader — **prerequisito externo obligatorio, no auditado** |

## 6. Hashes calculados por nosotros (no publicados por upstream como manifiesto independiente)

Ver tabla completa en `docs/UPSTREAM_CODE_MAP.md` §2.3. Calculados sobre el clon local de S-01 el 2026-10-15; no se comparó contra un manifiesto de checksums publicado por el autor (el README de S-01 no publica hashes de los artefactos del repositorio, solo de la imagen `.img` que el propio `build-img.sh` genera en el momento).

## 7. Limitaciones generales de este registro

- Todo se consultó vía `git clone --depth 1` y la API de GitHub (`gh api`); no se usó ningún navegador ni se guardó HTML de páginas de GitHub.
- El historial completo de commits solo se revisó para `ps4-linux/ps4-linux-loader` (2026-10-15); del resto, solo el HEAD.
- No se consultó ningún foro, Discord, Reddit o wiki de la comunidad PS4-Linux fuera de GitHub.
- No se verificó la identidad real de ningún usuario de GitHub citado (mantenedores o reportantes); se los identifica por su nombre de usuario tal como aparece en la API.
