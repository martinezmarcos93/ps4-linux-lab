# Contención de R-USB-001: configuración opcional fuera del candidato

**Fecha:** 2026-10-16  
**Rama:** `chatgpt/05-usb-only-hardening`  
**Estado:** medida de contención documental; no equivale a corregir el helper C ni autoriza ejecución.

## Decisión provisional

Para el primer candidato de arranque, **no incluir** `bootargs.txt` ni `vram.txt`. Se usarán exclusivamente los valores por defecto del loader parcheado. La decisión reduce la superficie de entrada y evita depender de una lectura de configuración opcional cuyo error puede quedar sin comprobar en el código C.

Esto no convierte en correcto el manejo de errores de `read_file()`; el defecto general permanece abierto hasta que se corrija y se reconstruya el loader o se demuestre que una versión concreta hace fail-closed.

## Contrato del candidato USB-only

1. La carpeta de arranque candidata contiene `bzImage` e `initramfs.cpio.gz` obligatorios.
2. Los dos archivos deben provenir de la misma carpeta USB seleccionada y corresponder a la misma release documentada.
3. `bootargs.txt` y `vram.txt` no deben existir en la carpeta candidata. Su presencia es un fallo de preflight, incluso si el contenido parece válido.
4. Los archivos obligatorios deben ser archivos regulares, no enlaces simbólicos; el preflight debe comprobar formato, tamaño y SHA-256 contra el catálogo.
5. La inspección y las pruebas se hacen sobre directorios/archivos temporales del host. No se montan ni escriben dispositivos físicos.
6. Cualquier resultado que no pueda verificarse de forma concluyente debe terminar en fallo, no en advertencia que permita continuar.

## Matriz de casos para preflight

| Caso | Resultado exigido | Motivo |
|---|---|---|
| Kernel e initramfs presentes, hashes y release correctos, sin opcionales | Aceptar solo los niveles de preflight efectivamente verificados | Caso base de candidato |
| Falta kernel o initramfs | Rechazar | Artefacto obligatorio ausente |
| Kernel/initramfs con hash desconocido o release distinta | Rechazar | Evitar artefactos alterados o mezclados |
| `bootargs.txt` presente, aunque sea válido | Rechazar el candidato | Mantener el primer intento en defaults |
| `vram.txt` presente, aunque sea válido | Rechazar el candidato | Mantener el primer intento en defaults |
| Opcional presente como enlace simbólico, directorio o archivo vacío | Rechazar | Evitar ambigüedad de tipo y lectura |
| Entrada obligatoria como enlace simbólico, directorio o archivo vacío | Rechazar | No aceptar rutas que eludan el contrato de archivos regulares |
| Error de lectura, salida incompleta o manifiesto inválido | Rechazar y preservar evidencia | Fail-closed |

## Qué queda pendiente

- [ ] Implementar un modo explícito de preflight estricto que rechace la presencia de ambos opcionales, en vez de solo validar su contenido.
- [ ] Añadir pruebas unitarias de esa política: ausentes, presentes válidos, vacíos, symlinks y directorios.
- [ ] Ejecutar la suite en un entorno host-side limpio y guardar el comando/salida real.
- [ ] Corregir o sustituir `read_file()` para validar todas las operaciones y publicar `ptr/size` solo tras una lectura completa.
- [ ] Reconstruir la variante parcheada desde el commit upstream fijado y verificar el artefacto resultante.
- [ ] Mantener el NO-GO físico hasta que la cadena completa, la procedencia/licencia y la inspección de initramfs/rootfs estén cerradas y Marcos autorice expresamente el hito.

## Limitación de la evidencia

Esta medida solo restringe el contenido de la carpeta candidata. No prueba que el kernel o el rootfs no accedan al almacenamiento interno en runtime, ni que el kernel Baikal candidato arranque en la consola.
