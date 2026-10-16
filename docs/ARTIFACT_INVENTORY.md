# Inventario y trazabilidad de artefactos

Fecha de la consulta: 2026-10-15. Nada de lo listado se incorpora al repositorio (D-004); los archivos binarios viven fuera del árbol (`PS4-Linux-artefactos/`) y aquí solo se registran hashes, tamaños y procedencia. Una coincidencia de hash prueba **igualdad con el valor publicado**; no prueba que el publicador sea quien dice ser ni que el contenido sea seguro.

**Niveles de confianza** — `ALTA`: fuente primaria del autor, revisión fija y contenido leído/contrastado por nosotros; `MEDIA`: fuente primaria identificable pero no contrastada de forma independiente o no reproducida; `BAJA`: binario comunitario de procedencia incompleta o no reproducible; `SIN DATOS`: no se obtuvo el artefacto.

**Hash `local`** = calculado por nosotros sobre el archivo descargado. **Hash `API`** = digest que GitHub publica para el asset (no lo calculamos sobre un archivo que no tenemos). **Hash `SHA256SUMS`** = lista que publica el mismo autor del release (misma fuente que el binario: no es independiente).

## 1. Fuentes oficiales (primarias, código legible)

| ID | Artefacto y función | Origen | Revisión | Licencia | Hash / tamaño | Plataforma / config | Dependencias | Procedencia | Confianza | Verificación |
|---|---|---|---|---|---|---|---|---|---|---|
| A-01 | Código fuente del **loader** (payload kexec `main-aio.c`, `fw_detect.c`, `ps4-kexec-common/`) | https://github.com/ps4-linux/ps4-linux-loader | `master` @ `f70f43a60a973b3662daeb29c1f115d95408db93` (2026-09-23) | Sin licencia en la raíz (API: `null`); `linux/ps4-kexec-common/LICENSE` = BSD de 2 cláusulas (marcan, shuffle2); `lib/` y headers FreeBSD con licencias propias | commit SHA-1 fijado; 71 commits clonados | FW 5.05-13.52; Aeolia/Belize/Belize2/Baikal (detección en runtime) | `gcc`, `yasm`, `objcopy`, `ld`, `python3` + **red** (`lib/syscalls.py`), headers FreeBSD vendorizados | Repositorio del mantenedor (ArabPixel/rmuxnet/colaboradores); nombre anterior `ArabPixel/ps4-linux-payloads` | ALTA (el código) | Leído y auditado (`UPSTREAM_CODE_MAP.md`). Compilación **no** reproducida (§4). |
| A-02 | **Guía/distribución**: README, scripts de imagen | https://github.com/X-F1REBALL-X/PS4-Linux | `main` @ `66e21cb8c15f20189254e2608c6e9bf957eb8078` (2026-10-04) | GPL-3.0 sobre guía y scripts; kernels GPL-2.0; el resto "mantiene sus licencias" (NOTICE) | `tools/build-img.sh` sha256 `3a9bfd67…2a2` (2147 B), `tools/write-img.ps1` `893dc5ac…0fe4868` (4808 B) — locales y en `SHA256SUMS` | Linux/WSL (bash); Windows (PowerShell) | `sfdisk`, `losetup`, `mkfs.*`, `7z` | Repositorio de 1 autor, creado 2026-09-28, 7 commits | MEDIA | Scripts leídos y revisados; hashes locales = `SHA256SUMS`. |
| A-03 | **GoldHEN oficial** 2.4b18 (jailbreak/FTP/BinLoader) | https://github.com/GoldHEN/GoldHEN/releases/tag/2.4b18 | tag `2.4b18` (2024-10-28) | Sin licencia declarada (API `null`); **código fuente privado** (README) | `GoldHEN_v2.4b18.7z` local sha256 `d0c84c79…fca38d` (258 065 B); `goldhen.bin` extraído `eb9fee5e…9525a3` (260 160 B) | FW hasta 11.00 (lista del release); **no** 13.52 | – | Release del autor (SiSTR0) | MEDIA (identidad del autor no verificada criptográficamente) | Descargado y extraído en carpeta aislada; solo referencia de comparación (`payload_static`). No se ejecutó. |
| A-04 | Exploit web y host **raw13g** (JS, `goldhen.bin`, `payload2.bin`, parches 1302/1350/1352) | https://github.com/raw13g/raw13g.github.io | `9ba2f07` (2026-09-26) | MIT (código del repo; terceros mantienen la suya) | `goldhen.bin` `df3f27c1b35bc7c40e3a08caab948930914dc7d0301a73b68945cf6ffe40ea12` (293 120 B); resto en `manifests/raw13g-9ba2f07.json` | PS4 13.02/13.04/13.50/13.52 (navegador) | – | Repo de `raw13g`; disputa de crédito pública sin resolver (D-F) | BAJA para el binario nativo; MEDIA para el JS | JS leído; `goldhen.bin` analizado estáticamente (`EXPLOIT_AUDIT_13.52.md`). **No ejecutado.** |

## 2. Binarios comunitarios, de procedencia incompleta

| ID | Artefacto y función | Origen | Licencia | Hash / tamaño | Plataforma / config destino | Evidencia de procedencia | Confianza | Verificación |
|---|---|---|---|---|---|---|---|---|
| B-01 | Releases del **loader** (`ps4-linux-loader-v25.1.zip` y anteriores) | GitHub Releases de A-01 | ver A-01 | v25.1 `7ee03018982cc25a6a6fcb44221b004406168cb33261dd62d82560144316da74` (363 871 B), v25 `fe64a196…e34` (344 640 B); **API** | FW 5.05-13.52, todos los southbridges | El workflow de CI **no** crea releases; sin build reproducible | BAJA | **No descargado.** Contenido interno sin comparar. |
| B-02 | Payloads ELF del loader (9 tamaños de VRAM) incluidos en A-02 y en su release `v1.0` | A-02 `payload/` y release | ver A-01 | `linux-1024mb.elf` `623c3b68…98f` (320 936 B); los 9 con hash local = `SHA256SUMS` (ver `manifests/distro-66e21cb.json`) | Cualquier FW/southbridge soportado | ELF sin strip, `GCC 16.2.1 20260810`; `fw_table` = `fw_offsets.h@f70f43a` (20/20); rutas solo de lectura (`elf_audit`); los 9 difieren en 21-24 B (build-id + VRAM) | MEDIA (coherente con A-01) / BAJA (no reproducido) | Estático hecho; **compilación reproducible pendiente** (§4). |
| B-03 | Kernel Linux **Baikal** `bzImage-baikal-7.0.8` | A-02 `boot/baikal/bzImage` y release | GPL-2.0 (NOTICE) | `46c835f762e7b0b5400ea762b8daa1bcec638a1b769c7ec0905137bc565b1ba8` (13 841 408 B); local = API = `SHA256SUMS` | Southbridge Baikal; cabecera: Linux `7.0.8-Strawberry-FullLTO-Baikal-+`, compilado 2026-09-08 | Atribuido a rmuxnet ("Strawberry"); sin fuente ni `.config` de esta variante; sin build reproducible | BAJA | Cabecera x86 válida y versión leída (`verify_boot_chain`); **arranque no probado**. |
| B-04 | Kernel Linux **Belize/Aeolia** `bzImage-belize-7.1.7` | idem | GPL-2.0 | `072113898347932c34888cfdc7556953ee27233c0727cc45f419a57119242480` (20 415 488 B); local = API = `SHA256SUMS` | Southbridge Belize (Aeolia: "debería", sin prueba); Linux `7.1.7-Strawberry-General-FullLTO+`, compilado 2026-08-25 | idem; `.config` publicado (`a159bc5a…f5c8`, 145 676 B) | BAJA | idem. |
| B-05 | **Initramfs** `initramfs.cpio.gz` (better-initramfs 0.9.1 adaptado, Psxitarch) | idem | BSD-3 (better-initramfs, cabecera del `init`); resto sin declarar | `3f373bd6c469e490eaf4e5cf4d2e8ed77cf7bb91449b6a18da6a6529d479169b` (4 102 011 B); local = API = `SHA256SUMS` | Monta `LABEL=psxitarch`; firmware AMD/Marvell incluido | Atribuido a PSXITA Team; scripts leídos (`UPSTREAM_CODE_MAP.md` §2.9); contiene binarios (busybox, dropbear, cryptsetup, lvm) y firmware sin auditar | MEDIA (scripts) / BAJA (binarios) | gzip/cpio íntegros (48 entradas, `verify_boot_chain`); sin ejecución. |
| B-06 | **Imagen USB / rootfs** Arch Linux + KDE (`psxitarch-usb.img.xz`, 2 partes) | release `v1.0` de A-02 | Mixta (Arch + paquetes; "mantienen sus licencias") | `part1` `4063f338…bf588` y `part2` `e62aa04d…2df2d` (1 088 315 226 B c/u; local = API = `SHA256SUMS`); `.img.xz` `153cec02…89b3`; `.img` `badd4873…0143` (8 871 489 536 B) | p1 FAT32 512 MiB (`initramfs.cpio.gz`, `bzImage.belize`); p2 ext4 `psxitarch` ~7,76 GiB | Rootfs "Arch Linux KDE v1.1.1" (Erkkola); paquetes Mesa de centi07/DionKill; sin firma | BAJA | Leído sin montar (`inspect_image`, `debugfs`, `7z`): `fstab` vacío, sin `/etc/cryptmount`; **rootfs sin auditar** (paquetes, usuarios, servicios). |
| B-07 | GoldHEN "2.4b18.12" servido por raw13g | A-04 `goldhen.bin` | Sin licencia identificable | `df3f27c1…ea12` | FW 13.52 | El cuerpo se declara `v2.4b18.12`; **no existe en el repositorio oficial**; ~75 % de cadenas comunes con 2.4b18 | BAJA | Estático parcial; **sin ejecución autorizada**. |

## 3. Herramientas auxiliares y dependencias de compilación

| ID | Qué | Para qué | Estado / procedencia |
|---|---|---|---|
| T-01 | `gcc`, `objcopy`, `ld` (binutils) | Compilar el loader | Instalados localmente (sistema); versión del ELF de la distribución: GCC 16.2.1 20260810 (otra) |
| T-02 | `yasm` 1.3.0 | Ensamblar `lib/crt.asm` y `syscalls.asm` | Solo dentro del contenedor de compilación (`build-env/loader/Dockerfile`, paquete Ubuntu 24.04 `yasm 1.3.0-4`); **no** instalado en el host; sin evaluar con `dependency-auditor` (entorno desechable) |
| T-03 | `lib/syscalls.py` | Genera `syscalls.asm` desde `syscalls.master` (FreeBSD stable/9) y una página archivada de psdevwiki | Entrada remota sin integridad en origen; **no se usó**: `syscalls.asm` está versionado y se comprobó byte-idéntico al regenerarlo sin red (`docs/LOADER_BUILD_REPRO.md` §1) |
| T-04 | `freebsd-headers/` (en A-01) | Headers FreeBSD 9 vendorizados | Licencias BSD de FreeBSD; sin auditar |
| T-05 | `Al-Azif/ps4-skeleton` | Origen (MIT) del método de detección de FW | Mencionado en `fw_detect.c`; no auditado |
| T-06 | Herramientas del laboratorio (`sfdisk`, `mkfs.vfat`, `mkfs.ext4`, `fsck.vfat`, `e2fsck`, `debugfs`, `7z`, `fakeroot`, `shellcheck`) | Construir/verificar imágenes y revisar scripts | Instaladas del sistema; los tests se omiten si faltan |
| T-07 | Herramientas propias (`tools/*.py`, `patches/`) | Verificación, análisis estático, construcción de imágenes | Este repositorio; sin dependencias de terceros más allá de la biblioteca estándar de Python |

## 4. No obtenidos o no auditados (registro explícito, nada se simula)

| Artefacto | Por qué importa | Estado |
|---|---|---|
| `psxitarch.tar.xz`, `kernel.zip`, `payloads.zip`, `tools.zip` descritos en el README de A-02 | El README los describe; el release `v1.0` publica otros assets (D-D) | **No existen en el release consultado**; no se obtuvieron |
| Código fuente y `.config` del kernel "Strawberry" (rmuxnet) 7.0.8-Baikal y 7.1.7 | Sin él no hay reproducibilidad ni auditoría del kernel | Repositorio **no identificado** |
| Kernel "5.4.247 Baikal build" del issue #10 | Es la configuración que probó CUH-2208B | **Sin enlace** en el issue; no existe como artefacto trazable |
| Rootfs "Arch Linux KDE v1.1.1" original (Erkkola), paquetes Mesa/video (centi07, DionKill), Psxitarch v3 | Componentes del rootfs/initramfs | No obtenidos; licencias sin resolver (Q-004) |
| Zips de los *releases* del loader (B-01) | Binarios que realmente se usan | Hash `API` anotado; **no descargados ni comparados** |
| Compilación bit a bit idéntica a la de la distribución | Ligaría B-01/B-02 con A-01 | **No lograda**: compila y es determinista (GCC 13.3), pero el compilador de la distribución fue GCC 16.2.1-20260810; coherente, no idéntica |
| Transcripción/descripción del video | Contexto del encargo | **No obtenida** (solo el título) |

### Reproducir el loader (hecho en parte, 2026-10-16)
`scripts/build_loader_isolated.sh` + `build-env/loader/Dockerfile` compilan `f70f43a` en un contenedor sin red; resultados y hashes en `docs/LOADER_BUILD_REPRO.md` y `manifests/loader-f70f43a-build.json`. Para una identidad bit a bit con B-02 faltaría el compilador exacto (GCC 16.2.1 20260810) o el código fuente de los releases.

## 5. Estado resumido de la procedencia

| Componente | ¿Procedencia verificada? |
|---|---|
| Código del loader (A-01) | Sí, a nivel de código fuente en una revisión fija |
| Scripts de la distribución (A-02) | Sí (leídos, hash = lista del autor) |
| GoldHEN oficial 2.4b18 (A-03) | Parcial (release del autor; sin firma) |
| ELF del loader (B-02) | **Parcial**: coherentes con A-01 (tabla, rutas, símbolos; recompilados de A-01 con otro compilador); no idénticos bit a bit |
| Kernels, initramfs, rootfs (B-03…B-06) | **No**: hash = valores publicados por el mismo autor; sin fuente ni build reproducible |
| `goldhen.bin` de raw13g (A-04/B-07) | **No**: sin fuente; identificado solo estáticamente |
| Releases del loader (B-01) | **No**: no descargados |
