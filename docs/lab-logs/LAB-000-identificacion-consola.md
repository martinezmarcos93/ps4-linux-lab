# Registro de experimento

- ID: LAB-000
- Fecha/hora: 2026-10-15
- Operador: Marcos
- Objetivo: identificar la consola disponible sin modificarla (solo observación pasiva).
- Modelo CUH: **DESCONOCIDO**. La consola no tiene etiqueta en la base (informado por Marcos). No se ha encontrado otra fuente del CUH.
- Firmware: 13.52 (Ajustes → Sistema → Información del sistema).
- Southbridge/revisión: **DESCONOCIDO**. Solo se puede obtener ejecutando el payload (`GetSouthbridgeName()`), ver regla 3 de `COMPATIBILITY_MATRIX.md` §6.
- Método de jailbreak/payload: ninguno. No se ejecutó nada.
- Hash payload: n/a
- Kernel + hash: n/a
- Initramfs + hash: n/a
- Imagen/rootfs + hash: n/a
- Medio USB (marca/modelo/capacidad): n/a
- Reserva VRAM: n/a
- Pantalla/HDMI/HDCP: con el monitor de la PC no hay detección de señal (causa sin determinar). Con un televisor la consola da imagen y se pudo operar el menú.
- Cambios desde el experimento anterior: primer registro.

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
- **Familia: Slim.** Inferida de una foto frontal oscura (losa de una sola altura, bordes redondeados, logo "PS4" en lateral). No hay etiqueta ni foto trasera verificada por el laboratorio.
- **Capacidad de fábrica: clase 1 TB (letra B).** 861,4 GB es incompatible con un modelo de 500 GB (~440 GB mostrados). El disco interno pudo haber sido reemplazado; no verificado.
- **Revisión (20xx/21xx/22xx) y región:** sin datos. Las listas de candidatos recibidas de terceros se descartan por no tener fuente verificable (ver nota en `COMPATIBILITY_MATRIX.md` §1b).

## Procedimiento
1. Escaneo pasivo de la LAN 192.168.1.0/24 con `nmap -sn` y `avahi-browse`.
2. Sondeo TCP de puertos típicos de PS4/GoldHEN sobre los hosts activos.
3. Lectura manual de Información del sistema y Almacenamiento en la consola.
4. Búsqueda de etiqueta en la base: sin resultado.

## Resultado observado
- Indicadores luminosos: no registrados.
- Tiempo hasta vídeo: n/a
- Tiempo hasta escritorio: n/a
- Periféricos: n/a
- Temperatura: n/a
- Logs capturados: ninguno guardado.

## Resultado
- Estado: IN_PROGRESS (identificación parcial; bloqueada para el CUH).
- Evidencia: tabla de datos observados arriba (lectura directa en pantalla y escaneo de red).
- Hipótesis confirmada/refutada: confirmado que 13.52 está dentro de la lista de firmwares del loader (`COMPATIBILITY_MATRIX.md` §3). No confirmado que haya método de jailbreak viable en esta consola concreta.
- Variable única para el próximo intento: obtener el CUH por otra vía (etiqueta en otra ubicación, caja, comprobante) o aceptar determinarlo vía el log del payload.
- Rollback ejecutado y resultado: n/a, no se modificó nada.

## Pendientes antes de poder avanzar
1. Buscar el CUH en otra ubicación (parte trasera, caja, factura).
2. Desactivar descargas automáticas de actualización y no aceptar ninguna.
3. D-008 y Q-006 están resueltas como política (USB-only; no se escribe en el interno); lo pendiente es demostrar USB-only (`docs/USB_ONLY_DESIGN.md` §4) antes de cualquier ejecución.
4. Diagnosticar el HDMI con el monitor (probar otra entrada/cable, modo seguro → cambiar resolución).
