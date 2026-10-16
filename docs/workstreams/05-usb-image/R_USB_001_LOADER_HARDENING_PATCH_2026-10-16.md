# R-USB-001 — endurecimiento propuesto del loader

**Estado:** parche de fuente propuesto; todavía no aplicado a un checkout upstream ni compilado.
**Fecha:** 2026-10-16
**Base:** `ps4-linux/ps4-linux-loader@f70f43a60a973b3662daeb29c1f115d95408db93`

## Cambios propuestos

El segundo parche, `patches/loader-read-file-hardening-f70f43a.patch`, se aplica después de `patches/loader-usb-only-f70f43a.patch`.

1. `read_file()` inicializa `*ptr = NULL` y `*sz = 0`, valida el `lseek()` de tamaño y reinicio, valida `mmap()`, procesa lecturas parciales y libera el buffer/descriptor ante fallos. Solo publica el buffer después de una lectura completa.
2. La configuración mínima deja de cargar `bootargs.txt` y `vram.txt`; usa la línea de órdenes y VRAM predeterminadas compiladas. El preflight del host rechaza estos archivos, incluidas variantes de mayúsculas/minúsculas.
3. Las lecturas se limitan a bloques de 1 MiB para evitar pedir a `read()` el tamaño completo del archivo de una sola vez.

## Qué se verificó en este repositorio

`tests/test_loader_read_file_hardening_patch.py` valida el texto del parche, sus contadores de hunks y algunas invariantes del contrato. Son pruebas estáticas del archivo de parche, no pruebas de ejecución del código C.

La CI host-side del repositorio no compila automáticamente el loader upstream ni aplica este parche a un checkout. No se debe presentar como compilado ni validado por CI.

## Puerta obligatoria antes de promover el parche

- [ ] Aplicar ambos parches en un checkout limpio del commit upstream fijado.
- [ ] Ejecutar `git apply --check` antes de aplicar y guardar la salida.
- [ ] Compilar en entorno aislado con toolchain documentada.
- [ ] Comparar el diff final y registrar SHA-256 del código fuente resultante y del ELF.
- [ ] Añadir pruebas de host con fallos simulados de `lseek`, `mmap`, lecturas parciales y EOF temprano, idealmente contra una extracción testeable de la rutina C.
- [ ] Confirmar que los opcionales no se leen y que la selección de kernel/initramfs sigue limitada a una única carpeta USB.
- [ ] Revisión independiente antes de cambiar la decisión del workstream.

## Límites

Este cambio no demuestra que Linux ya arrancará en la PS4 Slim, ni que initramfs/rootfs no accederán o escribirán al almacenamiento interno en runtime. Tampoco resuelve procedencia/licencias de todos los artefactos. **NO-GO para prueba física** permanece vigente.
