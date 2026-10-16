# Plan de pruebas

Casos concretos, derivados de `docs/BOOT_FLOW.md`, `docs/TROUBLESHOOTING.md` y `docs/GPU_AND_LLM_RESEARCH.md`. Cada caso usa la plantilla de `docs/LAB_LOG_TEMPLATE.md` para su registro real; este documento solo define **qué** probar, **en qué orden**, con qué precondición y qué evidencia guardar — no sustituye al registro de ejecución.

Ningún caso de este plan sobre la consola se ha ejecutado todavía. Ninguno puede marcarse `VERIFIED` sin una entrada de log real con hashes y resultado observado. (Las herramientas de PC sí tienen tests automáticos; ver "Resultados de ejecución host-side" al final.)

## TP-01 — Identificación de hardware (precondición de todo lo demás)

- **Precondición:** consola disponible, apagada, se puede ver la etiqueta trasera sin desarmar nada.
- **Pasos:** fotografiar/anotar el modelo CUH exacto y su revisión si es visible; encender en modo normal y registrar el firmware en Ajustes → Sistema → Información del sistema; **no actualizar**.
- **Resultado esperado:** modelo CUH y firmware exactos registrados en `docs/LAB_LOG_TEMPLATE.md`.
- **Evidencia a guardar:** foto de la etiqueta (sin datos de cuenta visibles), captura de la versión de firmware.
- **Condición de aborto:** si la consola pide actualizar al encenderla, no aceptar — desconectar red si es necesario y registrar el bloqueo.

## TP-02 — Verificación de artefactos descargados (en la PC, sin consola)

- **Precondición:** TP-01 completo (para saber qué kernel/southbridge buscar).
- **Pasos:** descargar únicamente desde `Releases` de cada repositorio (ver `docs/EVIDENCE_SOURCES.md`); calcular SHA-256 de cada archivo y compararlo contra los valores de esta auditoría (`docs/UPSTREAM_CODE_MAP.md` §2.3) o contra el manifiesto que el propio `build-img.sh` imprime.
- **Resultado esperado:** todos los hashes coinciden; tamaños de archivo coinciden con los declarados en el README (`psxitarch.tar.xz` 2.8 GB, `kernel.zip` 36.4 MB, `payloads.zip` 185 KB, `tools.zip` 5 KB).
- **Condición de aborto:** cualquier hash o tamaño que no coincida — no continuar con ese archivo, volver a descargarlo desde la fuente oficial.

## TP-03 — Construcción de imagen USB (en la PC, sin consola)

- **Precondición:** TP-02 completo; entorno Linux o WSL disponible; USB de prueba de al menos 32 GB (recomendado) dedicado, sin datos importantes.
- **Pasos:** ejecutar `tools/build-img.sh` con los argumentos documentados en `docs/BOOT_FLOW.md` Fase 1; registrar el hash SHA-256 que el script imprime al final.
- **Resultado esperado:** archivo `.img` de ~12 GB generado, hash registrado.
- **Evidencia a guardar:** salida completa del script, hash final.
- **Condición de aborto:** cualquier error de `sfdisk`/`mkfs`/`tar` antes de llegar a `BUILD_IMG_OK` — no continuar a TP-04 con una imagen a medio construir.

## TP-04 — Escritura del USB (en la PC, Windows, sin consola)

- **Precondición:** TP-03 completo; disco USB físico identificado y confirmado como no-booteable/no-sistema vía `Get-Disk`.
- **Pasos:** ejecutar `tools/write-img.ps1` como Administrador, confirmando el número de disco manualmente (sin `-Force` en la primera vez).
- **Resultado esperado:** `WRITE_DONE_OK` en la salida; tamaño escrito igual al tamaño de la imagen.
- **Evidencia a guardar:** salida completa del script.
- **Condición de aborto:** el script mismo aborta si el disco no es USB o es de arranque/sistema — no hay override seguro para eso; si aborta, verificar el número de disco con `Get-Disk` de nuevo antes de reintentar.

## TP-05 — Cadena USB-only lista y verificada en la PC (puerta previa al primer intento)

- **Precondición:** TP-01 a TP-04 completos y southbridge conocido (si no, este caso queda `BLOCKED`). La ubicación del kernel **ya está decidida** (D-008: dentro de la FAT del USB; no se escribe en el interno).
- **Pasos:** extraer la FAT de la imagen final y ejecutar `python3 tools/verify_boot_chain.py <carpeta> --catalogo manifests/arranque-catalogo.json --southbridge <confirmado> --requerir estructura,integridad,formato,compatibilidad`; confirmar que no hay `bzImage.*` sobrantes ni mezcla de releases; registrar la salida.
- **Resultado esperado:** niveles OK; el nivel `arranque` queda `NO_EVALUADO` hasta que exista un registro de laboratorio.
- **Evidencia a guardar:** salida completa, hashes del catálogo, versión de la herramienta (commit).
- **Condición de aborto:** cualquier nivel en `FALLO`, o southbridge sin confirmar.

## TP-06 — Primer intento de arranque (en la consola, con USB)

- **Precondición:** TP-05 completo (cadena USB-only verificada en la PC); listado FTP de solo lectura de `/data/linux/boot/` y `/user/system/boot/` sin archivos ajenos (P5 de `USB_ONLY_DESIGN.md`); jailbreak/GoldHEN funcionando en la consola (fuera de alcance de este laboratorio, pero precondición dura).
- **Pasos:** conectar el USB antes de encender; jailbreak; enviar `payloads/linux-1024mb.elf` (tamaño recomendado para un primer intento, ver `docs/TROUBLESHOOTING.md` caso 2) vía el método elegido (PayLoader/`nc` o carpeta de GoldHEN); cronometrar el cambio de LED y el tiempo hasta video.
- **Resultado esperado:** LED pasa a azul/violeta en ~15 s; pantalla negra normal de hasta 2 minutos; login de KDE Plasma.
- **Evidencia a guardar:** tiempos exactos observados, fotos/video de la LED si es posible, cualquier mensaje visible.
- **Condición de aborto:** si la LED no cambia en 20+ segundos, seguir el árbol del caso 2 de `docs/TROUBLESHOOTING.md` — no reintentar la misma combinación sin cambiar una variable.
- **Variable única a cambiar en reintentos:** en este orden — (1) método de transferencia del payload, (2) verificar integridad del `.elf`, (3) el kernel del USB (solo si hay una segunda candidata documentada para el mismo southbridge; **nunca** moviendo el kernel al almacenamiento interno).

## TP-07 — Validación de retorno al sistema original

- **Precondición:** TP-06 alcanzó al menos la Fase 4 de `BOOT_FLOW.md` (handoff ocurrió), independientemente de si llegó a escritorio.
- **Pasos:** reiniciar la consola y confirmar que arranca OrbisOS normalmente, sin errores, sin pedir restauración.
- **Resultado esperado:** la consola vuelve a su sistema original sin intervención adicional.
- **Condición de aborto/escalación:** si la consola no vuelve a arrancar normalmente, este deja de ser un problema de este laboratorio — es un Nivel 5 de `docs/RECOVERY_STRATEGY.md` (fuera de alcance de los scripts automáticos); detener todo intento adicional y documentar el estado exacto antes de buscar un procedimiento específico verificado.

## TP-08 — Inventario de hardware/drivers desde dentro de Linux

- **Precondición:** TP-06 exitoso (login alcanzado).
- **Pasos:** ejecutar la secuencia de la sección 2 de `docs/GPU_AND_LLM_RESEARCH.md` (`lspci -k`, `dmesg`, `glxinfo -B`, `vulkaninfo --summary`, `free -h`, lectura de VRAM del driver, temperatura si hay sensor).
- **Resultado esperado:** inventario completo registrado, incluyendo la confirmación de `GetSouthbridgeName()` si se pudo capturar el log temprano del payload (UART) — este es el dato que permitiría avanzar las filas "Untested" de `docs/COMPATIBILITY_MATRIX.md`.
- **Evidencia a guardar:** salida completa de cada comando.

## TP-09 — Prueba gráfica mínima reproducible

- **Precondición:** TP-08 completo, con renderizado por hardware confirmado (no `llvmpipe`).
- **Pasos:** correr `glmark2` y/o `vkmark`/`vkcube` dos veces en arranques separados.
- **Resultado esperado:** FPS/puntaje registrado con baja varianza entre corridas (coherente con el reloj de GPU fijo documentado en `GPU_AND_LLM_RESEARCH.md` §1); cualquier varianza alta se investiga antes de reportar un número.
- **Condición de aborto:** renderer software detectado — detener y resolver el driver antes de seguir con benchmarks.

## TP-10 — Baseline de inferencia LLM en CPU

- **Precondición:** TP-08 completo.
- **Pasos:** compilar `llama.cpp` sin ningún backend GPU; correr un modelo pequeño cuantizado (GGUF, ~1-3B parámetros, 4 bits) con un prompt fijo y reproducible.
- **Resultado esperado:** tokens/s de generación y de prompt processing registrados, con uso de RAM y temperatura.
- **Esto es el piso de comparación obligatorio antes de TP-11.**

## TP-11 — Exploración de backend GPU para LLM (exploratorio, puede terminar en descarte documentado)

- **Precondición:** TP-10 completo; investigación bibliográfica adicional sobre backends de cómputo para GCN1/GCN4 (fuera del alcance de código auditado en esta sesión).
- **Pasos:** según lo que la investigación previa encuentre — no se prescribe un backend concreto todavía.
- **Resultado esperado:** o bien una medición comparable contra TP-10, o bien una entrada en `docs/DECISION_LOG.md` documentando por qué se descarta, con la evidencia que lo sostiene.

## Orden de dependencia resumido

```text
TP-01 -> TP-02 -> TP-03 -> TP-04 -> TP-05 (verificación USB-only) -> TP-06 -> TP-07
                                                            |
                                                            v
                                                   TP-08 -> TP-09
                                                            |
                                                            v
                                                   TP-10 -> TP-11
```


## Resultados de ejecución host-side

| Fecha | Suite | Resultado | Alcance/límite |
|---|---|---|---|
| 2026-10-15 | `python -m unittest discover -v` sobre el primer verificador de artefactos | **11/11 PASS** en sandbox local | Incluye hashes, tamaño, archivo ausente/vacío, manifiesto inválido y rutas inseguras. No prueba dispositivos físicos ni arranque PS4. El resultado del workflow CI de GitHub debe comprobarse por separado. |
| 2026-10-15 | `bash scripts/check.sh` (`compileall` + `python3 -m unittest discover`) tras endurecer `verify_artifacts` e incorporar `ps4lab` e `inspect_image` | **PASS** (suite completa, ver nota) | En esta máquina el intérprete es `python3` (no existe `python`). Se corrigieron 5 fallos reales de `verify_artifacts` (`schema_version: true` aceptado, byte NUL y nombre largo con excepción no controlada, rutas duplicadas aceptadas, JSON muy anidado con `RecursionError`), cada uno con test de regresión. |
| 2026-10-15 | `tests/test_inspect_image.py` (24 casos con fixtures sintéticos MBR/GPT: válidas, vacía, truncada, CRC malo, solapadas, GPT sin MBR protector, dispositivo/FIFO/symlink/directorio) | **24/24 PASS** | Prueba de mutación: se rompieron a propósito 4 comprobaciones (CRC de cabecera GPT, límite de imagen, solape, apertura `O_RDWR`) y **cada mutación hizo fallar al menos un test**. |
| 2026-10-15 | `python3 tools/inspect_image.py` sobre la imagen real `psxitarch-usb.img` (release v1.0, 8 871 489 536 bytes, SHA-256 `badd4873…0143` = el publicado) | **OBSERVADO** | MBR; p1 tipo 0x0c, LBA 2048, 512 MiB, firma FAT32; p2 tipo 0x83, LBA 1050624, ~7,76 GiB, firma ext2/3/4. El final de p2 coincide con el tamaño de la imagen. Sin advertencias. Ninguna escritura ni montaje. |
| 2026-10-15 | GitHub Actions `tests.yml` | **FAIL, causa externa** | El job nunca arranca (`runner_id=0`, 0 pasos): anotación de GitHub sobre pagos fallidos / límite de gasto. Detalle en `docs/CI_DIAGNOSIS.md`. No se deshabilitó el workflow. |
| 2026-10-15 | `bash scripts/check.sh` tras el barrido resolutivo (`compileall` + `unittest discover`), Python 3.12.3 local | **PASS** — 212 tests (`Ran 212 tests … OK`) + `tools/check_docs.py` sin problemas (`CHECK_OK`) | Nuevos: `verify_boot_chain` (59, 5 niveles), `payload_static` (16), `elf_audit` (10), `loader_model` + parche (21), `fat32_add_file` (12, contra `fsck.vfat`/7z reales), `build_usb_image` (20). Los tests que requieren `mkfs.vfat`/`sfdisk`/`mkfs.ext4` se omiten si faltan o si se ejecuta como root. Ninguno toca hardware ni dispositivos de bloque. |
| 2026-10-15 | `tools/verify_boot_chain.py` sobre copias de `bzImage-belize-7.1.7` + `initramfs.cpio.gz` del release | **OBSERVADO** | Estructura, integridad (catálogo), formato y compatibilidad (`--southbridge belize`) en OK; `arranque` `NO_EVALUADO`. Con `--southbridge baikal` el nivel de compatibilidad da `FALLO` (el catálogo declara belize). Lee la versión real del kernel (D-009). |
| 2026-10-15 | `tools/elf_audit.py linux-1024mb.elf --fuente fw_offsets.h@f70f43a --comparar` | **OBSERVADO** | 20/20 filas de `fw_table` iguales a la fuente; rutas literales: solo las 4 de lectura y las de `libc/libkernel/libSceSysUtil`; los 9 ELF difieren en 21-24 bytes (build-id y constante de VRAM). |
| 2026-10-15 | `tools/fat32_add_file.py` sobre una copia de la p1 real (512 MiB) | **OBSERVADO** | `fsck.vfat -n` limpio antes y después; `bzImage` agregado (20 415 488 B) leído con 7z da el mismo sha256; copia descartada. |
| 2026-10-15 | `tools/build_usb_image.py` con kernel+initramfs reales y un directorio de prueba como rootfs (120 MiB dispersos) | **OBSERVADO** | `inspect_image`: p1 FAT32 64 MiB, p2 ext4; `fsck.vfat -n` de p1 limpio; imagen descartada. No es una imagen utilizable (rootfs ficticio) ni selecciona kernel para esta consola. |
