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

### 1.8 Lo que el código **no** hace (verificado por ausencia) y qué pasó con la "copia automática"

**Alcance de la búsqueda (2026-10-15, historial completo de 71 commits clonado en una carpeta aislada, sin ejecutar nada):**
- `git log --all -S"O_CREAT"` y `-S"O_WRONLY"` sobre todo el historial: solo el commit inicial `d55dd2c` (2022-10-26, "linuxpayloads"), en el `main()` de prueba de `acpi.c` (`fd = open(argv[1], O_RDWR)`, no forma parte del payload). `-S"creat("`, `-S"time="` y `-S"CURRENTTIME"` sobre fuentes no-markdown: **sin resultados**. `-S"/data/linux"` aparece solo en las definiciones de lectura (`HDD_BOOT_PATH`).
- Estado del código en cinco instantáneas (`2d5cb44` 2025-09-26, `e82e513` 2025-12-31, `e9ddc48^` 2026-03-28, `e9ddc48` 2026-04-01 —la unificación AIO—, `f70f43a` HEAD): en todas, los archivos de arranque solo se **leen** con la macro/lógica `L(...)` (`main.c`/`main-baikal.c` antes de AIO, `main-aio.c` después).
- La frase "Automatic boot files placement — … copied automatically to /data/linux/boot on the internal drive" entra en el `README.md` en `8a1468f` (2025-09-26, commit **solo de README**), cuando el código era `main.c`/`main-baikal.c` y no tenía ninguna escritura. El matiz "from the external fat32 partition" lo agrega `7280a37` (2026-04-02, otro commit solo de README). La frase sobre pasar la hora a `time=CURRENTTIME` entra en el mismo commit `8a1468f` y **tampoco** tiene código en ningún commit.
- En los artefactos que sí se pudieron inspeccionar: el `init` y `functions.sh` del initramfs v0.9.1 no copian a `/data/linux/boot` ni procesan `time=`; el ELF `linux-1024mb.elf` tiene como únicas rutas literales las de lectura (`tools/elf_audit.py`), y su tabla `fw_table` coincide con `fw_offsets.h` de `f70f43a`.

**Respuestas a las preguntas del encargo (todas con el límite indicado):**
| Pregunta | Respuesta demostrable |
|---|---|
| ¿Qué componente realiza la copia? | **DESCONOCIDO.** Ningún componente inspeccionado la realiza. Quedan sin inspeccionar: el código real de los *releases* (el workflow de CI no los publica) y cualquier initramfs distinto del v0.9.1 de la distribución. |
| ¿En qué versión se introdujo? | La *afirmación* se introduce en el README el 2025-09-26 (`8a1468f`), antes de la v23 (2026-03-28) que algunos documentos citaban; **ningún commit** introduce el *código*. |
| ¿Cuándo ocurre? ¿Es obligatoria? | No determinable: no hay código. Se descarta que sea obligatoria para el binario cuyo código se leyó (arranca con solo leer). |
| ¿Puede combinar archivos de distintas ubicaciones? | **Sí, demostrado por código** (`main-aio.c` 375-389): resuelve cada archivo por separado. Modelado en `tools/loader_model.py`. |
| ¿Rutas de escritura adicionales? | Ninguna encontrada en el payload ni en el ELF distribuido. El kernel Linux resultante es una incógnita aparte (§1.5: recibe `key/eap_hdd_key.bin`, línea 381-382 de `ps4-kexec-common/firmware.c`). |
| ¿Qué evidencia faltaría? | Código fuente de los releases + compilación reproducible; el contenido de cualquier otro initramfs que se vaya a usar; y una observación de laboratorio del disco interno antes/después (D-017). |

Esto reemplaza la nota anterior ("posible función de v23 removida"): **esa hipótesis queda refutada para las instantáneas revisadas**, no resuelta en general.

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

(Lista completa de los 9 payloads en `docs/EVIDENCE_SOURCES.md`.) Todos los `payload/linux-*mb.elf` pesan exactamente 320 936 bytes — consistente con que el tamaño de VRAM se parametriza en runtime vía `vram.txt`/nombre de payload, no con un binario distinto por tamaño en esta build concreta. **Verificado el 2026-10-15** (`tools/elf_audit.py --comparar`, solo lectura): los 9 ELF **no** son idénticos (9 sha256 distintos) pero difieren de `linux-1024mb.elf` en solo 21-24 bytes: 19-20 en `.note.gnu.build-id` y 2-4 en `.text` (la constante de `VRAM_MB_DEFAULT`). Es decir, el mismo código con distinto tamaño de VRAM por defecto. Además, el ELF de 1024 MB está sin strip, compilado con `GCC: (GNU) 16.2.1 20260810`, y su tabla `fw_table` (20 firmwares, de 5.05 a 13.52) coincide fila a fila con `linux/fw_offsets.h` de `f70f43a`. Eso es coherencia entre binario y código en esa tabla y en los literales de ruta; **no** es una compilación reproducible: los blobs `kexec.bin` embebidos no se han podido comparar.

### 2.4 `tools/build-img.sh` (bash, 43 líneas) — hallazgos puntuales con línea exacta

- Línea 20: ruta fija `/root/psxitarch-usb.img` (no es un directorio temporal único por ejecución).
- Línea 21: `rm -f "$IMG"` antes de crear — borra sin confirmar si ya existiera algo con ese nombre exacto (bajo riesgo, ruta fija dentro de `/root`, pero no es una práctica que replicaríamos en herramientas propias).
- Líneas 22-25: partición 1 FAT32 512 MiB (boot), partición 2 ext4 etiquetada `psxitarch` (rootfs) — **el script NO coloca ningún `bzImage` en la partición 1 por defecto**, solo `initramfs.cpio.gz` (línea 33) y, opcionalmente, "kernels de repuesto" renombrados como `bzImage.<carpeta>` para que el loader los ignore (línea 34, documentado en cabecera líneas 11-13).
- Línea 37: verifica el filesystem con `e2fsck -fn` (solo lectura) tras desmontar.
- Línea 41: calcula SHA-256 del `.img` final — util para verificación posterior, consistente con nuestra política de hashes.
- Ejecuta herramientas de partición/filesystem como root (uso esperado dentro de una VM/WSL dedicada, no en el sistema host de producción).

**Hallazgos adicionales de la revisión de 2026-10-15 (revisión manual; `shellcheck` no reporta nada):**
- No hay `trap` de limpieza: con `set -e`, un fallo tras `losetup`/`mount` deja el dispositivo loop y los montajes `/mnt/psx` y `/mnt/psxboot` activos (se desmontan solo al final feliz, línea 36-38).
- Los puntos de montaje son fijos y no se comprueba que estén libres ni que `mount` no se haya aplicado ya a otra cosa.
- `sleep 2` después de `losetup -Pf` es una carrera (debería esperarse a udev/`partprobe`).
- El destino `OUT` (`$3`) no se valida: pasar un dispositivo (`/dev/sdX`) haría que `cp --sparse=never "$IMG" "$OUT"` escriba la imagen sobre el disco. El uso documentado es un archivo, pero nada lo exige.
- `"${SPARE[@]}"` bajo `set -u` falla con bash < 4.4 si no hay kernels de repuesto.
- Tamaño fijo de 12 GiB incompatible con el mínimo de 16 GB si el USB real es algo menor que su capacidad nominal.
Todo esto se mitiga en `tools/build_usb_image.py` (solo archivo, sin root, temporal + `os.replace`, rechazo de rutas del sistema y de dispositivos, `fsck.vfat` sobre p1). No se modifica el script upstream.

### 2.5 `tools/write-img.ps1` (PowerShell, 106 líneas) — hallazgos puntuales, con corrección a nuestra auditoría previa

- Líneas 56-58: **estas comprobaciones (`BusType -ne 'USB'`, `IsBoot/IsSystem`, tamaño insuficiente) son incondicionales — `-Force` NO las omite.** Esto corrige una imprecisión de `docs/UPSTREAM_AUDIT.md` (que decía que `-Force` "permite omitir la confirmación" sin aclarar qué parte); `-Force` (línea 64) **solo** omite el paso interactivo de reescribir el número de disco como segunda confirmación (líneas 64-67), no los chequeos de seguridad estructurales.
- Líneas 86-94: técnica deliberada de escritura — pone a cero el primer MB, escribe el resto, y **recién al final** escribe el MBR real — para evitar que Windows monte una partición a mitad de la escritura.
- Soporta `.img.xz` descomprimiendo al vuelo vía `7z.exe` (líneas 40-47, 74-78) — introduce una dependencia externa (7-Zip) no declarada como prerequisito explícito en el README.
- Requiere PowerShell como Administrador (líneas 32-35) — coherente con nuestro entorno Windows-first.

**Hallazgos adicionales (2026-10-15):** la comprobación `BusType -eq 'USB'` admite un **disco USB externo de datos** del PC (no solo un pendrive): la salvaguarda real es el número de disco tecleado por la persona. Entre la consulta de `Get-Disk` y la escritura (tras la confirmación interactiva) no se vuelve a enumerar el disco, de modo que un cambio de numeración por desconexión/reconexión no se detecta. El `Clear-Disk -RemoveData -RemoveOEM` se ejecuta si hay particiones. El proyecto no incorpora este script ni lo ejecuta (D-013); el procedimiento de escritura física queda como paso manual revisado.

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

### 2.7 Nomenclatura de versión del kernel — RESUELTA por observación directa

La hipótesis anterior ("7.1.7/7.0.8 serían numeración propia del fork") queda **refutada** (D-009): la cabecera de arranque x86 de cada `bzImage` trae la cadena `kernel_version` y dice `7.0.8-Strawberry-FullLTO-Baikal-+ … Tue Sep 8 03:09:52 CEST 2026` y `7.1.7-Strawberry-General-FullLTO+ … Tue Aug 25 18:56:41 UTC 2026`. Son Linux 7.0.8 y 7.1.7. El "Kernel 5.4.247" del issue #10 es otra compilación. Lectura reproducible con `tools/verify_boot_chain.py`.

### 2.8 Licencias

- `LICENSE` (raíz): GPL-3.0 completo.
- `NOTICE`: aclara explícitamente que esa GPL-3 cubre "guía, scripts e instalación de imagen" (es decir, `build-img.sh`/`write-img.ps1`/README), que los **kernels son GPLv2** (herencia obligatoria de Linux), y que "el loader, el initramfs y la imagen de Arch Linux fueron hechos por otras personas y mantienen sus licencias originales" — sin especificar cuáles son esas licencias para cada componente. Esto es insuficiente para nuestra política (`docs/LICENSE_POLICY.md`): antes de redistribuir o modificar el rootfs Arch+KDE o el initramfs, hay que identificar la licencia real de Psxitarch/better-initramfs/Erkkola-KDE-rootfs en sus propios repositorios — **no auditados en esta sesión**.

### 2.9 Initramfs y rootfs de la imagen publicada (lectura estática, 2026-10-15)

Origen: `initramfs.cpio.gz` sha256 `3f373bd6…9169b` (48 entradas, `VERSION` = `v0.9.1`, better-initramfs) extraído solo para leer texto, y la imagen `psxitarch-usb.img` del release `v1.0` (sha256 contrastado con `SHA256SUMS`) leída **sin montar** con `debugfs`/`7z`. No se ejecutó nada.
- `init` (100 líneas): monta `proc`, `sys`, `dev`; procesa la línea de órdenes; `sleep 10`; **`mount LABEL=psxitarch /newroot`**; `switch_root`; si falla, `rescueshell`. No monta discos internos ni copia archivos. No existe `/hooks`.
- `bin/install-psxitarch.sh` (115 líneas, **manual**, no se invoca desde `init`): recorre `/dev/sda…/dev/sdk`, monta la partición 1 de cada uno y elige el primero que contenga `bzImage`, `initramfs.cpio.gz` **y** `psxitarch.tar.gz`; a ese dispositivo le aplica `fdisk` (`o`, `n`, `w`), `mkfs.vfat` y `mke2fs`. Riesgo: si el disco interno de la PS4 aparece como `/dev/sd?`, el script solo lo tocaría si su partición 1 tuviera esos tres archivos (no ocurre en un disco de PS4), pero es un script destructivo que opera sobre dispositivos elegidos por heurística. También copia `/key/eap_hdd_key.bin` a `/newroot/etc/cryptmount`, persistiendo en el USB la clave del disco de **esa** consola. La imagen publicada no trae `/etc/cryptmount`, o sea, ese script no se ejecutó para armarla.
- `bin/start-psxitarch.sh`: monta `LABEL=psxitarch` y `switch_root`.
- Rootfs (partición 2): `/etc/fstab` **vacío** (solo comentarios), servicios habilitados en `multi-user.target.wants`: `NetworkManager.service`, `remote-fs.target`; `display-manager`, `bluetooth` y `timesyncd` presentes; usuario `abc` en `/home`; `/boot` con `vmlinuz-linux-lts` e `initramfs-linux-lts.img` (kernel de Arch dentro del rootfs, no usado por el loader); no existe `/data`.
- No se auditó el resto del rootfs (paquetes, credenciales por defecto, servicios de red); queda como riesgo (R-?) en `RISK_REGISTER.md`.

---

## 3. Relación entre ambos repositorios

`X-F1REBALL-X/PS4-Linux` **consume** el payload de `ps4-linux/ps4-linux-loader` (o de su upstream real, `ArabPixel/ps4-linux-payloads`) como un binario ya compilado (`payload/linux-1024mb.elf`), y lo combina con un kernel y rootfs de otra procedencia. No comparten código fuente propio: la relación es de **integración de distribución**, no de fork. Cualquier decisión sobre el método de arranque (parámetros de `vram.txt`, firmware soportado, detección de southbridge) depende del código auditado en la Sección 1; cualquier decisión sobre el rootfs/kernel/instalación depende de la Sección 2.

## 4. Limitaciones de esta auditoría

- Historial: el del loader se clonó completo el 2026-10-15 (71 commits) para la búsqueda de §1.8; el de `X-F1REBALL-X/PS4-Linux` y los demás siguen sin revisarse más allá de HEAD.
- No se auditó `Al-Azif/ps4-skeleton`, `ArabPixel/ps4-linux-payloads` (el upstream real del loader), el kernel "Strawberry" de rmuxnet, Psxitarch, `better-initramfs`, el rootfs de Erkkola, los paquetes de Mesa de centi07/DionKill, ni GoldHEN. Son dependencias de hecho de este proyecto y deberían auditarse antes de depender de ellas en producción.
- Los `.elf` se inspeccionaron con `readelf`/`tools/elf_audit.py` (secciones, símbolos, `.rodata`, `fw_table`), no se desensamblaron; los blobs `kexec` embebidos no se compararon con una compilación. El `bzImage` solo se leyó en su cabecera de arranque.
- Los 20 offsets de `fw_offsets.h` no se validaron independientemente; el commit `9acef9f` marca los de 13.52 como "from 12.02" y el de `gpu_devid_is_9924` de 13.02 estuvo mal hasta `f70f43a` (2026-09-23). Coinciden con los del ELF distribuido, lo que prueba consistencia, no corrección.
