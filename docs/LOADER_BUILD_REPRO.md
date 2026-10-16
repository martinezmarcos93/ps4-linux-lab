# Compilación aislada del loader (original y con parche USB-only)

Fecha: 2026-10-16. Autorización: Marcos autorizó compilar el loader original y el parcheado en un entorno aislado; **no** autorizó ejecutar el loader, payloads o exploits, arrancar Linux en la PS4, escribir pendrives ni tocar el almacenamiento interno. **Ningún ELF resultante se ejecutó.** Registro máquina: `manifests/loader-f70f43a-build.json`; hashes de fuentes: `manifests/loader-f70f43a-sources.sha256`; logs y respuestas HTTP: `docs/evidence/loader-build/`.

## 1. Revisión previa de la cadena de construcción (antes de compilar)

Revisión fijada: `ps4-linux/ps4-linux-loader@f70f43a60a973b3662daeb29c1f115d95408db93` (tree `dd06961bd7cd893581fd4ad222253deacc6c4945`, 2123 archivos versionados; `git fsck` limpio).

| Pregunta | Respuesta |
|---|---|
| ¿Qué URLs se consultan? | Solo `lib/syscalls.py`: (1) `https://raw.githubusercontent.com/freebsd/freebsd/stable/9/sys/kern/syscalls.master`; (2) `http://web.archive.org/web/20210124215126js_/https://psdevwiki.com/ps4/edit/Syscalls` (**HTTP sin TLS**). Ningún otro archivo de la cadena (`Makefile`s, `crt.asm`, `dl.c`, `ps4-kexec-common/Makefile`) accede a la red. |
| ¿Qué se descarga y cómo se verifica? | Esos dos documentos de texto. **Sin verificación de integridad en el origen** (ni hash ni firma; `stable/9` es una rama y la página de wiki es de terceros). Se descargaron aparte con `curl`, sin ejecutarlos: `syscalls.master` sha256 `a6dbae69…574a` (43 988 B) y la página archivada `0de41eb6…03bb` (40 941 B). |
| ¿Qué ejecuta `syscalls.py`? | Solo **analiza texto** (`split`, enteros) e **imprime ensamblador**; no hay `eval`/`exec`/`subprocess`/`os.system` ni se ejecuta contenido descargado. El único riesgo es de **entrada** (texto remoto no fijado que decide el ensamblador generado), no de ejecución de código remoto. |
| ¿Se necesita la red al compilar? | **No.** `lib/syscalls.asm` (54 718 B) está versionado. `lib/Makefile` solo regenera `syscalls.asm` si `syscalls.py` es más nuevo (marcas de tiempo de un `git clone` no lo garantizan); `make clean` incluso lo **borra** (es un archivo versionado). Se evitó `make clean` y se marcó `syscalls.asm` como más nuevo. |
| ¿El `.asm` versionado corresponde a esas fuentes? | **Sí, verificado:** `syscalls.py` ejecutado en un contenedor `--network none` con las dos fuentes locales (`regen_syscalls_sin_red.py`) produce una salida **byte-idéntica** (sha256 `dbbeccde…2b5c`). Es una verificación de que, con las fuentes tal como están hoy, el `.asm` coincide; no demuestra que esas fuentes no vayan a cambiar. |
| Comandos durante la compilación | `yasm -f elf64 crt.asm`, `gcc -c dl.c`, `yasm -f elf64 syscalls.asm`, `ld -r crt.o dl.o syscalls.o -o lib.a`; por cada uno de 20 firmwares `gcc -c … -Werror` + `ar` + `gcc … -T kexec.ld` + `objcopy -O binary` (`ps4-kexec-common`); por cada uno de 9 tamaños de VRAM `gcc … main-aio.c fw_detect.c` (los blobs se incrustan con `.incbin`) + `objcopy`. No se ejecuta ningún binario ni script descargado. |
| Red y permisos reales | Red: **ninguna** durante la compilación (solo `apt` al construir la imagen del entorno). Permisos: usuario sin privilegios, sin capacidades, raíz de solo lectura, `/tmp` en memoria. |

**Conclusión de la revisión:** no hay descargas ejecutables ni ejecución de contenido remoto en la ruta usada; el hallazgo (entrada remota sin integridad en `syscalls.py`) queda **neutralizado** al no usarse y documentado. La etapa **no** se detuvo porque no se detectó ejecución de contenido remoto no fijado.

## 2. Entorno aislado
`build-env/loader/Dockerfile` (base `ubuntu:24.04@sha256:534baea6…eb55`; `build-essential binutils make yasm`; sin Python, sin red al ejecutar) y `scripts/build_loader_isolated.sh`. Ejecución: `docker run --rm --network none --read-only --tmpfs /tmp --cap-drop ALL --security-opt no-new-privileges --pids-limit 512 --memory 2g --cpus 4`, usuario `10001`, montando solo una copia de las fuentes y una carpeta de salida; sin dispositivos, sin `$HOME`, sin `/var/run/docker.sock`. Imagen construida: `sha256:73cc189a…3a03`. Herramientas: GCC 13.3.0 (Ubuntu), GNU ld 2.42, yasm 1.3.0, GNU Make 4.3, libc6-dev 2.39.

## 3. Comandos
```bash
git clone https://github.com/ps4-linux/ps4-linux-loader.git src && git -C src checkout f70f43a60a973b3662daeb29c1f115d95408db93
bash scripts/build_loader_isolated.sh <src> <salida-original>                                   # original
bash scripts/build_loader_isolated.sh <src> <salida-parcheado> --patch patches/loader-usb-only-f70f43a.patch
# dentro del contenedor:  touch lib/syscalls.asm && make -C linux -j4
```
El parche (sha256 `7f9b0313…90ee`) pasó `git apply --check` y se aplicó sin conflictos sobre una copia limpia.

## 4. Resultados

| Pregunta | Resultado |
|---|---|
| Compilación original | **Compila** (`make exit=0`; 20 `kexec.bin`, 9 ELF y 9 BIN). 0 advertencias de GCC; 50 de `ld` (pila ejecutable y segmento RWX, propias del diseño de estos binarios). |
| Compilación original, repetida | Los 18 hashes **idénticos** a la primera: construcción determinista en este entorno. |
| ¿"Reproducida" frente al binario de la distribución? | **NO reproducida bit a bit.** El ELF de la distribución se compiló con GCC 16.2.1 (20260810), aquí con GCC 13.3.0: 320 936 B vs 325 048 B; los 20 `kexec.bin` no aparecen byte a byte en el ELF de la distribución. Sí coinciden: la tabla `fw_table` (20/20 contra `fw_offsets.h`), los 4 grupos de rutas literales, el conjunto de símbolos, `.data`/`.bss`. Reproducir bit a bit exigiría el mismo compilador y flags, que no tenemos. |
| Compilación parcheada | **Compila** (`make exit=0`, mismas advertencias de `ld`). Los 20 `kexec.bin` son **idénticos** a los de la original (el parche solo toca `main-aio.c`); los 18 hashes de ELF/BIN cambian. |
| Integridad de fuentes y artefactos | Fuentes: tree y commit fijados, 41 sha256 + agregado (`manifests/loader-f70f43a-sources.sha256`). Artefactos: 18+18 hashes en `manifests/loader-f70f43a-build.json`. |

### Diferencias demostrables estáticamente entre original (A) y parcheado (B), sin ejecutar nada
(`linux-1024mb.elf`; herramientas: `tools/elf_audit.py`, `nm`, `readelf`, `objdump`)

| Aspecto | A (original) | B (parcheado) |
|---|---|---|
| Literales de ruta en el binario | `/mnt/usb0/`, `/mnt/usb1/`, `/data/linux/boot/`, `/user/system/boot/` (× 4 archivos) | solo `/mnt/usb0/` y `/mnt/usb1/`; **no** existen los bytes `/data/linux` ni `/user/system` |
| Símbolos | – | +`join_path`, `file_readable`, `select_usb_boot_dir`, `load_from` |
| Llamadas a `open` | `get_firmware`, `read_file` | `get_firmware`, `read_file`, `file_readable` |
| Llamadas a `read_file` | 16 desde `main` | 1 desde `load_from` (que solo recibe la carpeta elegida) |
| Escritura/borrado/montaje | Ningún llamador de `write` (solo `log_msg`), `creat`, `unlink`, `mkdir`, `mount`… | ídem |
| `fw_table` (`.data`) | 20/20 = `fw_offsets.h` | 20/20 = `fw_offsets.h` (sin cambios) |
| Cadena de error | – | contiene `USB-only: no hay una carpeta USB con bzImage e initramfs.cpio.gz` |
| `select_usb_boot_dir` (desensamblado) | – | recorre exactamente 2 carpetas y exige que **ambos** archivos obligatorios sean legibles en la **misma** carpeta |

Esto demuestra, **sobre el código compilado**, que la variante parcheada no contiene referencias a rutas internas y selecciona una sola carpeta USB. No demuestra su comportamiento al ejecutarse.

## 5. Qué NO queda demostrado (riesgos y límites abiertos)
- Que el loader arranque, que USB-only esté garantizado **en ejecución** (el kernel/rootfs pueden acceder al disco interno por su cuenta; recibe `eap_hdd_key`), ni que el hardware sea compatible. Una compilación exitosa no prueba nada de eso.
- Que el binario de la distribución provenga de este código: coherente (tabla, rutas, símbolos), **no probado**. Para decidirlo haría falta su compilador exacto (GCC 16.2.1-20260810) y flags.
- Que los **releases** (`B-01`) sean lo que publican: no descargados.
- Las entradas remotas de `syscalls.py` siguen sin integridad en origen; se neutralizan usando el `.asm` versionado y verificado. Si una compilación regenerara el `.asm`, el resultado dependería de contenido mutable.
- Defectos de `main-aio.c` fuera de alcance (retorno de `read` tratado como sin signo, `mmap` sin comprobar, `get_sb_id()` = -1 sin manejo): presentes en A y en B.
- El parche mantiene `bootargs.txt`/`vram.txt` opcionales de la **misma** carpeta USB; si faltan, usa los valores por defecto.
- La salvaguarda de que `/data/linux/boot/` no tenga archivos ajenos (P5) sigue siendo de laboratorio.
