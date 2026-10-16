# Diseño de un flujo USB-only verificable

Política: [D-008](DECISION_LOG.md) — todo el material de arranque vive en el USB y no se escribe en el almacenamiento interno. Este documento convierte esa política en propiedades que se pueden comprobar, dice cuáles ya lo están y cuáles no, y fija la arquitectura recomendada. **Nada de lo descrito se ha probado en la consola.**

## 1. Propiedades que debe cumplir el flujo

| ID | Propiedad | Cómo se comprobaría |
|---|---|---|
| P1 | El loader solo lee archivos de arranque de una carpeta USB | Inspección del código o del binario del loader |
| P2 | Kernel e initramfs provienen de la **misma** carpeta (sin mezcla de orígenes) | Lógica del loader; modelo de pruebas |
| P3 | Kernel e initramfs son de la **misma release** (sin mezcla de versiones) | Catálogo de procedencia en la PC |
| P4 | Ningún componente (loader, initramfs, rootfs) escribe en el almacenamiento interno | Inspección estática + prueba de laboratorio |
| P5 | Antes de cada intento, `/data/linux/boot/` y `/user/system/boot/` no contienen archivos ajenos | Listado FTP de solo lectura (requiere GoldHEN ejecutándose: fase con ejecución autorizada) |

## 2. Qué demuestra la evidencia disponible (2026-10-15)

Revisiones fijadas: loader `ps4-linux/ps4-linux-loader@f70f43a60a973b3662daeb29c1f115d95408db93`; distribución `X-F1REBALL-X/PS4-Linux@66e21cb8c15f20189254e2608c6e9bf957eb8078`.

| Hecho | Nivel | Dónde |
|---|---|---|
| El loader busca cada archivo (`bzImage`, `initramfs.cpio.gz`, `bootargs.txt`, `vram.txt`) por separado en `/mnt/usb0/`, `/mnt/usb1/`, `/data/linux/boot/`, `/user/system/boot/`, en ese orden | CÓDIGO | `linux/main-aio.c` líneas 375-389 |
| Por tanto puede mezclar orígenes y cae al almacenamiento interno sin avisar (P1 y P2 **no** se cumplen en el código upstream) | CÓDIGO + modelo | `tools/loader_model.py`, `tests/test_loader_model.py::TestUpstreamTalCualEs` |
| Ningún commit del historial (71) añade escritura de archivos al payload: `O_CREAT`/`O_WRONLY` solo aparecen en el commit inicial `d55dd2c` (2022, una utilidad `main()` de `acpi.c` que no forma parte del payload) | CÓDIGO (historial) | `git log -S` sobre todo el historial |
| El ELF de la distribución (`linux-1024mb.elf`, sha256 `623c3b68…98f`) contiene exactamente las 4 familias de rutas de lectura, ninguna ruta de escritura, y su `fw_table` (20 filas) coincide fila a fila con `fw_offsets.h` de `f70f43a` | ESTÁTICO | `tools/elf_audit.py` |
| Los 9 ELF de distinto VRAM difieren solo en `.note.gnu.build-id` (20 B) y 4 B de `.text` (constante de VRAM) | ESTÁTICO | `tools/elf_audit.py --comparar` |
| El `init` del initramfs (better-initramfs 0.9.1) monta únicamente `LABEL=psxitarch` y no hay directorio `/hooks` | ESTÁTICO (texto leído) | `docs/UPSTREAM_CODE_MAP.md` §2.9 |
| `bin/install-psxitarch.sh` (script **manual**, no automático) reparticiona con `fdisk` el dispositivo `/dev/sd?` cuya partición 1 contenga `bzImage`, `initramfs.cpio.gz` y `psxitarch.tar.gz`; además copia `eap_hdd_key.bin` al rootfs | ESTÁTICO | idem |
| El `fstab` del rootfs está vacío y no existe `/etc/cryptmount` ni `/data` en la imagen publicada | ESTÁTICO (lectura con `debugfs`) | idem |

Lo que **no** demuestra (ver §4): que los releases del loader provengan de ese código, qué hace el kernel Linux con el disco interno en runtime, ni que algo de esto arranque.

## 3. Comparación de enfoques

| # | Enfoque | P1 | P2 | P3 | P4 | Costo / riesgo | Veredicto |
|---|---|---|---|---|---|---|---|
| A | **Configuración USB-only sin tocar el loader** (poner `bzImage` en la FAT del USB; no usar `/data/linux/boot/`) | ❌ no garantizado (fallback interno) | ❌ | ❌ | ◐ solo por código/estático | Muy bajo; es lo único posible con el binario publicado | Necesario, **insuficiente** |
| B | **Variante auditada del loader** que no usa rutas internas (`patches/loader-usb-only-f70f43a.patch`) | ✅ por construcción; **compilada y verificada estáticamente** en el binario (2026-10-16, `docs/LOADER_BUILD_REPRO.md`) | ✅ una sola carpeta | ❌ | ◐ | Compila en un contenedor sin red; el binario resultante sería de procedencia propia (GCC 13.3, no el de la distribución) y **sin ejecutar** | Única opción que vuelve P1/P2 propiedad del binario |
| C | **Verificación previa de todos los artefactos** y rechazo de faltantes (`tools/verify_boot_chain.py` + catálogo) | ◐ detecta archivos ausentes en la PC | ◐ solo en el USB, no en la consola | ✅ | ❌ | Bajo; no depende del loader | Necesario para P3, complementario |
| D | **Detección y rechazo de mezclas de versiones** (catálogo con `release`) | – | – | ✅ | – | Bajo | Incluido en C |

Ninguna opción cubre P5 por sí sola: solo se puede comprobar con acceso a la consola.

## 4. Bloqueo exacto: por qué USB-only todavía no se puede dar por demostrado

1. **El binario que se usaría no es el que auditamos.** El workflow de CI del loader solo sube artefactos de Actions; los *releases* se publican aparte. Actualización 2026-10-16: se **compiló** `f70f43a` (con y sin parche) en un contenedor sin red y es repetible en el entorno fijado, pero **no es bit a bit idéntico** al ELF de la distribución (compilador distinto: GCC 16.2.1 vs 13.3.0); es consistente en tabla de offsets, rutas y símbolos. Detalle y límites en `docs/LOADER_BUILD_REPRO.md`.
2. **El kernel Linux y el rootfs no están auditados.** Los kernels son binarios comunitarios (versiones reales 7.0.8 y 7.1.7 según su cabecera, D-009) y la imagen trae `systemd` y KDE (según su README; no auditados). Un `fstab` vacío no impide que un servicio monte el disco interno si Linux lo ve. Además `sys_kexec` añade en RAM al initramfs la clave `key/eap_hdd_key.bin` de la consola (`ps4-kexec-common/firmware.c`: `copy_eap_hdd_key`, usada en la línea 382), de modo que el sistema que arranca **tiene el material para descifrar el almacenamiento interno**. Que no lo use es una propiedad por demostrar, no un hecho.
3. **P5 requiere hardware.** Comprobar que `/data/linux/boot/` y `/user/system/boot/` están vacíos exige el servidor FTP de GoldHEN, es decir, ejecutar el exploit y el payload GoldHEN (D-010).
4. **La prueba final es de laboratorio.** Que el primer arranque no modifique el disco interno solo se demuestra con un procedimiento de laboratorio (hash/listado del interno antes y después, en una consola que Marcos autorice a ejecutar).

**Solución técnica concreta para desbloquear (estado 2026-10-16):**
1. ~~Compilar `f70f43a` sin parche en un entorno desechable y comparar con `linux-1024mb.elf`.~~ **Hecho, resultado parcial:** compila y es repetible en el entorno fijado, pero **no es idéntico bit a bit** (otro compilador); coincide en tabla de offsets, rutas y símbolos. Para cerrar la procedencia del binario de la distribución haría falta su compilador exacto (GCC 16.2.1-20260810) o el código fuente de los releases.
2. ~~Compilar con el parche y comprobar que no hay rutas internas.~~ **Hecho:** el ELF parcheado no contiene los bytes `/data/linux` ni `/user/system`, solo `/mnt/usb0/` y `/mnt/usb1/`; 4 funciones nuevas; `kexec.bin` idénticos a los originales.
3. Pendiente: P4 (ningún componente escribe en el interno en runtime) y P5 siguen exigiendo laboratorio con autorización.

## 5. Arquitectura recomendada (D-019)

Capas, de la PC a la consola; cada una es verificable por separado:

1. **Catálogo de procedencia** (`manifests/arranque-catalogo.json`): hashes, tamaños y *release* de kernels e initramfs. Es la fuente de P3.
2. **Construcción de la imagen** con `tools/build_usb_image.py`: genera un `.img` (nunca un dispositivo) con `bzImage` + `initramfs.cpio.gz` en la FAT, tras validar el formato de ambos. Ejemplo (el kernel concreto depende del southbridge, aún desconocido):
   ```bash
   python3 tools/build_usb_image.py --salida ~/ps4/usb-prueba.img --initramfs <initramfs.cpio.gz> \
       --kernel <bzImage> --rootfs-dir <directorio-rootfs> --p1-mib 512 --tamano-mib 12288 --dry-run
   ```
   Para un rootfs real con propietarios correctos, preparar el directorio y ejecutar bajo `fakeroot`.
3. **Edición de una copia de imagen ya hecha** con `tools/fat32_add_file.py` (p. ej. añadir `bzImage` a la FAT de la imagen publicada), siempre sobre una copia; después `fsck.vfat -n` sobre la partición.
4. **Verificación previa** con `tools/verify_boot_chain.py <carpeta-FAT-extraída> --catalogo manifests/arranque-catalogo.json --requerir estructura,integridad,formato` (y `--southbridge` solo cuando esté confirmado).
5. **Loader USB-only**: `patches/loader-usb-only-f70f43a.patch`. Aplica limpio con `git apply --check` y **compila** (`docs/LOADER_BUILD_REPRO.md`); el binario parcheado no contiene literales de rutas internas. No se ha ejecutado.
6. **Precondición de laboratorio (P5)** antes de cada intento: listado FTP de solo lectura de las dos rutas internas; abortar si tienen contenido ajeno.

**Por qué esta combinación:** A y C/D se pueden hacer ya y son reversibles; B es la única que vuelve P1/P2 una propiedad del binario, pero depende de un entorno de compilación y de una revisión que todavía no existen. Se recomienda A+C+D hoy y B en cuanto §4.1 esté resuelto; sin B, el sistema **no** es USB-only por construcción, solo por configuración y disciplina de laboratorio.

## 6. Cómo revisar y probar el parche sin ejecutar nada en la consola

```bash
git clone https://github.com/ps4-linux/ps4-linux-loader.git && cd ps4-linux-loader
git checkout f70f43a60a973b3662daeb29c1f115d95408db93
git apply --check <repo>/patches/loader-usb-only-f70f43a.patch      # debe aplicar sin fuzz
git apply <repo>/patches/loader-usb-only-f70f43a.patch
cd linux && gcc -fsyntax-only -Wall -Wextra -isystem ../freebsd-headers -nostdinc -ffreestanding -I. \
    -DVRAM_MB_DEFAULT=1024 -DVRAM_MB_MIN=32 -DVRAM_MB_MAX=4096 main-aio.c   # solo sintaxis (hecho: mismas advertencias que el original)
python3 -m unittest tests.test_loader_model                          # lógica de selección y contenido del parche
```
La compilación completa (`make`) en contenedor sin red y la comparación estática de ELF se hicieron el 2026-10-16: `scripts/build_loader_isolated.sh`, `docs/LOADER_BUILD_REPRO.md`.

### Limitaciones del parche y del modelo
- Es un parche de **diseño**: no se ha compilado a ELF ni ejecutado. `tools/loader_model.py` modela el algoritmo; no es el loader.
- No corrige otros defectos observados en `main-aio.c` que quedan fuera del encargo: `read_file` trata el valor de retorno de `read` como `unsigned` (un error de lectura no se detecta), `mmap` sin comprobar y `get_sb_id()` devuelve `-1` sin manejo posterior (la familia de southbridge pasaría a `0xF`). Recomendable reportarlos aguas arriba.
- Si falta `bootargs.txt`/`vram.txt` en la carpeta USB elegida, se usan los valores por defecto del loader (1024 MB); no se busca en ningún otro lugar.

## 7. Qué no cubre este documento
Seguridad del payload GoldHEN, red/PSN (D-012/D-016), elección del kernel (depende del southbridge, `COMPATIBILITY_MATRIX.md` §7) ni la política de licencias (`LICENSE_POLICY.md`).

## 8. Diagnóstico de faltantes para la imagen virtual de esta consola (2026-10-16)

**No se construyó ninguna imagen**, a propósito: no se simula una construcción exitosa. Qué falta, exactamente:

| # | Falta | Estado | Cómo se desbloquea |
|---|---|---|---|
| 1 | **Kernel elegido.** Hay dos candidatos locales (Baikal 7.0.8 y Belize 7.1.7) y el southbridge de la CUH-2115B es desconocido; no hay ningún reporte del modelo exacto (`COMPATIBILITY_MATRIX.md` §7.4) | BLOQUEANTE | Southbridge confirmado con evidencia fiable; hoy solo se obtiene ejecutando código en la consola (no autorizado) |
| 2 | **Rootfs como entrada.** No existe como archivo/tarball/directorio; solo dentro de p2 de la imagen publicada (ext4, `e2fsck -fn` OK) | No bloqueante si se parte de la imagen publicada | Ver ruta A |
| 3 | `bzImage` dentro de la FAT del USB: la imagen publicada trae `bzImage.belize` (renombrado), no `bzImage` | Resuelto por herramienta (`fat32_add_file.py`), pendiente del punto 1 | – |

**Ruta A (recomendada cuando el punto 1 esté resuelto; no requiere root ni extraer el rootfs):** copiar `psxitarch-usb.img` (8,9 GB, hash `badd4873…0143`) a un directorio de trabajo con ≥ 9 GB libres → `python3 tools/fat32_add_file.py <copia> --particion 1 --nombre bzImage --archivo <kernel elegido>` → `fsck.vfat -n` sobre p1, `e2fsck -fn <copia>?offset=1050624*512` sobre p2 y `tools/verify_boot_chain.py` sobre la FAT extraída con `--catalogo manifests/arranque-catalogo.json --southbridge <confirmado>` → registrar hashes. Mecánica ya ensayada sobre una copia de p1 (2026-10-15); no se repite con un kernel porque elegirlo sería inventar compatibilidad.
**Ruta B:** `tools/build_usb_image.py` exige `--rootfs-dir` con propietarios correctos (root:root). Extraer p2 con `debugfs rdump` no conserva propietarios; haría falta `fakeroot` o root. Más costosa y sin ventaja mientras el rootfs publicado sirva.

Verificación ya hecha sobre la imagen publicada (solo lectura): MBR válido, p1 FAT32 `fsck.vfat -n` rc 0, p2 ext4 `e2fsck -fn` rc 0 (249 277 de 516 096 inodos usados). Eso valida los sistemas de archivos, no el contenido del rootfs ni el arranque.

