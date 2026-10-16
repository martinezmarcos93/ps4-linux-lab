# Secuencia de arranque: del loader al escritorio (o a la consola de rescate)

Basado en la lectura de código documentada en [`docs/UPSTREAM_CODE_MAP.md`](UPSTREAM_CODE_MAP.md). Cada paso indica su naturaleza (HECHO DOCUMENTADO / OBSERVACIÓN DE CÓDIGO / HIPÓTESIS), precondiciones, resultado esperado y cómo abortar sin dañar nada. Complementa, sin reemplazar, [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) (que describe las capas a nivel conceptual) y [`docs/RECOVERY_STRATEGY.md`](RECOVERY_STRATEGY.md) (niveles de diagnóstico).

## Fase 0 — Prerequisito fuera de este laboratorio: jailbreak

**Fuera de alcance de esta auditoría.** El payload que auditamos depende de un mecanismo externo de ejecución de código en el kernel de OrbisOS — en la práctica, **GoldHEN** (créditos README de `X-F1REBALL-X/PS4-Linux`, autor SiSTR0). No auditamos GoldHEN en esta sesión. Sin él, nada de lo que sigue es alcanzable.

- **Precondición:** consola jailbreakeable en su firmware actual, con GoldHEN instalado y su servidor FTP/PayLoader activo.
- **Resultado esperado:** la consola acepta payloads por FTP (puerto 2121) y/o por el puerto del PayLoader (9020, con 9090 como alternativa documentada en el README de la distribución).
- **Condición de aborto:** si el jailbreak mismo falla, esto es un problema de GoldHEN/exploit, no de este laboratorio — no continuar a la Fase 1.

## Fase 1 — Preparación de medios (en la PC, sin tocar la consola)

1. Verificar hashes de los artefactos descargados contra `docs/EVIDENCE_SOURCES.md`.
2. Construir la imagen USB **a un archivo**, nunca a un dispositivo, con `tools/build_usb_image.py` (herramienta propia, sin root, valida rutas y limpia temporales ante fallos). No usar `build-img.sh` upstream como sustituto: la auditoría de `docs/UPSTREAM_CODE_MAP.md` §2.4 documenta riesgos de rutas fijas, limpieza incompleta y destino insuficientemente validado. Además, ese script no coloca ningún `bzImage` en la partición de arranque por defecto; solo `initramfs.cpio.gz`. En la política USB-only (D-008) el `bzImage` **sí** va dentro de la FAT; `build_usb_image.py` lo exige.
3. Verificar la cadena con `tools/verify_boot_chain.py` (estructura, integridad con catálogo, formato) — un resultado OK no prueba que arranque. La escritura al USB físico (`tools/write-img.ps1` de la distribución u otro método) es un **paso manual revisado** que este laboratorio no automatiza ni ejecuta — `UPSTREAM_CODE_MAP.md` §2.5.
4. **Resultado esperado:** USB con partición 1 FAT32 (512 MB, con `initramfs.cpio.gz`) y partición 2 ext4 etiquetada `psxitarch` (rootfs Arch+KDE).
5. **Condición de aborto:** cualquier hash que no coincida, o cualquier disco objetivo que `write-img.ps1` identifique como no-USB o de arranque/sistema (el script aborta solo; no forzar con `-Force` para saltar eso, porque esos chequeos no son opcionales — ver `UPSTREAM_CODE_MAP.md` §2.5).

## Fase 2 — Ubicación del kernel: USB-only (D-008) — política decidida, propiedad NO demostrada

**Decisión (D-008):** `bzImage`, `initramfs.cpio.gz` y los opcionales viven en la FAT del USB; no se escribe en el almacenamiento interno y la escritura interna no es un fallback automático. Diseño y bloqueos: [`USB_ONLY_DESIGN.md`](USB_ONLY_DESIGN.md).

**HECHO DOCUMENTADO (README de la distribución):** el procedimiento de `X-F1REBALL-X/PS4-Linux` sube por FTP (puerto 2121) `bzImage` e `initramfs.cpio.gz` a `/data/linux/boot/` del almacenamiento interno, y deja el rootfs en el USB, para compartir un mismo USB entre consolas con distinto southbridge. **Ese procedimiento no se sigue.**

**OBSERVACIÓN DE CÓDIGO (loader @ `f70f43a`, `linux/main-aio.c` líneas 375-389, macro `L(...)`):** cada archivo (`bzImage`, `initramfs.cpio.gz`, `bootargs.txt`, `vram.txt`) se busca **por separado** en `/mnt/usb0/`, `/mnt/usb1/`, `/data/linux/boot/` y `/user/system/boot/`, y se usa el primero que se pueda abrir. Consecuencias que **no** deben leerse al revés:
- La búsqueda prioritaria en USB **no** es aislamiento: si falta un archivo en el USB, el loader toma el del almacenamiento interno sin avisar.
- Puede combinar orígenes (p. ej. `bzImage` del USB con `initramfs.cpio.gz` del interno, o dos USB distintos). Modelado en `tools/loader_model.py` y probado en `tests/test_loader_model.py`.
- Un `vram.txt` o `bootargs.txt` olvidado en `/data/linux/boot/` también se usaría.
- Ningún commit del loader contiene código que escriba esos archivos (D-017): la "copia automática" del README no está respaldada por el código disponible.

**Qué hace el flujo USB-only en la práctica:**
1. La FAT del USB lleva `bzImage` (el que corresponda al southbridge, **aún desconocido**) e `initramfs.cpio.gz`, con esos nombres exactos.
2. Antes de cada intento (fase con ejecución autorizada) se comprueba por FTP de solo lectura que `/data/linux/boot/` y `/user/system/boot/` no contengan archivos ajenos.
3. Si el loader no encuentra ambos archivos en el USB, el comportamiento upstream es seguir buscando en el interno; con el parche de `patches/loader-usb-only-f70f43a.patch` (compilado y revisado estáticamente, no ejecutado) se rechazaría con una alerta.
4. Si el flujo no pudiera demostrarse USB-only, se detiene y se documenta; no se pasa a escritura interna.

**Estado real:** política decidida (`IMPLEMENTADO`); propiedad de aislamiento **no demostrada** (`PENDIENTE`), con los bloqueos de `USB_ONLY_DESIGN.md` §4.

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
3. La inspección estática documentada en `docs/USB_ONLY_DESIGN.md` §2 indica que el `init` de better-initramfs 0.9.1 monta `LABEL=psxitarch` y que no se encontró directorio `/hooks` en el initramfs inspeccionado. Esto es una revisión parcial del artefacto disponible, no una auditoría completa de la distribución ni una prueba de ejecución. El initramfs/rootfs de la imagen final todavía debe verificarse por hash y procedencia antes de cualquier intento.
4. **Resultado esperado:** login de KDE Plasma en el monitor conectado por HDMI, a la resolución indicada en el cmdline o autodetectada si no se fuerza.
5. **Señal de fallo distinta a la Fase 3:** si el kernel llega a inicializar (hay señal de video, aunque sea consola de texto) pero el rootfs no monta, el síntoma típico es caer en una shell de rescate con `mounting LABEL=psxitarch failed` — indica que el USB no fue detectado/montado por el kernel, no un fallo del exploit. Ver `docs/TROUBLESHOOTING.md`.

## Fase 6 — Retorno al sistema original

**HECHO DOCUMENTADO (README):** tras un reinicio, la consola vuelve a OrbisOS normalmente; para volver a Linux hay que rehacer el jailbreak y reenviar el payload. El USB puede quedar conectado. No hay, en el código auditado, ninguna persistencia que sobreviva un reinicio salvo lo que se haya escrito deliberadamente en `/data/linux/boot/` (en la política USB-only no debería haber nada; si hubiera archivos allí, vienen de un procedimiento ajeno a este laboratorio y deben revisarse antes de cualquier intento, D-017).

## Resumen visual

```text
[Jailbreak GoldHEN] (fuera de alcance)
        |
        v
[USB: build-img.sh -> write-img.ps1]         [Kernel+initramfs: FAT del USB (D-008, USB-only; propiedad por demostrar)]
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
