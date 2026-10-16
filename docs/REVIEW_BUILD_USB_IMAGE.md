# Revisión estática: construcción de imagen USB

Fecha: 2026-10-16  
Rama de trabajo: `chatgpt/documentar-cuh-2115b`  
Alcance: lectura estática de `tools/build_usb_image.py`; no se ejecutó el código ni se creó una imagen en este turno.

## Hallazgo R-IMG-01 — La comprobación FAT puede omitirse sin que la construcción falle

En `_verificar_p1()`, si no se encuentra `fsck.vfat` en el sistema, la función retorna sin verificar la partición FAT. La función `construir()` continúa y puede renombrar la imagen temporal al destino como si la verificación posterior hubiera terminado normalmente.

Esto no demuestra que la imagen esté corrupta; significa que el resultado no distingue claramente entre:
- FAT comprobada y aceptada por `fsck.vfat -n`;
- FAT no comprobada porque falta la herramienta.

### Recomendación

1. Para el flujo de validación estricto, tratar la ausencia de `fsck.vfat` como error, o exponer una opción explícita que permita omitir la comprobación y lo registre en el resultado.
2. Registrar las verificaciones realmente ejecutadas (p. ej. `fsck.vfat`, `e2fsck -fn`/alternativa no destructiva para ext4) en un informe de imagen, sin afirmar que un filesystem fue comprobado si no se ejecutó la herramienta.
3. Añadir tests que simulen la ausencia de `fsck.vfat` y comprueben que la salida no se etiqueta como completamente verificada. Añadir asimismo un caso de fallo de `fsck.vfat` que confirme que el archivo final no se publica.
4. Mantener la separación actual: la herramienta genera únicamente un archivo `.img`; no debe escribir en dispositivos físicos.

## Límites de esta revisión

- Es una revisión estática del código alojado en la rama, no una prueba de ejecución.
- No se ha verificado si la suite actual ya cubre total o parcialmente este caso; debe comprobarse antes de añadir tests redundantes.
- No se recomienda preparar el medio físico hasta cerrar la compatibilidad del kernel, validar los artefactos concretos y verificar la imagen virtual.
