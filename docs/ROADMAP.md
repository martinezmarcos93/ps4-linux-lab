# Roadmap

**Última revisión de estado:** 2026-10-16. Este roadmap distingue trabajo documental, inspección de código, tests host-side y pruebas físicas. No declarar una fase `VERIFIED` sin evidencia propia en hardware.

Auditoría cruzada documental 2026-10-16: [`docs/CROSS_DOC_AUDIT_2026-10-16.md`](CROSS_DOC_AUDIT_2026-10-16.md). Los cambios son documentales; no implican pruebas de hardware.

**Estado de fase:** `PLANNED`, `IN_PROGRESS`, `BLOCKED`, `COMPLETADA`, `VERIFIED` o `REJECTED`. `VERIFIED` solo se usa con prueba propia en hardware (etiqueta `LAB`) y registro con hashes: documentación, código escrito o reportes de terceros **nunca** lo justifican (D-020).

**Nota de consolidación (merge a main, 2026-10-16):** este archivo tenía fases duplicadas (`Fase 3`, `5`, `6`, `7`, `8` aparecían dos veces con contenidos distintos) porque las ramas `main` y `chatgpt/ps4-audit-roadmap` lo evolucionaron en paralelo sin renumerar. Se consolidó en una sola secuencia 0–12, conservando el contenido más reciente y mejor evidenciado de cada fase (ver [`docs/INTEGRACION_RAMAS_2026-10-16.md`](INTEGRACION_RAMAS_2026-10-16.md)).

## Escala de evidencia

| Etiqueta | Significado |
|---|---|
| `PENDIENTE` / `BLOQUEADO` | No hecho / no puede avanzar (se indica por qué) |
| `IMPLEMENTADO` | Existe el código o el documento; sin verificación independiente |
| `TERCEROS` | Lo afirma o reporta un tercero (README, issue); sin reproducción propia |
| `CÓDIGO` | Confirmado leyendo código o binarios upstream (revisión citada); no es prueba de ejecución |
| `TESTS` | Verificado por tests automáticos host-side (`bash scripts/check.sh`); no prueba comportamiento en la consola |
| `OBSERVADO` | Dato leído directamente por el operador en la consola, registrado en el laboratorio; sin artefacto con hash ni prueba de arranque. No equivale a `LAB` ni a `VERIFIED`. |
| `LAB` | Prueba propia en hardware con registro y hashes; requiere evidencia reproducible del ensayo. **Ningún arranque Linux está verificado.** |

## Fase 0 — Inicialización, documentación y publicación
**Estado:** base documental creada; mantenimiento continuo.
- [x] `IMPLEMENTADO` Repositorio y estructura de documentación, herramientas, manifiestos y tests.
- [x] `IMPLEMENTADO` Registrar fuentes, riesgos, decisiones, inventario y reglas de evidencia.
- [x] `IMPLEMENTADO` Preparar README y normas para colaboración pública.
- [ ] `PENDIENTE` Verificar todos los documentos y enlaces internos tras el barrido público.
- [ ] `PENDIENTE` Resolver la configuración del CI y decidir protección de `main`.
- [ ] `PENDIENTE` Revisar de forma completa los metadatos GitHub (descripción, topics, licencia visible y settings).

## Fase 1 — Identificación de consola
**Estado:** PARCIAL — firmware 13.52 **observado**, modelo **CUH-2115B confirmado**, familia Slim confirmada por el modelo y capacidad 861,4 GB **observada**; southbridge **Baikal B1 (`0x30201`) observado por el operador con GoldHEN v2.2.3 el 2026-10-16**. La identificación del southbridge está completada a nivel observacional; la selección del kernel sigue pendiente de validación. Registro: [`docs/lab-logs/LAB-001-southbridge.md`](lab-logs/LAB-001-southbridge.md). Registro: [`docs/lab-logs/LAB-000-identificacion-consola.md`](lab-logs/LAB-000-identificacion-consola.md). Ejecutable como caso **TP-01** de [`docs/TEST_PLAN.md`](TEST_PLAN.md).
- [x] `IMPLEMENTADO` Registrar CUH-2115B confirmado en `docs/lab-logs/LAB-000-identificacion-consola.md` y `docs/COMPATIBILITY_MATRIX.md`.
- [ ] `PENDIENTE` Registrar firmware exacto sin actualizarlo.
- [ ] `PENDIENTE` Registrar estado de arranque original y síntomas existentes.
- [ ] `PENDIENTE` Determinar qué datos requieren respaldo.
- [x] `OBSERVADO` Registrar southbridge Baikal B1 (`0x30201`) leído por el operador mediante GoldHEN v2.2.3; ver `docs/lab-logs/LAB-001-southbridge.md`. La captura no está guardada como artefacto con hash; no se eleva a `LAB` ni `VERIFIED`. La cifra de versión de GoldHEN reportada en pantalla es inconsistente con el binario conocido (riesgo R-23 de `AUDITORIA_CADENA_BAIKAL.md`).

**Bloqueo principal:** el southbridge está observado a nivel `OBSERVADO`, no `LAB`/`VERIFIED`; no elegir kernel solo por este dato sin validar la cadena completa (kernel/initramfs/rootfs) y resolver R-23.

## Fase 2 — Auditoría de upstream, artefactos y licencias
**Estado:** auditoría de código de dos repositorios upstream avanzada; dependencias adicionales siguen pendientes.
- [x] `CÓDIGO` Revisar README, commits fijados, historial y áreas clave del loader/distribución.
- [x] `CÓDIGO` Inspeccionar scripts de construcción y escritura USB, payload y flujo de lectura del loader.
- [x] `IMPLEMENTADO` Registrar fuentes, hashes, resultados y límites de la auditoría.
- [x] `IMPLEMENTADO` Crear matriz de compatibilidad e inventario de artefactos.
- [ ] `PENDIENTE` Auditar individualmente kernel, distribución, initramfs/rootfs, paquetes gráficos, skeletons y payloads candidatos.
- [ ] `PENDIENTE` Confirmar licencia, procedencia, integridad y permisos de redistribución de cada dependencia.
- [ ] `PENDIENTE` Completar la auditoría de cualquier payload candidato; no ejecutar un binario no verificado.

## Fase 2.1 — Auditoría estática del exploit/payload para firmware 13.52
**Estado:** COMPLETADA CON LÍMITES (informe estático hecho; **no** es `VERIFIED`). Autorización de identificación por software: **CONCEDIDA por Marcos el 2026-10-16**; ver [`docs/AUTHORIZATION_KERNEL_IDENTIFICATION_2026-10-16.md`](AUTHORIZATION_KERNEL_IDENTIFICATION_2026-10-16.md). Esta autorización cubre la lectura del southbridge mediante GoldHEN o lector auditado, no una escritura USB física ni escritura en almacenamiento interno.
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

## Fase 2.2 — Herramientas de verificación y tests
**Estado:** utilidades y suite host-side implementadas; el resultado actual debe confirmarse ejecutando el comando en el entorno de trabajo. Seguimiento detallado tarea por tarea en [`docs/workstreams/02-tools-tests/ROADMAP.md`](workstreams/02-tools-tests/ROADMAP.md).
- [x] `IMPLEMENTADO` Verificación de manifiestos y hashes.
- [x] `IMPLEMENTADO` Verificación por niveles de cadena de arranque.
- [x] `IMPLEMENTADO` Análisis estático de ELF/payload.
- [x] `IMPLEMENTADO` Constructor/preflight de imagen con modo de simulación.
- [x] `IMPLEMENTADO` Validaciones de documentación y pruebas automatizadas.
- [ ] `PENDIENTE` Ejecutar `bash scripts/check.sh` en entorno limpio y conservar el resultado actual.
- [ ] `PENDIENTE` Confirmar que CI corre y publica un estado verificable.

## Fase 3 — Selección del método de arranque
**Estado:** BLOQUEADA — la política USB-only (D-008) sigue sin validación técnica. Southbridge observado: Baikal B1 (`0x30201`). `bzImage-baikal-7.0.8` es candidato prioritario para revisión, no una selección final ni una aprobación de arranque. Procedimiento con citas de código en [`docs/BOOT_FLOW.md`](BOOT_FLOW.md); diseño verificable en [`docs/USB_ONLY_DESIGN.md`](USB_ONLY_DESIGN.md).
- [x] `TERCEROS` Existe un exploit/payload que dice cubrir el firmware registrado (13.52): guías y repositorio `raw13g` (no verificado por nosotros); depende de GoldHEN (D-010). La lista de 20 firmwares con offsets está en `UPSTREAM_CODE_MAP.md` §1.7 (`CÓDIGO`).
- [x] `CÓDIGO` Requisitos y riesgos del método seleccionado — `docs/TROUBLESHOOTING.md` y `UPSTREAM_CODE_MAP.md` §1.6.
- [x] `LAB` Identificar el southbridge observado: Baikal B1 (`0x30201`), registro `docs/lab-logs/LAB-001-southbridge.md`.
- [ ] `PENDIENTE` Seleccionar formalmente el kernel tras revisar hashes, procedencia y coherencia kernel/initramfs/rootfs. Baikal 7.0.8 es candidato prioritario, no selección final.
- [x] `IMPLEMENTADO` Decisión D-008 tomada: USB-only como arquitectura objetivo; la escritura interna no es fallback (ver `DECISION_LOG.md`).
- [ ] `PENDIENTE` Demostrar que el flujo USB-only es una propiedad real. Hecho: loader original y parcheado **compilados** en contenedor sin red y comparados estáticamente (`TESTS`/`CÓDIGO`, `LOADER_BUILD_REPRO.md`). Falta: comprobar rutas internas vacías y observar el disco interno antes y después en laboratorio (`USB_ONLY_DESIGN.md` §4).
- [x] `IMPLEMENTADO` Ruta de rollback por paso — `BOOT_FLOW.md` Fase 6 y `TROUBLESHOOTING.md` (documental; no ensayada).
- [ ] `PENDIENTE` Registrar qué cambios persisten en el sistema original: por código, el loader no escribe archivos (D-017); falta probar el kernel/rootfs en runtime.
- [x] `IMPLEMENTADO` Ensayo documental del procedimiento — `BOOT_FLOW.md` y `TEST_PLAN.md` (TP-01 a TP-07); **ningún caso se ha ejecutado**.

## Fase 4 — Diseño USB-only
**Estado:** arquitectura decidida; aislamiento completo no demostrado.
- [x] `IMPLEMENTADO` Definir el objetivo de evitar escritura en almacenamiento interno.
- [x] `CÓDIGO` Documentar rutas de lectura/escritura observadas en el loader y scripts upstream.
- [ ] `PENDIENTE` Revisar todos los caminos de arranque, fallos y recuperación.
- [ ] `PENDIENTE` Definir y probar criterios de aborto antes de conectar el USB a la consola.
- [ ] `BLOQUEADO` Declarar USB-only verificado hasta tener evidencia suficiente, no solo una revisión de código.

## Fase 5 — Preparación de medio externo
**Estado:** BLOCKED — el southbridge ya se identificó como Baikal B1; la fase depende de la selección final del kernel, la procedencia y las licencias. Ejecutable como casos **TP-02 a TP-04** de `docs/TEST_PLAN.md`.
- [ ] `PENDIENTE` Construir imagen reproducible en PC: la herramienta existe (`tools/build_usb_image.py`); falta ejecutarla con el rootfs real bajo `fakeroot` y con el kernel que corresponda.
- [x] `TESTS` Verificar formato, particiones y filesystem de la imagen de prueba (`fsck.vfat -n` sobre p1, lectura de p2 con `debugfs`).
- [ ] `BLOQUEADO` Confirmar correspondencia kernel/initramfs/rootfs con Baikal B1 (`0x30201`); el dato de hardware está identificado, pero la cadena completa aún no está validada.
- [x] `IMPLEMENTADO` Política de kernel en el USB: el `bzImage` va **dentro de la FAT** (USB-only, D-008); no se usan kernels de repuesto renombrados para esta consola.
- [x] `TESTS` Validar el procedimiento con imagen virtual antes de escribir a un disco real (incluye una imagen de prueba con artefactos reales en una ubicación temporal, descartada).

## Fase 6 — Primer arranque Linux
**Estado:** BLOCKED — la consola y el southbridge están identificados, pero no hay medio aprobado y la política USB-only (D-008) aún no está validada como propiedad técnica. Procedimiento detallado con tiempos y señales esperadas (LED, video) en [`docs/BOOT_FLOW.md`](BOOT_FLOW.md) Fases 3-6; árboles de diagnóstico ante fallo en [`docs/TROUBLESHOOTING.md`](TROUBLESHOOTING.md); ejecutable como casos **TP-05 a TP-07** de `docs/TEST_PLAN.md`.
- [ ] `PENDIENTE` Ejecutar solo el procedimiento específico aprobado (no genérico).
- [ ] `PENDIENTE` Registrar vídeo, indicador luminoso (LED), tiempos y logs.
- [ ] `PENDIENTE` Cambiar una sola variable por intento ante un fallo.
- [ ] `PENDIENTE` Clasificar la etapa del fallo (USB / exploit-kernel / rootfs / firmware-southbridge) usando la tabla resumen de `docs/TROUBLESHOOTING.md` §8.
- [ ] `PENDIENTE` Verificar retorno al sistema original tras cada intento.

## Puertas de seguridad obligatorias

No avanzar a escritura de USB físico ni prueba de arranque hasta que se cumplan todas las condiciones aplicables: compatibilidad razonada con evidencia, procedencia/licencias revisadas, imagen auditada, destino identificado inequívocamente, recuperación preparada, tests aprobados y autorización explícita del mantenedor.

El proyecto puede progresar en auditoría, documentación y tests host-side mientras la prueba física permanece bloqueada.

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
**Estado:** PLANNED. Árboles de diagnóstico específicos para esta pila (no genéricos) ya redactados en [`docs/TROUBLESHOOTING.md`](TROUBLESHOOTING.md), con casos derivados de issues reales del upstream (LED blanca/sin handoff, rootfs no monta, bug de EDID). Ver también [`docs/RECOVERY_STRATEGY.md`](RECOVERY_STRATEGY.md) para los niveles generales de recuperación. El protocolo de aborto, paquete de diagnóstico y recuperación para el primer intento está en [`docs/RECOVERY_PLAN.md`](RECOVERY_PLAN.md); es documental y no se ha ensayado en hardware.
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

## Fase 12 — Publicación de resultados reproducibles
**Estado:** parcialmente preparada; no hay resultado funcional de arranque que publicar.
- [x] `IMPLEMENTADO` Publicar documentación de investigación, riesgos y herramientas.
- [ ] `PENDIENTE` Publicar reporte final del primer arranque, si se consigue.
- [ ] `PENDIENTE` Documentar limitaciones, pasos reproducibles y matriz de compatibilidad basada en pruebas propias.
- [ ] `PENDIENTE` Resolver licencias y avisos antes de publicar artefactos redistribuibles.

## Dependencias críticas
- La identificación de Fase 1 ya registró Baikal B1; la selección/validación del kernel y la cadena USB-only siguen bloqueando las fases 3, 5 y 6.
- Fase 2 bloquea la selección/reutilización de componentes.
- Fase 3 requiere Fase 1 (southbridge) y la validación de USB-only (`USB_ONLY_DESIGN.md` §4).
- Fase 4 puede avanzar en la PC usando solo archivos/imágenes virtuales, sin esperar a la Fase 1.
- Las fases 8 y 9 esperan arranque y estabilidad reproducibles (fases 6 y 7).
