# Auditoría estática de initramfs/rootfs y límites USB-only — 2026-10-16

**Estado:** parcial, basada en la evidencia textual disponible del inventario y del mapa upstream. No se extrajeron binarios nuevos en esta iteración, no se ejecutó ningún artefacto, no se montó la imagen para ejecución y no se realizó prueba física. **Decisión: NO-GO para boot físico.**

## Resumen ejecutivo

La evidencia actual no permite afirmar que el sistema Linux completo sea USB-only ni que preserve intacto el almacenamiento interno. Sí permite identificar algunos comportamientos concretos y separar los hechos de las incógnitas.

1. El README de la distribución PS4-Linux fijado en commit 66e21cb8c15f20189254e2608c6e9bf957eb8078 indica que el kernel debe permanecer en /data/linux/boot/bzImage en el disco interno y que el initramfs se sube a /data/linux/boot/initramfs.cpio.gz. Por lo tanto, **el procedimiento upstream publicado no cumple el requisito USB-only estricto**.
2. El loader upstream f70f43a60a973b3662daeb29c1f115d95408db93 lee por separado kernel, initramfs, bootargs.txt y vram.txt de USB0, USB1 y dos rutas internas. La mezcla de orígenes por archivo es posible en el upstream sin modificar.
3. El parche local propuesto cambia la selección de kernel/initramfs a una sola carpeta USB y deja de cargar los archivos opcionales. Pero su aplicación y compilación en checkout limpio siguen pendientes. Los tests de CI del laboratorio solo inspeccionan el texto del parche.
4. El análisis anterior del initramfs publicado indica que init monta proc, sys y dev, espera y monta LABEL=psxitarch en /newroot, luego ejecuta switch_root; no se observó una orden explícita de montar el disco interno en ese script. Esto es evidencia limitada sobre un único script, no una prueba de ausencia de acceso interno en todo el runtime.
5. El initramfs contiene herramientas como BusyBox, Dropbear, cryptsetup y LVM, además de firmware. El inventario completo de sus binarios, versiones, licencias y configuración no está cerrado.
6. El script manual bin/install-psxitarch.sh se describe en el análisis anterior como potencialmente destructivo: enumera dispositivos /dev/sda…/dev/sdk, busca archivos marcadores y usa fdisk, mkfs.vfat y mke2fs; también copia eap_hdd_key.bin a /newroot/etc/cryptmount. No hay evidencia de que ese script se invoque automáticamente desde el init publicado, y **no debe ejecutarse**.
7. El loader copia a RAM material relacionado con eap_hdd_key.bin durante el handoff, según el mapa de código existente. Eso no demuestra que Linux use la clave ni que escriba el HDD; sí significa que no se puede declarar aislamiento total del disco solo porque fstab esté vacío.

## Matriz de evidencia

| Área | Observación respaldada por la evidencia existente | Estado | Qué falta |
|---|---|---|---|
| Procedimiento del README | Kernel e initramfs se suben a /data/linux/boot/ | Confirmado para el README fijado | No usar ese procedimiento para la cadena estricta USB-only |
| Loader upstream | Fallback por archivo entre USB0, USB1 y rutas internas | Confirmado en código fijado | Aplicar/validar la variante modificada |
| Loader modificado | Parche propone una única carpeta USB y elimina opcionales | Propuesto, no compilado en checkout limpio | git apply --check, build, hash de fuente/ELF y revisión independiente |
| Initramfs init | Monta LABEL=psxitarch y hace switch_root; no se vio montaje interno explícito en ese script | Observación parcial de análisis anterior | Extraer/leer todos los scripts, binarios relevantes y configuración |
| Rootfs /etc/fstab | Inventario previo indica archivo vacío/comentarios | Observación limitada | Revisar servicios, scripts, udev, systemd, swap, automount, reglas y herramientas |
| Script de instalación | Script manual usa herramientas de particionado/formateo sobre dispositivo detectado por heurística | Riesgo alto si se ejecuta | Mantener excluido; verificar que no sea invocado por ningún flujo automático |
| Clave HDD | El handoff puede incorporar eap_hdd_key.bin a la RAM/initramfs; script manual la copia a /etc/cryptmount | Riesgo/uso no resuelto | Seguir referencias de la clave y demostrar si rootfs la consume |
| Escrituras en HDD desde Linux | No hay evidencia suficiente para declarar ausencia | No demostrado | Auditoría estática integral y, solo tras gate separado, validación controlada autorizada |
| Procedencia/licencias | Kernel Baikal sin fuente/config exactas; initramfs y rootfs con inventario parcial; licencia global del loader sin resolver | Bloqueado | Fuente exacta, manifests por componente, avisos y decisiones de redistribución |

## Discrepancias y cautelas documentales

- El README upstream habla de una instalación en la que kernel/initramfs están en almacenamiento interno, mientras que el objetivo del laboratorio es una cadena que no dependa de ese almacenamiento. Son procedimientos distintos; no deben combinarse como si fueran compatibles.
- La frase “no se encontró un acceso interno en el script init” debe limitarse a ese archivo y a la revisión examinada. No equivale a “el rootfs nunca accede al HDD”.
- fstab vacío no excluye montajes hechos por systemd, udev, scripts, servicios o programas ejecutados por otros medios.
- Un hash que coincide con el publicado por el mismo distribuidor confirma consistencia respecto de esa publicación, no autoría, seguridad, compatibilidad ni derecho de redistribución.
- La detección reportada de Baikal B1 por el operador no resuelve la compatibilidad de la combinación exacta de kernel, loader, firmware y rootfs.

## Barrido técnico requerido para cerrar la auditoría

### A. Extraer sin ejecutar

En una máquina host aislada, copiar los artefactos a un directorio de análisis fuera del repositorio y registrar SHA-256 antes/después. No montar rootfs con ejecución ni invocar scripts incluidos. Inspeccionar archivos con herramientas de solo lectura.

### B. Initramfs

- Enumerar cada entrada de CPIO, tipo, tamaño, permisos, symlinks y hash.
- Leer init, scripts de inicio, reglas, configuración de montaje y scripts de rescate.
- Inventariar BusyBox, Dropbear, cryptsetup, LVM y firmware: versión, hash, procedencia y licencia.
- Buscar llamadas y cadenas relevantes: mount, umount, swapon, fsck, mkfs, fdisk, parted, dd, cp, rsync, cryptsetup, lvm, /dev/sd, /dev/mapper, /data, eap_hdd_key.bin, cryptmount, LABEL= y UUID=.
- Distinguir los scripts del arranque normal de los scripts de instalación/manuales.

### C. Rootfs

- Obtener un manifiesto de paquetes con versiones a partir de la base de datos de paquetes, sin arrancar servicios.
- Inspeccionar unidades systemd habilitadas, scripts de inicio, udev rules, fstab, crypttab, udisks, automounts, swap y tareas periódicas.
- Buscar referencias a discos/particiones y escrituras persistentes, con falsos positivos revisados manualmente.
- Verificar el destino del rootfs por UUID/LABEL y qué hace el sistema cuando el USB no aparece.

### D. Loader y cadena

- Aplicar en checkout limpio el parche USB-only y el parche de endurecimiento en orden, con git apply --check.
- Compilar con toolchain documentada y guardar logs/hashes.
- Revisar que todos los archivos obligatorios procedan de la misma carpeta USB y que ninguna ruta interna permanezca en la variante compilada.
- No ejecutar el loader en consola como parte de esta auditoría.

## Criterios para cambiar el NO-GO

La decisión solo puede revisarse cuando estén documentados: aplicación y compilación del loader modificado, artefactos exactos y licencias, auditoría estática del initramfs/rootfs, rutas de almacenamiento y escrituras identificadas, manifiesto de hashes, pruebas sintéticas negativas y plan de recuperación. La aprobación documental no autoriza automáticamente la prueba física; esa autorización es independiente.

## Fuentes internas de esta conclusión

- docs/ARTIFACT_INVENTORY.md
- docs/UPSTREAM_CODE_MAP.md
- docs/LOADER_BUILD_REPRO.md
- docs/USB_ONLY_DESIGN.md
- docs/workstreams/05-usb-image/ARTIFACT_PROVENANCE_LICENSE_AUDIT_2026-10-16.md
- docs/workstreams/05-usb-image/USB_ONLY_CHAIN_REVIEW_2026-10-16.md
- docs/workstreams/05-usb-image/R_USB_001_LOADER_HARDENING_PATCH_2026-10-16.md

Este documento registra el estado de la evidencia; no certifica seguridad del sistema ni compatibilidad de arranque.
