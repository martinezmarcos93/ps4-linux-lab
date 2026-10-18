# Auditoría de artefactos y bloque 1 en Linux nativo — 2026-10-17

Ejecutada en Ubuntu (Python 3.12.3, Docker, `sfdisk`/`dosfstools`/`e2fsprogs`/`zstd`/`7z` nativos). Todo es de **solo lectura sobre los artefactos**; no se ejecutó ningún binario del loader, del kernel ni de GoldHEN, y no se tocó la consola. Cierra los puntos 1–7 del roadmap de `HANDOFF_LINUX_2026-10-16.md`. Nada de esto eleva ninguna fase a `LAB`/`VERIFIED`.

## 1. Línea base de tests (`TESTS`)
- `main` (`b080b3e`): `bash scripts/check.sh` → 321 tests, 0 fallos, 0 errores, 0 omitidos; `CHECK_OK`.
- Rama `integracion/2026-10-17` (main + 11 ramas de ChatGPT/OpenCode): 341 tests, 0 fallos; `CHECK_OK`.
- Confirma que los fallos del entorno Windows eran del entorno, no del código.

## 2. Integración de ramas (`IMPLEMENTADO`, sin push a `main`)
Se fusionaron en `integracion/2026-10-17` (merge commits, nada tocado en `main`):
`audit-doc-state`, `catalog-schema-validation`, `host-validation-gates`, `kernel-inspect-zstd-footer`, `preflight-rescue-shell-profile`, `rootfs-traversal-fail-closed`, `usb-only-doc-reconciliation`, `gzip-stream-integrity`, `usb-only-elf-audit`, `image-input-snapshot-ci-fix` e `image-input-snapshot-integrity`.
- Único conflicto: `tools/build_usb_image.py` (los helpers de `rootfs-traversal` y de `image-input-snapshot` se insertaron en el mismo punto). Se conservaron ambos bloques sin cambios.
- `image-input-snapshot-integrity` (ChatGPT) y `image-input-snapshot-ci-fix` (OpenCode) tienen el mismo código en `tools/`; la de OpenCode solo añade una corrección de un test.
- Revisión del diff de `tools/`: sin red, sin escritura a dispositivos, sin `shell=True`; `unlink`/`os.replace` solo en la publicación no-clobber de la imagen.
- **Validado contra artefactos reales** (no solo fixtures): el endurecimiento de zstd (`kernel_inspect`) y de gzip (`verify_boot_chain`) acepta los dos kernels reales y el `initramfs.cpio.gz` real.
- Quedan sin integrar `claude/2026-10-16-inventario-imagen`, `claude/auditoria-cadena-baikal`, `opencode/ps4-usb-build-hardening` y `chatgpt/ps4-audit-roadmap` (0 commits por delante de `main`, ya contenidas).

## 3. Loader fijado `f70f43a` compilado (`TESTS`)
`scripts/build_loader_isolated.sh` (Docker sin red, GCC 13.3.0 / ld 2.42 / yasm 1.3.0); ambas variantes: make=0, verificación=0, 9 ELF + 9 BIN + 20 `kexec.bin`, 38 artefactos con hash.

| Variante | `linux-1024mb.elf` SHA-256 |
|---|---|
| original | `86ed667bc7b484123d14c53d487faeafd49b07fbf306b487d1a117405aecb068` |
| parcheada USB-only (`patches/loader-usb-only-f70f43a.patch`, sha256 `7f9b0313…90ee`) | `a0d1eadb962bcde701a74285182c2426493789c6e0677a49d2a7c0e5b29ddbde` |
| publicado por el distro (otra revisión y compilador) | `623c3b68592437b612ede22a4fc1a6f1eef6b17c4b16a1270100ece04cb3c98f` |

Comprobación estática sobre el binario compilado (`strings` + `tools/elf_audit.py`, sin ejecutarlo):
- Original: contiene `/data/linux/boot/*`, `/user/system/boot/*`, `/mnt/usb0/*` y `/mnt/usb1/*`.
- Parcheado: **sin** ninguna ruta `/data/...` ni `/user/system/...`; solo `/mnt/usb0/` y `/mnt/usb1/`, con los mensajes `USB-only: no hay una carpeta USB con bzImage e initramfs.cpio.gz` y `USB-only: no se pudo leer ...` (falla cerrado). Tabla `fw_table` con 20 firmwares, incluido 1352.
- Límite: esto confirma el contenido del binario, no su comportamiento en la consola. Los ELF de nuestra compilación no son idénticos bit a bit a los publicados.

## 4. Loader upstream nuevo `d0f4d4c` — decisión: **no adoptar, mantener `f70f43a`**
`d0f4d4c` ("Add PS4 14.00 support") añade el firmware 14.00 (`1400.h`, fila en `fw_table`, bloque en `magic.h`, blob `kexec_1400`). Revisado el diff: la fila y el bloque de 13.52 **no cambian** (solo un comentario). Cambia además `kern_off_set_nclk_mem_spd` de `0` a `0x436650` en el bloque de **11.50**, que no es el nuestro. Sin efecto para FW 13.52; mantener el pin auditado y el parche USB-only sin rebasar. Reabrir solo si se necesita 14.00.

## 5. Inventario de artefactos reales (`TESTS`)
`tools/inventariar_artefactos.py` → `manifests/inventario-linux-2026-10-17.json` (20 artefactos).
- Hashes de `release-v1.0/SHA256SUMS`: la imagen, el `.xz` y las dos partes coinciden. Las coincidencias con listas del mismo autor prueban igualdad, no autenticidad.
- `distro/boot/baikal/bzImage`, `belize/bzImage` e `initramfs.cpio.gz` coinciden con `manifests/arranque-catalogo.json` y con `SHA256SUMS`.
- `raw13g-9ba2f07/goldhen.bin` = `payload2.bin` = `df3f27c1b35bc7c4…` (coincide con el hash fijado en `manifests/raw13g-9ba2f07.json`). El GoldHEN oficial 2.4b18 es distinto (`eb9fee5e…`). La discrepancia R-23 sigue abierta.

## 6. Imagen `psxitarch-usb.img` (8 871 489 536 B)
- MBR: p1 FAT32 (0x0c, 512 MiB), p2 ext4 (0x83, 8,3 GB). `fsck.vfat -n` y `e2fsck -fn` limpios (`TESTS`).
- **Hallazgo H-1 (importante):** la FAT de la imagen contiene solo `initramfs.cpio.gz` y `bzImage.belize` (kernel Belize 7.1.7). **No incluye el kernel Baikal ni ningún archivo llamado `bzImage`.** El loader USB-only exige `bzImage` + `initramfs.cpio.gz` en el USB. Para el CUH-2115B con Baikal observado, la imagen publicada tal cual no sirve: la candidata debe llevar `bzImage` = Baikal 7.0.8 (decisión D-026: construirla con los artefactos reales, no una de demostración).
- `7z` avisa de 2048 B tras el final de la FAT (cola; no afecta a `fsck.vfat`).

## 7. Kernels (`kernel_inspect.py`, `TESTS`)
| | Baikal 7.0.8 | Belize 7.1.7 |
|---|---|---|
| SHA-256 bzImage | `46c835f7…565b1ba8` | `07211389…19242480` |
| Compresión / pie de tamaño | zstd, coincide (43 755 952 B) | zstd, coincide (63 462 272 B) |
| `X86_PS4` / `X86_PS4_BAIKAL` | `y` / `y` | `y` / ausente |
| Compilador | clang 21.1.8 (Ubuntu), LTO completo | clang 18.1.3, runner de GitHub |
| Compilado por | `pask@pask-MacBookPro16-1` (máquina personal) | `runner@runnervmgx7h7` |

Procedencia: el Baikal se compiló en una máquina personal de un tercero, sin fuente verificable (pendiente de acceso a `gitlab.com/rmuxnet/linux`); no hay forma de reproducirlo. Riesgo a registrar, no bloqueo.

## 8. initramfs (better-initramfs v0.9.1, 34 archivos; `CÓDIGO`)
- `init` monta por `LABEL=psxitarch`, no por dispositivo ni UUID; con USB-only y sin disco interno ext4 con esa etiqueta no hay ambigüedad, pero un segundo medio con esa etiqueta sería ambiguo.
- `SetupNetwork` y `sshd` están **comentados** (sin red ni Dropbear activos en el initramfs, aunque `dropbear`/`dbclient` están empaquetados).
- Ante fallo o con la opción `rescueshell` cae a un shell de rescate **sin autenticación** (requiere acceso físico).
- Incluye `busybox`, `cryptsetup`, `lvm`, `mdadm`, firmware `amdgpu` y `mrvl`.
- `install-psxitarch.sh` / `start-psxitarch.sh` pertenecen al flujo de instalación upstream que usa discos (`/dev/sd[a-k]`); **no** deben ejecutarse en la consola.

## 9. rootfs (Arch + KDE, 837 paquetes; `CÓDIGO`, extraído parcialmente con `debugfs`, sin montar)
- Usuarios con shell: `root` y `abc`, **ambos con contraseña** (hash yescrypt, no se reproduce); `abc` con `NOPASSWD: ALL` y autologin en SDDM/Plasma.
- Servicios activados: NetworkManager, bluetooth, systemd-timesyncd. **No hay `sshd`** (`openssh` no está instalado) y las reglas de `iptables` existen pero no se activan.
- Implicación: con Wi-Fi/Ethernet la consola queda sin cortafuegos y con credenciales del lado upstream. Para laboratorio, mantener la consola sin salida a Internet (Gate 3) y cambiar las contraseñas antes de conectar a ninguna red.
- Paquetes relevantes: `mesa-ps4` y `lib32-mesa-ps4` 25.3.3, `linux-lts` 6.12.66 (su kernel de `/boot` no es el que arranca la PS4), `linux-firmware` 20260110.
- Quedan pendientes: inventario completo de binarios SUID, timers y servicios de usuario.

## 10. Consecuencias
1. Antes de cualquier prueba hay que construir la imagen candidata con Baikal (H-1); la imagen publicada solo arrancaría el kernel Belize y con el nombre equivocado.
2. La cadena de procedencia del kernel Baikal es el eslabón más débil.
3. Pendiente de Marcos: merge de `integracion/2026-10-17` a `main`, acceso a `rmuxnet/linux`, captura de GoldHEN para R-23.
