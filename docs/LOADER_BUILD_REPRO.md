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

## 2. Entorno aislado y fijado
Archivos: `build-env/loader/Dockerfile`, `build-env/loader/paquetes.lock`, `build-env/loader/inner_build.sh`, `scripts/build_loader_isolated.sh`, verificador `tools/verify_loader_build.py`.

| Elemento | Fijación |
|---|---|
| Arquitectura | `linux/amd64` (anfitrión `x86_64`); `docker run --platform linux/amd64` |
| Imagen base | `ubuntu:24.04@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55` (digest del índice multi-arquitectura; la variante resuelta es `amd64/linux`) |
| Repositorios apt | Snapshot con fecha `snapshot.ubuntu.com/ubuntu/20261016T040000Z` (noble, noble-updates, noble-security). La base no trae `ca-certificates`: el TLS **no se verifica** y la integridad la da la firma GPG de apt sobre `InRelease`/`Packages` |
| Paquetes | Versiones exactas (gcc-13 13.3.0-6ubuntu2~24.04.1, binutils 2.42-4ubuntu2.10, make 4.3-4.1build2, yasm 1.3.0-4, libc6-dev 2.39-0ubuntu8.9…) y **lista completa de 148 paquetes** comparada con `paquetes.lock` al construir la imagen: si difiere, la construcción **falla** |
| Imagen construida | `ps4lab-loader-build:2` = `sha256:83708191dc7c9362453fb5b269fb07b8718109dea5d301504ed886c513be45ce` |
| Ejecución | `--network none --read-only --tmpfs /tmp --cap-drop ALL --security-opt no-new-privileges --pids-limit 512 --memory 2g --cpus 4`, con el **uid/gid del anfitrión** (sin `chmod` globales; nada queda escribible por terceros), sin dispositivos, sin `$HOME`, sin `docker.sock`. Se montan solo la copia de las fuentes (rw), la carpeta de salida (rw) y `inner_build.sh` (ro) |

**Qué se puede y qué no se puede afirmar sobre reproducibilidad**
- *Repetible en el entorno actual:* **sí**. Las construcciones repetidas dan los mismos hashes, también al reconstruir la imagen con la fijación (la primera imagen, sin fijar, resolvió las mismas versiones y dio los mismos 38 hashes).
- *Reproducible a largo plazo:* **no garantizado.** Sigue variando o dependiendo de terceros: que el registro conserve el digest de la imagen base, que `snapshot.ubuntu.com` conserve esa fecha, y la versión de Docker/containerd del anfitrión (no verificado que no influya). La construcción de la imagen **falla en voz alta** si alguna versión cambia, en lugar de resolver otra en silencio.
- *Reproducción del ELF publicado:* **NO demostrada.** El ELF de la distribución se compiló con GCC 16.2.1 (20260810); aquí GCC 13.3.0. Esa diferencia sigue sin resolverse.

## 3. Comandos
```bash
git clone https://github.com/ps4-linux/ps4-linux-loader.git src && git -C src checkout f70f43a60a973b3662daeb29c1f115d95408db93
bash scripts/build_loader_isolated.sh <src> <salida-original>   --manifiesto manifests/loader-f70f43a-build.json --variante original
bash scripts/build_loader_isolated.sh <src> <salida-parcheado>  --patch patches/loader-usb-only-f70f43a.patch \
     --manifiesto manifests/loader-f70f43a-build.json --variante parcheado
# dentro del contenedor (inner_build.sh): touch lib/syscalls.asm && make -C linux -j4
```
**Código de salida del script:** `0` solo si (a) `make` terminó con `0` (el código real se guarda en `make.exit` y se propaga; ya no hay un `exit 0` incondicional), (b) existen, son archivos regulares y no están vacíos los **9 ELF** (con firma `7f ELF`), **9 BIN** y **20 `kexec.bin`**, (c) no hay archivos inesperados en `payloads/` ni directorios inesperados en `kexec-build/`, (d) no hay hashes duplicados y (e) los hashes coinciden con el manifiesto si se indicó. Cualquier otra cosa devuelve distinto de 0 (el código de `make`/contenedor si falló, `1` si el conjunto es inválido, `2` por uso o parche, `3` si no se pudo construir la imagen), conserva los logs y los resultados parciales **sin modificarlos ni borrarlos**, y escribe `verificacion.json`. `artefactos.sha256` solo se genera ante éxito.

## 4. Resultados — seis afirmaciones distintas

| # | Afirmación | Estado | Evidencia |
|---|---|---|---|
| 1 | Compilación exitosa del código **original** | **Sí** (`make` 0; 9+9+20 artefactos válidos) | `build-original.log.gz`, `manifests/loader-f70f43a-build.json` |
| 2 | Compilación exitosa del código **parcheado** | **Sí** (ídem; los 20 `kexec.bin` idénticos a la original) | `build-parcheado.log.gz` |
| 3 | **Repetibilidad** de hashes dentro del entorno fijado | **Sí** (dos corridas originales: 38/38 idénticas; ambas variantes coinciden con el manifiesto) | corridas del 2026-10-16 |
| 4 | **Comparación estática** original ↔ parcheado | **Hecha** (tabla de abajo) | `tools/elf_audit.py`, `nm`, `objdump` |
| 5 | **Reproducción del ELF publicado** | **NO demostrada** (GCC 16.2.1 vs 13.3.0: 320 936 B vs 325 048 B; los `kexec.bin` no aparecen bit a bit en el ELF de la distribución). Coinciden: `fw_table` 20/20, rutas literales, símbolos, `.data`/`.bss` | `manifests/...-build.json` |
| 6 | **Funcionamiento en una PS4 real** | **No probado** (nada se ejecutó) | – |

Integridad: fuentes por commit/tree y 41 sha256 (+ agregado de 2123) en `manifests/loader-f70f43a-sources.sha256`; artefactos: 38 hashes por variante en el manifiesto, contrastados por el propio script. Coincidencia de código, tabla de firmware o cadenas **no** convierte el ELF publicado en reproducido.

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

## 5. Riesgos y límites abiertos
- Que el loader arranque, que USB-only esté garantizado **en ejecución** (el kernel/rootfs pueden acceder al disco interno por su cuenta; recibe `eap_hdd_key`), ni que el hardware sea compatible. Una compilación exitosa no prueba nada de eso.
- Que el binario de la distribución provenga de este código: coherente (tabla, rutas, símbolos), **no probado**. Para decidirlo haría falta su compilador exacto (GCC 16.2.1-20260810) y flags.
- Que los **releases** (`B-01`) sean lo que publican: no descargados.
- Las entradas remotas de `syscalls.py` siguen sin integridad en origen; se neutralizan usando el `.asm` versionado y verificado. Si una compilación regenerara el `.asm`, el resultado dependería de contenido mutable.
- Defectos de `main-aio.c` fuera de alcance (retorno de `read` tratado como sin signo, `mmap` sin comprobar, `get_sb_id()` = -1 sin manejo): presentes en A y en B.
- El parche mantiene `bootargs.txt`/`vram.txt` opcionales de la **misma** carpeta USB; si faltan, usa los valores por defecto.
- La salvaguarda de que `/data/linux/boot/` no tenga archivos ajenos (P5) sigue siendo de laboratorio.
- **Advertencias del enlazador (visibles, sin silenciar):** en cada variante `ld` emite 30 avisos de pila ejecutable (`missing .note.GNU-stack` / `requires executable stack`) y 20 de segmento `LOAD` con permisos RWX (los `kexec.elf`). Son consecuencia de cómo están escritos estos binarios (código que se copia y ejecuta en memoria del kernel). **No se cambiaron flags** para silenciarlas ni se investigó si hacerlo alteraría el comportamiento del payload: quedan como riesgo pendiente (R-20) y el verificador las cuenta en cada corrida.
- **Límite del propio ensayo de fallos:** las pruebas ejecutan el script y `inner_build.sh` reales, pero con `docker` y `make` simulados; no prueban el aislamiento del contenedor (eso solo se comprobó ejecutando las compilaciones reales).
