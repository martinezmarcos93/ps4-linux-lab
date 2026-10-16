# Registro de riesgos

Escala inicial: Probabilidad y severidad `Baja`, `Media`, `Alta`, `Crítica`. Revisar al cambiar de fase.

| ID | Riesgo | Prob. | Impacto | Mitigación / condición de avance |
|---|---|---:|---:|---|
| R-01 | Firmware no compatible con el exploit disponible | Alta hasta identificarlo | Alta | Registrar versión exacta; no actualizar; confirmar evidencia antes de actuar. |
| R-02 | Kernel equivocado para southbridge/revisión | Media | Alta | Confirmar modelo/revisión y usar tabla con fuentes; no probar kernels al azar en bucle. |
| R-03 | Pantalla negra confundida con brick | Media | Media/Alta | Esperar el tiempo documentado, registrar indicadores y seguir árbol de diagnóstico. |
| R-04 | Escritura accidental sobre disco interno de PS4 o PC | Baja con controles; crítica sin ellos | Crítica | No tocar disco interno; confirmar serial/tamaño/bus; dry-run y doble confirmación. |
| R-05 | Imagen USB corrupta o incompleta | Media | Media | SHA-256, lectura posterior, verificación de particiones y filesystem. |
| R-06 | Script upstream borra archivo temporal equivocado | Baja/Media | Alta | Auditar rutas; usar directorios temporales únicos; no ejecutar como root sin revisión. |
| R-07 | Firmware/bootfiles alterados y pérdida de arranque normal | Baja/Media | Alta | Minimizar persistencia; documentar cambios; detener si el método escribe en almacenamiento interno. |
| R-08 | Temperatura o ventilación inadecuada bajo carga | Media | Alta | Inspección física, monitorización, pruebas cortas y límites conservadores. |
| R-09 | Wi-Fi/Bluetooth/audio/HDMI incompletos | Alta | Media | Plan alternativo por Ethernet y USB; registrar soporte real. |
| R-10 | Aceleración GPU no disponible para el backend LLM | Alta | Media | Validar driver/API primero; CPU baseline; no instalar stack pesado antes de tiempo. |
| R-11 | Reutilización de código incompatible con licencia | Media | Alta | Inventario de licencias y procedencia por componente antes de copiar/distribuir. |
| R-12 | Descarga maliciosa o artefacto alterado | Baja/Media | Alta | Fuente oficial, hash publicado, inspección, no ejecutar binarios opacos sin necesidad. |
| R-13 | Corrupción del rootfs por apagado brusco | Media | Media | Apagado controlado; filesystem checks; backups de configuración; evitar suspensión. |
| R-14 | Falsos positivos de rendimiento por renderizado software | Media | Media | Registrar renderer y comprobar hardware acceleration antes de benchmark. |
| R-15 | Sobreestimar utilidad como PC/LLM | Alta | Media | Medir consumo, rendimiento, compatibilidad y coste de mantenimiento; criterios de salida explícitos. |
| R-16 | El loader upstream toma archivos del almacenamiento interno si faltan en el USB o mezcla orígenes (kernel del USB + initramfs interno) | Alta (por código) | Alta | USB-only no es propiedad del binario: verificación previa (`verify_boot_chain`), imagen con `bzImage` en la FAT, parche revisable `patches/loader-usb-only-f70f43a.patch`, y listado FTP de solo lectura de las rutas internas antes de cada intento (`docs/USB_ONLY_DESIGN.md`). |
| R-17 | Binarios del loader/kernel/initramfs/rootfs no reproducibles ni firmados | Alta | Alta | Catálogo de hashes, comparación estática de ELF (`elf_audit`), no redistribuir (D-004), compilar en entorno aislado antes de confiar (`USB_ONLY_DESIGN.md` §4.1); inventario en `docs/ARTIFACT_INVENTORY.md`. |
| R-18 | El kernel que arranca recibe la clave `eap_hdd_key` de la consola (en el initramfs en RAM) y el script manual `install-psxitarch.sh` puede persistirla en el USB (`/etc/cryptmount`) | Media | Alta | No ejecutar `install-psxitarch.sh`; no copiar la clave a medios; tratar el USB como medio que podría contener secretos si se usó ese script; verificar que la imagen no tenga `/etc/cryptmount` (así es la publicada). |
| R-20 | Binarios del loader con pila ejecutable y segmentos `LOAD` RWX (30 + 20 avisos de `ld` por compilación); no se investigó si corregirlo cambia el comportamiento del payload | Alta (por diseño) | Media | Visible y contado en cada corrida (`verify_loader_build`); no cambiar flags del enlazador sin estudiar el efecto; riesgo ya inherente a ejecutar código en el kernel de la consola (D-010). |
| R-19 | Rootfs de terceros (Arch + KDE + NetworkManager) con credenciales/servicios no auditados en una LAN personal | Media | Media/Alta | Aislar la consola de internet (D-016), no reutilizar contraseñas, auditar usuarios/servicios del rootfs antes de conectarlo a una red con otros equipos. |

## Reglas de parada

Detener la fase y reevaluar si:
- no puede identificarse con confianza el dispositivo de destino;
- un procedimiento requiere modificar el almacenamiento interno sin un plan de rollback;
- el hash no coincide con el manifiesto;
- el kernel/payload elegido no tiene evidencia razonable para la combinación concreta;
- aparecen artefactos inesperados, errores de filesystem o comportamiento térmico anormal;
- no puede determinarse la licencia del código que se pretende incorporar.
