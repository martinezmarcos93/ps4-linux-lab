# Handoff a entorno Linux — 2026-10-16

Cierre de la sesión de consolidación e inicio de validación. Esta sesión corrió en Windows
(sin `sfdisk`/`dosfstools`/`e2fsprogs`/WSL-bash reales, con Docker Desktop disponible). Este
documento separa **lo que ya quedó resuelto y verificado** de **lo que falta y requiere un
entorno Linux real** (o el disco externo con los artefactos), con los comandos exactos para
retomarlo.

## 1. Qué se completó en esta sesión (verificado, no solo intentado)

### Integración de ramas
13 ramas (`workstream/01..05`, `chatgpt/*`, `claude/*`, `opencode/*`, `audit/provenance-usb-internal-risk`)
fusionadas a `main` en 10 merge commits + commits de corrección, pusheadas a `origin/main` con
autorización explícita de Marcos. Detalle completo de cada conflicto y cómo se resolvió en los
mensajes de esos commits (`git log --oneline` desde `5a8d012` hasta `HEAD`). Ninguna rama quedó
sin fusionar; las 13 se borraron (local y remoto) después de confirmar que eran ancestros de `main`.

### Defectos reales corregidos (reproducidos, no supuestos)
- **OCH-001** (`tools/build_usb_image.py`): el informe `.json` podía seguir un symlink o pisar un
  archivo preexistente al escribirse con `open()` simple. Corregido adoptando el diseño de
  `opencode/v0-kernel-inspect-hardening` (hash SHA-256, verificación real de FAT *y* ext4,
  publicación con `os.link` y sin sobrescritura también para el informe).
- **TOCTOU en la publicación final de la imagen**: una rama reintroducía `os.replace(parcial, destino)`
  sobre el `.img` final; se descartó esa variante y se mantuvo el publicador no-clobber.
- **`tests/test_kernel_inspect.py`**: `TypeError` en Python 3.9 por `int | None` sin
  `from __future__ import annotations` — el módulo entero no cargaba (0 de 11 tests corrían).
- **`tools/inspect_image.py`**: `OSError` crudo si `fstat()` fallaba tras un `open()` exitoso
  (ventana entre `lstat` y `fstat`); no se convertía a `ImageError` y podía dejar pasar una traza
  sin manejar por la CLI.
- **`tools/check_docs.py`**: la etiqueta de evidencia `OBSERVADO` (ya usada en `ROADMAP.md` y
  `COMPATIBILITY_MATRIX.md`) no estaba en `ETIQUETAS`; el validador la marcaba como "sin etiqueta".
- **`.gitattributes` (nuevo)**: `core.autocrlf=true` en Windows convertía `.sh` y `.patch` a CRLF.
  Esto rompía la ejecución de `scripts/build_loader_isolated.sh` bajo bash real (`$'\r': command
  not found`, error de sintaxis en `case ... in\r`) y hacía que el hash SHA-256 de
  `patches/loader-usb-only-f70f43a.patch` en disco no coincidiera con el registrado en el
  manifiesto (el hash registrado es el del blob LF que guarda git). **No afecta al CI real**
  (GitHub Actions clona en Linux sin esa conversión); era un problema solo del checkout local
  en Windows, y ya se corrigió renormalizando el working tree.

### Renumeración de decisiones duplicadas
`docs/DECISION_LOG.md` tenía `D-022`/`D-023` usados dos veces cada uno para decisiones distintas
(bug de una consolidación anterior a esta sesión). Se dedupe y renumeró sin perder ninguna
decisión; ver ese archivo para la numeración final (`D-022` a `D-028`) y las referencias cruzadas
corregidas en `ROADMAP.md` y `PLAN_VALIDACION_BAIKAL.md`.

### Validación de tests — clasificación completa, no "preexistentes" sin verificar
Se corrió la suite completa en tres puntos para poder afirmar causas con evidencia:

| Dónde | Resultado | Qué significa |
|---|---|---|
| Windows, antes de esta sesión (`5a8d012`, vía `git worktree`) | 292 tests: 21 failures, 30 errors | Línea base real, no supuesta |
| Windows, HEAD actual de esta sesión | 321 tests: 21 failures, 29 errors (mismo conjunto exacto de nombres que la base, menos el import roto de `test_kernel_inspect` ya corregido) | Cero regresiones nuevas, confirmado comparando nombres de test uno a uno, no solo conteos |
| **Linux real** (Ubuntu 24.04 en contenedor Docker, Python 3.11, `sfdisk`/`dosfstools`/`e2fsprogs`/`7z`/`gcc`/`yasm` instalados, usuario sin privilegios) | **321 tests: 0 failures, 0 errors, 2 skipped** (`sin zstd`, porque no instalé el paquete `zstd`) | Prueba real de que el código funciona correctamente en el entorno para el que está escrito; todo lo que fallaba en Windows era el entorno, no el código |

Las 21 failures / 29-30 errors de Windows tienen causa demostrada, no asumida (cada una se leyó
el código y se reprodujo el mecanismo exacto):

| Módulo | Causa confirmada |
|---|---|
| `test_inspect_image.py` (20) | `os.pread` no existe en el `os` de Windows (syscall POSIX) |
| `test_loader_build_script.py` (18, ya 0 tras el fix de `.gitattributes`) | CRLF en `scripts/build_loader_isolated.sh` rompía el parseo de bash |
| `test_inventariar_artefactos.py` (6) | Claves de ruta con `/` esperadas en el test; `Path.relative_to()` usa `\` en Windows |
| `test_loader_build_record.py` (2, ya 0) | Uno por CRLF en el `.patch` (hash no coincide); otro por invocar `bash` real sobre un script con CRLF |
| `test_build_usb_image.py` (2) | `os.geteuid`/`os.mkfifo` no existen en Windows |
| `test_verify_boot_chain.py` (1) | NTFS es case-insensitive: crear `BZIMAGE` después de `bzImage` sobrescribe el mismo archivo en vez de crear uno nuevo |
| `test_plan_usb_image_build.py` (1) | Rutas POSIX absolutas (`/etc`, `/dev/shm`) no tienen el mismo significado bajo Git Bash/Windows |

## 2. Qué queda pendiente y por qué

### Fase B.3/B.4 — Compilar el loader (original y parcheado USB-only)
**Bloqueo:** se armó un entorno Docker con Docker-en-Docker (socket montado, funciona en esta
máquina) y se iba a instalar `build-essential`/`docker.io`/etc. cuando el sistema se quedó sin
memoria y el harness mató la instalación por su cuenta (no fue un fallo del comando). No se
reintentó para no repetir el problema.

**Para retomarlo en Linux (nativo, sin necesidad de Docker-en-Docker):**
```bash
# 1) Clonar en limpio y fijar la revisión auditada
git clone https://github.com/ps4-linux/ps4-linux-loader.git /tmp/loader-src
cd /tmp/loader-src && git checkout f70f43a60a973b3662daeb29c1f115d95408db93 && cd -

# 2) Variante original (requiere Docker; el script construye su propia imagen aislada)
bash scripts/build_loader_isolated.sh /tmp/loader-src /tmp/build-original

# 3) Variante parcheada USB-only
bash scripts/build_loader_isolated.sh /tmp/loader-src /tmp/build-parcheado \
  --patch patches/loader-usb-only-f70f43a.patch

# 4) (opcional) variante con el hardening de lectura de archivos también aplicado
bash scripts/build_loader_isolated.sh /tmp/loader-src /tmp/build-ambos-parches \
  --patch patches/loader-usb-only-f70f43a.patch
# nota: el script solo acepta un --patch; para aplicar los dos hay que concatenarlos
# o aplicar el segundo manualmente antes de invocar el script sobre esa copia.
```
Resultados esperados en `/tmp/build-*/`: `build.log`, `make.exit`, `versiones.txt`, `paquetes.txt`
y (si hay `--patch`) `parche.txt` con su hash. Comparar con lo ya documentado en
`docs/LOADER_BUILD_REPRO.md` (la compilación anterior fue con GCC 13.3.0/ld 2.42/yasm 1.3.0; no
es bit a bit idéntica a la del release oficial, que usa GCC 16.2.1).

Después de compilar: verificar estáticamente (Fase B.4 del encargo original) que la variante
parcheada no busca kernel/initramfs/`bootargs.txt`/`vram.txt` en rutas internas y que falla
cerrado (sin fallback) si faltan en el USB — esto ya está parcialmente auditado en
`docs/workstreams/05-usb-image/USB_ONLY_CHAIN_REVIEW_2026-10-16.md` y `R_USB_001_*`; falta
confirmarlo sobre el binario recién compilado, no solo sobre el código fuente.

### Fase C — Auditoría profunda de initramfs/rootfs y Fase D — imagen candidata
**Bloqueo real, no de memoria:** los artefactos binarios (kernel Baikal `bzImage`, `initramfs.cpio.gz`,
la imagen `psxitarch-usb.img` con el rootfs) viven en el disco externo de Marcos
(`PS4-Linux-artefactos/`, ruta omitida por privacidad en los manifiestos) y **no están accesibles
desde esta máquina/sesión** — se buscó explícitamente y no aparecen. Sin ellos no se puede:
- extraer y auditar el CPIO del initramfs (scripts de init, BusyBox/Dropbear/cryptsetup/LVM, firmware);
- inventariar paquetes/servicios/systemd del rootfs Arch+KDE;
- construir una imagen candidata real con `tools/build_usb_image.py` (el "candidato" tendría que
  usar los artefactos reales, no un kernel/rootfs ficticio — construir con datos de prueba violaría
  la decisión D-026: *"no se construye una imagen 'de demostración' con un kernel arbitrario"*).

**Para retomarlo con el disco externo conectado a la PC Linux:**
```bash
# Inventario real (ya existe un corrido anterior en manifests/inventario-local-2026-10-16.json;
# repetirlo confirma que nada cambió desde entonces)
python3 tools/inventariar_artefactos.py --raiz artefactos=/ruta/al/disco/PS4-Linux-artefactos \
  --catalogo manifests/arranque-catalogo.json --markdown

# Verificación de la imagen ya publicada (solo lectura, sin montar)
python3 tools/inspect_image.py /ruta/al/disco/.../psxitarch-usb.img
fsck.vfat -n ...   # partición 1, offset correcto según inspect_image
e2fsck -fn ...     # partición 2 (rootfs)

# Construcción de la imagen candidata (cuando el kernel esté decidido, no antes — ver D-024/D-028)
python3 tools/build_usb_image.py --salida /ruta/de/trabajo/candidata.img \
  --initramfs /ruta/al/disco/.../initramfs.cpio.gz \
  --kernel /ruta/al/disco/.../bzImage-baikal \
  --rootfs-dir /ruta/al/disco/.../rootfs-extraido
```
El rootfs como *directorio* no existe hoy (solo vive dentro de la partición ext4 de la imagen
publicada); extraerlo a un directorio bajo `fakeroot` es un paso previo no hecho todavía.

### Discrepancia de GoldHEN (v2.2.3 vs v2.4b18.12) — sigue sin resolver, a propósito
No se inventó cuál versión es la correcta (riesgo R-23 de `AUDITORIA_CADENA_BAIKAL.md`). Se
necesita la captura original de pantalla *About* de GoldHEN para calcular el hash del binario
realmente cargado. Mientras no esté esa captura, `docs/lab-logs/LAB-001-southbridge.md` y
`docs/DECISION_LOG.md` (D-024/D-028) quedan con la versión v2.2.3 reportada por el operador,
marcando explícitamente el dato en disputa.

## 3. Links que pasó Marcos — qué se encontró en cada uno

- **`https://github.com/ps4-linux/ps4-linux-loader`**: ya es la fuente A-01 del inventario, pinneada
  en `f70f43a60a973b3662daeb29c1f115d95408db93`. `pushed_at` actual: 2026-10-16 (más nuevo que la
  revisión fijada); no se re-auditó el HEAD actual, sigue fijada la revisión ya auditada a propósito.
- **`https://github.com/feeRnt/ps4-linux-12xx`** y **`/releases`**: se listaron las 17 releases por
  API. Ninguna tiene tag `7.0.8` ni nombre `Strawberry`; sus kernels Baikal son `5.4.247` (release
  `v5.4.247__baikal*`, base `DFAUS-git/ps4-baikal-5.4.247-kernel`), ya documentados en
  `ARTIFACT_INVENTORY.md` §7. **Esto descarta explícitamente** a este repositorio como fuente del
  kernel 7.0.8 que usamos — no es que no se haya mirado, es que se confirmó que no está ahí.
- **`https://dionkill.github.io/ps4-linux-tutorial/`**: guía general (autor real: Diego Pireddu,
  MIT solo para la guía). No menciona Baikal, Psxitarch, GoldHEN ni el loader por nombre. Pero
  su página `docs/updating-kernel.md` enlaza un script (gist de `GattoDev-debug`) que **sí** apunta
  a la API de GitLab del repositorio real del kernel — ver el hallazgo en la sección 1 y en
  `ARTIFACT_INVENTORY.md` §4 y §7: **`https://gitlab.com/rmuxnet/linux`**, confirmado por API
  (no por una búsqueda web — un intento anterior de encontrar este repo en GitHub resultó ser una
  alucinación de la búsqueda, descartada explícitamente). El repo es público pero compila/releases
  detallados dan `403 Forbidden` ("Request access"); el siguiente paso concreto es pedirle acceso
  a `rmuxnet` en GitLab, ahí sí con la cuenta de Marcos.

## 4. Los tres bloqueos técnicos más importantes y la siguiente acción concreta

1. **Compilación real del loader (original + parcheado).** Siguiente acción: correr los comandos
   de la sección 2 en la PC Linux (no necesita el disco externo, solo Docker y red).
2. **Acceso al código/`.config` real del kernel Baikal 7.0.8.** Siguiente acción: solicitar acceso
   a `rmuxnet` en `https://gitlab.com/rmuxnet/linux` (GitLab, no GitHub). Sin eso, el kernel sigue
   siendo un binario sin fuente verificable, por más que ahora se sepa dónde vive.
3. **Auditoría de initramfs/rootfs e imagen candidata real.** Siguiente acción: conectar el disco
   externo `PS4-Linux-artefactos/` a la PC Linux y correr el inventario + extracción de solo
   lectura de la sección 2. No se puede avanzar nada de esto sin los artefactos reales.

## 5. Estado del repositorio al cierre

- Rama: `main`, limpia, sincronizada con `origin/main` (push autorizado y hecho).
- `python tools/check_docs.py`: pasa limpio.
- `python -m unittest discover` en Windows: 321 tests, 21 failures + 29 errors, **todos clasificados
  y explicados en la tabla de la sección 1** (ninguno es una regresión de esta sesión).
- En Linux real: 321 tests, 0 failures, 0 errors, 2 skipped (falta `zstd`, instalable con
  `apt install zstd` si se quiere cubrir también esos 2).
