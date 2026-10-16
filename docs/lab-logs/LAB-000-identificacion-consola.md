# Registro de experimento

- ID: LAB-000
- Fecha/hora: 2026-10-16 (actualización de identificación)
- Operador: Marcos
- Objetivo: identificar la consola disponible sin modificarla (solo observación pasiva).
- Modelo CUH: **CUH-2115B**, confirmado por Marcos tras localizar la etiqueta de la consola (2026-10-16).
- Firmware: 13.52 (Ajustes → Sistema → Información del sistema).
- Southbridge/revisión de placa: **DESCONOCIDO**. El CUH no basta para inferirlo con certeza. Solo se puede obtener ejecutando el payload (`GetSouthbridgeName()`), ver regla 3 de `COMPATIBILITY_MATRIX.md` §6.
- Método de jailbreak/payload: ninguno. No se ejecutó nada.
- Hash payload: n/a
- Kernel + hash: n/a
- Initramfs + hash: n/a
- Imagen/rootfs + hash: n/a
- Medio USB (marca/modelo/capacidad): n/a
- Reserva VRAM: n/a
- Pantalla/HDMI/HDCP: con el monitor de la PC no hay detección de señal (causa sin determinar). Con un televisor la consola da imagen y se pudo operar el menú.
- Cambios: CUH-2115B confirmado por el operador; familia Slim confirmada por el modelo.

## Datos observados (consola)
| Dato | Valor | Fuente |
|---|---|---|
| Nombre de sistema | PS4-199 | Información del sistema |
| Software del sistema | 13.52 | Información del sistema |
| MAC LAN | f8:46:1c:c1:70:e9 | Información del sistema |
| MAC Wi-Fi | 40:99:22:0b:e1:43 | Información del sistema |
| Hostname en red | PS4-C170E9.local (mDNS, sufijo = últimos 3 bytes de la MAC LAN) | `avahi-browse` |
| IP (Wi-Fi) | 192.168.1.98 (DHCP, puede cambiar) | mDNS + `nmap -sn` |
| Almacenamiento | 555,1 GB / 861,4 GB (no se sabe si el primero es libre o usado) | Ajustes → Almacenamiento |
| Puertos TCP abiertos | ninguno de 1-1024, 2121, 3232, 9090, 9295-9302 | `nmap -sT` |
| Servicio mDNS | `_spotify-connect._tcp` | `avahi-browse` |

## Inferencias (NO confirmadas)
- **Familia: Slim.** Confirmada por el modelo CUH-2115B.
- **Capacidad de fábrica: clase 1 TB (letra B).** 861,4 GB es incompatible con un modelo de 500 GB (~440 GB mostrados). El disco interno pudo haber sido reemplazado; no verificado.
- **Southbridge:** sigue sin confirmar. No inferir Baikal/Belize únicamente a partir del CUH; ver `COMPATIBILITY_MATRIX.md` §7.

## Procedimiento
1. Escaneo pasivo de la LAN 192.168.1.0/24 con `nmap -sn` y `avahi-browse`.
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
- Estado: IN_PROGRESS (CUH y firmware identificados; southbridge y compatibilidad de arranque aún pendientes).
- Evidencia: tabla de datos observados arriba (lectura directa en pantalla y escaneo de red).
- Hipótesis confirmada/refutada: confirmado que 13.52 está dentro de la lista de firmwares del loader (`COMPATIBILITY_MATRIX.md` §3). No confirmado que haya método de jailbreak viable en esta consola concreta.
- Variable única para el próximo intento: revisar el inventario de artefactos y la evidencia de compatibilidad; el southbridge continúa desconocido.
- Rollback ejecutado y resultado: n/a, no se modificó nada.

## Pendientes antes de poder avanzar
1. Resolver el southbridge con evidencia fiable y autorización; no inferirlo solo por CUH.
2. Desactivar descargas automáticas de actualización y no aceptar ninguna.
3. D-008 y Q-006 están resueltas como política (USB-only; no se escribe en el interno); lo pendiente es demostrar USB-only (`docs/USB_ONLY_DESIGN.md` §4) antes de cualquier ejecución.
4. Diagnosticar el HDMI con el monitor (probar otra entrada/cable, modo seguro → cambiar resolución).


## Actualización de autorización — 2026-10-16
Marcos autorizó expresamente todas las acciones técnicas necesarias para descubrir el kernel compatible, incluida la identificación del southbridge por software mediante GoldHEN o lectura de `hw.sce_subsys_subid`, y la ejecución del exploit/payload necesario para esa lectura. Esta autorización **no** equivale a autorizar escritura en almacenamiento interno, escritura física de una imagen USB o arranque Linux.
Procedimiento y límites: [`docs/AUTHORIZATION_KERNEL_IDENTIFICATION_2026-10-16.md`](../AUTHORIZATION_KERNEL_IDENTIFICATION_2026-10-16.md).
- Southbridge: pendiente de lectura observada.
- Estado de laboratorio: no se ha ejecutado nada en la consola en esta sesión; hace falta la operación local en la PS4.
