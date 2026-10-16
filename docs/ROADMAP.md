# Roadmap

**Estado de fase:** `PLANNED`, `IN_PROGRESS`, `BLOCKED`, `COMPLETADA`, `VERIFIED` o `REJECTED`. `VERIFIED` solo se usa con prueba propia en hardware (etiqueta `LAB`) y registro con hashes: documentación, código escrito o reportes de terceros **nunca** lo justifican (D-020).

**Etiqueta de evidencia de cada tarea** (de menor a mayor fuerza):

| Etiqueta | Significado |
|---|---|
| `PENDIENTE` / `BLOQUEADO` | No hecho / no puede avanzar (se indica por qué) |
| `IMPLEMENTADO` | Existe el código o el documento; sin verificación independiente |
| `TERCEROS` | Lo afirma o reporta un tercero (README, issue); sin reproducción propia |
| `CÓDIGO` | Confirmado leyendo código o binarios upstream (revisión citada); no es prueba de ejecución |
| `TESTS` | Verificado por tests automáticos host-side (`bash scripts/check.sh`); no prueba comportamiento en la consola |
| `LAB` | Probado en laboratorio con la consola, con registro y hashes. **Ninguna tarea tiene esta etiqueta todavía.** |

Una puerta de salida requiere evidencia registrada; una declaración upstream no equivale a validación propia.

## Fase 0 — Inicialización y gobernanza
**Estado:** COMPLETADA en alcance inicial; mantenimiento continuo.
- [x] `IMPLEMENTADO` Crear repositorio privado `martinezmarcos93/ps4-linux-lab`.
- [x] `IMPLEMENTADO` Incorporar README y documentos base.
- [x] `IMPLEMENTADO` Registrar riesgos y prioridad de almacenamiento externo.
- [ ] `PENDIENTE` Revisar enlaces/estados después de cada barrido.
- [ ] `PENDIENTE` Definir política de protección de `main` y CI cuando existan checks automáticos.
- [ ] `PENDIENTE` Definir retención y almacenamiento de logs/artefactos.

**Salida:** documentos de gobernanza coherentes; no implica soporte de hardware.

## Fase 1 — Identificación de consola
**Estado:** PARCIAL — firmware 13.52 **observado**, modelo **CUH-2115B confirmado**, familia Slim confirmada por el modelo y capacidad 861,4 GB **observada**; southbridge **desconocido**. La identificación de la consola sigue incompleta y por eso **la selección de kernel no está resuelta**. Registro: [`docs/lab-logs/LAB-000-identificacion-consola.md`](lab-logs/LAB-000-identificacion-consola.md). Ejecutable como caso **TP-01** de [`docs/TEST_PLAN.md`](TEST_PLAN.md).
- [x] `IMPLEMENTADO` Registrar CUH-2115B confirmado en `docs/lab-logs/LAB-000-identificacion-consola.md` y `docs/COMPATIBILITY_MATRIX.md`.
- [ ] `PENDIENTE` Registrar firmware exacto sin actualizarlo.
- [ ] `PENDIENTE` Registrar estado de arranque original y síntomas existentes.
- [ ] `PENDIENTE` Determinar qué datos requieren respaldo.
- [ ] `PENDIENTE` Clasificar identificación de southbridge como hecho, inferencia o desconocido — el mecanismo real de detección en runtime (`sysctlbyname("hw.sce_subsys_subid")`) está documentado en [`docs/UPSTREAM_CODE_MAP.md`](UPSTREAM_CODE_MAP.md) §1.3 paso 5; es el dato que permitiría avanzar las filas "Untested" de [`docs/COMPATIBILITY_MATRIX.md`](COMPATIBILITY_MATRIX.md), pero solo se obtiene ejecutando el payload, no antes.

**Salida:** ficha de hardware y procedencia de cada dato, sin acciones destructivas.

## Fase 2 — Auditoría de upstream y licencias
**Estado:** IN_PROGRESS — auditoría de código completada 2026-10-15; quedan dependencias de terceros sin auditar.
- [x] `CÓDIGO` Leer los README de PS4-Linux y ps4-linux-loader.
- [x] `CÓDIGO` Inspeccionar scripts de construcción de imagen y escritura USB (hallazgos adicionales en `UPSTREAM_CODE_MAP.md` §2.4-2.5).
- [x] `CÓDIGO` Inspeccionar el código fuente del payload (`main-aio.c`, `ps4-kexec-common/*`), no solo el README — ver [`docs/UPSTREAM_CODE_MAP.md`](UPSTREAM_CODE_MAP.md).
- [x] `IMPLEMENTADO` Fijar y registrar los commits exactos consultados de cada repositorio — ver `UPSTREAM_CODE_MAP.md`, cabecera.
- [x] `CÓDIGO` Revisar releases y comparar fechas/changelog contra el código del commit auditado — ver [`docs/EVIDENCE_SOURCES.md`](EVIDENCE_SOURCES.md) §2.
- [x] `TERCEROS` Revisar issues y un pull request mergeado relevantes (EDID, reportes de compatibilidad) — ver `EVIDENCE_SOURCES.md` §3.
- [x] `IMPLEMENTADO` Contrastar compatibilidad por firmware, southbridge, kernel y loader, con nivel de evidencia por fila — ver [`docs/COMPATIBILITY_MATRIX.md`](COMPATIBILITY_MATRIX.md).
- [x] `IMPLEMENTADO` Registrar hashes de los artefactos de `X-F1REBALL-X/PS4-Linux` auditados — ver `UPSTREAM_CODE_MAP.md` §2.3.
- [x] `IMPLEMENTADO` No reutilizar código sin confirmar la licencia aplicable — mantenido; hallazgo de licencias mixtas (BSD-2 en `ps4-kexec-common`, GPLv2 en el kernel, GPL-3 solo sobre guía/scripts) en `UPSTREAM_CODE_MAP.md` §1.3/§2.8.
- [ ] `PENDIENTE` Auditar las dependencias de terceros (inventario y estado en [`docs/ARTIFACT_INVENTORY.md`](ARTIFACT_INVENTORY.md)) no incluidas en ninguno de los dos repos (kernel "Strawberry", Psxitarch/better-initramfs, rootfs Erkkola, paquetes Mesa de centi07/DionKill, `Al-Azif/ps4-skeleton`, `ArabPixel/ps4-linux-payloads`, GoldHEN) — listadas en `EVIDENCE_SOURCES.md` §5, ninguna auditada todavía.
- [ ] `PENDIENTE` Identificar licencia exacta de cada una de esas dependencias antes de redistribuir o modificar el rootfs/initramfs.

**Puerta de salida (cumplida para el código propio de ambos repos; pendiente para dependencias de terceros):** matriz de compatibilidad con fuente y nivel de confianza → entregada en `docs/COMPATIBILITY_MATRIX.md`.

**Hallazgo que afecta la Fase 1 (resuelto como política, no como propiedad demostrada):** el procedimiento *recomendado por la distribución* `X-F1REBALL-X/PS4-Linux` copia el kernel al almacenamiento interno (`/data/linux/boot/`); el *código del loader* lee de USB con prioridad pero **también** de rutas internas y puede mezclar orígenes. La decisión D-008 fija USB-only como arquitectura objetivo; que el flujo completo la cumpla sigue sin demostrarse — ver [`docs/USB_ONLY_DESIGN.md`](USB_ONLY_DESIGN.md).

## Fase 2.1 — Auditoría estática del exploit/payload para firmware 13.52
**Estado:** COMPLETADA CON LÍMITES (informe estático hecho; **no** es `VERIFIED`). Autorización de ejecución en hardware: **CERRADA**, a la espera del "sí" de Marcos (D-010, D-014). Ambos estados son independientes: avanzar la auditoría no desbloquea la ejecución.
- [x] `IMPLEMENTADO` Registrar hashes del repositorio de exploit consultado y distinguirlo del payload (`manifests/raw13g-9ba2f07.json`).
- [x] `CÓDIGO` Revisar estáticamente el JavaScript y documentar el alcance y las limitaciones.
- [x] `CÓDIGO` Registrar que el hash del payload no corresponde a una release oficial de GoldHEN verificada (el cuerpo declara `v2.4b18.12`; el último release oficial es `2.4b18`).
- [x] `TESTS` Análisis reproducible del arranque y del cuerpo zlib con `tools/payload_static.py` (16 tests con blobs ficticios; reproduce 636 760 B y `4e2864fb…`).
- [x] `CÓDIGO` Contrastar con un artefacto oficial: `GoldHEN_v2.4b18.7z` descargado y extraído (sha256 `d0c84c79…`); ~75 % de cadenas y ~65 % de ventanas de 16 bytes en común. **Es parentesco, no equivalencia**, y la referencia no es la versión exacta.
- [ ] `BLOQUEADO` Reproducir el hash del binario desde el commit upstream fijado: `raw13g` no publica código fuente del payload.
- [ ] `PENDIENTE` Desensamblar el cuerpo de 636 KB (hoy solo el arranque está leído, con desensamblado lineal); registrar herramienta, versión y dirección base.
- [ ] `PENDIENTE` Documentar las regiones no interpretadas con ventanas de entropía y sin conclusiones basadas solo en cadenas.
- [x] `IMPLEMENTADO` Mantener el payload fuera de la consola hasta cerrar la revisión y las puertas de seguridad.
- [x] `IMPLEMENTADO` No instalar REA ni cambiar configuración de agentes (D-011).
**Salida:** informe reproducible de análisis estático, sin ejecución del payload (`docs/EXPLOIT_AUDIT_13.52.md`). Conclusión sostenida: "identificable como GoldHEN, sin hosts ajenos en cadenas"; **no sostenida**: que sea seguro.

## Fase 3 — Selección del método de arranque
**Estado:** BLOQUEADA — la política está decidida (D-008: USB-only) pero **no validada**, y aunque el CUH-2115B ya está identificado, falta resolver el southbridge/compatibilidad, por lo que **no se puede elegir kernel**. Procedimiento con citas de código en [`docs/BOOT_FLOW.md`](BOOT_FLOW.md); diseño verificable en [`docs/USB_ONLY_DESIGN.md`](USB_ONLY_DESIGN.md).
- [x] `TERCEROS` Existe un exploit/payload que dice cubrir el firmware registrado (13.52): guías y repositorio `raw13g` (no verificado por nosotros); depende de GoldHEN (D-010). La lista de 20 firmwares con offsets está en `UPSTREAM_CODE_MAP.md` §1.7 (`CÓDIGO`).
- [x] `CÓDIGO` Requisitos y riesgos del método seleccionado — `docs/TROUBLESHOOTING.md` y `UPSTREAM_CODE_MAP.md` §1.6.
- [x] `TERCEROS` Investigación de evidencia de compatibilidad de CUH-2115B/FW 13.52 y de métodos para identificar el southbridge (2026-10-16): el modelo corresponde a **dos** southbridges posibles (wiki); procedimiento y criterios en [`KERNEL_SELECTION.md`](KERNEL_SELECTION.md). Es evidencia de terceros, no verificada en la consola.
- [ ] `BLOQUEADO` **Elegir kernel según revisión/southbridge.** No resuelto: el southbridge de la consola es desconocido y solo se obtiene ejecutando el payload (`GetSouthbridgeName()`), lo que exige autorización. Tabla de decisión por southbridge en `COMPATIBILITY_MATRIX.md` §7; no se selecciona ningún binario para esta consola.
- [x] `IMPLEMENTADO` Decisión D-008 tomada: USB-only como arquitectura objetivo; la escritura interna no es fallback (ver `DECISION_LOG.md`).
- [ ] `PENDIENTE` Demostrar que el flujo USB-only es una propiedad real. Hecho: loader original y parcheado **compilados** en contenedor sin red y comparados estáticamente (`TESTS`/`CÓDIGO`, `LOADER_BUILD_REPRO.md`). Falta: comprobar rutas internas vacías y observar el disco interno antes y después en laboratorio (`USB_ONLY_DESIGN.md` §4).
- [x] `IMPLEMENTADO` Ruta de rollback por paso — `BOOT_FLOW.md` Fase 6 y `TROUBLESHOOTING.md` (documental; no ensayada).
- [ ] `PENDIENTE` Registrar qué cambios persisten en el sistema original: por código, el loader no escribe archivos (D-017); falta probar el kernel/rootfs en runtime.
- [x] `IMPLEMENTADO` Ensayo documental del procedimiento — `BOOT_FLOW.md` y `TEST_PLAN.md` (TP-01 a TP-07); **ningún caso se ha ejecutado**.

**Puerta de salida:** procedimiento específico revisado y documentado (cumplida en lo documental); ejecución real bloqueada por la Fase 1 y por la validación de USB-only.

## Fase 4 — Herramientas USB seguras
**Estado:** IN_PROGRESS — verificación, inspección y construcción de imágenes **solo-archivo** implementadas y con tests; la escritura a medio físico **no se implementa a propósito** (queda como paso manual revisado). Suite local: `bash scripts/check.sh` (CI remoto bloqueado por facturación, `docs/CI_DIAGNOSIS.md`). Requisitos de seguridad en [`docs/SAFETY_AND_TOOLING.md`](SAFETY_AND_TOOLING.md).
- [ ] `PENDIENTE` `inspect-host`/`doctor`: sistema operativo, herramientas disponibles, espacio y permisos.
- [x] `TESTS` `verify_artifacts.py`: SHA-256, tamaño opcional y manifiesto JSON de solo lectura (`docs/ARTIFACT_MANIFEST.md`).
- [x] `TESTS` `verify_boot_chain.py`: cinco niveles independientes (estructura, integridad, formato, compatibilidad, arranque) con catálogo de procedencia (`manifests/arranque-catalogo.json`) y detección de mezcla de releases; 59 tests. **Un resultado OK no prueba que la consola arranque.**
- [x] `TESTS` `inspect_image.py`: MBR/GPT de imágenes (24 tests, con pruebas de mutación).
- [x] `TESTS` `fat32_add_file.py`: agrega archivos a la FAT de una imagen sin root, contrastado con `fsck.vfat -n` y 7z (12 tests).
- [x] `TESTS` `build_usb_image.py` (hallazgo R-IMG-01 cerrado: sin `fsck.vfat`/`e2fsck` la construcción falla salvo `--omitir-fsck`, que queda registrado como NO verificada; ext4 verificado con `e2fsck -fn`; informe `.informe.json`): construye un `.img` (nunca un dispositivo), sin root, con validación de rutas/entradas/tamaños y limpieza ante fallo (20 tests con imágenes de 72 MiB). **No ejecutado con el rootfs real** (requiere `fakeroot` para propietarios correctos).
- [x] `TESTS` `verify_loader_build.py` + `scripts/build_loader_isolated.sh`: compilación aislada que **no puede reportar éxito falso** (propaga el código de `make`, exige 9 ELF + 9 BIN + 20 `kexec.bin` válidos); 15 pruebas de inyección de fallos (23 en `tests/test_loader_build_script.py`) y 6 mutaciones detectadas. Entorno fijado por digest, snapshot y lock de paquetes (`docs/LOADER_BUILD_REPRO.md`).
- [x] `TESTS` `plan_usb_image_build.py` (origen: rama `chatgpt/image-build-preflight`, integrada): planificador de solo lectura del pipeline upstream, 13 tests; auditoría del pipeline en [`docs/BUILD_PIPELINE_SAFETY_AUDIT.md`](BUILD_PIPELINE_SAFETY_AUDIT.md).
- [x] `TESTS` `payload_static.py` y `elf_audit.py`: análisis estático de solo lectura de payloads y ELF (16 + 10 tests).
- [x] `TESTS` `loader_model.py`: modelo de la resolución de rutas upstream y de la variante USB-only (21 tests; incluye el parche).
- [ ] `PENDIENTE` `inspect-disks`: lista discos con modelo, tamaño, bus, serial y particiones.
- [ ] `BLOQUEADO` `write-usb-image`: no se implementa mientras no haya aprobación de Marcos para escribir en un dispositivo físico (límite del encargo); procedimiento propuesto en `USB_ONLY_DESIGN.md`/`SAFETY_AND_TOOLING.md`.
- [ ] `PENDIENTE` `verify-usb-image` posterior a la escritura; `collect-diagnostics`.
- [ ] `PENDIENTE` `--dry-run` en toda herramienta con efectos secundarios (hecho en `build_usb_image.py`).
- [x] `TESTS` Pruebas de integración con imágenes virtuales (`build_usb_image`, `fat32_add_file`); nunca con discos reales.

**Puerta de salida:** tests automáticos demuestran que los casos ambiguos o peligrosos abortan (destino ambiguo, disco de sistema, tamaño insuficiente, confirmación ausente) — cumplida para la construcción de imágenes; pendiente para la escritura física (no implementada).

## Fase 5 — Preparación de medio externo
**Estado:** BLOCKED — depende de la Fase 1 (southbridge → kernel) y de la procedencia/licencias. Ejecutable como casos **TP-02 a TP-04** de `docs/TEST_PLAN.md`.
- [ ] `BLOQUEADO` Construir/preparar la imagen de esta consola: **no se construyó** (D-022). Faltan el kernel (southbridge desconocido) y, para `build_usb_image.py`, un rootfs como directorio; la ruta A (`USB_ONLY_DESIGN.md` §8) parte de la imagen publicada y solo necesita el kernel elegido.
- [x] `TESTS` Inventario real de artefactos locales con hash, procedencia y formato (`tools/inventariar_artefactos.py`, 9 tests; `manifests/inventario-local-2026-10-16.json`). Imagen publicada verificada en solo lectura: `fsck.vfat -n` y `e2fsck -fn` rc 0.
- [x] `TESTS` Verificar formato, particiones y filesystem de la imagen de prueba (`fsck.vfat -n` sobre p1, lectura de p2 con `debugfs`).
- [ ] `BLOQUEADO` Confirmar correspondencia kernel/initramfs/rootfs con el hardware identificado: southbridge desconocido.
- [x] `IMPLEMENTADO` Política de kernel en el USB: el `bzImage` va **dentro de la FAT** (USB-only, D-008); no se usan kernels de repuesto renombrados para esta consola.
- [x] `TESTS` Validar el procedimiento con imagen virtual antes de escribir a un disco real (incluye una imagen de prueba con artefactos reales en una ubicación temporal, descartada).

**Salida:** artefacto USB reproducible y validado antes de conectar a la consola.

## Fase 6 — Primer arranque Linux
**Estado:** BLOCKED — no hay consola identificada ni medio aprobado, y la política USB-only (D-008) aún no está validada como propiedad técnica. Procedimiento detallado con tiempos y señales esperadas (LED, video) en [`docs/BOOT_FLOW.md`](BOOT_FLOW.md) Fases 3-6; árboles de diagnóstico ante fallo en [`docs/TROUBLESHOOTING.md`](TROUBLESHOOTING.md); ejecutable como casos **TP-05 a TP-07** de `docs/TEST_PLAN.md`.
- [ ] `PENDIENTE` Ejecutar solo el procedimiento específico aprobado (no genérico).
- [ ] `PENDIENTE` Registrar vídeo, indicador luminoso (LED), tiempos y logs.
- [ ] `PENDIENTE` Cambiar una sola variable por intento ante un fallo.
- [ ] `PENDIENTE` Clasificar la etapa del fallo (USB / exploit-kernel / rootfs / firmware-southbridge) usando la tabla resumen de `docs/TROUBLESHOOTING.md` §8.
- [ ] `PENDIENTE` Verificar retorno al sistema original tras cada intento.

**Salida:** arranque externo reproducible y regreso comprobado.

## Fase 7 — Estabilidad y periféricos
**Estado:** PLANNED. Casos conocidos (Bluetooth a re-emparejar cada arranque, Wi-Fi 5GHz en pruebas, suspensión deshabilitada) documentados en [`docs/TROUBLESHOOTING.md`](TROUBLESHOOTING.md) §6. Ejecutable como caso **TP-08** de `docs/TEST_PLAN.md`.
- [ ] `PENDIENTE` Inventariar CPU, RAM, GPU, kernel, módulos y driver (`lspci -k`, `dmesg`, `free -h`).
- [ ] `PENDIENTE` Probar red, audio, USB, Bluetooth, HDMI y mandos por separado.
- [ ] `PENDIENTE` Medir temperatura y estabilidad bajo carga progresiva.
- [ ] `PENDIENTE` Documentar filesystem y modo rescate.

**Salida:** perfil estable durante una ventana definida; periféricos esenciales caracterizados.

## Fase 8 — GPU, juegos y emulación
**Estado:** PLANNED. Protocolo de medición (qué comandos correr, qué invalida una medición, qué ya sabemos por código sobre el reloj fijo de GPU) en [`docs/GPU_AND_LLM_RESEARCH.md`](GPU_AND_LLM_RESEARCH.md) §1 y §3. Único dato de terceros disponible (no verificado por nosotros): issue [#10](https://github.com/ps4-linux/ps4-linux-loader/issues/10) reporta RADV/Vulkan 1.2.145 y Proton 10 funcionando en CUH-2208B. Ejecutable como caso **TP-09**.
- [ ] `PENDIENTE` Distinguir renderizado hardware/software (`glxinfo -B`, `vulkaninfo --summary`) antes de cualquier FPS.
- [ ] `PENDIENTE` Capturar capacidades reales de OpenGL/Vulkan, versión de Mesa y módulos cargados.
- [ ] `PENDIENTE` Definir benchmarks breves y reproducibles (2 corridas mínimo, en arranques distintos).
- [ ] `PENDIENTE` Probar cada aplicación/emulador individualmente.
- [ ] `PENDIENTE` Registrar resolución, settings, FPS, temperatura, duración y fallos.
- [ ] `PENDIENTE` Distinguir compatibilidad del juego, rendimiento y estabilidad del sistema — no asumir compatibilidad solo por tener escritorio.

**Salida:** matriz de resultados basada en mediciones propias, no en reportes de terceros.

## Fase 9 — Cómputo GPU y LLM
**Estado:** PLANNED; incertidumbre alta. Protocolo completo (orden obligatorio CPU-baseline → exploración GPU, qué no instalar sin evidencia previa, criterio de descarte explícito) en [`docs/GPU_AND_LLM_RESEARCH.md`](GPU_AND_LLM_RESEARCH.md) §4. **Pendiente adicional (pregunta Q-008 de `DECISION_LOG.md`):** la investigación bibliográfica (`GPU_AND_LLM_RESEARCH.md` §5) indica que ROCm no tiene soporte oficial para Liverpool y que Vulkan/RADV es un candidato experimental; es evidencia de terceros (`TERCEROS`) sin prueba en la consola. Ejecutable como casos **TP-10/TP-11**.
- [ ] `PENDIENTE` Registrar baseline de CPU: tokens/s, RAM, temperatura, sin ningún backend GPU.
- [ ] `PENDIENTE` Identificar APIs de cómputo realmente disponibles en la GPU (no asumir soporte de Vulkan-compute/OpenCL/ROCm).
- [ ] `PENDIENTE` Elegir un modelo pequeño cuantizado y fijar sus parámetros para que la comparación CPU/GPU sea válida.
- [ ] `PENDIENTE` Medir tokens/s, RAM disponible, VRAM reservada, latencia, temperatura y errores exactos si un backend GPU falla al inicializar.
- [ ] `PENDIENTE` Comparar GPU frente al baseline de CPU en condiciones equivalentes.
- [ ] `PENDIENTE` Descartar la aceleración GPU, con la evidencia que lo sostenga, si el coste de hacerla funcionar supera el beneficio medido.
- [ ] `PENDIENTE` No instalar toolchains pesadas (ROCm, etc.) antes de validar que existe un backend viable para esta GPU.

**Salida:** benchmark reproducible y decisión documentada en `docs/DECISION_LOG.md`, sea cual sea el resultado.

## Fase 10 — Diagnóstico y recuperación
**Estado:** PLANNED. Árboles de diagnóstico específicos para esta pila (no genéricos) ya redactados en [`docs/TROUBLESHOOTING.md`](TROUBLESHOOTING.md), con casos derivados de issues reales del upstream (LED blanca/sin handoff, rootfs no monta, bug de EDID). Ver también [`docs/RECOVERY_STRATEGY.md`](RECOVERY_STRATEGY.md) para los niveles generales de recuperación.
- [ ] `PENDIENTE` Árbol de diagnóstico por síntoma (ya cubierto para los síntomas conocidos en `TROUBLESHOOTING.md`; ampliar con los que aparezcan en pruebas propias).
- [ ] `PENDIENTE` Herramientas de solo lectura para recolección de logs.
- [ ] `PENDIENTE` Backup antes de editar cualquier configuración; restauración atómica.
- [ ] `PENDIENTE` `--dry-run` en toda acción futura con efectos secundarios.
- [ ] `PENDIENTE` Tests de fallos inducidos sobre imágenes de laboratorio, nunca sobre la consola real.
- [ ] `PENDIENTE` Separar siempre recuperación de Linux de recuperación del firmware original de la PS4 — esta última queda fuera del alcance de cualquier script de este proyecto (Nivel 5 de `RECOVERY_STRATEGY.md`).

**Salida:** cada reparación incluye precondiciones, condición de aborto, verificación posterior y rollback.

## Fase 11 — Decisión de uso final
**Estado:** PLANNED.
- [ ] `PENDIENTE` Comparar utilidad real como mini-PC, equipo de emulación, servidor headless o nodo de inferencia, con mediciones propias (no expectativas).
- [ ] `PENDIENTE` Comparar consumo, ruido, limitaciones y mantenimiento contra alternativas de hardware disponibles.
- [ ] `PENDIENTE` Identificar tareas que no justifican más investigación y documentar por qué.
- [ ] `PENDIENTE` Documentar limitaciones no resueltas y conclusión final.

**Salida:** decisión respaldada por evidencia registrada, no por expectativas iniciales.

## Dependencias críticas
- Fase 1 bloquea las fases 3, 5 y 6.
- Fase 2 bloquea la selección/reutilización de componentes.
- Fase 3 requiere Fase 1 (southbridge) y la validación de USB-only (`USB_ONLY_DESIGN.md` §4).
- Fase 4 puede avanzar en la PC usando solo archivos/imágenes virtuales, sin esperar a la Fase 1.
- Las fases 8 y 9 esperan arranque y estabilidad reproducibles (fases 6 y 7).
