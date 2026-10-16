# Plan de validación por etapas — kernel Baikal 7.0.8 en la CUH-2115B (FW 13.52)

Estado: **V0 en curso; evidencia visual recibida y registrada, artefactos de imagen aún no verificados.** El trabajo de PC/archivos regulares sigue en curso. Una etapa que toque la consola exige autorización específica de Marcos para esa etapa (D-014). Complementa `RECOVERY_PLAN.md` (límites, criterios de aborto y paquete de diagnóstico generales) y `AUDITORIA_CADENA_BAIKAL.md` (hallazgos). Cada etapa termina en `APROBADA`, `ABORTADA` o `FALLIDA`; no se pasa a la siguiente sin la anterior. **Ninguna etapa se marca `VERIFIED` sin registro `LAB` con hashes** (D-020).

Reglas comunes: un solo cambio de variable por intento; máximo 3 intentos por etapa con la misma combinación; nunca escribir en el almacenamiento interno; nunca ejecutar `install-psxitarch.sh`; hashes de todos los artefactos registrados antes de cada intento; no incluir claves ni credenciales en los registros.

## V0 — Cierre de evidencia en la PC (sin consola)
- **Hecho:** capturas recibidas y SHA-256 registrados en `LAB-001`; payload candidato decidido por D-025: loader parcheado USB-only.
- **Pendiente:** comprobar que los artefactos están disponibles en el entorno de trabajo; ejecutar las verificaciones de kernel/initramfs/rootfs/loader y construir la imagen candidata como archivo regular en la PC si los insumos existen. No escribir un dispositivo físico.
- **Aceptación:** capturas registradas con hash; artefactos presentes y catalogados; todos los niveles de verificación en OK; ni un `bzImage.*` sobrante en la FAT; hash de imagen igual al informe; `bootargs.txt` y `vram.txt` válidos si existen.
- **Aborto:** discrepancia southbridge (el ID no es 0x30201), hash distinto del catálogo, nivel en FALLO, falta de espacio.
- **Rollback:** borrar el archivo de imagen de trabajo; no hay nada en la consola.

## V1 — Revisión cruzada y autorización
- **Hacer:** ChatGPT revisa el diff y esta cadena; Marcos autoriza por escrito la etapa V2 concreta (payload, imagen y USB identificados por hash).
- **Aceptación:** revisión sin hallazgos bloqueantes abiertos y autorización registrada en `docs/lab-logs/`.
- **Aborto:** cualquier hallazgo bloqueante sin resolver.

## V2 — Pre-chequeos de laboratorio (consola encendida en Orbis, sin Linux)
- **Hacer:** (1) barrera de red (D-016) comprobada: DNS manual y sin sesión de PSN; (2) listado **solo lectura** por FTP de `/data/linux/boot/` y `/user/system/boot/` (P5): deben estar vacíos o inexistentes; (3) registrar espacio libre y estado general; (4) identificar el USB por modelo+serie+tamaño.
- **Aceptación:** rutas internas sin archivos ajenos; red aislada; sin actualizaciones pendientes.
- **Aborto:** archivos en las rutas internas (no se borran: se documentan y se detiene el plan), actualización solicitada, comportamiento anómalo.
- **Rollback:** reiniciar la consola; el exploit no persiste.

## V3 — Handoff y llegada al *rescue shell* del initramfs (sin rootfs, sin escritorio)
- **Hacer:** USB con la imagen escrita **por Marcos tras una autorización separada** (esta tarea no escribe medios); `bootargs.txt` = parámetros por defecto del loader **más la palabra `rescueshell`** (el loader reemplaza el cmdline entero; el `init` detiene el arranque en una shell antes de montar el rootfs); payload de 1024 MB; observar LED, vídeo y la shell. En la shell: solo lectura (`cat /proc/version`, `lsblk`, `dmesg`), **sin montar nada**.
- **Aceptación:** `/proc/version` = `7.0.8-Strawberry-FullLTO-Baikal-+`; el kernel enumera el USB y los discos; ningún montaje de particiones internas; `dmesg` guardado.
- **Aborto:** LED blanco > 20 s sin vídeo, panic, petición de particionado, o `dmesg` que muestre acceso de escritura al disco interno. No encadenar otro kernel (`KERNEL_SELECTION.md` Paso 5).
- **Rollback:** apagado completo (mantener el botón), reiniciar a Orbis; sin escrituras persistentes esperables por diseño; comprobar el sistema original.
- **Qué demuestra:** etapa 4-5 de `RECOVERY_PLAN.md` (kernel inicia, initramfs ejecuta). Nada sobre el escritorio ni la GPU.

## V4 — Montaje del rootfs y escritorio mínimo
- **Hacer:** repetir con el `bootargs.txt` por defecto (sin `rescueshell`); no abrir Dolphin ni montar dispositivos; registrar tiempos y vídeo.
- **Aceptación:** `mounting LABEL=psxitarch` exitoso, login de KDE o consola, `lsblk` mostrando que ninguna partición interna está montada (`findmnt`).
- **Aborto:** rescue shell con error de montaje (se resuelve en el host, no a ciegas), cualquier montaje interno.
- **Rollback:** apagado completo y retorno a Orbis.

## V5 — Retorno al sistema original y comprobación de integridad
- **Hacer:** apagar; arrancar Orbis; repetir el listado FTP de solo lectura de las rutas internas; comparar con V2; comprobar que el sistema original inicia y funciona.
- **Aceptación:** rutas internas idénticas a V2; Orbis normal. Con esto y los registros V2-V4, recién se puede discutir `LAB` para "arranque USB-only sin escritura interna observable" (el alcance se redactará con cuidado: no prueba ausencia de escrituras no listadas).
- **Aborto/hallazgo:** cualquier diferencia ⇒ incidente: preservar el estado, no reparar, análisis separado.

## Qué no cubre este plan
Rendimiento de GPU, Wi‑Fi/Bluetooth, estabilidad prolongada, compatibilidad con otros firmwares y cualquier uso del instalador de la distribución.
