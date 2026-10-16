# Preflight de construcción de imagen USB

**Estado:** herramienta preliminar de solo lectura; no construye una imagen. Origen: rama `chatgpt/image-build-preflight`, revisada e integrada el 2026-10-15; endurecida con rechazo de salidas bajo rutas del sistema (`/dev`, `/etc`, `/usr`, …) y 3 tests más.

**Relación con la política USB-only (D-008):** este planificador describe el flujo *upstream* (construcción con `losetup`/`mount`, que exige root, a partir de un `rootfs.tar.xz`) y su opción `--spare-kernel` corresponde al esquema de la distribución, donde los kernels de reserva se renombran para que el loader los ignore. **Ese esquema no cumple por sí solo D-008**: en la política USB-only el `bzImage` va dentro de la FAT del USB. Para ese caso use `tools/build_usb_image.py` (sin root, solo archivo, con `--dry-run`); este planificador queda como control previo para evaluar el pipeline upstream.

## Uso

Desde la raíz del repositorio:

```bash
python3 tools/plan_usb_image_build.py \
  /ruta/rootfs.tar.xz \
  /ruta/initramfs.cpio.gz \
  /ruta/nueva-imagen.img
```

Se pueden añadir kernels de respaldo repitiendo `--spare-kernel /ruta/kernel`, cambiar el tamaño estimado con `--image-size-gib N` o indicar un directorio temporal con `--temp-dir /ruta/tmp`.

La ruta de salida debe ser nueva y su directorio padre debe existir. La herramienta no sobrescribe salidas existentes y rechaza enlaces simbólicos como archivos de entrada o destino. Los argumentos de entrada deben ser archivos regulares legibles.

## Qué valida

- Existencia, resolución, tipo y legibilidad de los archivos de entrada.
- Colisiones entre entradas, entradas duplicadas y destino preexistente.
- Existencia del directorio de salida y del directorio temporal.
- Espacio libre estimado para la imagen temporal y la copia final, con margen conservador.
- Presencia de los comandos habituales que requeriría un constructor futuro.

El resultado es JSON e incluye las rutas resueltas, espacio libre observado, comandos ausentes y una lista de limitaciones. Código de salida: `0` si el preflight termina sin comandos ausentes, `1` si falla la validación y `2` si la validación de rutas/espacio pasa pero faltan comandos.

## Límites y seguridad

Este programa **no** ejecuta los comandos listados, no crea archivos de imagen, no monta sistemas de archivos, no crea loop devices, no valida el contenido real del archivo comprimido ni del initramfs y no escribe en dispositivos físicos. La comprobación de espacio libre es una fotografía del momento y puede quedar obsoleta. Que el preflight pase no demuestra que la imagen resultante sea válida ni que PS4 Linux arranque.

Los archivos usados en las pruebas son datos ficticios dentro de directorios temporales. No se deben usar los tests como validación de formatos de imagen o de hardware.

## Pruebas

```bash
python3 -m unittest tests.test_plan_usb_image_build -v
```

La herramienta es un primer control no destructivo; no sustituye la implementación posterior de un constructor aislado con limpieza garantizada y validación del artefacto resultante.
