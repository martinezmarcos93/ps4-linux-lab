# Matriz de compatibilidad

Esta tabla registra declaraciones preliminares de upstream, no garantías de funcionamiento. La validación propia exige evidencia reproducible.

| Combinación/plataforma | Firmware declarado | Southbridge declarado | Evidencia preliminar | Estado de laboratorio |
|---|---|---|---|---|
| CUH-2116A, PS4 Slim | 13.52 | Baikal | README de PS4-Linux consultado lo declara probado | UPSTREAM-CLAIM, no probado aquí |
| CUH-7116B, PS4 Pro | 13.52 | Belize | README de PS4-Linux consultado lo declara probado | UPSTREAM-CLAIM, no probado aquí |
| Otras variantes Fat/Slim/Pro | varios | Aeolia, Belize(2), Baikal u otros según versión | referencias comunitarias con diferente certidumbre | desconocido hasta identificar hardware |
| Loader en general | README menciona 5.05–13.52 | Aeolia, Belize(2), Baikal | declaración de ps4-linux-loader; algunos tags son inciertos | UPSTREAM-CLAIM; contrastar artefacto |

## Campos obligatorios por combinación
- Modelo CUH exacto y método de identificación.
- Revisión/southbridge y confianza del dato.
- Firmware exacto, no solo rango.
- Tag/commit y SHA-256 de loader/payload/kernel/initramfs/rootfs.
- Método de lanzamiento, dependencias, límites y síntomas.
- Fuente primaria con enlace inmutable y fecha.
- Evidencia separada para carga, kernel, rootfs, escritorio, GPU y estabilidad.
- Registro local, si existe.

## Niveles de evidencia
- **E0:** desconocido.
- **E1:** declarado en README/release upstream.
- **E2:** código observado en commit/tag.
- **E3:** informe de tercero identificable.
- **E4:** reproducción externa con evidencia independiente.
- **E5:** prueba propia con hardware, firmware, hashes, logs y procedimiento reproducible.

Solo E5 permite marcar `VERIFIED` en este laboratorio, y únicamente para el alcance probado. Arranque, Wi-Fi, GPU y estabilidad pueden tener niveles distintos en la misma consola.

## Estado actual
- CUH/firmware/southbridge: no registrados.
- Loader/kernel/initramfs/rootfs: sin seleccionar.
- Arranque propio, GPU y LLM: no probados.

No seleccionar artefactos hasta completar el inventario y contrastar una versión específica de upstream.