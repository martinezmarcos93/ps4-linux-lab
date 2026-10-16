# Matriz de compatibilidad

Ver [`docs/UPSTREAM_CODE_MAP.md`](UPSTREAM_CODE_MAP.md) para el detalle de cómo se obtuvo cada hallazgo de código, y [`docs/EVIDENCE_SOURCES.md`](EVIDENCE_SOURCES.md) para las fuentes completas con URL y fecha.

**Niveles de evidencia usados en la columna "Evidencia":**

- **CÓDIGO** — confirmado leyendo el código fuente upstream (archivo/línea citados).
- **REPORTADO-TERCEROS** — un usuario externo lo reporta (issue/comentario), sin confirmación independiente nuestra ni, necesariamente, del mantenedor.
- **ACEPTADO-MANTENEDOR** — un reporte de terceros al que el mantenedor respondió con agradecimiento o sin refutar (en el issue #10: "Thanks for confirming with a detailed report"). Sigue siendo un reporte de terceros: no equivale a reproducción ni a prueba propia, y en el roadmap se trata como `TERCEROS`.
- **README-UPSTREAM** — declarado en la documentación de la distribución o del loader, sin log, foto ni hash adjuntos. Las filas CUH-2116A y CUH-7116B de §1 son de este nivel (el repositorio es del 2026-09-28 con 7 commits): es la **afirmación del empaquetador**, más débil que un reporte con detalle.
- **REPRODUCIDO-LABORATORIO** — probado por nosotros en este laboratorio, con registro en `docs/LAB_LOG_TEMPLATE.md`. **No hay ninguna entrada en este nivel todavía.**
- **DESCONOCIDO** — sin evidencia encontrada en esta auditoría.

No extrapolar una fila a modelos/revisiones vecinos. "Slim CUH-2xxx" y "Pro CUH-7xxx" abarcan varias revisiones de placa con southbridge distinto (Belize o Baikal) que **no se puede determinar por el número de modelo solo** — ver `UPSTREAM_CODE_MAP.md` §1.6 sobre la detección en runtime vía `sysctlbyname`.

## 1. Combinaciones con evidencia directa (reporte detallado, no solo mención)

| Modelo CUH | Familia | Southbridge | Firmware | Jailbreak | Kernel/loader | VRAM probada | Resultado | Evidencia | Fuente | Fecha |
|---|---|---|---|---|---|---|---|---|---|---|
| CUH-2116A | Slim | Baikal | 13.52 | GoldHEN | `bzImage-baikal-7.0.8` + loader v25/v25.1 | 1024 MB | Arranca a escritorio KDE | README-UPSTREAM | README de `X-F1REBALL-X/PS4-Linux`, tabla de compatibilidad | consultado 2026-10-15 |
| CUH-7116B | Pro | Belize | 13.52 | GoldHEN | `bzImage-belize-7.1.7` + loader v25/v25.1 | 1024 MB | Arranca a escritorio KDE | README-UPSTREAM | idem | consultado 2026-10-15 |
| CUH-2208B | Slim | Baikal | 13.52 | GoldHEN beta + PayLoader | Loader v25, "Kernel 5.4.247 Baikal build" (ver nota de versión abajo) | 3072 MB | Escritorio KDE + RADV/Vulkan 1.2.145 + Proton 10/DXVK funcionando; Portal 2 60 FPS | ACEPTADO-MANTENEDOR | Issue [#10](https://github.com/ps4-linux/ps4-linux-loader/issues/10), reconocido por el mantenedor `ArabPixel` sin refutar | reporte 2026-09-22, confirmado 2026-09-23 |

**Nota sobre la versión de kernel en la fila CUH-2208B (resuelta por D-009):** el reporte dice "Kernel 5.4.247 Baikal build". Los kernels del catálogo de este proyecto traen en su cabecera de arranque la cadena `7.0.8-Strawberry-FullLTO-Baikal-+` y `7.1.7-Strawberry-General-FullLTO+`: son Linux 7.0.8 y 7.1.7 reales, **no** una numeración propia. Por tanto el issue #10 es una compilación distinta (5.4.x) y **no respalda** los kernels 7.x del catálogo; solo refuerza la combinación hardware/firmware/southbridge.

## 1b. Consola del laboratorio (observada, no probada)

| Modelo CUH | Familia | Southbridge | Firmware | Capacidad | Estado | Evidencia | Registro |
|---|---|---|---|---|---|---|---|
| **CUH-2115B** | Slim | **DESCONOCIDO** | 13.52 | 861,4 GB (clase 1 TB observada; disco posiblemente reemplazado) | Sin arranque probado | CUH comunicado por Marcos tras leer la etiqueta; firmware y capacidad observados; southbridge desconocido | `docs/lab-logs/LAB-000-identificacion-consola.md` |

Esta fila **no** es `REPRODUCIDO-LABORATORIO`: no se ejecutó ningún payload ni arranque. El CUH identifica el modelo, pero no confirma el southbridge ni valida un kernel.

**Nota:** se recibieron listas de CUH candidatos (p. ej. 2014/2114/2214 con sufijo A/B) generadas por terceros a partir de una foto. Se descartan: el CUH no se deduce de una foto frontal, los códigos regionales citados se contradicen entre sí y no hay fuente verificable. Hasta tener el dato real, no extrapolar ninguna fila de §1 a esta consola (regla D-002).

## 2. Reportes negativos o sin confirmar (igual de importantes que los positivos)

| Modelo CUH | Familia | Southbridge | Firmware | Resultado reportado | Evidencia | Fuente |
|---|---|---|---|---|---|---|
| CUH-7216B | Pro | Desconocido (no confirmado por el reportante) | No especificado | "doesn't work" (sin detalle de síntoma) | REPORTADO-TERCEROS | Comentario de `EnderPanel` en issue [#10](https://github.com/ps4-linux/ps4-linux-loader/issues/10), 2026-09-26 |
| PS4 Slim (no especifica CUH) | Slim | Belize (según el reportante) | 13.52 | GoldHEN v2.4 + Loader v25; payload (256/128 MB) se lanza, LED blanca fija, sin handoff a kexec, HDMI "sin señal". Otro usuario sugirió payload de 1024 MB, envío por red y arrancar desde el pendrive; el reportante cerró el issue el 2026-09-26 diciendo que ya funciona "al arrancar desde USB". Causa raíz **no diagnosticada** | REPORTADO-TERCEROS (sin diagnóstico; la respuesta del mantenedor solo pidió revisar el kernel) | Issue [#11](https://github.com/ps4-linux/ps4-linux-loader/issues/11), abierto 2026-09-23, cerrado 2026-09-26 por el autor |

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

## 7. Identificación de la consola y tabla de decisión kernel/loader (no selecciona binario para esta consola)

**El firmware 13.52 es un dato del software; no identifica el hardware.** Para esta consola: firmware 13.52 *observado*, modelo **CUH-2115B confirmado**, familia Slim confirmada por el modelo y southbridge *desconocido* (`LAB-000`). **No se elige kernel hasta resolver la compatibilidad con evidencia suficiente.**

### 7.1 Datos que se pueden obtener sin ejecutar un payload ni tocar el almacenamiento interno

| Dato | Fuente | Qué permite | Qué NO garantiza | Estado |
|---|---|---|---|---|
| Modelo CUH con sufijo (CUH-2xxxA/B…) | Etiqueta trasera/inferior, caja, factura | Acotar la familia de placas y buscar reportes del mismo modelo | El southbridge: Slim y Pro tienen revisiones con Belize o Baikal (README de la distribución: "el número de modelo por sí solo no basta") | **Confirmado: CUH-2115B** |
| Región/sufijo de la etiqueta | Etiqueta | Distinguir variantes del mismo CUH | El southbridge | Falta |
| Número de serie | Etiqueta | Identificar la unidad | Ninguna correspondencia con southbridge publicada y verificada | No registrado |
| Firmware | Ajustes → Sistema → Información del sistema | Elegir entrada de offsets del loader (13.52 tiene fila propia) | El hardware | Observado: 13.52 |
| Nombre, MAC LAN/Wi-Fi, IP | Información del sistema, `nmap`/`avahi` (LAB-000) | Inventario de red | Modelo o southbridge | Observado |
| Apariencia (Slim: una sola altura, bordes redondeados) | Foto | Familia | Revisión o southbridge | Inferido |
| Capacidad del disco (861,4 GB observados) | Ajustes → Almacenamiento | Clase nominal de capacidad | Modelo: el disco pudo reemplazarse | Observado; no usar para inferir CUH |
| Southbridge (`hw.sce_subsys_subid`) | Solo ejecutando el payload (`GetSouthbridgeName()`) o GoldHEN ≥ 2.2.3 ("Southbridge info") | **Es el dato que decide el kernel** | – | **No obtenible sin ejecución autorizada** (D-010/D-014) |
| Revisión de placa por inspección interna | Abrir la consola | Posible lectura directa | – | No es una primera opción (sellos, riesgo); no se hace |

Las listas de CUH candidatos recibidas de terceros (§1b) siguen descartadas: el modelo ya fue leído directamente por el operador.

### 7.2 Qué kernel y loader corresponden a cada southbridge (según documentación; nada probado por nosotros)

| Southbridge confirmado | Kernel del catálogo (`manifests/arranque-catalogo.json`) | Loader / payload | Evidencia existente | ¿Se puede elegir hoy para esta consola? |
|---|---|---|---|---|
| Baikal | `bzImage-baikal-7.0.8` (Linux 7.0.8, sha256 `46c835f7…ba8`) | Loader v25.1 (`f70f43a`); payload `linux-1024mb.elf` de la distribución (sha256 `623c3b68…98f`, **procedencia no reproducida**) | CUH-2116A: README-UPSTREAM; CUH-2208B: TERCEROS con kernel 5.4.247 (otra compilación) | **No** (southbridge desconocido) |
| Belize | `bzImage-belize-7.1.7` (Linux 7.1.7, sha256 `07211389…480`) | idem | CUH-7116B: README-UPSTREAM; Slim Belize del issue #11: falla inicial sin diagnóstico; CUH-7216B (southbridge no indicado): falla sin diagnóstico | **No** |
| Aeolia (Fat CUH-10xx/11xx) | `bzImage-belize-7.1.7` según el README ("debería") | idem | Ninguna prueba | **No** |
| Belize2 (`SB_BELIZE2`, 0x4) | El README no declara cuál; **ningún kernel local declara soporte** | idem | Ninguna con SB confirmado. **Posible southbridge de la CUH-2115B** (wiki) | **No** |
| **Desconocido (esta consola)** | **Ninguno seleccionado** | – | – | **No: no se elige ni se ejecuta un payload solo para averiguarlo sin autorización de Marcos** |

Lectura segura: la tabla dice qué asocia la documentación, no que funcione. El verificador (`tools/verify_boot_chain.py --southbridge …`) devuelve `NO_EVALUADO` en compatibilidad si el southbridge es desconocido y `FALLO` si no coincide con el catálogo.

### 7.3 Siguiente paso concreto para reducir la incertidumbre
1. CUH-2115B registrado en `LAB-000`. Los reportes del mismo modelo pueden acotar, pero no confirmar el southbridge.
2. Solo con autorización explícita y las condiciones de `PLAN_INMEDIATO.md` Etapa 3 se obtiene el southbridge real del log del payload.

### 7.4 Evidencia para CUH-2115B, firmware 13.52 y cada kernel candidato (2026-10-16)

| Pregunta | Evidencia encontrada | Conclusión |
|---|---|---|
| ¿Hay reportes de CUH-2115B? | Issues/PR de `ps4-linux-loader`, `X-F1REBALL-X/PS4-Linux` y `feeRnt/ps4-linux-12xx` (API de GitHub, 2026-10-16): **0 resultados** para "2115". **Única mención:** la release `v5.4.247__baikal` (2025-08-29) de `feeRnt/ps4-linux-12xx` dice "CUH-21xx (CUH-2115B): Tested functional" con un kernel **Baikal 5.4.247** | **TERCEROS, débil:** declaración del mantenedor sin logs, **firmware no indicado** (anterior al exploit 13.52). No sirve para 13.52 ni para los kernels 7.x locales. Contradice además su propia afirmación para CUH-7116B frente al README de la distribución (`KERNEL_SELECTION.md` #9) |
| ¿Modelos "vecinos"? | CUH-2116A (Baikal, README de la distribución), CUH-2208B (Baikal, issue #10), Slim Belize sin CUH (issue #11) | **No sirven para esta consola** (D-002): el sufijo y el número de revisión pueden cambiar de placa; un mismo rango tiene Belize y Baikal |
| ¿Southbridge de CUH-2115B? | **psdevwiki** (*Hardware Info*, copia Wayback 2025-12-18): CUH-2115B figura con **Baikal B1 (30201)** y con **Belize2 A0 (40100)**; CUH-2115A con Belize2 A0. *Southbridge* (Wayback 2026-03-03): chasis 2100 = Belize 2 (placas SAE-001/003) o Baikal (SAE-002/004). Lectura directa solo con `hw.sce_subsys_subid` (ejecutando código) o con el código de placa (abriendo la consola) | **DESCONOCIDO, pero ahora acotado a dos valores:** Baikal B1 o Belize2 A0 (HECHO según la wiki, colaborativa). El modelo no lo decide |
| ¿Firmware 13.52 soportado? | Fila 13.52 en `fw_table` (verificado en el ELF y en el código); reportes de terceros de arranque en otros modelos | Soporte en código; **sin prueba en esta consola** |
| Kernel Baikal `bzImage-baikal-7.0.8` | Declarado por el README de la distribución para CUH-2116A | Candidato **solo si** el southbridge fuera Baikal; sin evidencia para esta consola |
| Kernel Belize `bzImage-belize-7.1.7` | Declarado para CUH-7116B (Pro); falla reportada sin diagnóstico en un Slim Belize (issue #11) y en CUH-7216B | Candidato **solo si** el southbridge fuera Belize/Aeolia; sin evidencia para esta consola |

**Decisión:** no se selecciona ningún kernel. Procedimiento, criterios de aceptación/rechazo y estado por southbridge en [`KERNEL_SELECTION.md`](KERNEL_SELECTION.md). Elegir por analogía con CUH vecinos (p. ej. "2115B se parece a 2116A → Baikal") está descartado.

