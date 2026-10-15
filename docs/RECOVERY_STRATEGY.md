# Estrategia de diagnóstico y recuperación

## Principio

“Reparación” significa primero recopilar evidencia y aislar el fallo. No ejecutar cambios automáticamente. Las herramientas futuras deben operar con permisos mínimos y tener modo `--dry-run`.

## Niveles de recuperación

### Nivel 0 — Preparación en PC
- Verificar herramientas y espacio.
- Verificar origen, tamaño y SHA-256 de los artefactos.
- Inspeccionar imagen y particiones sin escribir en discos reales.
- Generar un manifiesto del medio USB.

### Nivel 1 — Medio USB
- Detectar particiones y etiquetas esperadas.
- Verificar que el initramfs y el rootfs correspondan a la versión elegida.
- Confirmar que no haya un `bzImage` ambiguo en el USB si el flujo seleccionado depende del kernel guardado en otro lugar.
- Comprobar integridad del filesystem y guardar logs.

### Nivel 2 — Fallo de arranque
- Registrar firmware, modelo, payload, kernel, reserva VRAM, pantalla/HDMI y tiempo de espera.
- Diferenciar: payload no recibido, kernel no iniciado, kernel iniciado sin vídeo, rootfs no encontrado y escritorio no iniciado.
- Cambiar una variable por intento.
- No inferir corrupción del firmware por una pantalla negra.

### Nivel 3 — Linux en modo rescate
- Recopilar `dmesg`, `journalctl -b`, `lsblk -f`, `findmnt`, `free -h`, `lspci` si está disponible, `lsmod`, versión Mesa y temperaturas.
- Montar en solo lectura cuando sea posible.
- Hacer copia de configuración antes de editar.
- No usar comandos de reparación de filesystem sobre una partición montada en modo escritura.

### Nivel 4 — Recuperación de configuración
- Copiar archivo original con timestamp y checksum.
- Aplicar cambio atómico.
- Validar sintaxis y dependencias.
- Registrar resultado.
- Si falla, restaurar copia y verificar hash.

### Nivel 5 — Sistema original/firmware
Fuera del alcance de los scripts automáticos de este proyecto. Si un problema sucede antes del loader o afecta al firmware original, documentar síntomas y consultar un procedimiento específico verificado. No improvisar escrituras de firmware.

## Diseño de scripts futuros

Cada herramienta debe definir:
- alcance y acciones que nunca realizará;
- sistema operativo compatible;
- prerequisitos y permisos;
- parámetros explícitos;
- `--dry-run`;
- confirmación interactiva de destino para acciones destructivas;
- logs y código de salida;
- rollback;
- tests de unidad e integración sobre imágenes de archivo/dispositivos virtuales.

## Scripts propuestos

| Herramienta | Función | ¿Destructiva? |
|---|---|---|
| `ps4lab doctor` | Recolectar estado de PC/herramientas | No |
| `ps4lab verify` | Verificar hashes y manifiesto | No |
| `ps4lab inspect-image` | Revisar particiones/etiquetas | No |
| `ps4lab inspect-disks` | Enumerar discos con identificadores completos | No |
| `ps4lab build-image` | Crear imagen en directorio temporal | Solo escribe archivo de salida |
| `ps4lab write-usb` | Escribir imagen en dispositivo confirmado | Sí; bloqueado sin confirmación |
| `ps4lab verify-usb` | Verificar escritura | No |
| `ps4lab collect-logs` | Empaquetar logs con redacción | No |
| `ps4lab diagnose-boot` | Guiar por síntomas conocidos | No |
| `ps4lab restore-config` | Restaurar archivo desde backup | Modifica archivos de Linux, no firmware |

No crear `ps4lab repair-firmware`. No ejecutar acciones de escritura sobre el disco interno de la consola desde este proyecto.
