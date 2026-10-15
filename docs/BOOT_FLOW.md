# Secuencia de arranque: del loader al escritorio (o a la consola de rescate)

Basado en la lectura de código documentada en [`docs/UPSTREAM_CODE_MAP.md`](UPSTREAM_CODE_MAP.md). Cada paso indica su naturaleza (HECHO DOCUMENTADO / OBSERVACIÓN DE CÓDIGO / HIPÓTESIS), precondiciones, resultado esperado y cómo abortar sin dañar nada. Complementa, sin reemplazar, [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) (que describe las capas a nivel conceptual) y [`docs/RECOVERY_STRATEGY.md`](RECOVERY_STRATEGY.md) (niveles de diagnóstico).

## Fase 0 — Prerequisito fuera de este laboratorio: jailbreak

**Fuera de alcance de esta auditoría.** El payload que auditamos depende de un mecanismo externo de ejecución de código en el kernel de OrbisOS — en la práctica, **GoldHEN** (créditos README de `X-F1REBALL-X/PS4-Linux`, autor SiSTR0). No auditamos GoldHEN en esta sesión. Sin él, nada de lo que sigue es alcanzable.

- **Precondición:** consola jailbreakeable en su firmware actual, con GoldHEN instalado y su servidor FTP/PayLoader activo.
- **Resultado esperado:** la consola acepta payloads por FTP (puerto 2121) y/o por el puerto del PayLoader (9020, con 9090 como alternativa documentada en el README de la distribución).
- **Condición de aborto:** si el jailbreak mismo falla, esto es un problema de GoldHEN/exploit, no de este laboratorio — no continuar a la Fase 1.

## Fase 1 — Preparación de medios (en la PC, sin tocar la consola)

1. Verificar hashes de los artefactos descargados contra `docs/EVIDENCE_SOURCES.md`.
2. Construir la imagen USB con `tools/build-img.sh` (bash, dentro de WSL o Linux) — ver auditoría detallada en `UPSTREAM_CODE_MAP.md` §2.4. **OBSERVACIÓN DE CÓDIGO:** el script NO coloca ningún archivo `bzImage` en la partición de arranque del USB por defecto; solo `initramfs.cpio.gz`.
3. Escribir la imagen al USB físico con `tools/write-img.ps1` (PowerShell, Administrador) — `UPSTREAM_CODE_MAP.md` §2.5.
4. **Resultado esperado:** USB con partición 1 FAT32 (512 MB, con `initramfs.cpio.gz`) y partición 2 ext4 etiquetada `psxitarch` (rootfs Arch+KDE).
5. **Condición de aborto:** cualquier hash que no coincida, o cualquier disco objetivo que `write-img.ps1` identifique como no-USB o de arranque/sistema (el script aborta solo; no forzar con `-Force` para saltar eso, porque esos chequeos no son opcionales — ver `UPSTREAM_CODE_MAP.md` §2.5).

## Fase 2 — Ubicación del kernel: la decisión que choca con nuestro principio de "no tocar el disco interno"

Esta es la fase que requiere una **DECISIÓN** explícita antes de proceder (ver `docs/DECISION_LOG.md`, entrada pendiente D-008).

**HECHO DOCUMENTADO (README de la distribución):** el procedimiento oficial de `X-F1REBALL-X/PS4-Linux` instruye subir por FTP (puerto 2121) el `bzImage` correspondiente al southbridge detectado y `initramfs.cpio.gz` a `/data/linux/boot/` en el **almacenamiento interno** de la consola. El USB solo contiene el rootfs, nunca el kernel, para poder compartir un mismo USB entre consolas con southbridge distinto (el README lo explicita: "Do not put a file named `bzImage` on the USB").

**OBSERVACIÓN DE CÓDIGO (del loader):** `main-aio.c` (macro `L(...)`, líneas 375-389 de `linux/main-aio.c`) busca `bzImage`/`initramfs.cpio.gz`/`bootargs.txt`/`vram.txt` primero en `/mnt/usb0/` y `/mnt/usb1/`, y solo si no los encuentra ahí, cae a `/data/linux/boot/` y luego a `/user/system/boot/`. Es decir, **el código del payload sí permite un flujo 100% externo** (todo en el USB, incluyendo el `bzImage`), aunque el procedimiento recomendado por la distribución elegida no lo use así.

**DECISIÓN A TOMAR (no resuelta en este documento):**
- **Opción A (procedimiento oficial de la distribución):** copiar `bzImage` + `initramfs.cpio.gz` a `/data/linux/boot/` vía FTP. Esto modifica el almacenamiento interno, pero de forma acotada (una carpeta nueva con 2 archivos, reversible borrándola) — no toca el sistema de archivos de OrbisOS ni sus particiones.
- **Opción B (aprovechar la prioridad de USB del propio código):** poner también `bzImage` en la partición 1 del USB (el `tools/build-img.sh` soporta "kernels de repuesto" pero los renombra para que el loader los ignore — habría que adaptar el nombre o el script). Esto mantiene el almacenamiento interno sin tocar, a costa de que un mismo USB ya no sirva automáticamente para dos consolas con southbridge distinto sin intervención manual.
- Hasta que Marcos decida, **no ejecutar la Fase 2 con la Opción A** sin una autorización explícita separada de "no escribir en almacenamiento interno", porque contradice el Hito A del `PROJECT_CHARTER.md` ("ninguna modificación del disco interno"). La Opción B es la que mantiene el principio original, pero no está probada por ningún reporte de terceros — sería terreno no documentado por upstream.

## Fase 3 — Envío del payload

1. Con el USB conectado y la consola jailbreakeada, enviar el ELF del payload (p. ej. `linux-1024mb.elf`) al puerto del PayLoader de GoldHEN.
   - **HECHO DOCUMENTADO (README):** vía `nc -q 1 <IP-de-la-PS4> 9020 < payloads/linux-1024mb.elf`, con 9090 como puerto alternativo si 9020 no responde.
   - **REPORTADO-TERCEROS (issue #11):** existe también un flujo donde GoldHEN autolanza payloads colocados en `/data/GoldHEN/payloads/` en la propia consola — un comentario de la comunidad sugiere que enviar el payload "por internet" (presumiblemente el método `nc`/PayLoader) fue más confiable que vía FTP en su caso particular. Tratar como anécdota, no como regla.
2. **Resultado esperado según el README:** la luz de la consola pasa de blanca a azul/violeta en ~15 segundos — eso indica que el kernel arrancó y Linux está cargando. Pantalla negra por 1-2 minutos es normal antes de llegar al login de KDE.
3. **Señal de fallo en la etapa de exploit (no de video):** la luz permanece blanca por más de 20 segundos. Esto indica, según el propio código (`UPSTREAM_CODE_MAP.md` §1.3, pasos 7-8), que el handoff vía `kexec` no ocurrió — no es necesariamente un problema de kernel/southbridge incorrecto, puede ser el exploit mismo. Ver `docs/TROUBLESHOOTING.md`.
4. **Condición de aborto / reintento:** apagado completo (mantener el botón de power), esperar unos segundos, rehacer el jailbreak y reintentar. El README de la distribución y el issue #11 coinciden en que el 2.º o 3.er intento suele funcionar — **tratar esto como comportamiento empírico conocido, no como garantía**.

## Fase 4 — Handoff a Linux (automático, sin intervención del usuario)

Documentado en detalle de código en `UPSTREAM_CODE_MAP.md` §1.3, pasos 7-8. Resumen funcional, en orden:

1. El exploit en kernel ejecuta `kernel_main()`: parchea 3 bytes del kernel Orbis y salta al blob `kexec.bin` embebido para el firmware detectado.
2. `sys_kexec()` fija frecuencias y power-gating de la GPU (distinto para Pro vs Fat/Slim), copia la imagen de Linux y el initramfs a memoria, y **extrae el firmware AMD de la propia consola** (PFP/ME/CE/MEC/RLC/SDMA + EDID del monitor) para anexarlo al initramfs.
3. Al apagar el sistema (manual o automáticamente), un hook instalado en `icc_query_nowait` dispara: reconstrucción de tablas ACPI, detención de las demás CPUs, reconfiguración de VRAM/MTRR/GDT, soft-reset de la GPU, habilitación de salida de audio, y finalmente el salto real al kernel Linux cargado.
4. **No hay intervención del usuario en este tramo.** Si falla, el síntoma observable es indirecto (LED, video, tiempo transcurrido) — no hay un mensaje de error visible sin UART.

## Fase 5 — Arranque del kernel Linux e initramfs

1. El kernel recibe los parámetros vía `boot_params` (formato de arranque x86 estándar de Linux, adaptado por `linux_boot.c`) y el cmdline por defecto: `panic=0 clocksource=tsc consoleblank=0 net.ifnames=0 radeon.dpm=0 amdgpu.dpm=0 drm.debug=0 console=ttyS0,115200n8 console=tty0 video=HDMI-A-1:1920x1080@60` (salvo que exista `bootargs.txt`, que lo reemplaza entero).
2. **OBSERVACIÓN relevante para diagnóstico/GPU:** `radeon.dpm=0 amdgpu.dpm=0` deshabilita la gestión dinámica de energía de ambos drivers posibles — cualquier medición de rendimiento debe asumir reloj de GPU fijo (fijado ya en el paso anterior por `sys_kexec()`), no escalado dinámico.
3. El initramfs monta el rootfs real (USB, partición `psxitarch`) y hace `switch_root` — detalle del script `init` del initramfs **no auditado en esta sesión** (pertenece a "better-initramfs"/Psxitarch, no incluido en ninguno de los dos repos auditados).
4. **Resultado esperado:** login de KDE Plasma en el monitor conectado por HDMI, a la resolución indicada en el cmdline o autodetectada si no se fuerza.
5. **Señal de fallo distinta a la Fase 3:** si el kernel llega a inicializar (hay señal de video, aunque sea consola de texto) pero el rootfs no monta, el síntoma típico es caer en una shell de rescate con `mounting LABEL=psxitarch failed` — indica que el USB no fue detectado/montado por el kernel, no un fallo del exploit. Ver `docs/TROUBLESHOOTING.md`.

## Fase 6 — Retorno al sistema original

**HECHO DOCUMENTADO (README):** tras un reinicio, la consola vuelve a OrbisOS normalmente; para volver a Linux hay que rehacer el jailbreak y reenviar el payload. El USB puede quedar conectado. No hay, en el código auditado, ninguna persistencia que sobreviva un reinicio salvo lo que se haya escrito deliberadamente en `/data/linux/boot/` (Fase 2, si se eligió la Opción A).

## Resumen visual

```text
[Jailbreak GoldHEN] (fuera de alcance)
        |
        v
[USB: build-img.sh -> write-img.ps1]         [Kernel+initramfs: USB o /data/linux/boot/ -- DECISIÓN PENDIENTE]
        |                                                   |
        v                                                   v
[Enviar payload .elf -> puerto PayLoader (9020/9090) o FTP (2121)]
        |
        v
[kernel_main(): detecta FW, offsets, southbridge -> salta a kexec.bin embebido]
        |
        v
[sys_kexec(): fija clocks/power de GPU, extrae firmware AMD+EDID de la consola, arma handoff]
        |
        v
[Apagado -> hook ACPI/VRAM/GDT/GPU-reset -> jump real a Linux]
        |
        v
[Kernel Linux + initramfs -> monta rootfs USB (psxitarch) -> switch_root]
        |
        v
[KDE Plasma]  <-- o shell de rescate si el rootfs no monta
```
