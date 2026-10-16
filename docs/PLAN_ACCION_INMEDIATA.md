# Plan de acción inmediata — PS4 Linux Lab

**Objetivo:** pasar de la auditoría documental a la preparación de artefactos verificables en PC, sin saltar las puertas de seguridad ni asumir compatibilidad no demostrada.

**Estado de partida (2026-10-16):**
- Firmware 13.52: observado.
- Familia Slim: inferida de una foto.
- Capacidad indicada: 861,4 GB; no identifica por sí sola la revisión.
- CUH y southbridge: desconocidos.
- Loader USB-only: compilación aislada integrada en `main` (2026-10-16) con el script corregido (propagación de errores, conjunto completo de artefactos validado, entorno fijado); sin ejecutar y sin reproducir el ELF publicado.
- Arranque Linux propio en la consola: ninguno.
- Escritura en USB físico, ejecución de exploit/payload y escritura en almacenamiento interno: no autorizadas por este plan.

## Secuencia mínima de trabajo

### Gate 0 — Cerrar la compilación aislada
**Responsable:** Claude Code. **Estado:** correcciones hechas e integradas en `main`; pendiente solo la revisión independiente (ChatGPT). Evidencia: `docs/LOADER_BUILD_REPRO.md`, `docs/TEST_PLAN.md`.

- [x] El script propaga el código de salida real de `make`.
- [x] La compilación solo pasa con el conjunto completo esperado: 9 ELF, 9 BIN y 20 `kexec.bin` (confirmar nombres contra la revisión fijada).
- [x] Pruebas de fallo inducido cubren make fallido, artefactos ausentes, parciales y vacíos.
- [x] Imagen de construcción fijada por digest y paquetes versionados o snapshot documentado.
- [x] Permisos del host limitados al directorio de trabajo.
- [x] `bash scripts/check.sh` ejecutado y resultado registrado.
- [x] Original y parcheado construidos en el entorno corregido; hashes verificados contra los manifiestos.
- [ ] Revisión independiente del diff terminada.

**Criterio de salida:** no existe una ruta conocida por la que el script pueda informar éxito ante una compilación fallida o incompleta. Esto no demuestra que el loader funcione en hardware.

### Gate 1 — Identificar la consola sin abrirla
**Responsable:** Marcos, con asistencia de ChatGPT. **Estado:** bloqueado por datos faltantes.

- [ ] Leer la etiqueta exterior o caja y registrar el código de modelo completo (CUH-xxxx) y revisión si aparece.
- [ ] Confirmar firmware actual sin actualizarlo.
- [ ] Registrar si la consola arranca normalmente y cualquier síntoma preexistente.
- [ ] No abrir la consola, no retirar sellos y no inferir el CUH a partir de capacidad o apariencia.
- [ ] Mantener southbridge como desconocido hasta obtener evidencia fiable; no seleccionar kernel mientras falte la compatibilidad requerida.

**Criterio de salida:** ficha de consola con cada dato clasificado como observado, inferido o desconocido. Una etiqueta CUH por sí sola puede no resolver el southbridge.

### Gate 2 — Inventariar entradas reales en PC
**Responsable:** ChatGPT guía; Marcos aporta las rutas o archivos que ya tenga disponibles. **Estado:** puede comenzar sin hardware.

- [ ] Localizar las fuentes de kernel, initramfs y rootfs que ya estén disponibles.
- [ ] Registrar origen, versión/release, tamaño y SHA-256 de cada entrada.
- [ ] Verificar licencias y procedencia antes de redistribuir o modificar componentes.
- [ ] No descargar ni usar un kernel candidato como si fuera compatible antes de resolver la matriz de hardware.
- [ ] No almacenar claves, credenciales ni secretos en los manifiestos.

**Criterio de salida:** inventario de entradas identificadas, con faltantes explícitos y sin sustituciones silenciosas.

### Gate 3 — Preparar una imagen virtual, no un dispositivo
**Responsable:** ChatGPT y Marcos. **Estado:** bloqueado hasta tener entradas coherentes y resolver compatibilidad.

- [ ] Elegir kernel solo después de resolver la compatibilidad relevante.
- [ ] Confirmar que kernel, initramfs y rootfs pertenecen a una combinación documentada.
- [ ] Construir únicamente un archivo de imagen nuevo en un directorio temporal o de laboratorio.
- [ ] Ejecutar las herramientas existentes de verificación de cadena de arranque, manifiesto y filesystem.
- [ ] Comprobar el archivo de imagen final con herramientas de inspección de solo lectura y guardar hashes/logs.
- [ ] No escribir la imagen en un pendrive físico en esta fase.

**Criterio de salida:** archivo de imagen íntegro, con procedencia, hash, resultado de verificaciones y limitaciones registradas. Una imagen válida no prueba compatibilidad ni arranque.

### Gate 4 — Decisión explícita sobre la prueba física
**Estado:** BLOQUEADO; este documento no concede autorización.

Antes de cualquier prueba física deben revisarse:
- compatibilidad de hardware/firmware y procedencia de todos los artefactos;
- el riesgo residual de kernel/rootfs y acceso al almacenamiento interno;
- aislamiento de red y actualizaciones automáticas;
- procedimiento de aborto y retorno al sistema original;
- una autorización explícita de Marcos para la acción concreta.

La autorización para compilar o preparar archivos no autoriza escribir medios físicos, ejecutar payloads/exploits, arrancar Linux en la consola ni tocar el almacenamiento interno.

## Próxima acción concreta de Marcos

1. Enviar una foto legible de la etiqueta exterior con el código CUH, o transcribirlo exactamente. Puede ocultar números de serie, códigos QR y otros identificadores.
2. Indicar qué archivos de kernel, initramfs o rootfs ya tiene descargados y dónde están, sin subir claves ni datos sensibles.
3. No conectar ni escribir un USB de prueba todavía.

## Regla de reporte

Cada etapa debe informar: evidencia examinada, comandos ejecutados realmente, resultado, hashes cuando corresponda, limitaciones y criterio de salida. No convertir reportes de terceros, análisis estático o tests host-side en una afirmación de arranque probado. No abrir tareas nuevas de infraestructura salvo que desbloqueen uno de estos gates.
