# Roadmap

Estados: `PLANNED`, `IN_PROGRESS`, `BLOCKED`, `VERIFIED` y `REJECTED`. Una puerta de salida requiere evidencia registrada; una declaración upstream no equivale a validación propia.

## Fase 0 — Inicialización y gobernanza
**Estado:** COMPLETADA en alcance inicial; mantenimiento continuo.
- [x] Crear repositorio privado `martinezmarcos93/ps4-linux-lab`.
- [x] Incorporar README y documentos base.
- [x] Registrar riesgos y prioridad de almacenamiento externo.
- [ ] Revisar enlaces/estados después de cada barrido.
- [ ] Definir política de protección de `main` y CI cuando existan checks automáticos.
- [ ] Definir retención y almacenamiento de logs/artefactos.

**Salida:** documentos de gobernanza coherentes; no implica soporte de hardware.

## Fase 1 — Identificación de consola
**Estado:** PARCIAL — firmware 13.52 observado, familia Slim inferida y capacidad 861,4 GB observada; CUH/southbridge desconocidos. Registro: [`docs/lab-logs/LAB-000-identificacion-consola.md`](lab-logs/LAB-000-identificacion-consola.md). Ejecutable como caso **TP-01** de [`docs/TEST_PLAN.md`](TEST_PLAN.md).
- [ ] Registrar modelo CUH y revisión visible.
- [ ] Registrar firmware exacto sin actualizarlo.
- [ ] Registrar estado de arranque original y síntomas existentes.
- [ ] Determinar qué datos requieren respaldo.
- [ ] Clasificar identificación de southbridge como hecho, inferencia o desconocido — el mecanismo real de detección en runtime (`sysctlbyname("hw.sce_subsys_subid")`) está documentado en [`docs/UPSTREAM_CODE_MAP.md`](UPSTREAM_CODE_MAP.md) §1.3 paso 5; es el dato que permitiría avanzar las filas "Untested" de [`docs/COMPATIBILITY_MATRIX.md`](COMPATIBILITY_MATRIX.md), pero solo se obtiene ejecutando el payload, no antes.

**Salida:** ficha de hardware y procedencia de cada dato, sin acciones destructivas.

## Fase 2 — Auditoría de upstream y licencias
**Estado:** IN_PROGRESS — auditoría de código completada 2026-10-15; quedan dependencias de terceros sin auditar.
- [x] Leer los README de PS4-Linux y ps4-linux-loader.
- [x] Inspeccionar scripts de construcción de imagen y escritura USB.
- [x] Inspeccionar el código fuente del payload (`main-aio.c`, `ps4-kexec-common/*`), no solo el README — ver [`docs/UPSTREAM_CODE_MAP.md`](UPSTREAM_CODE_MAP.md).
- [x] Fijar y registrar los commits exactos consultados de cada repositorio — ver `UPSTREAM_CODE_MAP.md`, cabecera.
- [x] Revisar releases y comparar fechas/changelog contra el código del commit auditado — ver [`docs/EVIDENCE_SOURCES.md`](EVIDENCE_SOURCES.md) §2.
- [x] Revisar issues y un pull request mergeado relevantes (EDID, reportes de compatibilidad) — ver `EVIDENCE_SOURCES.md` §3.
- [x] Contrastar compatibilidad por firmware, southbridge, kernel y loader, con nivel de evidencia por fila — ver [`docs/COMPATIBILITY_MATRIX.md`](COMPATIBILITY_MATRIX.md).
- [x] Registrar hashes de los artefactos de `X-F1REBALL-X/PS4-Linux` auditados — ver `UPSTREAM_CODE_MAP.md` §2.3.
- [x] No reutilizar código sin confirmar la licencia aplicable — mantenido; hallazgo de licencias mixtas (BSD-2 en `ps4-kexec-common`, GPLv2 en el kernel, GPL-3 solo sobre guía/scripts) en `UPSTREAM_CODE_MAP.md` §1.3/§2.8.
- [ ] Auditar las dependencias de terceros no incluidas en ninguno de los dos repos (kernel "Strawberry", Psxitarch/better-initramfs, rootfs Erkkola, paquetes Mesa de centi07/DionKill, `Al-Azif/ps4-skeleton`, `ArabPixel/ps4-linux-payloads`, GoldHEN) — listadas en `EVIDENCE_SOURCES.md` §5, ninguna auditada todavía.
- [ ] Identificar licencia exacta de cada una de esas dependencias antes de redistribuir o modificar el rootfs/initramfs.

**Puerta de salida (cumplida para el código propio de ambos repos; pendiente para dependencias de terceros):** matriz de compatibilidad con fuente y nivel de confianza → entregada en `docs/COMPATIBILITY_MATRIX.md`.

**Hallazgo que afecta la Fase 1 (releer antes de continuar):** la Fase 1 asume implícitamente que el flujo de arranque puede mantenerse 100% externo. La auditoría de código encontró que el procedimiento *recomendado por la distribución* `X-F1REBALL-X/PS4-Linux` requiere copiar el kernel al almacenamiento interno (`/data/linux/boot/`), aunque el *código del loader* sí soporta un flujo USB-only. Es una decisión pendiente, no algo que se resuelva en esta fase — ver Fase 3 y D-008 en `docs/DECISION_LOG.md`.

## Fase 2.1 — Auditoría estática del exploit/payload para firmware 13.52
**Estado:** IN_PROGRESS — análisis del JavaScript documentado; payload nativo sin auditar.
- [x] Registrar hashes del repositorio de exploit consultado y distinguirlo del payload.
- [x] Revisar estáticamente el JavaScript y documentar el alcance y las limitaciones.
- [x] Registrar que el hash del payload no corresponde a una release oficial de GoldHEN verificada.
- [ ] Reproducir el hash del binario desde el commit upstream fijado.
- [ ] Desensamblar offline con Rizin/objdump si están disponibles; registrar versión, arquitectura y dirección base asumida.
- [ ] Documentar regiones que no se pueden interpretar y evitar conclusiones basadas solo en strings.
- [ ] Contrastar con un artefacto oficial verificable si se consigue una referencia fiable.
- [ ] Mantener el payload fuera de la consola hasta cerrar la revisión y las puertas de seguridad.
- [ ] No instalar REA ni cambiar configuración de agentes hasta demostrar necesidad.
**Salida:** informe reproducible de análisis estático, sin ejecución del payload.

## Fase 3 — Selección del método de arranque
**Estado:** BLOCKED — requiere Fase 1 **y** la decisión D-008 (ubicación del kernel: interno vía FTP vs. USB-only). El procedimiento completo, con citas de código línea por línea, ya está documentado en [`docs/BOOT_FLOW.md`](BOOT_FLOW.md) — esta fase pasa a ejecutarse, no a investigarse, en cuanto D-008 se resuelva.
- [x] Confirmar si existe un exploit/payload compatible con el firmware registrado — mecanismo documentado en `BOOT_FLOW.md` Fases 0 y 3-4 (depende de GoldHEN, no auditado). La lista exacta de 20 firmwares con offsets reales está en `UPSTREAM_CODE_MAP.md` §1.7, no solo en el README.
- [x] Confirmar requisitos y riesgos del método seleccionado — ver `docs/TROUBLESHOOTING.md` y el tratamiento asimétrico de southbridges en `UPSTREAM_CODE_MAP.md` §1.6.
- [ ] Elegir kernel según revisión/southbridge; no inferir solo por "Fat/Slim/Pro" — mecanismo de detección en runtime documentado, falta ejecutarlo sobre hardware real (Fase 1).
- [ ] **Decisión D-008 (bloqueante):** ¿se acepta copiar `bzImage`+`initramfs.cpio.gz` a `/data/linux/boot/` (procedimiento oficial de la distribución, modifica el almacenamiento interno de forma acotada y reversible) o se adapta `tools/build-img.sh` para mantener el flujo 100% USB que el propio código del loader permite? Ver `docs/BOOT_FLOW.md` Fase 2 y `docs/DECISION_LOG.md`.
- [x] Definir ruta de rollback para cada paso — ver `docs/BOOT_FLOW.md` Fase 6 y `docs/TROUBLESHOOTING.md`.
- [x] Registrar qué cambios persisten en el sistema original, si los hubiera — documentado explícitamente como pendiente de decisión (D-008), no como hecho consumado.
- [x] Ensayar el procedimiento documentalmente antes de ejecutarlo — `docs/BOOT_FLOW.md` y `docs/TEST_PLAN.md` (TP-01 a TP-07) cumplen esto.

**Puerta de salida:** procedimiento específico revisado y documentado (cumplida); ejecución real pendiente de D-008 + Fase 1.

## Fase 4 — Herramientas USB seguras
**Estado:** IN_PROGRESS — primera utilidad host-side de verificación implementada; inspección de imágenes y discos aún pendientes. **Nota de auditoría:** `X-F1REBALL-X/PS4-Linux` ya trae `tools/build-img.sh` y `tools/write-img.ps1`, auditados línea por línea en `docs/UPSTREAM_CODE_MAP.md` §2.4-2.5. Confirmado: `write-img.ps1` **no** permite omitir las comprobaciones de BusType/IsBoot/IsSystem/tamaño con `-Force` (solo omite la reconfirmación manual del número de disco) — esto corrige una imprecisión de `docs/UPSTREAM_AUDIT.md`. Evaluar reutilizar/envolver estos scripts en vez de reescribirlos desde cero.
- [ ] `inspect-host`/`doctor`: sistema operativo, herramientas disponibles, espacio y permisos.
- [x] Primera versión de `verify-artifacts`: SHA-256, tamaño opcional y manifiesto JSON de solo lectura (`tools/verify_artifacts.py`). Formato y uso: `docs/ARTIFACT_MANIFEST.md`.
- [ ] Ampliar `verify-artifacts` con procedencia, versión y formato de artefacto cuando exista un manifiesto fuente verificable.
- [ ] `inspect-disks`: lista discos con modelo, tamaño, bus, serial y particiones.
- [ ] `build-usb-image`: construcción en directorio temporal único; limpiar solo archivos propios, no borrar rutas arbitrarias.
- [ ] `write-usb-image`: modo seguro, reidentificación del disco justo antes de escribir, doble confirmación, sin bypass genérico tipo `--force` que elimine las comprobaciones estructurales.
- [ ] `verify-usb-image`: lectura de muestra o verificación completa posterior a escritura.
- [ ] `collect-diagnostics`: empaqueta logs sin secretos ni identificadores innecesarios.
- [ ] Añadir `--dry-run` comprobable a toda herramienta con efectos secundarios.
- [x] Tests unitarios para hash correcto/incorrecto, tamaño, archivo ausente, archivo vacío, JSON inválido, manifiesto vacío, hash inválido, rutas absolutas/traversal y symlinks (`tests/test_verify_artifacts.py`). 11/11 pasan en sandbox local; CI remoto pendiente de confirmar.
- [ ] Tests de integración con imágenes virtuales; nunca con discos reales por defecto.

Ver también [`docs/SAFETY_AND_TOOLING.md`](SAFETY_AND_TOOLING.md) para los requisitos de seguridad detallados (manifiesto, logging/privacidad, reglas de escritura física) que estas herramientas deben cumplir antes de implementarse.

**Puerta de salida:** tests automáticos demuestran que los casos ambiguos o peligrosos abortan (destino ambiguo, disco de sistema, tamaño insuficiente, confirmación ausente).

## Fase 5 — Preparación de medio externo
**Estado:** BLOCKED — depende de las fases 1-4 y de la procedencia/licencias. Ejecutable como casos **TP-02 a TP-04** de `docs/TEST_PLAN.md`.
- [ ] Construir imagen reproducible en PC (`tools/build-img.sh` o equivalente propio).
- [ ] Verificar hashes, formato, particiones, etiquetas y espacio.
- [ ] Confirmar correspondencia kernel/initramfs/rootfs con el hardware identificado en Fase 1.
- [ ] Evitar kernels ambiguos según el loader (no dejar un `bzImage` sin nombre especial en el USB si el flujo elegido depende del interno — ver `docs/BOOT_FLOW.md` Fase 1).
- [ ] Validar el procedimiento con imagen virtual antes de escribir a un disco real.

**Salida:** artefacto USB reproducible y validado antes de conectar a la consola.

## Fase 6 — Primer arranque Linux
**Estado:** BLOCKED — no hay consola identificada ni medio aprobado, y depende de la decisión D-008. Procedimiento detallado con tiempos y señales esperadas (LED, video) en [`docs/BOOT_FLOW.md`](BOOT_FLOW.md) Fases 3-6; árboles de diagnóstico ante fallo en [`docs/TROUBLESHOOTING.md`](TROUBLESHOOTING.md); ejecutable como casos **TP-05 a TP-07** de `docs/TEST_PLAN.md`.
- [ ] Ejecutar solo el procedimiento específico aprobado (no genérico).
- [ ] Registrar vídeo, indicador luminoso (LED), tiempos y logs.
- [ ] Cambiar una sola variable por intento ante un fallo.
- [ ] Clasificar la etapa del fallo (USB / exploit-kernel / rootfs / firmware-southbridge) usando la tabla resumen de `docs/TROUBLESHOOTING.md` §8.
- [ ] Verificar retorno al sistema original tras cada intento.

**Salida:** arranque externo reproducible y regreso comprobado.

## Fase 7 — Estabilidad y periféricos
**Estado:** PLANNED. Casos conocidos (Bluetooth a re-emparejar cada arranque, Wi-Fi 5GHz en pruebas, suspensión deshabilitada) documentados en [`docs/TROUBLESHOOTING.md`](TROUBLESHOOTING.md) §6. Ejecutable como caso **TP-08** de `docs/TEST_PLAN.md`.
- [ ] Inventariar CPU, RAM, GPU, kernel, módulos y driver (`lspci -k`, `dmesg`, `free -h`).
- [ ] Probar red, audio, USB, Bluetooth, HDMI y mandos por separado.
- [ ] Medir temperatura y estabilidad bajo carga progresiva.
- [ ] Documentar filesystem y modo rescate.

**Salida:** perfil estable durante una ventana definida; periféricos esenciales caracterizados.

## Fase 8 — GPU, juegos y emulación
**Estado:** PLANNED. Protocolo de medición (qué comandos correr, qué invalida una medición, qué ya sabemos por código sobre el reloj fijo de GPU) en [`docs/GPU_AND_LLM_RESEARCH.md`](GPU_AND_LLM_RESEARCH.md) §1 y §3. Único dato de terceros disponible (no verificado por nosotros): issue [#10](https://github.com/ps4-linux/ps4-linux-loader/issues/10) reporta RADV/Vulkan 1.2.145 y Proton 10 funcionando en CUH-2208B. Ejecutable como caso **TP-09**.
- [ ] Distinguir renderizado hardware/software (`glxinfo -B`, `vulkaninfo --summary`) antes de cualquier FPS.
- [ ] Capturar capacidades reales de OpenGL/Vulkan, versión de Mesa y módulos cargados.
- [ ] Definir benchmarks breves y reproducibles (2 corridas mínimo, en arranques distintos).
- [ ] Probar cada aplicación/emulador individualmente.
- [ ] Registrar resolución, settings, FPS, temperatura, duración y fallos.
- [ ] Distinguir compatibilidad del juego, rendimiento y estabilidad del sistema — no asumir compatibilidad solo por tener escritorio.

**Salida:** matriz de resultados basada en mediciones propias, no en reportes de terceros.

## Fase 9 — Cómputo GPU y LLM
**Estado:** PLANNED; incertidumbre alta. Protocolo completo (orden obligatorio CPU-baseline → exploración GPU, qué no instalar sin evidencia previa, criterio de descarte explícito) en [`docs/GPU_AND_LLM_RESEARCH.md`](GPU_AND_LLM_RESEARCH.md) §4. **Pendiente adicional (pregunta Q-008 de `DECISION_LOG.md`):** no se investigó en la auditoría de esta sesión si existe soporte ROCm o Vulkan-compute maduro para esta generación GCN — es el primer vacío a cerrar antes de cualquier prueba. Ejecutable como casos **TP-10/TP-11**.
- [ ] Registrar baseline de CPU: tokens/s, RAM, temperatura, sin ningún backend GPU.
- [ ] Identificar APIs de cómputo realmente disponibles en la GPU (no asumir soporte de Vulkan-compute/OpenCL/ROCm).
- [ ] Elegir un modelo pequeño cuantizado y fijar sus parámetros para que la comparación CPU/GPU sea válida.
- [ ] Medir tokens/s, RAM disponible, VRAM reservada, latencia, temperatura y errores exactos si un backend GPU falla al inicializar.
- [ ] Comparar GPU frente al baseline de CPU en condiciones equivalentes.
- [ ] Descartar la aceleración GPU, con la evidencia que lo sostenga, si el coste de hacerla funcionar supera el beneficio medido.
- [ ] No instalar toolchains pesadas (ROCm, etc.) antes de validar que existe un backend viable para esta GPU.

**Salida:** benchmark reproducible y decisión documentada en `docs/DECISION_LOG.md`, sea cual sea el resultado.

## Fase 10 — Diagnóstico y recuperación
**Estado:** PLANNED. Árboles de diagnóstico específicos para esta pila (no genéricos) ya redactados en [`docs/TROUBLESHOOTING.md`](TROUBLESHOOTING.md), con casos derivados de issues reales del upstream (LED blanca/sin handoff, rootfs no monta, bug de EDID). Ver también [`docs/RECOVERY_STRATEGY.md`](RECOVERY_STRATEGY.md) para los niveles generales de recuperación.
- [ ] Árbol de diagnóstico por síntoma (ya cubierto para los síntomas conocidos en `TROUBLESHOOTING.md`; ampliar con los que aparezcan en pruebas propias).
- [ ] Herramientas de solo lectura para recolección de logs.
- [ ] Backup antes de editar cualquier configuración; restauración atómica.
- [ ] `--dry-run` en toda acción futura con efectos secundarios.
- [ ] Tests de fallos inducidos sobre imágenes de laboratorio, nunca sobre la consola real.
- [ ] Separar siempre recuperación de Linux de recuperación del firmware original de la PS4 — esta última queda fuera del alcance de cualquier script de este proyecto (Nivel 5 de `RECOVERY_STRATEGY.md`).

**Salida:** cada reparación incluye precondiciones, condición de aborto, verificación posterior y rollback.

## Fase 11 — Decisión de uso final
**Estado:** PLANNED.
- [ ] Comparar utilidad real como mini-PC, equipo de emulación, servidor headless o nodo de inferencia, con mediciones propias (no expectativas).
- [ ] Comparar consumo, ruido, limitaciones y mantenimiento contra alternativas de hardware disponibles.
- [ ] Identificar tareas que no justifican más investigación y documentar por qué.
- [ ] Documentar limitaciones no resueltas y conclusión final.

**Salida:** decisión respaldada por evidencia registrada, no por expectativas iniciales.

## Dependencias críticas
- Fase 1 bloquea las fases 3, 5 y 6.
- Fase 2 bloquea la selección/reutilización de componentes (y la decisión D-008 de Fase 3).
- Fase 4 puede avanzar en la PC usando solo archivos/imágenes virtuales, sin esperar a la Fase 1.
- Las fases 8 y 9 esperan arranque y estabilidad reproducibles (fases 6 y 7).
