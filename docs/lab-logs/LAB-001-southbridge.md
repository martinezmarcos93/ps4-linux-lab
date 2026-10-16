# Registro de laboratorio — LAB-001: southbridge

- Fecha: 2026-10-16
- Operador: Marcos
- Consola: PS4 Slim CUH-2115B
- Firmware observado en pantalla: HEN 13.52
- GoldHEN observado en pantalla About: v2.4b18.12
- Método reportado: navegador PS4 → WebKitty → GoldHEN; luego Ajustes → Sistema → Información del sistema.
- Resultado: la pantalla de información del sistema muestra literalmente `Southbridge Baikal B1 (0x30201)`.
- Evidencia visual recibida en la conversación el 2026-10-16:
  - Información del sistema: PNG, 512294 bytes, SHA-256 `079ac880e54ba9f015db699073138d1f563f9f3e4c4c90d59a83ac754db6311d`.
  - About GoldHEN: PNG, 765856 bytes, SHA-256 `5ea6c8b5f90194c3cfc4897875f2d50cfa935fbfced0c82f9fbbcaa917f2fd7b`.
  - Las capturas originales se recibieron como adjuntos de la conversación; los hashes identifican esos archivos recibidos. No están incorporados como blobs del repositorio.
- Kernel: `bzImage-baikal-7.0.8` queda como candidato prioritario de inspección por incluir `CONFIG_X86_PS4_BAIKAL=y`; no está aprobado como compatible ni se ha ejecutado en la consola.
- Initramfs/rootfs: combinación todavía no validada como cadena indivisible para esta consola.
- USB físico: no escrito.
- Almacenamiento interno: no se ha modificado intencionalmente.
- Linux: no arrancado.
- Estado: IDENTIFICACIÓN DE SOUTHBIDGE DOCUMENTADA; verificación de artefactos y cadena de arranque en curso.

## Siguiente trabajo de V0
1. Verificar en la PC hashes, tamaños, formatos y procedencia de kernel, initramfs, rootfs y loader.
2. Ejecutar las comprobaciones automatizadas del repositorio en el commit exacto y corregir fallos reproducibles.
3. Construir una imagen candidata como archivo regular de la PC, nunca sobre un dispositivo, solo si los artefactos de entrada pasan las comprobaciones.
4. Revisar el flujo USB-only: el loader upstream tiene rutas fallback internas; usar una variante USB-only auditada no demuestra por sí mismo que kernel/initramfs/rootfs no accedan al almacenamiento interno.
5. Registrar cada resultado con comando, código de salida, hashes y límites de lo que se demuestra.

## Límites de evidencia
- La pantalla confirma la identificación que reporta GoldHEN, pero no demuestra que el kernel candidato arranque en esta unidad.
- La presencia de soporte Baikal en el kernel es un indicador de compatibilidad potencial, no una prueba de funcionamiento.
- La seguridad USB-only requiere revisar loader, kernel, initramfs y rootfs; no se infiere solo de que la imagen se cree en la PC.
- No se ha escrito ningún USB físico ni ejecutado un nuevo payload como parte de este trabajo.

## Referencias
- `docs/AUDITORIA_CADENA_BAIKAL.md`
- `docs/PLAN_VALIDACION_BAIKAL.md`
- `docs/USB_ONLY_DESIGN.md`
