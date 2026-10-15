# Roadmap

Estados: `PLANNED`, `IN_PROGRESS`, `BLOCKED`, `VERIFIED`, `REJECTED`.

## Fase 0 — Inicialización del proyecto
**Estado:** IN_PROGRESS

- [ ] Crear `martinezmarcos93/ps4-linux-lab` como repositorio privado.
- [ ] Añadir este esqueleto en un commit inicial revisable.
- [ ] Proteger `main` y usar una rama temporal para cambios posteriores.
- [ ] Añadir plantillas de incidencias y un registro de decisiones.
- [ ] Definir política para artefactos grandes: no versionar imágenes USB ni rootfs.

**Puerta de salida:** repositorio privado creado, estructura revisada y referencias documentadas.

## Fase 1 — Inventario de la consola
**Estado:** BLOCKED — falta identificar la consola.

- [ ] Fotografiar la etiqueta de modelo CUH y registrar revisión visible.
- [ ] Consultar y registrar firmware exacto sin actualizarlo.
- [ ] Registrar si la consola arranca normalmente y si el lector/disco funcionan.
- [ ] Registrar síntomas de temperatura, ruido, apagados y conectores.
- [ ] Identificar capacidad y estado del almacenamiento sin borrarlo.
- [ ] Decidir si hace falta preservar partidas o datos.

**Puerta de salida:** ficha de hardware completa; sin acciones destructivas.

## Fase 2 — Auditoría de upstream y licencias
**Estado:** IN_PROGRESS — auditoría de código completada 2026-10-15; quedan dependencias de terceros sin auditar.

- [x] Leer los README de PS4-Linux y ps4-linux-loader.
- [x] Inspeccionar scripts de construcción de imagen y escritura USB.
- [x] Inspeccionar el código fuente del payload (`main-aio.c`, `ps4-kexec-common/*`), no solo el README — ver [`docs/UPSTREAM_CODE_MAP.md`](UPSTREAM_CODE_MAP.md).
- [x] Revisar releases y comparar fechas/changelog contra el código del commit auditado — ver [`docs/EVIDENCE_SOURCES.md`](EVIDENCE_SOURCES.md) §2.
- [x] Revisar issues y un pull request mergeado relevantes (EDID, reportes de compatibilidad) — ver `EVIDENCE_SOURCES.md` §3.
- [x] Comparar soporte declarado por firmware, southbridge y kernel, con nivel de evidencia por fila — ver [`docs/COMPATIBILITY_MATRIX.md`](COMPATIBILITY_MATRIX.md).
- [x] Registrar hashes de los artefactos de `X-F1REBALL-X/PS4-Linux` auditados — ver `UPSTREAM_CODE_MAP.md` §2.3.
- [ ] Auditar las dependencias de terceros no incluidas en ninguno de los dos repos (kernel "Strawberry", Psxitarch/better-initramfs, rootfs Erkkola, paquetes Mesa de centi07/DionKill, `Al-Azif/ps4-skeleton`, `ArabPixel/ps4-linux-payloads`, GoldHEN) — listadas en `EVIDENCE_SOURCES.md` §5, ninguna auditada todavía.
- [ ] Identificar licencia exacta de cada una de esas dependencias antes de redistribuir o modificar el rootfs/initramfs.
- [x] No reutilizar código sin confirmar la licencia aplicable — mantenido; ver hallazgo de licencias mixtas (BSD-2 en `ps4-kexec-common`, GPLv2 en el kernel, GPL-3 solo sobre guía/scripts) en `UPSTREAM_CODE_MAP.md` §1.3/§2.8.

**Puerta de salida (cumplida para el código propio de ambos repos; pendiente para dependencias de terceros):** matriz de compatibilidad con fuente y nivel de confianza → entregada en `docs/COMPATIBILITY_MATRIX.md`.

**Hallazgo que afecta la Fase 1 original de este roadmap (releer antes de continuar):** la Fase 1 (Inventario de la consola) asume implícitamente que el flujo de arranque puede mantenerse 100% externo. La auditoría de código encontró que el procedimiento *recomendado por la distribución* `X-F1REBALL-X/PS4-Linux` requiere copiar el kernel al almacenamiento interno (`/data/linux/boot/`), aunque el *código del loader* sí soporta un flujo USB-only. Esto es una decisión pendiente, no un hallazgo que se pueda resolver en esta fase — ver Fase 3 corregida abajo y D-006 en `docs/DECISION_LOG.md`.

## Fase 3 — Selección del método de arranque
**Estado:** BLOCKED — requiere fase 1 **y** la decisión D-006 (ubicación del kernel: interno vía FTP vs. USB-only). El procedimiento completo, con citas de código línea por línea, ya está documentado en [`docs/BOOT_FLOW.md`](BOOT_FLOW.md) — esta fase pasa a ejecutarse, no a investigarse, en cuanto D-006 se resuelva.

- [x] Confirmar si existe un exploit/payload compatible con el firmware registrado — mecanismo documentado en `BOOT_FLOW.md` Fase 0 y 3-4 (depende de GoldHEN, no auditado). La lista exacta de 20 firmwares con offsets reales está en `UPSTREAM_CODE_MAP.md` §1.7, no solo en el README.
- [x] Confirmar requisitos y riesgos del método seleccionado — ver `docs/TROUBLESHOOTING.md` y la matriz de riesgos de código en `UPSTREAM_CODE_MAP.md` §1.6 (tratamiento asimétrico de southbridges).
- [ ] Elegir kernel según revisión/southbridge; no inferir solo por "Fat/Slim/Pro" — mecanismo de detección en runtime (`sysctlbyname`) documentado en `UPSTREAM_CODE_MAP.md` §1.3 paso 5; falta ejecutarlo sobre hardware real (Fase 1).
- [ ] **Decisión D-006 (nueva, bloqueante):** ¿se acepta copiar `bzImage`+`initramfs.cpio.gz` a `/data/linux/boot/` (procedimiento oficial de la distribución, modifica el almacenamiento interno de forma acotada y reversible) o se adapta `tools/build-img.sh` para mantener el flujo 100% USB que el propio código del loader permite? Ver `docs/BOOT_FLOW.md` Fase 2 y `docs/DECISION_LOG.md`.
- [x] Definir ruta de rollback para cada paso — ver `docs/BOOT_FLOW.md` Fase 6 y `docs/TROUBLESHOOTING.md`.
- [x] Registrar qué cambios persisten en el sistema original, si los hubiera — documentado explícitamente como pendiente de decisión (D-006), no como hecho consumado.
- [x] Ensayar el procedimiento documentalmente antes de ejecutarlo — `docs/BOOT_FLOW.md` y `docs/TEST_PLAN.md` (TP-01 a TP-07) cumplen esto.

**Puerta de salida:** procedimiento específico revisado y documentado (cumplida); ejecución real pendiente de D-006 + Fase 1.

## Fase 4 — Herramientas seguras de preparación USB
**Estado:** PLANNED. **Nota de auditoría:** `X-F1REBALL-X/PS4-Linux` ya trae `tools/build-img.sh` y `tools/write-img.ps1`, auditados línea por línea en `docs/UPSTREAM_CODE_MAP.md` §2.4-2.5. Confirmado: `write-img.ps1` **no** permite omitir las comprobaciones de BusType/IsBoot/IsSystem/tamaño con `-Force` (solo omite la reconfirmación manual del número de disco) — esto es mejor de lo que `docs/UPSTREAM_AUDIT.md` había asumido inicialmente. Evaluar reutilizar/envolver estos scripts en vez de reescribirlos desde cero antes de construir `ps4lab build-image`/`ps4lab write-usb`.

- [ ] `inspect-host`: sistema operativo, herramientas disponibles, espacio y permisos.
- [ ] `verify-artifacts`: SHA-256, tamaño, formato y manifiesto.
- [ ] `inspect-disks`: lista discos con modelo, tamaño, bus, serial y particiones.
- [ ] `build-usb-image`: construcción en entorno temporal; no borrar archivos arbitrarios.
- [ ] `write-usb-image`: modo seguro, reidentificación del disco, doble confirmación.
- [ ] `verify-usb-image`: lectura de muestra o verificación completa posterior a escritura.
- [ ] `collect-diagnostics`: empaqueta logs sin secretos ni identificadores innecesarios.
- [ ] Tests con dispositivos virtuales/archivos de imagen; nunca con discos reales por defecto.

**Puerta de salida:** tests automáticos demuestran que los casos ambiguos o peligrosos abortan.

## Fase 5 — Preparación y primer arranque externo
**Estado:** BLOCKED — depende de fases 1–4. Procedimiento detallado con tiempos y señales esperadas (LED, video) ya documentado en [`docs/BOOT_FLOW.md`](BOOT_FLOW.md) Fases 1-6 y ejecutable como casos TP-01 a TP-07 de [`docs/TEST_PLAN.md`](TEST_PLAN.md).

- [ ] Crear imagen USB en una PC.
- [ ] Verificar hashes y estructura de particiones.
- [ ] Comprobar etiqueta de rootfs e initramfs.
- [ ] Confirmar ausencia de kernels ambiguos que puedan ser seleccionados por error.
- [ ] Ejecutar payload según procedimiento validado.
- [ ] Registrar indicador luminoso, pantalla, tiempos y resultado.
- [ ] Si falla, cambiar una sola variable por intento.
- [ ] Verificar reinicio normal a OrbisOS.

**Puerta de salida:** arranque Linux reproducible desde USB y retorno al sistema original.

## Fase 6 — Diagnóstico y estabilización
**Estado:** PLANNED. Árboles de diagnóstico específicos para esta pila (no genéricos) ya redactados en [`docs/TROUBLESHOOTING.md`](TROUBLESHOOTING.md), con casos derivados de issues reales del upstream (LED blanca/no-handoff, rootfs no monta, EDID). Ejecutable como caso TP-08 de `TEST_PLAN.md`.

- [ ] Inventario de CPU, RAM, GPU, kernel, módulos y firmware.
- [ ] Probar Ethernet, Wi-Fi, Bluetooth, USB, audio HDMI y mando.
- [ ] Medir temperaturas y comportamiento de ventiladores.
- [ ] Desactivar suspensión/hibernación si el kernel no la soporta.
- [ ] Verificar integridad del filesystem tras apagado controlado.
- [ ] Definir perfiles de carga y límites térmicos conservadores.
- [ ] Documentar recuperación desde consola/rescue shell.

**Puerta de salida:** sesión estable y periféricos esenciales caracterizados.

## Fase 7 — Rendimiento gráfico y videojuegos
**Estado:** PLANNED. Protocolo de medición (qué comandos correr, qué invalida una medición, qué ya sabemos por código sobre el reloj fijo de GPU) en [`docs/GPU_AND_LLM_RESEARCH.md`](GPU_AND_LLM_RESEARCH.md) §1 y §3. Único dato de terceros disponible (no verificado por nosotros): issue [#10](https://github.com/ps4-linux/ps4-linux-loader/issues/10) reporta RADV/Vulkan 1.2.145 y Proton 10 funcionando en CUH-2208B. Ejecutable como caso TP-09.

- [ ] Identificar driver y versión de Mesa.
- [ ] Capturar `glxinfo -B`, `vulkaninfo --summary` si aplica, `dmesg` y módulos.
- [ ] Confirmar si el render es hardware o software.
- [ ] Ejecutar pruebas gráficas breves y reproducibles.
- [ ] Probar emuladores/juegos individualmente, con FPS, resolución, temperatura y estabilidad.
- [ ] Distinguir compatibilidad del juego, rendimiento y estabilidad del sistema.

**Puerta de salida:** matriz de resultados; no asumir compatibilidad por tener escritorio.

## Fase 8 — GPU compute y LLM
**Estado:** PLANNED; investigación de alto riesgo técnico. Protocolo completo (orden obligatorio CPU-baseline → exploración GPU, qué no instalar sin evidencia previa, criterio de descarte explícito) en [`docs/GPU_AND_LLM_RESEARCH.md`](GPU_AND_LLM_RESEARCH.md) §4. Pendiente adicional identificado: no se investigó en esta auditoría si existe soporte ROCm o Vulkan-compute maduro para esta generación GCN — es el primer vacío a cerrar, antes de cualquier prueba. Ejecutable como casos TP-10/TP-11.

- [ ] Identificar APIs de cómputo realmente disponibles en la GPU.
- [ ] Comprobar compatibilidad de Vulkan/OpenCL/ROCm u otros backends sin asumir soporte.
- [ ] Evaluar primero inferencia CPU como baseline.
- [ ] Probar un modelo pequeño cuantizado con parámetros registrados.
- [ ] Medir tokens/s, RAM disponible, VRAM reservada, latencia, temperatura y errores.
- [ ] Comparar GPU frente a CPU; abandonar aceleración GPU si el coste de compatibilidad supera el beneficio.
- [ ] No instalar toolchains pesadas antes de validar la base gráfica.

**Puerta de salida:** benchmark reproducible y conclusión basada en mediciones.

## Fase 9 — Automatización de reparación
**Estado:** PLANNED

- [ ] Árbol de diagnóstico por síntoma.
- [ ] Modo `--dry-run` obligatorio en utilidades de reparación.
- [ ] Backups antes de editar configuración.
- [ ] Restauración atómica de archivos.
- [ ] Recolección de logs con redacción de datos sensibles.
- [ ] Pruebas de fallo inducido sobre imágenes de laboratorio.
- [ ] Runbook de pantalla negra, kernel incorrecto, USB no detectado, rescue shell, red y filesystem.
- [ ] Separar recuperación de Linux de recuperación del firmware de PS4.

**Puerta de salida:** cada reparación tiene precondiciones, validación posterior y rollback.

## Fase 10 — Decisión de uso final
**Estado:** PLANNED

- [ ] Comparar utilidad real como mini-PC, consola de emulación y servidor headless.
- [ ] Comparar coste/consumo/ruido con hardware alternativo disponible.
- [ ] Definir si vale la pena mantenerlo permanentemente en Linux o usar arranque ocasional.
- [ ] Documentar limitaciones no resueltas y tareas descartadas.
