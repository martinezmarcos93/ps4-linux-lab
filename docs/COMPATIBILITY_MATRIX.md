# Matriz de compatibilidad

Ver [`docs/UPSTREAM_CODE_MAP.md`](UPSTREAM_CODE_MAP.md) para el detalle de cómo se obtuvo cada hallazgo de código, y [`docs/EVIDENCE_SOURCES.md`](EVIDENCE_SOURCES.md) para las fuentes completas con URL y fecha.

**Niveles de evidencia usados en la columna "Evidencia":**

- **CÓDIGO** — confirmado leyendo el código fuente upstream (archivo/línea citados).
- **REPORTADO-TERCEROS** — un usuario externo lo reporta (issue/comentario), sin confirmación independiente nuestra ni, necesariamente, del mantenedor.
- **ACEPTADO-MANTENEDOR** — un reporte de terceros que el mantenedor del proyecto reconoció sin refutar (no equivale a prueba propia).
- **README-UPSTREAM** — declarado en documentación oficial del proyecto, sin reporte de prueba asociado que hayamos encontrado.
- **REPRODUCIDO-LABORATORIO** — probado por nosotros en este laboratorio, con registro en `docs/LAB_LOG_TEMPLATE.md`. **No hay ninguna entrada en este nivel todavía.**
- **DESCONOCIDO** — sin evidencia encontrada en esta auditoría.

No extrapolar una fila a modelos/revisiones vecinos. "Slim CUH-2xxx" y "Pro CUH-7xxx" abarcan varias revisiones de placa con southbridge distinto (Belize o Baikal) que **no se puede determinar por el número de modelo solo** — ver `UPSTREAM_CODE_MAP.md` §1.6 sobre la detección en runtime vía `sysctlbyname`.

## 1. Combinaciones con evidencia directa (reporte detallado, no solo mención)

| Modelo CUH | Familia | Southbridge | Firmware | Jailbreak | Kernel/loader | VRAM probada | Resultado | Evidencia | Fuente | Fecha |
|---|---|---|---|---|---|---|---|---|---|---|
| CUH-2116A | Slim | Baikal | 13.52 | GoldHEN | `bzImage-baikal-7.0.8` + loader v25/v25.1 | 1024 MB | Arranca a escritorio KDE | README-UPSTREAM | README de `X-F1REBALL-X/PS4-Linux`, tabla de compatibilidad | consultado 2026-10-15 |
| CUH-7116B | Pro | Belize | 13.52 | GoldHEN | `bzImage-belize-7.1.7` + loader v25/v25.1 | 1024 MB | Arranca a escritorio KDE | README-UPSTREAM | idem | consultado 2026-10-15 |
| CUH-2208B | Slim | Baikal | 13.52 | GoldHEN beta + PayLoader | Loader v25, "Kernel 5.4.247 Baikal build" (ver nota de versión abajo) | 3072 MB | Escritorio KDE + RADV/Vulkan 1.2.145 + Proton 10/DXVK funcionando; Portal 2 60 FPS | ACEPTADO-MANTENEDOR | Issue [#10](https://github.com/ps4-linux/ps4-linux-loader/issues/10), reconocido por el mantenedor `ArabPixel` sin refutar | reporte 2026-09-22, confirmado 2026-09-23 |

**Nota sobre la versión de kernel en la fila CUH-2208B:** el reportante dice "Kernel 5.4.247 Baikal build". El repositorio de distribución audita un `kernel-7.1.7-Strawberry-General.config`. Es **HIPÓTESIS, no confirmada**, que "7.1.7" sea la numeración propia del fork "Strawberry" y no la versión real de Linux mainline (que podría ser una base 5.4.x LTS). No se puede, con la evidencia actual, afirmar que el issue #10 y el `kernel-7.1.7` de la distribución sean la misma build exacta. Tratar esta fila como refuerzo de la combinación hardware/firmware/southbridge, no como confirmación de una versión de kernel específica.

## 1b. Consola del laboratorio (observada, no probada)

| Modelo CUH | Familia | Southbridge | Firmware | Capacidad | Estado | Evidencia | Registro |
|---|---|---|---|---|---|---|---|
| **DESCONOCIDO** (sin etiqueta en la base) | Slim (inferida de foto) | **DESCONOCIDO** | 13.52 | 861,4 GB (clase 1 TB) | Sin arranque probado | OBSERVADO-LABORATORIO (firmware, MAC, capacidad); INFERENCIA (familia) | `docs/lab-logs/LAB-000-identificacion-consola.md` |

Esta fila **no** es `REPRODUCIDO-LABORATORIO`: no se ejecutó ningún payload ni arranque. Solo documenta qué se sabe de la consola real.

**Nota:** se recibieron listas de CUH candidatos (p. ej. 2014/2114/2214 con sufijo A/B) generadas por terceros a partir de una foto. Se descartan: el CUH no se deduce de una foto frontal, los códigos regionales citados se contradicen entre sí y no hay fuente verificable. Hasta tener el dato real, no extrapolar ninguna fila de §1 a esta consola (regla D-002).

## 2. Reportes negativos o sin confirmar (igual de importantes que los positivos)

| Modelo CUH | Familia | Southbridge | Firmware | Resultado reportado | Evidencia | Fuente |
|---|---|---|---|---|---|---|
| CUH-7216B | Pro | Desconocido (no confirmado por el reportante) | No especificado | "doesn't work" (sin detalle de síntoma) | REPORTADO-TERCEROS | Comentario de `EnderPanel` en issue [#10](https://github.com/ps4-linux/ps4-linux-loader/issues/10), 2026-09-26 |
| PS4 Slim (no especifica CUH) | Slim | Belize | 13.52 | Payload se lanza, LED queda blanca fija, sin handoff a kexec (video "sin señal") — **resuelto** al reinstalar arrancando desde USB en vez de FTP/HDD | ACEPTADO-MANTENEDOR (causa) + REPORTADO-TERCEROS (solución empírica) | Issue [#11](https://github.com/ps4-linux/ps4-linux-loader/issues/11), cerrado 2026-09-23 a 2026-09-26 |

La fila de CUH-7216B es un recordatorio directo de la regla D-002: un modelo "parecido" (Pro, rango 7xxx) a uno confirmado (CUH-7116B) **no funcionó** según ese único reporte, sin que se aclarara la causa (southbridge distinto, FW distinto, error de procedimiento). No convertir esto en conclusión de incompatibilidad tampoco — es un solo reporte sin diagnóstico.

## 3. Firmwares con soporte en el código pero sin ningún reporte de prueba encontrado

Fuente: `linux/Makefile` y `linux/fw_offsets.h` de `ps4-linux/ps4-linux-loader` (CÓDIGO). Lista completa de 20 firmwares soportados por el build: 5.05, 6.72, 7.00/7.01/7.02, 7.50/7.51/7.55, 8.00/8.01/8.03, 8.50/8.52, 9.00, 9.03/9.04, 9.50/9.51/9.60, 10.00/10.01, 10.50/10.70/10.71, 11.00, 11.02, 11.50/11.52, 12.00/12.02, 12.50/12.52, 13.00, 13.02/13.04, 13.50, **13.52 (único con reportes de prueba encontrados)**.

**DESCONOCIDO:** no se encontró, en los issues consultados de `ps4-linux/ps4-linux-loader` (los 11 existentes a la fecha de consulta), ningún reporte de prueba para firmwares distintos de 13.52. Esto no significa que no funcionen — significa que no hay evidencia pública localizada en esta auditoría. Cualquier intento con otro firmware debe tratarse como **PENDIENTE DE VERIFICACIÓN**, no como "debería funcionar porque está en la tabla".

## 4. Southbridges y su tratamiento en el código (no es matriz de hardware, es matriz de código)

| Southbridge | ID interno | Kernel de la distribución | Tratamiento especial en `linux_boot.c` | Evidencia |
|---|---|---|---|---|
| Aeolia | `SB_AEOLIA` (0x1) | `bzImage-belize-7.1.7` (según README, "debería" usarse para Fat Aeolia) | Comparte rama de código "no Baikal" (apagado de IOMMU/HPET) con Belize/Belize2 | CÓDIGO (`sb_detect.h`) + README-UPSTREAM (sin prueba) |
| Belize | `SB_BELIZE` (0x2) | `bzImage-belize-7.1.7` | Rama "no Baikal" | CÓDIGO + evidencia directa en CUH-7116B |
| Belize2 | `SB_BELIZE2` (0x4) | No se declara explícitamente en el README cuál usar | Rama "no Baikal" (misma que Aeolia/Belize, sin offsets MMIO propios documentados) | CÓDIGO; **DESCONOCIDO** si alguna consola real reportó esta familia |
| Baikal | `SB_BAIKAL` (0x3) | `bzImage-baikal-7.0.8` | Rama propia con offsets MMIO específicos | CÓDIGO + evidencia directa en CUH-2116A y CUH-2208B |

**Fat CUH-10xx/CUH-11xx (Aeolia):** el propio README de la distribución los marca como "Untested" pese a recomendar el kernel Belize para ellos. No hay ningún reporte de prueba encontrado para Aeolia en ninguno de los dos repositorios ni en los issues consultados.

## 5. Qué evidencia permitiría avanzar cada fila "Untested"/"Desconocido"

- Un reporte con: modelo CUH exacto + número de serie o revisión de placa (si está disponible) + firmware exacto + **salida de `get_sb_id()`/`GetSouthbridgeName()`** (requiere ejecutar el payload y capturar su log, no es visible antes de intentarlo) + resultado observado (LED, video, periféricos).
- Para Aeolia en particular: confirmación de que el kernel `belize-7.1.7` realmente inicializa el southbridge Aeolia, dado que el código de `linux_boot.c` trata a Aeolia igual que Belize solo para el apagado de IOMMU/HPET — eso no garantiza que el resto del árbol de dispositivos (red, Bluetooth) funcione igual.
- Para firmwares distintos de 13.52: al menos un reporte con captura de log (UART o `dmesg` temprano) que confirme `kernel_main()` ejecutándose y el `kexec` completando el handoff.

## 6. Reglas de esta matriz (no negociables para este laboratorio)

1. Ninguna fila pasa a `VERIFIED` en el roadmap del proyecto sin una entrada propia en `docs/LAB_LOG_TEMPLATE.md` con hash de payload/kernel/initramfs y resultado observado — ver D-002 en `docs/DECISION_LOG.md`.
2. Un reporte de terceros, aunque esté "ACEPTADO-MANTENEDOR", se trata como `REPORTADO` en nuestro propio roadmap, no como `VERIFIED`.
3. Al obtener el hardware real, el primer dato a registrar es el southbridge vía el log del propio payload (`GetSouthbridgeName()`), no una suposición por el número de modelo.
