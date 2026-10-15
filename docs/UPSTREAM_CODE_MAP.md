# Mapa de código upstream

**Estado:** áreas preliminares, no auditoría línea por línea. Confirmar rutas y SHA con el commit/tag usado.

## Fuentes
- [X-F1REBALL-X/PS4-Linux](https://github.com/X-F1REBALL-X/PS4-Linux), rama consultada: main.
- [ps4-linux/ps4-linux-loader](https://github.com/ps4-linux/ps4-linux-loader), rama consultada: master.

Las ramas cambian. Para decisiones importantes guardar commit inmutable y URL a archivo fijado a ese commit.

## PS4-Linux
| Ruta/área | Responsabilidad aparente | Riesgo/pregunta |
|---|---|---|
| README.md | guía, compatibilidad y artefactos | ¿qué combinaciones se probaron y con qué versiones? |
| tools/build-img.sh | construir imagen USB | ruta temporal fija, limpieza, root, espacio, errores y reproducibilidad |
| tools/write-img.ps1 | escribir imagen desde Windows | destino, enumeración cambiante, bypass -Force y verificación posterior |
| LICENSE | licencia del repo | ¿qué archivos/artefactos tienen licencias separadas? |
| releases/kernel/initramfs/rootfs | artefactos del sistema | hash, procedencia, licencia y correspondencia |

## ps4-linux-loader
| Área | Responsabilidad aparente | Riesgo/pregunta |
|---|---|---|
| README.md | firmware/southbridge, rutas y configuración | contrastar tabla con tags/commits |
| payloads | transferencia de control/preparación | no ejecutar; verificar procedencia/licencias |
| selector de kernel/rutas | seleccionar artefacto | precedencia USB/interno y fallback reales |
| configuración VRAM | reserva de memoria | rango, parsing, defaults y efecto real |
| initramfs/recursos | buscar/montar rootfs | rutas, errores y escrituras internas |

## Procedimiento de auditoría
Por archivo: guardar URL/commit/fecha; describir entradas, salidas, permisos y efectos; identificar dependencias/licencia; revisar errores, quoting, rutas, privilegios y limpieza; proponer pruebas no destructivas. Distinguir observación de inferencia y no copiar código si la licencia no está resuelta.