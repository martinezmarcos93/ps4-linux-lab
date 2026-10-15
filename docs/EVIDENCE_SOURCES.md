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
| S-09 | ps4-linux-loader | `v23` | 2026-03-28 | Según README: añade fallback a `/user/system/boot/` y "Automatic boot files placement" — **ver discrepancia §4** |
| S-10 | ps4-linux-loader | `v22`, `v21.5`, `v21`, `v20` | 2026-03-23 a 2025-12-24 | Historial de soporte incremental de firmwares, no auditado en detalle |

## 3. Issues y pull requests (evidencia de comunidad — nivel de confianza explícito en cada uno)

| # | Fuente | Tipo | Estado | Fecha | Resumen | Nivel de confianza |
|---|---|---|---|---|---|---|
| S-11 | [ps4-linux-loader#10](https://github.com/ps4-linux/ps4-linux-loader/issues/10) | Issue | Abierto | reporte 2026-09-22, ack 2026-09-23 | CUH-2208B (Baikal) FW 13.52 funcionando con detalle extenso (Wi-Fi, audio HDMI, KDE, RADV/Vulkan, Steam/Proton/DXVK) | **ACEPTADO-MANTENEDOR** — el mantenedor `ArabPixel` agradeció el reporte sin refutarlo; no es verificación independiente nuestra ni de un tercero distinto |
| S-12 | Comentario en S-11 | Comentario | — | 2026-09-26 | `EnderPanel`: "tengo un CUH-7216B y no funciona", sin detalle de síntoma ni diagnóstico | **REPORTADO-TERCEROS sin seguimiento** — no se registró causa ni se reabrió como issue propio |
| S-13 | [ps4-linux-loader#11](https://github.com/ps4-linux/ps4-linux-loader/issues/11) | Issue | Cerrado (resuelto) | 2026-09-23 a 2026-09-26 | PS4 Slim/Belize, FW 13.52, LED blanca fija ("no kexec handoff"); resuelto arrancando desde USB en vez del flujo que venía usando | **REPORTADO-TERCEROS, con solución empírica confirmada por el propio reportante** — no es una causa raíz confirmada por el mantenedor, es una solución que funcionó una vez |
| S-14 | [ps4-linux-loader#9](https://github.com/ps4-linux/ps4-linux-loader/pull/9) | Pull Request (mergeado) | Cerrado/mergeado | 2026-07-18 | `firmware: fix EDID buffer overflow and truncated extension blocks` — commit `3b5e038e88f7a88d39408d960a0a798b1bac56a7` sobre base `142f55ff42eaa5a494c14d096ce35170c6edbbbc` | **ALTA — cambio de código verificado línea por línea, confirmado presente en el commit auditado (S-02)** |
| S-15 | [ps4-linux-loader#8](https://github.com/ps4-linux/ps4-linux-loader/issues/8) | Issue (cerrado) | Cerrado | 2026-05-05 | "Dump current edid to be reused in linux" — contexto de por qué existe la extracción de EDID en runtime | Mención, cuerpo no leído en detalle en esta sesión |
| S-16 | [ps4-linux-loader#1](https://github.com/ps4-linux/ps4-linux-loader/issues/1) | Issue (cerrado) | Cerrado | 2026-02-14 | "master: Add fixed offset for gpu_devid_is_9924 for 12.50 FW" — evidencia histórica de que la detección Pro/no-Pro requirió offsets específicos por firmware | Título solamente, cuerpo no auditado |
| — | Issues de PS4-Linux (S-01) | — | — | — | Se consultó la API; **no hay issues registrados** en ese repositorio a la fecha de consulta | N/A |

## 4. Discrepancias encontradas (requieren resolución antes de citar como hecho firme)

### D-A — "Automatic boot files placement" del changelog (S-09, v23) vs. código auditado (S-02)

El README de `ps4-linux-loader` describe, en su sección de changelog para el release `v23`, una función que copiaría automáticamente el kernel e initramfs desde la partición FAT32 del USB al almacenamiento interno (`/data/linux/boot/`) en el primer arranque. **No se encontró ningún código, en el commit `f70f43a6` auditado, que escriba en esas rutas** (búsqueda explícita documentada en `docs/UPSTREAM_CODE_MAP.md` §1.8). Posibles explicaciones, ninguna confirmada: (a) la función existió en v23 y fue removida en una revisión posterior (el propio `v24b` describe una "unified AIO payload architecture" que pudo haber simplificado esto); (b) la función pertenece a una rama del upstream real (`ArabPixel/ps4-linux-payloads`) no incluida en este mirror; (c) imprecisión del changelog. **No usar esta función como supuesta en ningún procedimiento hasta confirmarla directamente en el código de la versión que se vaya a usar.**

### D-B — Numeración de versión del kernel: "7.1.7"/"7.0.8" (S-01) vs. "5.4.247" (S-11)

Ver detalle completo en `docs/UPSTREAM_CODE_MAP.md` §2.7 y `docs/COMPATIBILITY_MATRIX.md` §1 (nota al pie de la fila CUH-2208B). Resumen: el archivo de configuración del kernel en la distribución se autodenomina "7.1.7" (fork "Strawberry" de rmuxnet), mientras un reporte de comunidad habla de "Kernel 5.4.247". **Tratar como HIPÓTESIS no resuelta** que "7.1.7" sea una numeración propia del fork, no una versión real de Linux mainline — no confirmado porque no se auditó el repositorio fuente del kernel "Strawberry" (no identificado con una URL concreta en esta sesión).

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
- No se revisó el historial completo de commits de ningún repositorio, solo el HEAD de cada rama principal.
- No se consultó ningún foro, Discord, Reddit o wiki de la comunidad PS4-Linux fuera de GitHub.
- No se verificó la identidad real de ningún usuario de GitHub citado (mantenedores o reportantes); se los identifica por su nombre de usuario tal como aparece en la API.
