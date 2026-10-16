# Registro de experimento

- ID: LAB-000
- Fecha/hora: 2026-10-16 (actualización de identificación)
- Operador: Marcos
- Objetivo: identificar la consola disponible sin modificarla (solo observación pasiva).
- Modelo CUH: **CUH-2115B**, confirmado por Marcos tras localizar la etiqueta de la consola (2026-10-16).
- Firmware: 13.52 (Ajustes → Sistema → Información del sistema).
- Southbridge: **Baikal B1 (`0x30201`) observado mediante GoldHEN v2.2.3** el 2026-10-16; ver registro específico `LAB-001-southbridge.md`. El modelo CUH por sí solo no permitía inferirlo.
- Método de identificación: navegador PS4/WebKitty y GoldHEN v2.2.3; no se arrancó Linux.
- Hash payload: n/a
- Kernel + hash: n/a
- Initramfs + hash: n/a
- Imagen/rootfs + hash: n/a
- Medio USB (marca/modelo/capacidad): n/a
- Reserva VRAM: n/a
- Pantalla/HDMI/HDCP: con el monitor de la PC no hay detección de señal (causa sin determinar). Con un televisor la consola da imagen y se pudo operar el menú.
- Cambios: CUH-2115B confirmado por el operador; familia Slim confirmada por el modelo; southbridge leído como Baikal B1 (`0x30201`).

## Datos observados (consola)
| Dato | Valor | Fuente |
|---|---|---|
| Nombre de sistema | PS4-199 | Información del sistema |
| Software del sistema | 13.52 | Información del sistema |
| MAC LAN | **REDACTADO** (identificador de red sensible) | Información del sistema; valor omitido de la versión pública |
| MAC Wi-Fi | **REDACTADO** (identificador de red sensible) | Información del sistema; valor omitido de la versión pública |
| Hostname en red | **REDACTADO** | mDNS; valor omitido de la versión pública |
| IP (Wi-Fi) | **REDACTADO** (IP privada de LAN) | mDNS + `nmap -sn`; valor omitido de la versión pública |
| Almacenamiento | 555,1 GB / 861,4 GB (no se sabe si el primero es libre o usado) | Ajustes → Almacenamiento |
| Puertos TCP abiertos | ninguno de 1-1024, 2121, 3232, 9090, 9295-9302 | `nmap -sT` |
| Servicio mDNS | `_spotify-connect._tcp` | `avahi-browse` |

## Inferencias (NO confirmadas)
- **Familia: Slim.** Confirmada por el modelo CUH-2115B.
- **Capacidad de fábrica: clase 1 TB (letra B).** 861,4 GB es incompatible con un modelo de 500 GB (~440 GB mostrados). El disco interno pudo haber sido reemplazado; no verificado.
- **Southbridge:** observado como Baikal B1 (`0x30201`) mediante GoldHEN; no inferido a partir del CUH. Ver `LAB-001-southbridge.md`.

## Procedimiento
1. Escaneo pasivo de la LAN local con `nmap -sn` y `avahi-browse`; el rango y los identificadores se omiten en la versión pública.
2. Sondeo TCP de puertos típicos de PS4/GoldHEN sobre los hosts activos.
3. Lectura manual de Información del sistema y Almacenamiento en la consola.
4. Lectura de la etiqueta: CUH-2115B, dato comunicado por el operador.

## Resultado observado
- Indicadores luminosos: no registrados.
- Tiempo hasta vídeo: n/a
- Tiempo hasta escritorio: n/a
- Periféricos: n/a
- Temperatura: n/a
- Logs capturados: ninguno guardado.

## Resultado
- Estado: IN_PROGRESS (CUH, firmware y southbridge identificados; compatibilidad de arranque aún pendiente).
- Evidencia: tabla de datos observados arriba (lectura directa en pantalla y escaneo de red); identificadores de red redactados por privacidad.
- Hipótesis confirmada/refutada: confirmado que 13.52 está dentro de la lista de firmwares del loader (`COMPATIBILITY_MATRIX.md` §3). No confirmado que haya método de jailbreak viable en esta consola concreta.
- Variable única para el próximo paso: auditar artefactos Baikal y su compatibilidad; el kernel aún no está aprobado.
- Rollback ejecutado y resultado: n/a, no se modificó nada.

## Pendientes antes de poder avanzar
1. Registrar la observación de southbridge en LAB-001; no inferirlo solo por CUH.
2. Desactivar descargas automáticas de actualización y no aceptar ninguna.
3. D-008 y Q-006 están resueltas como política (USB-only; no se escribe en el interno); lo pendiente es demostrar USB-only (`docs/USB_ONLY_DESIGN.md` §4) antes de cualquier ejecución.
4. Diagnosticar el HDMI con el monitor (probar otra entrada/cable, modo seguro → cambiar resolución).


## Actualización de autorización — 2026-10-16
Marcos autorizó expresamente todas las acciones técnicas necesarias para descubrir el kernel compatible, incluida la identificación del southbridge por software mediante GoldHEN o lectura de `hw.sce_subsys_subid`, y la ejecución del exploit/payload necesario para esa lectura. Esta autorización **no** equivale a autorizar escritura en almacenamiento interno, escritura física de una imagen USB o arranque Linux.
Procedimiento y límites: [`docs/AUTHORIZATION_KERNEL_IDENTIFICATION_2026-10-16.md`](../AUTHORIZATION_KERNEL_IDENTIFICATION_2026-10-16.md).
- Southbridge: pendiente de lectura observada.
- Estado de laboratorio: se utilizó GoldHEN para leer el southbridge. No se escribió el USB físico ni se arrancó Linux.
