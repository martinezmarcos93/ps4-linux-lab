# Addendum del auditor independiente: procedencia, USB-only y almacenamiento interno

**Fecha:** 2026-10-16
**Rama de auditoría:** `audit/provenance-usb-internal-risk`
**Límite operativo:** inspección estática y pruebas host-side. No se ejecutaron payloads o exploits, no se arrancó la consola y no se escribió ningún USB físico ni almacenamiento de PS4.

Este addendum no sustituye ni repite los inventarios ya existentes. Consolida los resultados independientes y los deltas para los entregables solicitados; las fuentes primarias ya leídas por el proyecto están en `ARTIFACT_INVENTORY.md`, `UPSTREAM_CODE_MAP.md`, `EVIDENCE_SOURCES.md` y `USB_ONLY_DESIGN.md`.

## 1. Evidencia comprobada en esta revisión

### 1.1 Parche y cadena de carga

- El blob Git canónico de `patches/loader-usb-only-f70f43a.patch` tiene SHA-256 `7f9b0313705276fcc47b93f2e1d78f5f38620c5c9d81561c88ef734dbede90ee`, igual al registrado en `manifests/loader-f70f43a-build.json`.
- La copia de trabajo en Windows tiene SHA-256 `f2b7ebe637e0f28a6a0bad23472fb2dfb03a44ab95bf8a2ea5f7b8680eac8a87` porque Git informa `i/lf w/crlf` y `core.autocrlf=true`. No es una divergencia de contenido versionado. Los hashes de evidencia deben calcularse sobre el blob Git o con finales LF normalizados.
- El parche elimina el fallback de las rutas `/data/linux/boot/` y `/user/system/boot/` y selecciona una sola carpeta, `/mnt/usb0/` o `/mnt/usb1/`, que contenga **ambos** obligatorios (`bzImage`, `initramfs.cpio.gz`). Los opcionales se leen solamente desde esa carpeta. El nuevo acceso de comprobación es `open(..., O_RDONLY)`.
- `python -m unittest tests.test_loader_model -v` pasó: 21 pruebas, incluidas las de rechazo de mezcla USB/interno y entre USB para el modelo del parche.
- No hay un checkout de `ps4-linux-loader` junto a este repositorio; por tanto esta revisión no ejecutó `git apply --check` contra `f70f43a` ni recompiló el loader. La evidencia de compilación previa está registrada, pero no queda renovada por este addendum.

### 1.2 Nuevo hallazgo: la raíz no queda ligada al USB seleccionado por el loader

La evidencia estática previa del initramfs (`UPSTREAM_CODE_MAP.md` §2.9) establece que el `init` hace `mount LABEL=psxitarch /newroot` y después `switch_root`. El parche del loader escoge una carpeta USB para kernel e initramfs, pero no cambia esa regla de selección de raíz.

**Inferencia:** si hay más de un dispositivo visible con la etiqueta `psxitarch`, kernel/initramfs pueden proceder de un USB y el rootfs de otro dispositivo que satisfaga la búsqueda por etiqueta. Esto rompe la propiedad de cadena de un único medio. Si un dispositivo interno llegara a exponer esa etiqueta, también sería candidato; no hay evidencia de que el disco interno de esta PS4 la tenga.

No es una escritura interna demostrada. Es un bloqueo de aislamiento: el montaje normal es de lectura-escritura salvo que se indique lo contrario, de modo que seleccionar el dispositivo equivocado podría permitir escrituras posteriores (journal, servicios o usuario) en ese rootfs.

## 2. Procedencia y licencias por artefacto

| Artefacto | Fuente/revisión fijada | Hash y estado | Licencia comprobada | Conclusión |
|---|---|---|---|---|
| Kernel candidato `bzImage-baikal-7.0.8` | `X-F1REBALL-X/PS4-Linux@66e21cb8c15f20189254e2608c6e9bf957eb8078`, release `v1.0` | SHA-256 `46c835f762e7b0b5400ea762b8daa1bcec638a1b769c7ec0905137bc565b1ba8`, 13,841,408 B; coincidencia local/API/lista del mismo publicador ya registrada | `NOTICE` del empaquetador declara kernels GPL-2.0; fuente y `.config` de esta compilación no identificados | Integridad frente al empaquetador: comprobada previamente. Procedencia reproducible, fuente correspondiente y cumplimiento completo de GPL-2.0: **bloqueados**. Es solo candidato para Baikal B1, no evidencia de arranque en CUH-2115B/FW 13.52. |
| Código del loader | `ps4-linux/ps4-linux-loader@f70f43a60a973b3662daeb29c1f115d95408db93` | commit y tree fijados; build aislado previo registrado | Sin licencia en raíz; `linux/ps4-kexec-common/LICENSE` BSD-2; otros archivos/headers con licencias propias o sin declaración localizada | No atribuir una licencia única al loader. No redistribuir/modificar partes sin resolver la licencia de cada archivo aplicable. |
| Parche USB-only | Este repositorio, blob Git anterior | SHA-256 canónico `7f9b…90ee` | Documentación/patch propio del laboratorio; no cambia la licencia del código upstream al que aplica | Trazable al build manifest, pero requiere volver a aplicar/compilar al cambiar el upstream o antes de un gate físico. |
| Initramfs `initramfs.cpio.gz` | Mismo release de distribución | SHA-256 `3f373bd6c469e490eaf4e5cf4d2e8ed77cf7bb91449b6a18da6a6529d479169b`, 4,102,011 B; 48 entradas leídas anteriormente | Cabecera de `init`/better-initramfs: BSD-3 según inventario; binarios, firmware y adaptación Psxitarch no quedan cubiertos por esa afirmación | Licencia completa y SBOM: **pendientes**. El artefacto no está presente en esta copia para una segunda extracción independiente. |
| Rootfs/imagen `psxitarch-usb.img(.xz)` | Release `v1.0` de la distribución | `.img` SHA-256 `badd4873…0143`; partes `4063f338…bf588` y `e62aa04d…2df2d`, según inventario | Mixta: Arch/KDE y paquetes conservan licencias propias; el `NOTICE` no las enumera | Licencias, paquetes, servicios y credenciales: **no auditados exhaustivamente**. No redistribuir ni asumir que GPL-3 del empaquetador cubre el rootfs. |

La afirmación de compatibilidad que queda disponible es limitada: el loader mapea el valor reportado `0x30201` a Baikal B1 y el catálogo asocia el kernel candidato con Baikal. El valor fue comunicado por el usuario para esta auditoría; no se volvió a medir y no prueba handoff, vídeo, almacenamiento ni arranque Linux.

## 3. Riesgo de almacenamiento interno

| Componente/ruta | Evidencia comprobada | Riesgo de escritura interna | Estado |
|---|---|---|---|
| Loader upstream `f70f43a` | Busca cada archivo separadamente en USB0, USB1, `/data/linux/boot/`, `/user/system/boot/` | Fallback y mezcla de **lectura** desde interno; no se encontró escritura de archivos en el payload auditado | Eliminado para esos archivos por el parche; upstream sin parche: no apto para USB-only |
| Loader con parche | Solo rutas USB y `O_RDONLY`; pruebas del modelo pasan | No demuestra qué hace Linux después del handoff | Reduce P1/P2; no cierra P4 |
| `sys_kexec`/firmware | Copia en RAM firmware y `key/eap_hdd_key.bin` al initramfs, según `UPSTREAM_CODE_MAP.md` §1.5 y `USB_ONLY_DESIGN.md` §4 | No es escritura persistente por sí misma, pero entrega al Linux arrancado material sensible para acceder al interno | Riesgo condicionado; requiere auditoría runtime del kernel/rootfs |
| Initramfs `init` | Monta `LABEL=psxitarch`, sin `/hooks`; no se documentó montaje de `/data` ni copia de archivos | Selección global por etiqueta puede elegir raíz no prevista; montaje no declarado como solo lectura | Bloqueo alto de encadenamiento de medio; no es escritura interna confirmada |
| `bin/install-psxitarch.sh` | Script manual, no invocado por `init`; sondea `/dev/sda`…`/dev/sdk`, después usa `fdisk`, `mkfs.vfat`, `mke2fs` | Destructivo contra el dispositivo que cumpla su heurística; además persiste `eap_hdd_key.bin` en el rootfs USB | No ejecutar. No hay evidencia de activación automática ni de que tocaría el disco PS4 sin los tres archivos marcadores |
| Rootfs publicado | `fstab` vacío, no `/data`, servicios presentes (`NetworkManager`, `remote-fs`, display/bluetooth/timesyncd) | Un `fstab` vacío no prueba ausencia de automontaje ni de servicios que escriban en un dispositivo visible | Auditoría incompleta: bloqueo alto |

## 4. Bloqueos priorizados para una futura prueba de arranque

1. **P0 — No ejecutar mientras la raíz siga seleccionándose solo por `LABEL=psxitarch`.** Definir y verificar una asociación inequívoca entre el USB/carpeta elegida y su partición root (por UUID/partición derivada del dispositivo de boot, o rechazar más de una coincidencia). Debe fallar cerrado.
2. **P0 — Auditar kernel, initramfs y rootfs disponibles, incluidos servicios y automontajes.** Sin ello no puede afirmarse ausencia de escrituras en el interno; `fstab` vacío es insuficiente.
3. **P0 — Resolver procedencia/licencia distribuible.** Obtener fuente y configuración del kernel Baikal exacto, licencia por componente del initramfs/rootfs y una lista de paquetes/licencias. No redistribuir binarios no resueltos.
4. **P1 — Renovar evidencia de build del parche.** En un checkout limpio de `f70f43a`, ejecutar `git apply --check`, compilar aislado y asociar los nuevos ELF al hash canónico del patch. No usar el SHA de la copia CRLF de Windows como identidad de evidencia.
5. **P1 — Completar preflight de artefactos.** Verificar hashes, formato y release común de kernel/initramfs; el parche solo comprueba que los archivos se pueden abrir.
6. **P1 — Resolver R-USB-001.** Los errores de lectura de `bootargs.txt`/`vram.txt` se ignoran. Excluirlos del medio candidato o corregir la carga para fallar cerrado.
7. **P2 — Prueba física solo con autorización separada.** Antes/después de un intento autorizado, obtener evidencia de solo lectura de rutas internas y una medición diseñada para detectar cambios. Ninguna evidencia actual prueba el arranque de CUH-2115B/FW 13.52/Baikal B1.

## 5. Comandos y resultados reproducibles

Ejecutados desde la raíz del repositorio, sin payloads ni dispositivos:

```powershell
git status --short --branch
git branch --show-current
Get-FileHash patches\loader-usb-only-f70f43a.patch -Algorithm SHA256
git ls-files --eol patches/loader-usb-only-f70f43a.patch
python -m unittest tests.test_loader_model -v
```

Resultados relevantes: rama `audit/provenance-usb-internal-risk`; árbol sin cambios antes de este addendum; `i/lf w/crlf`; hash de copia de trabajo `f2b7…8a87`; 21/21 pruebas correctas.

Para obtener el hash canónico, no el transformado por `autocrlf`, se escribió y eliminó un archivo temporal fuera del repositorio a partir de `git show HEAD:patches/loader-usb-only-f70f43a.patch`; SHA-256 resultante: `7f9b0313705276fcc47b93f2e1d78f5f38620c5c9d81561c88ef734dbede90ee` (4,110 B).

## 6. Preguntas abiertas

- ¿Dónde están el código fuente, `.config`, commit y cadena de construcción exactos de `bzImage-baikal-7.0.8`?
- ¿Cuál es el mecanismo exacto que vincula el dispositivo de boot con `LABEL=psxitarch`, si existe fuera del `init` leído?
- ¿Qué servicios, udev rules, automontajes y paquetes del rootfs pueden descubrir/desbloquear/montar almacenamiento interno?
- ¿Hay una evidencia repetible del valor `0x30201` para la unidad CUH-2115B sin convertirla erróneamente en prueba de arranque?
