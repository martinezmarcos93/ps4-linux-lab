# Casos de aceptación para la política de configuración mínima USB-only

Estos casos son fixtures host-side y no deben abrir dispositivos de bloque ni ejecutar payloads.

La política candidata es deliberadamente más estricta que el verificador genérico: el primer arranque propuesto no distribuye `bootargs.txt` ni `vram.txt`. El verificador genérico actual acepta opcionales válidos y solo rechaza los que no cumplen sus reglas de estructura/formato; por tanto, **su salida OK actual no basta para probar la política de configuración mínima**.

## Pruebas requeridas

| ID | Preparación del directorio temporal | Resultado del modo estricto |
|---|---|---|
| USB-MIN-01 | Solo `bzImage` e `initramfs.cpio.gz`, ambos regulares, no vacíos | Acepta estructura |
| USB-MIN-02 | Agregar `bootargs.txt` válido | Rechaza por política |
| USB-MIN-03 | Agregar `vram.txt` válido | Rechaza por política |
| USB-MIN-04 | Agregar `bootargs.txt` vacío | Rechaza por estructura y política |
| USB-MIN-05 | Agregar `vram.txt` como directorio | Rechaza por estructura y política |
| USB-MIN-06 | Agregar cualquiera de los opcionales como symlink | Rechaza por estructura y política |
| USB-MIN-07 | Falta uno de los dos obligatorios | Rechaza |
| USB-MIN-08 | Kernel/initramfs correctos pero hash no catalogado | Rechaza el nivel de integridad |
| USB-MIN-09 | Kernel e initramfs pertenecen a releases distintas | Rechaza el nivel de integridad |
| USB-MIN-10 | Interrumpir una lectura o simular error de I/O | Rechaza sin reutilizar datos parciales |

## Resultado de inspección del código actual

- `verificar_estructura()` comprueba los obligatorios y, si los opcionales existen, comprueba que sean archivos regulares, legibles, no vacíos y de tamaño limitado.
- `verificar_formato()` valida el contenido de los opcionales si están presentes.
- No existe todavía un parámetro de política que rechace los opcionales por el mero hecho de estar presentes.
- Los tests actuales de `TestEstructura` y `TestFormato` verifican casos inválidos y formatos válidos, pero no la política estricta de ausencia.

Por tanto, la próxima modificación de código debe añadir una política explícita de modo estricto y tests que prueben USB-MIN-01 a USB-MIN-09. USB-MIN-10 requiere inyección de fallos o una abstracción de lectura; no debe simularse con una afirmación documental.
