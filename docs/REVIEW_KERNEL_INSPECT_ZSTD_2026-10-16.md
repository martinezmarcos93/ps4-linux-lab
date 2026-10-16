# Revisión host-side de kernel_inspect.py — 2026-10-16

## Hallazgo

La rama `claude/auditoria-cadena-baikal` incorporó `tools/kernel_inspect.py` para inspección estática de `bzImage`. En la ruta Zstandard, la versión revisada usaba `subprocess.run(..., capture_output=True)` y comprobaba `TOPE` después de capturar toda la salida. Por tanto, los 512 MiB eran una validación posterior, no un límite efectivo de memoria.

## Cambio aplicado en esta rama

- La entrada del proceso Zstandard se entrega desde un archivo temporal.
- La salida se consume por bloques y se aborta al superar `TOPE` (incluido el byte adicional que permite detectar exceso).
- Se añade un límite de tiempo de 300 segundos y se termina el proceso si se supera el tiempo o el tamaño.
- Se añade una prueba sintética que reduce temporalmente `TOPE` a 128 bytes y verifica que una salida mayor se rechaza sin necesitar reservar 512 MiB.

Archivos: `tools/kernel_inspect.py`, `tests/test_kernel_inspect.py`.

## Estado de verificación

**No ejecutado en este entorno.** La prueba nueva y la suite completa deben ejecutarse en el checkout de esta rama con `bash scripts/check.sh`. No se declara que haya pasado hasta ver la salida real. La prueba Zstandard se omite si el binario `zstd` no está instalado.

Este cambio no inspecciona ni modifica archivos de la consola, no construye una imagen USB, no escribe un dispositivo físico y no ejecuta payloads.

## Alcance

El cambio cierra el riesgo de acumulación ilimitada de salida en la ruta Zstandard. No demuestra que el kernel Baikal arranque en la CUH-2115B ni que el flujo USB-only sea seguro en tiempo de ejecución. V0 sigue pendiente de las capturas originales, la decisión documentada del payload y la validación local de los artefactos reales.
