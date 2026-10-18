# Auditoría de ELFs: USB-Only Loader (2026-10-16)

## Resumen
Se auditaron 9 ELFs de payloads contra sus contrapartes originales compiladas desde el código fuente del loader `f70f43a`.
El parche elimina exitosamente las rutas literales hacia `/data/linux` y `/user/system` y sus subdirectorios de boot.

## Resultados
Se ha verificado que todos los ELFs parcheados:
1. Mantienen la integridad de la tabla de firmwares (`fw_table`).
2. Eliminan las referencias literales restringidas en la sección `.rodata`.
3. Eliminan la presencia binaria de las rutas restringidas.

| Payload | Estado | Cambio (Tamaño) |
| :--- | :--- | :--- |
| linux-32mb.elf | VERIFICADO | +144 bytes |
| linux-64mb.elf | VERIFICADO | +144 bytes |
| linux-128mb.elf | VERIFICADO | +144 bytes |
| linux-256mb.elf | VERIFICADO | +144 bytes |
| linux-512mb.elf | VERIFICADO | +144 bytes |
| linux-1024mb.elf | VERIFICADO | +144 bytes |
| linux-2048mb.elf | VERIFICADO | +144 bytes |
| linux-3072mb.elf | VERIFICADO | +144 bytes |
| linux-4096mb.elf | VERIFICADO | +144 bytes |

---
*Nota: Los cambios de tamaño son consistentes debido a la modificación de las constantes de cadena en `.rodata`.*
