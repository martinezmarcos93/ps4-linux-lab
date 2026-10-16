# PS4 Linux Lab

Laboratorio privado para investigar Linux en PlayStation 4, priorizando seguridad, reproducibilidad y trazabilidad.

**Estado:** investigación y preparación. La consola del laboratorio es una PS4 Slim (familia **inferida** de una foto), firmware 13.52 **observado** y capacidad de 861,4 GB **observada**; CUH y southbridge **desconocidos** (la selección de kernel no está resuelta) y ningún arranque probado. La arquitectura objetivo es **USB-only** (D-008): está decidida, pero el flujo completo **no está validado**. Una declaración upstream no equivale a una prueba propia.

## Objetivos
- Identificar un método de arranque compatible con modelo CUH, firmware y southbridge.
- Auditar código, releases, dependencias y licencias.
- Preparar y verificar un USB en PC antes de conectarlo a la consola.
- Mantener intacto el almacenamiento interno durante las primeras fases.
- Diseñar diagnósticos no destructivos y recuperación.
- Medir GPU, Mesa, OpenGL/Vulkan, audio, red, temperatura y estabilidad.
- Evaluar juegos/emulación; investigar LLM solo si existe un backend viable.

## Referencias upstream
- [X-F1REBALL-X/PS4-Linux](https://github.com/X-F1REBALL-X/PS4-Linux)
- [ps4-linux/ps4-linux-loader](https://github.com/ps4-linux/ps4-linux-loader)

Consultar [la auditoría upstream](docs/UPSTREAM_AUDIT.md) y [la política de licencias](docs/LICENSE_POLICY.md) antes de reutilizar componentes. No se incorporan kernels, payloads, imágenes, rootfs ni binarios de terceros por defecto.

## Principios de seguridad
1. Registrar el firmware exacto; no actualizarlo como parte de la investigación inicial.
2. No escribir en el disco interno de la PS4 durante las primeras fases.
3. Identificar discos por modelo, tamaño, bus y serie; no confiar solo en un identificador volátil como /dev/sdX.
4. No ejecutar scripts de terceros sin inspección, procedencia y verificación de integridad.
5. Una herramienta destructiva futura debe mostrar el destino, volver a identificarlo y exigir confirmación explícita.
6. Guardar hashes, versiones, logs, condiciones y resultado de cada experimento.
7. Una pantalla negra no demuestra por sí sola un brick.
8. Separar declaraciones upstream, observaciones de código, inferencias, hipótesis y pruebas propias.

## Estado del proyecto
Etiquetas de evidencia como en el [roadmap](docs/ROADMAP.md): `IMPLEMENTADO`, `TESTS`, `CÓDIGO`, `TERCEROS`, `LAB`, `PENDIENTE`, `BLOQUEADO`. Ninguna tarea tiene `LAB` todavía.
- [x] `IMPLEMENTADO` Repositorio privado creado, documentación inicial, fuentes y riesgos registrados.
- [ ] `PENDIENTE` Completar identificación del modelo CUH y southbridge. *(parcial: firmware 13.52 observado, Slim inferida, capacidad de clase 1 TB; ver LAB-000)*
- [x] `CÓDIGO` Mapa de código y commits/tags exactos (loader `f70f43a`, distribución `66e21cb`); historial del loader revisado.
- [ ] `PENDIENTE` Resolver licencias de cada componente candidato (inventario en [ARTIFACT_INVENTORY](docs/ARTIFACT_INVENTORY.md)).
- [ ] `BLOQUEADO` Elegir método/kernel basado en evidencia para el hardware real (falta el southbridge).
- [x] `TESTS` Utilidades USB sobre archivos e imágenes virtuales (verificación en 5 niveles, FAT32 sin root, constructor de imágenes, auditoría estática de ELF y payload).
- [ ] `PENDIENTE` Demostrar que el flujo USB-only no toca el almacenamiento interno (ver [USB_ONLY_DESIGN](docs/USB_ONLY_DESIGN.md)).
- [ ] `BLOQUEADO` Primer arranque Linux externo y retorno al sistema original (requiere autorización de Marcos y los puntos anteriores).
- [ ] `PENDIENTE` Caracterizar periféricos, GPU, temperatura y estabilidad.
- [ ] `PENDIENTE` Decidir con mediciones si gaming, emulación o LLM son viables.

## Documentación
| Documento | Propósito |
|---|---|
| [Acta del proyecto](docs/PROJECT_CHARTER.md) | Alcance y criterios de éxito |
| [Roadmap](docs/ROADMAP.md) | Fases, dependencias y puertas de decisión |
| [Arquitectura](docs/ARCHITECTURE.md) | Componentes y flujo conceptual |
| [Auditoría upstream](docs/UPSTREAM_AUDIT.md) | Hallazgos y límites de revisión |
| [Auditoría del exploit 13.52](docs/EXPLOIT_AUDIT_13.52.md) | Análisis estático y límites del payload no verificado |
| [Evaluación de REA](docs/REA_EVALUATION.md) | Decisión sobre herramientas de ingeniería inversa |
| [Riesgos](docs/RISK_REGISTER.md) | Riesgos y mitigaciones |
| [Recuperación](docs/RECOVERY_STRATEGY.md) | Diagnóstico y rollback |
| [Licencias](docs/LICENSE_POLICY.md) | Procedencia y reutilización |
| [Decisiones](docs/DECISION_LOG.md) | Decisiones y preguntas pendientes |
| [Plantilla de experimento](docs/LAB_LOG_TEMPLATE.md) | Registro reproducible |
| [Flujo de arranque](docs/BOOT_FLOW.md) | Etapas y diagnóstico |
| [Matriz de compatibilidad](docs/COMPATIBILITY_MATRIX.md) | Evidencia de hardware/firmware |
| [Plan de pruebas](docs/TEST_PLAN.md) | Casos, resultados y criterios de aborto |
| [Solución de problemas](docs/TROUBLESHOOTING.md) | Diagnóstico no destructivo |
| [GPU y LLM](docs/GPU_AND_LLM_RESEARCH.md) | Evaluación basada en mediciones |
| [Mapa upstream](docs/UPSTREAM_CODE_MAP.md) | Áreas de código a revisar |
| [Fuentes de evidencia](docs/EVIDENCE_SOURCES.md) | Trazabilidad |
| [Seguridad de herramientas](docs/SAFETY_AND_TOOLING.md) | Requisitos para scripts futuros |
| [Plan de ejecución siguiente](docs/NEXT_EXECUTION_PLAN.md) | Tareas inmediatas, responsables y puertas de seguridad |
| [Plan de acción inmediata](docs/PLAN_ACCION_INMEDIATA.md) | Secuencia de cierre, preparación de imagen y puertas operativas |
| [Manifiestos de artefactos](docs/ARTIFACT_MANIFEST.md) | Formato y uso del verificador de integridad |
| [Auditoría del pipeline de imagen](docs/BUILD_PIPELINE_SAFETY_AUDIT.md) | Riesgos de `build-img.sh`/`write-img.ps1` y su mitigación |
| [Preflight de imagen](docs/USB_IMAGE_BUILD_PREFLIGHT.md) | Planificador de solo lectura del pipeline upstream |
| [Compilación aislada del loader](docs/LOADER_BUILD_REPRO.md) | Revisión de la cadena, entorno sin red, resultados y límites |
| [Selección del kernel](docs/KERNEL_SELECTION.md) | Evidencia de southbridge para CUH-2115B, criterios de aceptación/rechazo y conclusión |
| [Diseño USB-only](docs/USB_ONLY_DESIGN.md) | Propiedades verificables, qué está demostrado, bloqueos y arquitectura recomendada |
| [Inventario de artefactos](docs/ARTIFACT_INVENTORY.md) | Procedencia, hashes, licencias y nivel de confianza de cada binario |
| [Diagnóstico del CI](docs/CI_DIAGNOSIS.md) | Por qué falla Actions (facturación) y la alternativa local |

## Convenciones de evidencia
Estado de fase: PLANNED, IN_PROGRESS, BLOCKED, COMPLETADA, VERIFIED y REJECTED. `VERIFIED` exige prueba propia en hardware con registro y hashes (etiqueta `LAB`); documentación, código escrito o reportes de terceros no bastan.

Clasificar afirmaciones como UPSTREAM-CLAIM (`TERCEROS`), CODE-OBSERVATION (`CÓDIGO`), INFERENCE, HYPOTHESIS o LAB-VERIFIED (`LAB`). No guardar secretos, logs sensibles ni imágenes de gran tamaño en el repositorio.

## Herramientas disponibles
Todas son de solo archivo (no abren dispositivos de bloque, no montan, no ejecutan binarios de terceros). La suite local equivale al CI, que está bloqueado por facturación de GitHub:

```bash
bash scripts/check.sh                       # compileall + tests + validación de documentación
python3 tools/verify_boot_chain.py <carpeta-con-bzImage-e-initramfs> --catalogo manifests/arranque-catalogo.json
python3 tools/verify_artifacts.py --manifest /ruta/a/tu-manifiesto.json --root .
python3 tools/plan_usb_image_build.py rootfs.tar.xz initramfs.cpio.gz salida.img  # preflight upstream, solo lectura
python3 tools/build_usb_image.py --salida img.img --initramfs ... --kernel ... --rootfs-dir ... --dry-run
python3 tools/payload_static.py goldhen.bin --referencia <oficial>   # análisis estático, sin ejecutar
python3 tools/elf_audit.py linux-1024mb.elf --fuente fw_offsets.h    # ELF vs. código fuente fijado
python3 tools/inventariar_artefactos.py --raiz etiqueta=ruta --catalogo manifests/arranque-catalogo.json --markdown  # hashes y procedencia, solo lectura
python3 tools/check_docs.py                 # enlaces, referencias, estados del roadmap
bash scripts/build_loader_isolated.sh <src-loader> <salida-nueva> [--patch p] # compila el loader en contenedor sin red; falla si falta algún artefacto
```

`verify_boot_chain` separa estructura, integridad, formato, compatibilidad y arranque; un resultado OK en los primeros no prueba que la consola arranque. No hay herramienta que escriba en un dispositivo físico. Un hash no autentica el origen por sí solo; el valor esperado debe venir de una fuente confiable.
