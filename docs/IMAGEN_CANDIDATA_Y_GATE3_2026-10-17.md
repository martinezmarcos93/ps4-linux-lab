# Imagen candidata y preparación del Gate 3 — 2026-10-17

Todo es trabajo de PC con archivos regulares. **No se escribió ningún USB, no se ejecutó ningún payload y no se tocó la consola.** El arranque sigue `NO_EVALUADO` y no se autoriza nada.

## 1. Imagen candidata (`TESTS`)
Manifiesto: `manifests/candidata-baikal-2026-10-17.json`. Archivos fuera del repo, en `PS4-Linux-artefactos/candidata/` (`candidata-baikal.img`, `payload-usb-only/`).

Cómo se hizo y por qué no con `build_usb_image.py`: se copió `psxitarch-usb.img` y se agregó `bzImage` (Baikal 7.0.8) a la FAT con `tools/fat32_add_file.py`. `build_usb_image.py` exige un directorio de rootfs, y extraer el ext4 sin root (`debugfs rdump`) pierde propietarios y permisos, lo que puede romper servicios (dbus, polkit, etc.) en el primer arranque. Así el rootfs queda **byte a byte igual al publicado**.

Comprobaciones:
- MBR + hueco previo (sectores 0–2047) y toda la partición ext4: hash idéntico al de la imagen base.
- FAT: 6 archivos, `fsck.vfat -n` limpio; `bzImage` extraído = `46c835f7…565b1ba8`. `e2fsck -fn` limpio.
- `verify_boot_chain.py --southbridge baikal`: estructura, integridad (coincide con el catálogo), formato y compatibilidad (asociación documental) OK; arranque `NO_EVALUADO`.
- `strict_usb_preflight` perfil `minimal-default`: OK. El perfil `rescue-shell` falla por falta de `bootargs.txt` (esperado; no se usa).

Qué trae la FAT: `bzImage` (Baikal), `initramfs.cpio.gz` y `bzImage.belize` (extra, ignorado por el loader USB-only, que busca `bzImage`).
Payload a usar: `candidata/payload-usb-only/linux-1024mb.elf` (`a0d1eadb…ddbde`), compilado del loader fijado con el parche USB-only; **no** el ELF de la distribución.

Límites: no se probó que el kernel arranque ni que Linux evite el disco interno (el initramfs monta por `LABEL=psxitarch`, `fstab` vacío, pero el kernel puede detectar el disco interno de todos modos). El kernel Baikal sigue sin fuente verificable (R-22) y la versión de GoldHEN sigue sin conciliar (R-23).

## 2. Kernel elegido (decisión)
Baikal 7.0.8. Motivos: southbridge observado Baikal B1, `CONFIG_X86_PS4_BAIKAL=y` solo en este kernel, y la tabla del distro lo marca como funcional en un CUH-2116A con FW 13.52 (`TERCEROS`, otra unidad). El Belize no tiene soporte Baikal. Sigue siendo una elección documental, no una prueba.

## 3. Gate 3 — red aislada, actualizaciones, aborto (procedimiento; sin ensayar)
Verificado en el rootfs: `NetworkManager` está activo pero **no hay redes guardadas** (`system-connections` vacío), `sshd` no existe y no hay Wi-Fi configurado; Linux no se conectaría solo. Aun así hay cuentas con contraseña y `NOPASSWD`, así que la regla es no darle salida a Internet.

Procedimiento propuesto (a confirmar por Marcos):
1. **Enlace directo** PC ↔ PS4 por cable Ethernet, IPs fijas sin puerta de enlace ni DNS (por ejemplo 192.168.50.1 y .2). Sin router, no hay ruta a Internet. En la PC comprobar `sysctl net.ipv4.ip_forward` = 0.
2. El servidor del exploit corre en la PC y sirve solo los archivos verificados (`serve` con hashes), escuchando en esa IP.
3. En la PS4, desactivar las descargas/actualizaciones automáticas (Ajustes → Sistema → Descargas y subidas automáticas) y no activar "Actualizar en modo de reposo". No actualizar el firmware.
4. Antes de arrancar, anotar hashes y versiones en un LAB-002 y guardar el log del servidor del día y la captura de *About GoldHEN* (cierra R-23).
5. Registrar qué hace la luz: blanco→azul en ~15 s indica que el kernel arrancó; blanco >20 s, apagar y reintentar una vez.

Criterios de aborto (se suman a `RECOVERY_PLAN.md` §3): hash que no coincide con el manifiesto; la PS4 pide actualizar o conectarse a PSN; cualquier mensaje de escritura o formateo del disco interno; comportamiento distinto del previsto. No se prueban otras combinaciones a ciegas.

## 4. Estado de los gates
- G0 y G1: cumplidos a nivel host (inventario, loader compilado, suite 341/341).
- G2: imagen candidata inspeccionada en PC; falta la revisión estática de cómo el initramfs localiza la raíz sin tocar el disco interno (parcial en `INITRAMFS_ROOTFS_AUDIT_2026-10-16.md`).
- G3: pendiente la revisión independiente de ChatGPT y la decisión de Marcos. **Decisión actual: NO-GO físico hasta que Marcos autorice un hito concreto.**
