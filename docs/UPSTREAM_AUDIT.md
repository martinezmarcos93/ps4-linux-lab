# Auditoría inicial de upstream

**Fecha de lectura:** 2026-10-15.  
**Alcance:** README, licencia del primer proyecto y scripts de preparación de imagen/escritura USB disponibles en la rama por defecto. No equivale a una auditoría completa del código ni a una prueba en hardware.

## Fuentes

1. [X-F1REBALL-X/PS4-Linux](https://github.com/X-F1REBALL-X/PS4-Linux) — rama `main`.
2. [ps4-linux/ps4-linux-loader](https://github.com/ps4-linux/ps4-linux-loader) — rama `master`.

## Hallazgos de PS4-Linux

- Ofrece un entorno Arch Linux con KDE para PS4, preparado para arrancar desde USB.
- El README consultado declara firmware soportado hasta 13.52 por el flujo documentado.
- Solo declara probados algunos combos concretos: CUH-2116A (Slim/Baikal) y CUH-7116B (Pro/Belize), ambos con FW 13.52 y GoldHEN. Otras combinaciones aparecen como no probadas.
- La guía indica que el kernel debe coincidir con la familia de southbridge y advierte que algunos modelos Fat pueden presentar problemas de Wi-Fi/Bluetooth.
- La guía recomienda USB 3.0 de 32 GB y advierte que la escritura de imagen borra el dispositivo seleccionado.
- Recomienda mantener el kernel específico en el almacenamiento interno en una ruta de arranque; esto debe evaluarse cuidadosamente frente al objetivo de no modificar el disco interno.

### Observación sobre `tools/build-img.sh`

- Crea una imagen raw de 12 GiB con partición FAT32 para initramfs y ext4 etiquetada `psxitarch`.
- Usa una ruta temporal fija `/root/psxitarch-usb.img`, elimina ese archivo con `rm -f` y después copia la imagen al destino. Es una decisión que nuestro futuro script debería reemplazar por un directorio temporal único, comprobación de espacio y limpieza segura.
- Ejecuta herramientas de particionado/filesystem como root. El nuevo flujo debe validar prerequisitos, rutas y errores en cada etapa.
- Calcula SHA-256 al final, lo cual es útil, pero debemos conservar el manifiesto y permitir verificar la imagen más tarde.

### Observación sobre `tools/write-img.ps1`

- Incluye comprobación de administrador, bus USB, disco de arranque/sistema, tamaño y confirmación del número.
- `-Force` permite omitir la confirmación. En nuestra implementación no debería existir un bypass genérico para escribir un disco real; usar un modo de prueba separado.
- La identificación por número de disco puede cambiar al reconectar dispositivos. Nuestra herramienta debe volver a enumerar y mostrar modelo, tamaño, serial, bus y particiones inmediatamente antes de escribir.
- Es destructivo por diseño; probar únicamente con imágenes/discos virtuales durante desarrollo.

## Hallazgos de ps4-linux-loader

- El README declara payloads para firmware 5.05–13.52 y southbridge Aeolia, Belize(2) y Baikal.
- Describe rutas internas de boot, fallback de ruta y prioridad de USB.
- Expone configuraciones de reserva de VRAM desde 32 MB hasta 4096 MB, con 1024 MB como valor predeterminado según el README.
- Describe perfiles de baja reserva de VRAM para uso headless.
- La documentación reconoce que algunos firmwares se marcan con incertidumbre (`(?)`); no convertir una tabla de upstream en garantía de compatibilidad.

## Licencias y reutilización

- `X-F1REBALL-X/PS4-Linux` contiene un archivo `LICENSE` con GNU GPL versión 3.
- No se encontró `LICENSE` en la raíz del repositorio `ps4-linux/ps4-linux-loader` mediante la ruta comprobada; eso no prueba que todos los archivos carezcan de licencia. No copiar código hasta revisar metadatos, cabeceras y licencias de dependencias/archivos.
- La imagen rootfs, los kernels, payloads, initramfs y paquetes pueden tener licencias y autores distintos. Mantener inventario por artefacto.
- Preferir inicialmente integración por documentación, descarga desde release upstream y verificación de hashes; no subir binarios de terceros al repo privado salvo que licencia y procedencia lo permitan.
- Conservar avisos de copyright y licencia cuando se reutilice código de forma permitida. Marcar las modificaciones.

## Próximos pasos de auditoría

- Revisar releases/tags exactos, hashes y cambios recientes.
- Revisar todo script antes de ejecución y elaborar threat model para artefactos binarios.
- Verificar qué archivos se copian al almacenamiento interno durante el flujo de loader/initramfs.
- Confirmar la licencia del loader y del payload que finalmente se utilice.
- Revalidar la matriz de firmware con la consola real y no solo con documentación.
