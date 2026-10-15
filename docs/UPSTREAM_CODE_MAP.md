# Mapa de código upstream

**Fecha de consulta:** 2026-10-15.
**Método:** clon superficial (`--depth 1`) de ambos repositorios a un directorio temporal fuera de este laboratorio, lectura directa de archivos e historial vía `git log`/`gh api`. No se copió ningún binario, kernel, payload ni rootfs a este repositorio.
**Commits exactos auditados:**

| Repositorio | Rama | Commit | Fecha |
|---|---|---|---|
| `X-F1REBALL-X/PS4-Linux` | `main` | `66e21cb8c15f20189254e2608c6e9bf957eb8078` | 2026-10-04 |
| `ps4-linux/ps4-linux-loader` | `master` | `f70f43a60a973b3662daeb29c1f115d95408db93` | 2026-09-23 |

Todas las afirmaciones de este documento son **OBSERVACIÓN DE CÓDIGO** salvo que se marquen explícitamente como HIPÓTESIS o PENDIENTE. Las rutas son relativas a la raíz de cada repositorio, no de este laboratorio.

---

## 1. `ps4-linux/ps4-linux-loader` (el exploit/payload en sí)

### 1.1 Qué es realmente este repositorio

Es un **mirror/fork funcional de `ArabPixel/ps4-linux-payloads`**. El propio `README.md` (línea 86) instruye `git clone https://github.com/ArabPixel/ps4-linux-payloads` para compilar, y la sección de créditos (líneas 91-98, 164-176 en el otro repo) confirma que ArabPixel es quien mantiene el loader original. **PENDIENTE DE VERIFICACIÓN:** no determinamos si `ps4-linux/ps4-linux-loader` es un fork con historial compartido, un mirror manual, o un repositorio independiente con el mismo contenido; no se investigó la relación de forks en la API de GitHub.

No es un exploit de jailbreak. El propio `linux/ps4-kexec-common/README.md` (líneas 7-8) lo dice explícitamente: *"This is not an exploit. It is useless without some mechanism of injecting code into the PS4 OS kernel."* Depende de un mecanismo externo de ejecución de código en kernel — en la práctica, **GoldHEN** (jailbreak + servidor FTP + "PayLoader"), mencionado en ambos READMEs upstream.

### 1.2 Estructura real (excluyendo el árbol vendorizado `freebsd-headers/`)

```text
loader/
├── lib/                          # SDK mínimo: syscalls, crt, dlopen
│   ├── crt.asm, dl.c, syscalls.asm, syscalls.py, Makefile
├── linux/                        # El payload "AIO" (all-in-one)
│   ├── main-aio.c                # Entry point userspace + kernel_main()
│   ├── fw_detect.c / .h          # Detección de firmware vía SCE header
│   ├── fw_offsets.h              # Tabla de offsets de kernel por firmware
│   ├── sb_detect.h               # IDs de southbridge (Aeolia/Belize/Baikal/Belize2)
│   ├── magic.h, aio_types.h
│   ├── Makefile                  # Build: 20 firmwares × 9 tamaños de VRAM
│   └── ps4-kexec-common/         # Subproyecto con LICENCIA PROPIA (BSD-2-clause)
│       ├── kexec.c               # syscall sys_kexec: arma el handoff a Linux
│       ├── linux_boot.c          # Reconfigura VRAM, GDT, ACPI, jump real a Linux
│       ├── firmware.c            # Extrae firmware AMD (PFP/ME/CE/MEC/RLC/SDMA) del propio OrbisOS
│       ├── acpi.c                # Reconstruye tablas ACPI (RSDT/XSDT/FADT/IVRS) para Linux
│       ├── kernel.c/.h           # Resolución de símbolos del kernel FreeBSD/Orbis
│       └── LICENSE, README.md
└── .github/workflows/build.yml   # CI: compila y publica artefactos por push/PR
```

### 1.3 Flujo de componentes (quién llama a quién)

1. `main()` en `main-aio.c` (líneas 342-431) — corre en userspace, tras el jailbreak.
2. `get_firmware()` (`fw_detect.c`) lee el header SCE de `/system/common/lib/libc.sprx` para obtener el firmware **real** que corre la consola (no el SDK objetivo). Adaptado de `Al-Azif/ps4-skeleton` (MIT) según el comentario en `fw_detect.c:7` — **dependencia/atribución de un tercer proyecto no auditado en esta sesión**.
3. `find_offsets_by_fw()` busca en `fw_table[]` (`fw_offsets.h`, 20 entradas) los offsets de símbolos del kernel Orbis para ese firmware exacto. Si no hay entrada, aborta con alerta (`main-aio.c:354-358`).
4. `get_kexec_blob()` selecciona, de 20 blobs `kexec.bin` **embebidos en el mismo binario** vía `.incbin` (líneas 53-72), el que corresponde al firmware detectado.
5. `get_sb_id()` detecta el southbridge en runtime vía `sysctlbyname("hw.sce_subsys_subid", …)` (líneas 302-322) — **no** por el modelo CUH ni por heurística de nombre.
6. Carga `bzImage`, `initramfs.cpio.gz`, `bootargs.txt` y `vram.txt` probando en orden: `/mnt/usb0/`, `/mnt/usb1/`, `/data/linux/boot/`, `/user/system/boot/` (macro `L(...)`, líneas 375-389).
7. `kexec(kernel_main, NULL)` dispara el exploit de ejecución en kernel (mecanismo no incluido en este repo); `kernel_main()` (líneas 252-282) parchea 3 bytes del kernel Orbis en los offsets de la tabla, copia el blob `kexec.bin` embebido a memoria de kernel y salta a él.
8. El blob `kexec.bin` instala la syscall 153 (`sys_kexec`, `kexec.c:106-267`): fija frecuencias/power-gating de GPU (distintas para Pro vs Fat/Slim, líneas 136-158), copia imagen+initramfs, llama `firmware_extract()` para inyectar el firmware AMD de la propia consola al initramfs, e instala un hook en `icc_query_nowait`.
9. Al apagar el sistema (o al forzarlo vía syscalls de reboot), el hook (`hook_icc_query_nowait`, `kexec.c:450-474`) corre `fix_acpi_tables()` (`acpi.c`), detiene las demás CPUs y llama `cpu_quiesce_gate()` (`linux_boot.c:202-447`), que reconfigura VRAM (`configure_vram()`), MTRRs, GDT, hace soft-reset de la GPU y finalmente salta al kernel Linux copiado.

### 1.4 Parámetros de memoria/VRAM — mecanismo real

- `vram.txt` (texto plano, MB) tiene prioridad sobre el tamaño compilado en el payload elegido (`main-aio.c:401-408`).
- Rango válido: 32–4096 MB; fuera de rango cae al valor por defecto del payload (1024 MB) (`main-aio.c:286-294`).
- La reserva **no es solo lógica**: `configure_vram()` (`linux_boot.c:123-137`) escribe registros reales del controlador de memoria de la GPU (`MC_VM_FB_LOCATION`, `MC_VM_FB_OFFSET`, `HDP_NONSURFACE_BASE`, `CONFIG_MEMSIZE`) para recortar un rango de memoria unificada como framebuffer dedicado.
- El cmdline por defecto (`main-aio.c:395-399`) incluye `radeon.dpm=0 amdgpu.dpm=0` — **gestión dinámica de frecuencia/energía desactivada por defecto en el lado Linux**. Además, `sys_kexec()` fija manualmente las frecuencias de varios bloques de la GPU y el p-state (`kexec.c:138-164`) **antes** de que Linux arranque. Esto implica que cualquier benchmark debe registrar que el reloj de GPU está fijado por el payload, no gestionado dinámicamente ni por amdgpu ni por el firmware de Sony en modo Linux.

### 1.5 Extracción de firmware AMD (evita redistribuir binarios de Sony/AMD)

`firmware.c` extrae en runtime, desde las estructuras internas de OrbisOS (`gc_get_fw_info`/`Starsha_UcodeInfo`), los microcódigos PFP/ME/CE/MEC/MEC2/RLC/SDMA/SDMA1 y el EDID del monitor conectado, y los empaqueta como un cpio adicional que se concatena al initramfs (`kexec.c:180-201`, `firmware.c:367-475`). Esto es relevante para licencias: **el loader no distribuye firmware de AMD/Sony; lo copia desde la propia consola del usuario en cada arranque.** Distingue GPU "liverpool" (PS4 base) vs "gladius" (PS4 Pro, detectado por `gpu_devid_is_9924()`), con tamaños de firmware distintos por variante (`firmware.c:137-156`).

**Hallazgo con corrección histórica documentada:** el cálculo de tamaño del EDID tuvo un bug de desborde/truncamiento corregido en el PR #9 (`firmware: fix EDID buffer overflow and truncated extension blocks`, mergeado como `3b5e038e88f7a88d39408d960a0a798b1bac56a7` sobre base `142f55ff42eaa5a494c14d096ce35170c6edbbbc`). Antes: `edid_sz = (byte126 ? 256 : 128)` (binario, solo 2 valores posibles). Después: `edid_sz = 128 * (1 + ext_blocks)`, leyendo correctamente el número de bloques de extensión del byte 126 del EDID. El código auditado en el commit `f70f43a6` ya incluye la corrección (`firmware.c:387-388`). Relevancia directa: un EDID mal dimensionado puede truncar o corromper el bloque entregado a Linux, afectando detección de modos de video — causa plausible de "sin señal" o resoluciones incorrectas en consolas con monitores que reportan EDID con bloques de extensión.

### 1.6 Detección de southbridge y su tratamiento asimétrico

`sb_detect.h` define 4 familias: `SB_AEOLIA=1`, `SB_BELIZE=2`, `SB_BAIKAL=3`, `SB_BELIZE2=4`. En `linux_boot.c:357-380`, el apagado de IOMMU/MSI/HPET tiene **solo dos ramas de código**: una específica para Baikal (direcciones MMIO propias) y una genérica para "no Baikal" que usa **las mismas direcciones de Aeolia** para Aeolia, Belize y Belize2 por igual. **HIPÓTESIS (no confirmada en el código):** esto asume que Aeolia y Belize/Belize2 comparten offsets MMIO idénticos para estos registros; no se encontró en el código ninguna verificación o comentario que confirme esa equivalencia para Belize2 específicamente.

### 1.7 Firmwares soportados — lista canónica desde el Makefile, no desde el README

`linux/Makefile` (líneas `FIRMWARES = 505 672 700 750 800 850 900 903 960 1000 1050 1100 1102 1150 1200 1250 1300 1302 1350 1352`) es la fuente de verdad: son exactamente las mismas 20 versiones que tienen entrada en `fw_offsets.h`. El README puede listar "13.52(?)" con incertidumbre, pero el build únicamente genera blobs para estas 20 versiones exactas; cualquier firmware fuera de esta lista (incluyendo versiones posteriores a 13.52) **no tiene offsets** y `find_offsets_by_fw()` lo rechaza explícitamente.

### 1.8 Lo que el código **no** hace (verificado por ausencia)

Se buscó explícitamente (`grep -rni "O_CREAT|O_WRONLY|/data/linux|/user/system/boot|write_file|fwrite"` sobre `linux/` y `lib/`) cualquier escritura hacia `/data/linux/boot/` o `/user/system/boot/`. **No se encontró ninguna.** El payload auditado en este commit solo **lee** esas rutas como respaldo; nunca copia archivos hacia ellas. Esto contradice la entrada del changelog del propio README (ver `docs/EVIDENCE_SOURCES.md`, sección de discrepancias) que describe una función "Automatic boot files placement" de una versión anterior (v23) — **PENDIENTE DE VERIFICACIÓN:** no se determinó si esa función existió en v23 y fue removida, si pertenece a una rama distinta de ArabPixel/ps4-linux-payloads no incluida en este mirror, o si nunca estuvo en este payload "AIO" concreto.

### 1.9 Licencias dentro de este repositorio (no asumir una sola)

- `linux/ps4-kexec-common/LICENSE`: BSD de 2 cláusulas, Copyright shuffle2 y Hector Martin "marcan" (2015-2016). Permisiva, exige conservar el aviso de copyright.
- Resto de `linux/` (`main-aio.c`, `fw_detect.*`, `fw_offsets.h`, `sb_detect.h`): **sin archivo LICENSE propio encontrado**; `fw_detect.c` declara en comentario que está adaptado de `Al-Azif/ps4-skeleton (MIT)`.
- `lib/`: sin archivo LICENSE propio encontrado en la ruta auditada.
- No hay un archivo `LICENSE` ni `NOTICE` en la raíz del repositorio `ps4-linux/ps4-linux-loader` en el commit auditado.

---

## 2. `X-F1REBALL-X/PS4-Linux` (distribución lista para usar)

### 2.1 Qué es

Un **empaquetado de distribución**, no un proyecto de código fuente: integra un kernel precompilado, un rootfs Arch+KDE comprimido, el payload del proyecto anterior, y dos scripts de instalación. El propio README lo confirma en "Credits": no reivindica autoría del kernel, loader ni rootfs.

### 2.2 Estructura

```text
ps4-linux-fat/
├── LICENSE                 # GPL-3 (declarado para "guía, scripts y preparación de imagen")
├── NOTICE                  # Aclara que kernel=GPLv2, resto=licencias originales de cada autor
├── README.md               # Guía de instalación, tabla de compatibilidad, créditos
├── boot/
│   ├── baikal/bzImage                                  # 13.8 MB — kernel para Baikal
│   ├── belize/bzImage                                  # 20.4 MB — kernel para Aeolia/Belize
│   ├── belize/kernel-7.1.7-Strawberry-General.config   # defconfig, 151 KB
│   └── initramfs.cpio.gz                               # 4.1 MB
├── images/desktop.jpg      # captura de pantalla
├── payload/linux-{32,64,128,256,512,1024,2048,3072,4096}mb.elf   # 320,936 bytes cada uno
└── tools/
    ├── build-img.sh        # construye imagen USB de 12 GB (Linux/WSL)
    └── write-img.ps1        # escribe esa imagen a un disco físico (Windows)
```

### 2.3 Hashes SHA-256 (calculados en esta sesión sobre el clon local, no publicados por upstream)

| Archivo | SHA-256 |
|---|---|
| `boot/baikal/bzImage` | `46c835f762e7b0b5400ea762b8daa1bcec638a1b769c7ec0905137bc565b1ba8` |
| `boot/belize/bzImage` | `072113898347932c34888cfdc7556953ee27233c0727cc45f419a57119242480` |
| `boot/initramfs.cpio.gz` | `3f373bd6c469e490eaf4e5cf4d2e8ed77cf7bb91449b6a18da6a6529d479169b` |
| `payload/linux-1024mb.elf` | `623c3b68592437b612ede22a4fc1a6f1eef6b17c4b16a1270100ece04cb3c98f` |

(Lista completa de los 9 payloads en `docs/EVIDENCE_SOURCES.md`.) Todos los `payload/linux-*mb.elf` pesan exactamente 320 936 bytes — consistente con que el tamaño de VRAM se parametriza en runtime vía `vram.txt`/nombre de payload, no con un binario distinto por tamaño en esta build concreta. **PENDIENTE DE VERIFICACIÓN:** no se confirmó si estos 9 archivos son binariamente idénticos entre sí (no se comparó byte a byte); el tamaño igual es compatible con que solo cambie una constante de compilación (`VRAM_MB_DEFAULT`), lo cual a su vez es coherente con el código de `linux/Makefile` del otro repo.

### 2.4 `tools/build-img.sh` (bash, 43 líneas) — hallazgos puntuales con línea exacta

- Línea 20: ruta fija `/root/psxitarch-usb.img` (no es un directorio temporal único por ejecución).
- Línea 21: `rm -f "$IMG"` antes de crear — borra sin confirmar si ya existiera algo con ese nombre exacto (bajo riesgo, ruta fija dentro de `/root`, pero no es una práctica que replicaríamos en herramientas propias).
- Líneas 22-25: partición 1 FAT32 512 MiB (boot), partición 2 ext4 etiquetada `psxitarch` (rootfs) — **el script NO coloca ningún `bzImage` en la partición 1 por defecto**, solo `initramfs.cpio.gz` (línea 33) y, opcionalmente, "kernels de repuesto" renombrados como `bzImage.<carpeta>` para que el loader los ignore (línea 34, documentado en cabecera líneas 11-13).
- Línea 37: verifica el filesystem con `e2fsck -fn` (solo lectura) tras desmontar.
- Línea 41: calcula SHA-256 del `.img` final — util para verificación posterior, consistente con nuestra política de hashes.
- Ejecuta herramientas de partición/filesystem como root (uso esperado dentro de una VM/WSL dedicada, no en el sistema host de producción).

### 2.5 `tools/write-img.ps1` (PowerShell, 106 líneas) — hallazgos puntuales, con corrección a nuestra auditoría previa

- Líneas 56-58: **estas comprobaciones (`BusType -ne 'USB'`, `IsBoot/IsSystem`, tamaño insuficiente) son incondicionales — `-Force` NO las omite.** Esto corrige una imprecisión de `docs/UPSTREAM_AUDIT.md` (que decía que `-Force` "permite omitir la confirmación" sin aclarar qué parte); `-Force` (línea 64) **solo** omite el paso interactivo de reescribir el número de disco como segunda confirmación (líneas 64-67), no los chequeos de seguridad estructurales.
- Líneas 86-94: técnica deliberada de escritura — pone a cero el primer MB, escribe el resto, y **recién al final** escribe el MBR real — para evitar que Windows monte una partición a mitad de la escritura.
- Soporta `.img.xz` descomprimiendo al vuelo vía `7z.exe` (líneas 40-47, 74-78) — introduce una dependencia externa (7-Zip) no declarada como prerequisito explícito en el README.
- Requiere PowerShell como Administrador (líneas 32-35) — coherente con nuestro entorno Windows-first.

### 2.6 Créditos del README como mapa de procedencia (cadena completa reconstruida)

1. **fail0verflow (marcan, shuffle2)** — port original del kernel Linux a PS4 y `ps4-kexec` (= la base BSD-licenciada que auditamos en §1).
2. **rancido, PSXITA Team, eeply, valeryy, tihmstar, mircoho, codedwrench, crashniels** — parches de kernel (amdgpu, video Pro/Slim, audio HDMI, soporte Baikal y Belize).
3. **rmuxnet** — kernels "Strawberry" (7.1.7 para Aeolia/Belize; port a 7.0.8 para Baikal) y el rework del loader para ser agnóstico de firmware/southbridge (= lo que hoy es `main-aio.c`).
4. **ps4boot** — loader original `ps4-linux-payloads`.
5. **ArabPixel** — mantenedor actual de `ps4-linux-loader`/`ps4-linux-payloads`, soporte FW 12.5x y 13.00–13.52.
6. **PSXITA Team (Rancido)** — initramfs y scripts de instalación "Psxitarch v3".
7. **Piotr Karbowski** — `better-initramfs` (base del init usado).
8. **Erkkola** — rootfs "Arch Linux KDE v1.1.1".
9. **centi07, DionKill** — paquetes de Mesa y drivers de video parcheados para PS4.
10. **SiSTR0** — GoldHEN (jailbreak + servidor FTP + BinLoader/PayLoader) — **el mecanismo externo que el propio `ps4-kexec-common/README.md` dice que es indispensable y que este laboratorio no audita ni distribuye.**

### 2.7 Nomenclatura de versión del kernel — señal de alerta, no conclusión

El archivo de configuración se llama `kernel-7.1.7-Strawberry-General.config` y su primera línea es `# Linux/x86_64 7.1.7 Kernel Configuration`. En paralelo, un reporte de la comunidad (issue #10 del loader, ver `docs/EVIDENCE_SOURCES.md`) describe una instalación funcional usando "Kernel 5.4.247 Baikal build" — un número de versión mainline de Linux real y muy distinto. **HIPÓTESIS, no confirmada:** "7.1.7"/"7.0.8" son probablemente la numeración propia del fork "Strawberry" de rmuxnet (no la versión de Linux mainline), y la base real podría ser una rama LTS de Linux 5.4.x, dado que 5.4 fue una base común para ports de GPU GCN1/Polaris de esa época. No localizamos ni auditamos el repositorio fuente del kernel "Strawberry"; este punto queda **PENDIENTE DE VERIFICACIÓN** antes de citar una versión de Linux en cualquier documento técnico.

### 2.8 Licencias

- `LICENSE` (raíz): GPL-3.0 completo.
- `NOTICE`: aclara explícitamente que esa GPL-3 cubre "guía, scripts e instalación de imagen" (es decir, `build-img.sh`/`write-img.ps1`/README), que los **kernels son GPLv2** (herencia obligatoria de Linux), y que "el loader, el initramfs y la imagen de Arch Linux fueron hechos por otras personas y mantienen sus licencias originales" — sin especificar cuáles son esas licencias para cada componente. Esto es insuficiente para nuestra política (`docs/LICENSE_POLICY.md`): antes de redistribuir o modificar el rootfs Arch+KDE o el initramfs, hay que identificar la licencia real de Psxitarch/better-initramfs/Erkkola-KDE-rootfs en sus propios repositorios — **no auditados en esta sesión**.

---

## 3. Relación entre ambos repositorios

`X-F1REBALL-X/PS4-Linux` **consume** el payload de `ps4-linux/ps4-linux-loader` (o de su upstream real, `ArabPixel/ps4-linux-payloads`) como un binario ya compilado (`payload/linux-1024mb.elf`), y lo combina con un kernel y rootfs de otra procedencia. No comparten código fuente propio: la relación es de **integración de distribución**, no de fork. Cualquier decisión sobre el método de arranque (parámetros de `vram.txt`, firmware soportado, detección de southbridge) depende del código auditado en la Sección 1; cualquier decisión sobre el rootfs/kernel/instalación depende de la Sección 2.

## 4. Limitaciones de esta auditoría

- No se clonó el historial completo (`--depth 1`); no se revisaron commits anteriores al HEAD de cada rama.
- No se auditó `Al-Azif/ps4-skeleton`, `ArabPixel/ps4-linux-payloads` (el upstream real del loader), el kernel "Strawberry" de rmuxnet, Psxitarch, `better-initramfs`, el rootfs de Erkkola, los paquetes de Mesa de centi07/DionKill, ni GoldHEN. Son dependencias de hecho de este proyecto y deberían auditarse antes de depender de ellas en producción.
- No se abrió el binario `bzImage` ni los `.elf` con herramientas de desensamblado; el análisis de `payload/` se basa en el código fuente equivalente del otro repositorio, no en los binarios mismos.
- Los 20 offsets de `fw_offsets.h` no se validaron independientemente; se documentan como existen en el código.
