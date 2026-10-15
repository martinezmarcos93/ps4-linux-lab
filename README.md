# PS4 Linux Lab

Laboratorio privado para investigar Linux en PlayStation 4, priorizando seguridad, reproducibilidad y trazabilidad.

**Estado:** investigación y preparación documental. No hay todavía una PS4 identificada ni una combinación modelo/firmware validada en este laboratorio. Una declaración upstream no equivale a una prueba propia.

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
- [x] Repositorio privado creado.
- [x] Documentación inicial incorporada.
- [x] Fuentes de referencia y riesgos preliminares registrados.
- [ ] Identificar modelo CUH, firmware y estado de la consola disponible.
- [ ] Completar mapa de código y revisar commits/tags exactos.
- [ ] Resolver licencias de cada componente candidato.
- [ ] Elegir método de arranque basado en evidencia para el hardware real.
- [ ] Diseñar/probar utilidades USB usando archivos e imágenes virtuales.
- [ ] Primer arranque Linux externo y retorno al sistema original.
- [ ] Caracterizar periféricos, GPU, temperatura y estabilidad.
- [ ] Decidir con mediciones si gaming, emulación o LLM son viables.

## Documentación
| Documento | Propósito |
|---|---|
| [Acta del proyecto](docs/PROJECT_CHARTER.md) | Alcance y criterios de éxito |
| [Roadmap](docs/ROADMAP.md) | Fases, dependencias y puertas de decisión |
| [Arquitectura](docs/ARCHITECTURE.md) | Componentes y flujo conceptual |
| [Auditoría upstream](docs/UPSTREAM_AUDIT.md) | Hallazgos y límites de revisión |
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

## Convenciones de evidencia
Estados: PLANNED, IN_PROGRESS, BLOCKED, VERIFIED y REJECTED. Solo marcar VERIFIED con hardware/firmware identificados, evidencia guardada y procedimiento reproducible.

Clasificar afirmaciones como UPSTREAM-CLAIM, CODE-OBSERVATION, INFERENCE, HYPOTHESIS o LAB-VERIFIED. No guardar secretos, logs sensibles ni imágenes de gran tamaño en el repositorio.
