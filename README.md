# PS4 Linux Lab

Laboratorio público de investigación para ejecutar Linux desde almacenamiento externo en una PlayStation 4, con énfasis en auditoría técnica, reproducibilidad, seguridad y trazabilidad.

**Estado actual: investigación y preparación; todavía no se ha demostrado un arranque Linux propio en la consola.** El equipo de laboratorio es una PS4 Slim **CUH-2115B confirmada**, firmware **13.52 observado** y capacidad observada de **861,4 GB**. El southbridge está **observado** como **Baikal B1 (`0x30201`)** mediante GoldHEN v2.2.3 (ver [`docs/lab-logs/LAB-001-southbridge.md`](docs/lab-logs/LAB-001-southbridge.md)); es una observación del operador a nivel `OBSERVADO`, no una verificación `LAB`/`VERIFIED`, y la selección final de kernel/método sigue bloqueada. La arquitectura objetivo es **USB-only** (D-008): mantener intacto el almacenamiento interno durante las primeras fases es una decisión de diseño, no una propiedad ya verificada en hardware.

> Proyecto experimental y comunitario. No se garantiza compatibilidad, estabilidad ni ausencia de riesgos. No se deben ejecutar payloads, escribir imágenes en dispositivos físicos ni modificar la consola sin revisar las auditorías, los riesgos y los criterios de salida.

## Objetivos

- Determinar compatibilidad real entre modelo CUH, firmware, southbridge, loader y kernel.
- Auditar fuentes, releases, dependencias, artefactos y licencias de terceros.
- Desarrollar utilidades de verificación y preparación que operen sobre archivos/imágenes, no sobre dispositivos físicos.
- Diseñar un flujo USB-only y comprobar sus límites antes de cualquier prueba en hardware.
- Preservar el almacenamiento interno de la PS4 en las fases iniciales.
- Mantener procedimientos de diagnóstico, recuperación y registro reproducible.
- Medir GPU, Mesa, OpenGL/Vulkan, audio, red, temperatura y estabilidad solo después de lograr un arranque seguro.
- Evaluar gaming, emulación y, de forma secundaria y basada en mediciones, posibles usos de cómputo/LLM.

## Estado resumido

- **Investigación documental y auditoría estática:** avanzada; no equivale a compatibilidad demostrada.
- **Utilidades locales:** implementadas para inspección/verificación de archivos, manifiestos y pruebas automatizadas.
- **Cadena de arranque compatible con CUH-2115B + firmware 13.52:** pendiente; southbridge desconocido.
- **Flujo USB-only integral:** diseñado, no demostrado en hardware.
- **Arranque Linux propio en la consola:** no realizado/verificado.
- **Pruebas de GPU, periféricos, temperatura y estabilidad:** pendientes.
- **CI de GitHub Actions:** existe workflow, pero el estado registrado indica bloqueo previo a la ejecución del runner por facturación/configuración; volver a comprobar antes de darlo por resuelto.

La evidencia se etiqueta como `IMPLEMENTADO`, `TESTS`, `CÓDIGO`, `TERCEROS`, `LAB`, `PENDIENTE` o `BLOQUEADO`. **Ningún resultado de escritorio, test unitario o informe upstream prueba por sí solo que la consola arranque.** `LAB` requiere prueba propia en hardware, registro, hashes y condiciones reproducibles.

## Principios de seguridad

1. No actualizar el firmware como parte de la investigación inicial.
2. No escribir en el almacenamiento interno de la PS4 durante las primeras fases.
3. Identificar cualquier unidad por modelo, capacidad, bus y número de serie; no confiar únicamente en nombres volátiles como `/dev/sdX`.
4. No ejecutar scripts o binarios de terceros sin inspección, procedencia y verificación.
5. Cualquier futura operación destructiva debe mostrar el destino, reidentificarlo y exigir confirmación explícita; las herramientas actuales no deben operar sobre dispositivos físicos.
6. Registrar versiones, hashes, fuentes, condiciones, comandos, logs y resultados.
7. Una pantalla negra no demuestra por sí sola un brick.
8. Distinguir afirmaciones upstream, observaciones de código, inferencias, hipótesis y pruebas propias.
9. No publicar secretos, tokens, credenciales, datos personales, logs sensibles ni artefactos de terceros sin revisar procedencia y licencia.
10. No redistribuir kernels, payloads, rootfs, imágenes ni binarios de terceros por defecto; consultar la política de licencias y la auditoría correspondiente.

## Referencias upstream

- [X-F1REBALL-X/PS4-Linux](https://github.com/X-F1REBALL-X/PS4-Linux)
- [ps4-linux/ps4-linux-loader](https://github.com/ps4-linux/ps4-linux-loader)

Antes de reutilizar componentes, consultar [auditoría upstream](docs/UPSTREAM_AUDIT.md), [mapa de código](docs/UPSTREAM_CODE_MAP.md), [inventario de artefactos](docs/ARTIFACT_INVENTORY.md) y [política de licencias](docs/LICENSE_POLICY.md). Las referencias externas son fuentes de investigación, no avales ni garantías de compatibilidad.

## Documentación principal

| Documento | Propósito |
|---|---|
| [Acta del proyecto](docs/PROJECT_CHARTER.md) | Alcance, objetivos y criterios de éxito |
| [Roadmap](docs/ROADMAP.md) | Fases, dependencias y puertas de decisión |
| [Arquitectura](docs/ARCHITECTURE.md) | Componentes y flujo conceptual |
| [Auditoría upstream](docs/UPSTREAM_AUDIT.md) | Hallazgos y límites de revisión |
| [Auditoría del exploit 13.52](docs/EXPLOIT_AUDIT_13.52.md) | Análisis estático y límites del payload no verificado |
| [Evaluación de REA](docs/REA_EVALUATION.md) | Decisión sobre herramientas de ingeniería inversa |
| [Registro de riesgos](docs/RISK_REGISTER.md) | Riesgos y mitigaciones |
| [Estrategia de recuperación](docs/RECOVERY_STRATEGY.md) | Diagnóstico y rollback |
| [Política de licencias](docs/LICENSE_POLICY.md) | Procedencia y reutilización |
| [Registro de decisiones](docs/DECISION_LOG.md) | Decisiones y preguntas pendientes |
| [Plantilla de experimento](docs/LAB_LOG_TEMPLATE.md) | Registro reproducible |
| [Flujo de arranque](docs/BOOT_FLOW.md) | Etapas y diagnóstico |
| [Matriz de compatibilidad](docs/COMPATIBILITY_MATRIX.md) | Evidencia de hardware/firmware |
| [Plan de pruebas](docs/TEST_PLAN.md) | Casos, resultados y criterios de aborto |
| [Solución de problemas](docs/TROUBLESHOOTING.md) | Diagnóstico no destructivo |
| [GPU y LLM](docs/GPU_AND_LLM_RESEARCH.md) | Evaluación basada en mediciones |
| [Mapa upstream](docs/UPSTREAM_CODE_MAP.md) | Áreas de código revisadas |
| [Fuentes de evidencia](docs/EVIDENCE_SOURCES.md) | Trazabilidad de las fuentes |
| [Seguridad de herramientas](docs/SAFETY_AND_TOOLING.md) | Requisitos para scripts futuros |
| [Plan de ejecución siguiente](docs/NEXT_EXECUTION_PLAN.md) | Tareas inmediatas, responsables y puertas de seguridad |
| [Plan de acción inmediata](docs/PLAN_ACCION_INMEDIATA.md) | Secuencia de cierre, preparación de imagen y puertas operativas |
| [Plan de recuperación](docs/RECOVERY_PLAN.md) | Criterios de aborto, diagnóstico por etapas y límites de recuperación |
| [Manifiestos de artefactos](docs/ARTIFACT_MANIFEST.md) | Formato y uso del verificador de integridad |
| [Auditoría del pipeline de imagen](docs/BUILD_PIPELINE_SAFETY_AUDIT.md) | Riesgos de `build-img.sh`/`write-img.ps1` y su mitigación |
| [Preflight de imagen](docs/USB_IMAGE_BUILD_PREFLIGHT.md) | Planificador de solo lectura del pipeline upstream |
| [Compilación aislada del loader](docs/LOADER_BUILD_REPRO.md) | Revisión de la cadena, entorno sin red, resultados y límites |
| [Diseño USB-only](docs/USB_ONLY_DESIGN.md) | Propiedades verificables, qué está demostrado, bloqueos y arquitectura recomendada |
| [Inventario de artefactos](docs/ARTIFACT_INVENTORY.md) | Procedencia, hashes, licencias y nivel de confianza de cada binario |
| [Diagnóstico de CI](docs/CI_DIAGNOSIS.md) | Estado del workflow y alternativas |
| [Informe de estado público](docs/PUBLIC_PROJECT_STATUS.md) | Relevamiento de avances y pendientes |
| [Auditoría de publicación pública](docs/PUBLICATION_AUDIT.md) | Revisión de documentación para un repositorio público |
| [Auditoría de recursos externos y plan revisado](docs/AUDITORIA_RECURSOS_EXTERNOS_Y_PLAN_2026-10-16.md) | Análisis de todos los recursos propuestos, selección de kernel/initramfs y nuevas puertas de decisión |
| [Auditoría de cadena Baikal](docs/AUDITORIA_CADENA_BAIKAL.md) | Auditoría integrada de compatibilidad y bloqueos |
| [Selección de kernel](docs/KERNEL_SELECTION.md) | Comparación de candidatos y criterios de selección |
| [Plan de validación Baikal](docs/PLAN_VALIDACION_BAIKAL.md) | Puertas de validación por etapas |
| [Revisión de kernel_inspect](docs/REVIEW_KERNEL_INSPECT_ZSTD_2026-10-16.md) | Límites de la inspección estática del kernel |
| [Revisión independiente OpenCode](docs/OPENCODE_REVIEW_2026-10-16.md) | Hallazgos técnicos de revisión cruzada |
| [Revisión cruzada documental](docs/CROSS_DOC_AUDIT_2026-10-16.md) | Contradicciones y tareas de consolidación |
| [Revisión cruzada de rama Claude](docs/BRANCH_REVIEW_CLAUDE_2026-10-16.md) | Hallazgos estáticos sobre el inventario, la publicación del constructor y la divergencia de ramas |
| [Integración de ramas](docs/INTEGRACION_RAMAS_2026-10-16.md) | Merges, portado manual, conflictos y límites de consolidación |
| [Workstreams activos](docs/WORKSTREAMS.md) | Las cinco categorías de trabajo en curso, su rama y responsable |
| [Plan de workstreams](docs/WORKSTREAM_PLAN.md) | Orden de ejecución, dependencias y protocolo entre categorías |

## Herramientas locales

Las herramientas se diseñaron para trabajar con archivos y datos de prueba; no abren dispositivos de bloque, no montan unidades ni ejecutan binarios de terceros.

```bash
bash scripts/check.sh
python3 tools/verify_boot_chain.py <carpeta-con-bzImage-e-initramfs> --catalogo manifests/arranque-catalogo.json
python3 tools/verify_artifacts.py --manifest /ruta/a/tu-manifiesto.json --root .
python3 tools/plan_usb_image_build.py rootfs.tar.xz initramfs.cpio.gz salida.img
python3 tools/build_usb_image.py --salida img.img --initramfs ... --kernel ... --rootfs-dir ... --dry-run
python3 tools/payload_static.py goldhen.bin --referencia <referencia-verificada>
python3 tools/elf_audit.py linux-1024mb.elf --fuente fw_offsets.h
python3 tools/check_docs.py
python3 tools/kernel_inspect.py /ruta/a/bzImage
python3 tools/inventariar_artefactos.py --raiz kernel=/ruta/a/artefactos --markdown
bash scripts/build_loader_isolated.sh <src-loader> <salida-nueva> [--patch p]
```

Un resultado positivo en estructura, hash o formato no demuestra compatibilidad ni arranque. Un hash solo verifica igualdad con un valor esperado; no acredita por sí mismo la autenticidad de la fuente.

## Contribución y gobernanza

Las contribuciones deben ser pequeñas, reproducibles y respaldadas por evidencia. Revisar [CONTRIBUTING.md](CONTRIBUTING.md), el roadmap, los riesgos y la política de licencias. No se aceptan afirmaciones de compatibilidad sin fuente y nivel de evidencia. No se debe probar escritura destructiva en dispositivos reales como parte de los tests.

## Licencia y componentes de terceros

La publicación del código de este laboratorio no cambia las licencias de upstream ni otorga derechos sobre payloads, kernels, imágenes, rootfs o marcas de terceros. Revisar las licencias de cada componente y conservar avisos y atribuciones requeridos. Si un componente no tiene licencia identificada, tratarlo como **no autorizado para redistribución** hasta resolverlo.

## Etiquetas temáticas

`#PS4Linux` `#PlayStation4` `#Linux` `#Homebrew` `#ReverseEngineering` `#Cybersecurity` `#OpenSource` `#HardwareResearch` `#ReproducibleResearch` `#Gaming` `#LLM`

---

Proyecto experimental en desarrollo. La prioridad es demostrar compatibilidad y seguridad con evidencia propia antes de declarar éxito funcional.
