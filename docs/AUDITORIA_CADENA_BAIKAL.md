# Auditoría del kernel Baikal 7.0.8 y de la cadena de arranque (CUH-2115B, FW 13.52)

Fecha: 2026-10-16. **Alcance: estático y host-side.** Esta sesión no ejecutó nada en la consola, no escribió medios y no tocó el almacenamiento interno. Todo lo que dice "observado" sobre la consola proviene del operador (`lab-logs/LAB-001-southbridge.md`), sin captura archivada ni hash.

Niveles: **HECHO** (comprobado por nosotros sobre el archivo, con el comando indicado) · **CÓDIGO** (lectura de código upstream en revisión fija) · **TERCEROS** (lo afirma otro) · **OPERADOR** (lo informa Marcos, sin evidencia archivada) · **INFERENCIA** · **DESCONOCIDO**.

## 1. Conclusión

1. El kernel `bzImage-baikal-7.0.8` **existe localmente, es íntegro y es un kernel PS4 con soporte Baikal compilado**: Linux 7.0.8, `CONFIG_X86_PS4_BAIKAL=y` (HECHO, §3.1). El kernel Belize 7.1.7 **no** tiene ese símbolo.
2. El southbridge observado por el operador (Baikal B1, `0x30201`) **es coherente** con ese kernel y con una de las dos variantes que la wiki asigna al CUH-2115B. Es un dato OPERADOR: falta archivar la captura para tratarlo como evidencia de laboratorio.
3. **Eso no demuestra compatibilidad.** No hay reporte de `bzImage-baikal-7.0.8` en una CUH-2115B ni con el loader v25.1 en esta consola; el kernel se compiló en una máquina personal, sin fuentes enlazadas ni compilación reproducible; la cadena completa (kernel + initramfs + rootfs + payload) nunca se probó junta en esta unidad.
4. Estado del kernel: **candidato prioritario, no seleccionado, no autorizado para arrancar.** Un intento físico solo puede salir de la secuencia de `PLAN_VALIDACION_BAIKAL.md`, con autorización específica de Marcos.
5. **Contradicciones con D-008 en la documentación o el código del laboratorio: ninguna encontrada** (§5). Las propiedades de aislamiento del flujo siguen sin demostrarse y hay un riesgo concreto nuevo: el rootfs trae `udisks2`/Dolphin y el kernel trae UFS, SATA y dm-crypt integrados (§5.3).

## 2. Tabla de artefactos

Orígenes: todos del release `v1.0` / commit `66e21cb` de `X-F1REBALL-X/PS4-Linux` salvo lo indicado. Hashes recalculados localmente (`manifests/inventario-local-2026-10-16.json`).

| Artefacto | SHA-256 | Tamaño | Versión real (HECHO) | Licencia | Estado de verificación |
|---|---|---|---|---|---|
| `bzImage-baikal-7.0.8` | `46c835f762e7b0b5400ea762b8daa1bcec638a1b769c7ec0905137bc565b1ba8` | 13 841 408 B | `7.0.8-Strawberry-FullLTO-Baikal-+`, compilado 2026-09-08 por `pask@pask-MacBookPro16-1` con clang 21.1.8 (Ubuntu); carga zstd, 43 755 952 B descomprimidos = pie declarado | GPL-2.0 (kernel); **sin fuente enlazada** | Estructura, formato, catálogo, config embebida: OK. Procedencia: BAJA. Hardware: sin prueba |
| Config embebida de ese kernel (extraída con `tools/kernel_inspect.py`) | `ca48fc48a20cf9ba90ace56898e4787b2d8e557b6a266b869e4a18e0b3716835` | 5 068 líneas | `# Linux/x86_64 7.0.8 Kernel Configuration` | – | Derivada del binario; no hay `.config` publicado para esta variante |
| `bzImage-belize-7.1.7` (contraste) | `072113898347932c34888cfdc7556953ee27233c0727cc45f419a57119242480` | 20 415 488 B | `7.1.7-Strawberry-General-FullLTO+`, compilado 2026-08-25 en un runner de GitHub Actions (`runner@runnervmgx7h7`), clang 18.1.3 | GPL-2.0 | Su config embebida tiene el mismo SHA-256 (`a159bc5a…`) que el `.config` publicado: **el binario corresponde a su config publicada** (no ocurre para Baikal: no hay config publicada) |
| `initramfs.cpio.gz` | `3f373bd6c469e490eaf4e5cf4d2e8ed77cf7bb91449b6a18da6a6529d479169b` | 4 102 011 B | better-initramfs v0.9.1 (PSXITA Team) | BSD-3 (cabecera de `init`); resto sin declarar | gzip+cpio íntegros, 48 entradas; scripts leídos |
| Imagen `psxitarch-usb.img` (rootfs en p2) | `badd487308899edeaf43eafe67a5842b609b7ef809e5101bf77eb2762a1e0143` | 8 871 489 536 B | Arch Linux + KDE 6.5.5; `linux-lts 6.12.66-1` propio en `/boot`; `mesa-ps4 25.3.3` | Mixta (Arch + paquetes) | `fsck.vfat -n` y `e2fsck -fn` rc 0 (solo lectura). Contenido del rootfs sin auditar |
| Payload `linux-1024mb.elf` (distribución) | `623c3b68592437b612ede22a4fc1a6f1eef6b17c4b16a1270100ece04cb3c98f` | 320 936 B | GCC 16.2.1 20260810; `fw_table` 20/20 = `fw_offsets.h@f70f43a` (incluye 13.52) | sin licencia declarada (loader); `ps4-kexec-common` BSD-2 | Estático OK; **no reproducido bit a bit** |
| Payloads de compilación propia (no distribuidos) | original `86ed667b…`, parcheado USB-only `a0d1eadb…` (`linux-1024mb.elf`) | 325 048 B / 325 192 B | GCC 13.3.0 | ídem | Compilan y son repetibles; **no ejecutados**; no son el binario de la distribución |
| `goldhen.bin` (raw13g) | `df3f27c1b35bc7c40e3a08caab948930914dc7d0301a73b68945cf6ffe40ea12` | 293 120 B | se autodeclara `v2.4b18.12` | sin licencia identificable | Análisis estático parcial; **sin fuente** |

## 3. Auditoría de la cadena como un todo

### 3.1 Kernel ↔ southbridge (HECHO + CÓDIGO)
- Config del Baikal 7.0.8: `CONFIG_X86_PS4=y`, `CONFIG_X86_PS4_BAIKAL=y`, `CONFIG_PS4_DMI_SPOOF=y`, `CONFIG_USB_XHCI_AEOLIA=y`. Config del Belize 7.1.7: `X86_PS4=y` y **sin** `X86_PS4_BAIKAL` (`tools/kernel_inspect.py`).
- El loader pasa la familia de southbridge a `kexec`; con `sb_id == SB_BAIKAL` desactiva los MSI de las 8 funciones PCI de Baikal, y en otro caso aplica la rama Aeolia/Belize (`ps4-kexec-common/linux_boot.c` líneas 357-375 @ `f70f43a`). Un kernel y una rama del loader del mismo tipo es lo consistente; **una mezcla (rama Belize + kernel Baikal) no se probó**.
- Veredicto: coherente para Baikal. No prueba que el kernel arranque en B1 concretamente.

### 3.2 Kernel ↔ initramfs (HECHO)
El kernel trae integrados `BLK_DEV_INITRD`, `RD_GZIP`, `DEVTMPFS`, `USB_STORAGE`, `USB_XHCI_HCD`, `VFAT_FS`, `EXT4_FS`; el initramfs es gzip+cpio newc y su `init` monta `LABEL=psxitarch` tras `sleep 10`. Compatibles por construcción. El kernel es casi monolítico (solo 3 módulos `=m`, algoritmos TCP), por lo que **no importa** que `/lib/modules` del rootfs solo tenga `6.12.66-1-lts` (hallazgo: ni 7.0.8 ni 7.1.7 tienen directorio de módulos allí).

### 3.3 Kernel ↔ rootfs (parcial)
- El rootfs es el de Arch con su propio `linux-lts`, que **no se usa**: el loader arranca el `bzImage` del USB.
- Userland gráfico: `mesa-ps4 25.3.3` contra un kernel 7.0.8 con `DRM_AMDGPU=y`, `DRM_AMDGPU_CIK=y` y `DRM_RADEON` no establecido (amdgpu es el único driver). La interacción Mesa↔DRM de este kernel **no está probada**; el firmware de la GPU viene integrado en el kernel (`EXTRA_FIRMWARE` incluye `amdgpu/liverpool_*`), en el initramfs y lo extrae `kexec` de la consola.
- Wi‑Fi/Bluetooth: el kernel integra Marvell (`MWIFIEX_SDIO`, `BT_MRVL`) y firmware MediaTek; qué chip tiene esta consola es DESCONOCIDO.

### 3.4 Loader ↔ payload ↔ firmware 13.52 (CÓDIGO + HECHO)
`fw_table` del ELF distribuido tiene la fila 13.52 (offsets "from 12.02" según el commit `9acef9f`); la fila de 13.02 tuvo un offset erróneo hasta `f70f43a`. Coincidir con el código no prueba que los offsets sean correctos en un 13.52 real; los reportes de terceros (issue #10 en CUH-2208B) son la única evidencia de que funcionan, con otra consola y otro kernel.

### 3.5 Payload de la distribución vs. payload propio
El de la distribución conserva el fallback a rutas internas; el parcheado no, pero es una compilación nuestra (GCC 13.3, no ejecutada). **Decisión pendiente** (§ plan, etapa V0): usar el de la distribución (procedencia ajena, comportamiento upstream conocido) con la salvaguarda P5, o el parcheado (propio, sin historial de uso).

### 3.7 GoldHEN reportado v2.2.3 (DESCONOCIDO)
El operador reporta "GoldHEN v2.2.3" en la pantalla *About*. El binario de raw13g se autodeclara `v2.4b18.12` y ningún GoldHEN oficial cubre 13.52. La característica "Southbridge Info" es documentada desde la 2.2.3, lo que hace coherente la lectura del southbridge, pero **no explica la cifra de versión**. Pendiente: capturar la pantalla *About* y calcular el hash del archivo realmente cargado.

### 3.6 Mezcla de releases (HECHO)
Kernel, initramfs, imagen y payload provienen del mismo release de la misma distribución (hashes = `SHA256SUMS`). Aun así, los dos kernels tienen **constructores distintos** (CI vs máquina personal) y el tag `v1.0` se movió tras publicarse (D-D2): se fija por commit y hash. No se detectó mezcla de releases (`verify_boot_chain` con catálogo y `--southbridge baikal`: estructura, integridad, formato y compatibilidad en OK; con `--southbridge belize`: FALLO).

## 4. Qué demuestra la evidencia para Baikal B1 y qué sigue desconocido

| Pregunta | Estado |
|---|---|
| ¿El kernel tiene soporte Baikal compilado? | **Sí** (HECHO) |
| ¿El southbridge de esta consola es Baikal B1? | **OPERADOR** (0x30201); coherente con la wiki; sin captura archivada |
| ¿El binario es el que se compiló de unas fuentes conocidas? | **Desconocido**: sin fuente ni build reproducible; máquina personal |
| ¿Arranca en CUH-2115B con FW 13.52? | **Desconocido** (sin prueba; `feeRnt` declara CUH-2115B con un kernel Baikal **5.4.247**, otro binario y firmware desconocido) |
| ¿Funciona con el loader v25.1/payload 1024 MB en B1? | **Desconocido**. Evidencia de terceros en Baikal 13.52: CUH-2208B con kernel 5.4.247 (issue #10) y CUH-2116A con este kernel (README de la distribución, sin logs) |
| ¿Hay reportes negativos de Baikal + 7.x? | No encontrados; `feeRnt` cita que los Baikal "dejaron de funcionar" más allá de 5.4 y un 6.15.4 con LED blanco (otro binario) |
| ¿Qué etapa se demostraría con un LED blanco? | Ninguna (`RECOVERY_PLAN.md` §4) |

## 5. Auditoría USB-only (D-008)

### 5.1 Documentación y código del laboratorio
Se buscaron `/data/linux`, `/user/system`, "fallback" y "copia" en `docs/`, `README.md`, `scripts/`, `tools/` y `patches/`: **todas las menciones son prohibitivas, descriptivas del comportamiento upstream o del parche**; ninguna instruye usar el almacenamiento interno. No hay contradicción con D-008. Matiz: `docs/USB_IMAGE_BUILD_PREFLIGHT.md` (rama de ChatGPT) describe el flujo upstream con `--spare-kernel`, ya marcado como no conforme con D-008.

### 5.2 Lecturas alternativas al USB por componente
| Componente | Lectura/escritura alternativa | Evidencia | Mitigación |
|---|---|---|---|
| Loader upstream (y ELF distribuido) | Busca `bzImage`, `initramfs`, `bootargs.txt`, `vram.txt` en `/mnt/usb0`, `usb1`, `/data/linux/boot`, `/user/system/boot`, por separado | CÓDIGO + ELF | Parche USB-only (compilado, no ejecutado); P5: listado FTP de solo lectura previo |
| Loader | No escribe archivos | HECHO (historial, ELF, grafo de llamadas) | – |
| Kernel | Puede acceder al disco interno: `SATA_AHCI`, `BLK_DEV_SD`, `UFS_FS`, `DM_CRYPT`, `CRYPTO_XTS` integrados | HECHO (config) | No es un defecto; implica que la **protección es de userland**, no del kernel |
| Initramfs | `/key/eap_hdd_key.bin` (clave del disco de la consola) existe en RAM por `kexec`; `install-psxitarch.sh` (manual) reparticiona un `/dev/sd?`; `mount LABEL=psxitarch` busca por etiqueta en cualquier dispositivo | HECHO (scripts) | No ejecutar el instalador; verificar que ninguna partición interna se llame `psxitarch` (improbable) |
| Rootfs | `udisks2` + Dolphin/`kio` pueden montar particiones de bloque con un clic; `fstab` vacío; sin `/etc/cryptmount` | HECHO (`debugfs`) | **Riesgo nuevo R-21:** no abrir/montar dispositivos desde la sesión KDE; usar la etapa de *rescue shell* (V3) antes de iniciar el escritorio |

### 5.3 Conclusión
El flujo USB-only **no es una propiedad demostrada**: depende de (a) el payload usado, (b) la disciplina de userland y (c) la prueba de laboratorio del disco interno antes/después. Ninguna lectura alternativa ocurre "sola" según el código revisado, pero el kernel y el rootfs **sí permiten** que se produzca por acción humana.

## 6. Riesgos
R-17 (binarios no reproducibles), R-18 (clave en RAM/USB), R-20 (avisos RWX), y nuevos: **R-21** montaje accidental de particiones internas desde el escritorio; **R-22** kernel Baikal compilado en máquina personal sin fuente (integridad de la cadena de suministro); **R-23** versión de GoldHEN reportada inconsistente con el binario conocido; **R-24** offsets de 13.52 derivados de 12.02 sin validación independiente.

## 7. Licencias y redistribución
Kernel y derivados: GPL-2.0 (obliga a ofrecer fuentes a quien redistribuya; la distribución no las enlaza). `X-F1REBALL-X/PS4-Linux`: GPL-3.0 para guía/scripts (archivo UTF-16). `ps4-kexec-common`: BSD-2. better-initramfs: BSD-3. Rootfs Arch: licencias por paquete. Loader y GoldHEN: sin licencia declarada. **Este repositorio no redistribuye ningún binario** (D-004): solo hashes, tablas y parches propios.

## 8. Comandos ejecutados (todos de solo lectura)
`python3 tools/kernel_inspect.py <bzImage>` (ambos kernels; rc 0; extracción de config == extracción manual; Belize == `.config` publicado) · `python3 tools/verify_boot_chain.py <copia de kernel+initramfs> --catalogo manifests/arranque-catalogo.json --southbridge baikal|belize --requerir estructura,integridad,formato,compatibilidad` (baikal rc 0; belize rc 1 por compatibilidad) · `debugfs -R "ls /lib/modules"` y `ls /var/lib/pacman/local` sobre p2 de la imagen · `grep` sobre la config embebida · API de GitHub (licencias y releases). Sin ejecución de ningún binario del proyecto.
