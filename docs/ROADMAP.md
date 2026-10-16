# Roadmap

**Última revisión de estado:** 2026-10-16. Este roadmap distingue trabajo documental, inspección de código, tests host-side y pruebas físicas. No declarar una fase `VERIFIED` sin evidencia propia en hardware.

## Escala de evidencia

| Etiqueta | Significado |
|---|---|
| `PENDIENTE` / `BLOQUEADO` | No completado / no puede avanzar; indicar causa |
| `IMPLEMENTADO` | Existe código o documentación, todavía sin verificación independiente |
| `TERCEROS` | Lo reporta una fuente externa; no reproducido en este laboratorio |
| `CÓDIGO` | Confirmado mediante inspección de código o artefactos fijados |
| `TESTS` | Test automatizado host-side ejecutado; no demuestra arranque en consola |
| `LAB` | Prueba propia en hardware con registro reproducible, condiciones y hashes |

## Fase 0 — Inicialización, documentación y publicación
**Estado:** base documental creada; mantenimiento continuo.
- [x] `IMPLEMENTADO` Repositorio y estructura de documentación, herramientas, manifiestos y tests.
- [x] `IMPLEMENTADO` Registrar fuentes, riesgos, decisiones, inventario y reglas de evidencia.
- [x] `IMPLEMENTADO` Preparar README y normas para colaboración pública.
- [ ] `PENDIENTE` Verificar todos los documentos y enlaces internos tras el barrido público.
- [ ] `PENDIENTE` Resolver la configuración del CI y decidir protección de `main`.
- [ ] `PENDIENTE` Revisar de forma completa los metadatos GitHub (descripción, topics, licencia visible y settings).

## Fase 1 — Identificación de consola
**Estado:** parcial. Consola identificada como PS4 Slim CUH-2115B; firmware 13.52 y capacidad observada de 861,4 GB. Southbridge desconocido.
- [x] `IMPLEMENTADO` Registrar modelo CUH-2115B en el log y matriz de compatibilidad.
- [x] `IMPLEMENTADO` Registrar firmware observado 13.52 y capacidad informada.
- [ ] `PENDIENTE` Completar evidencia del firmware y estado de arranque original con registro fechado.
- [ ] `PENDIENTE` Identificar el southbridge con evidencia suficiente.
- [ ] `PENDIENTE` Registrar necesidades de respaldo y condiciones de recuperación.

**Bloqueo principal:** el southbridge no está identificado; no elegir kernel solo por semejanza de modelo o reportes de terceros.

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
**Estado:** análisis estático documentado con límites; no equivale a compatibilidad ni a autorización de ejecución.
- [x] `CÓDIGO` Registrar fuentes y analizar estáticamente el material disponible.
- [x] `TESTS` Incorporar tests host-side con datos ficticios para el analizador.
- [x] `IMPLEMENTADO` Documentar las diferencias entre artefacto observado y release oficial conocida.
- [ ] `PENDIENTE` Resolver procedencia y legitimidad del artefacto candidato antes de cualquier ejecución.
- [ ] `BLOQUEADO` Ejecución en hardware: requiere autorización explícita del mantenedor y superar todas las puertas de seguridad.

## Fase 3 — Herramientas de verificación y tests
**Estado:** utilidades y suite host-side implementadas; el resultado actual debe confirmarse ejecutando el comando en el entorno de trabajo.
- [x] `IMPLEMENTADO` Verificación de manifiestos y hashes.
- [x] `IMPLEMENTADO` Verificación por niveles de cadena de arranque.
- [x] `IMPLEMENTADO` Análisis estático de ELF/payload.
- [x] `IMPLEMENTADO` Constructor/preflight de imagen con modo de simulación.
- [x] `IMPLEMENTADO` Validaciones de documentación y pruebas automatizadas.
- [ ] `PENDIENTE` Ejecutar `bash scripts/check.sh` en entorno limpio y conservar el resultado actual.
- [ ] `PENDIENTE` Confirmar que CI corre y publica un estado verificable.

## Fase 4 — Diseño USB-only
**Estado:** arquitectura decidida; aislamiento completo no demostrado.
- [x] `IMPLEMENTADO` Definir el objetivo de evitar escritura en almacenamiento interno.
- [x] `CÓDIGO` Documentar rutas de lectura/escritura observadas en el loader y scripts upstream.
- [ ] `PENDIENTE` Revisar todos los caminos de arranque, fallos y recuperación.
- [ ] `PENDIENTE` Definir y probar criterios de aborto antes de conectar el USB a la consola.
- [ ] `BLOQUEADO` Declarar USB-only verificado hasta tener evidencia suficiente, no solo una revisión de código.

## Fase 5 — Selección y preparación de artefactos
**Estado:** bloqueada por compatibilidad y auditoría de procedencia.
- [ ] `BLOQUEADO` Seleccionar kernel compatible con CUH-2115B, firmware 13.52 y southbridge.
- [ ] `PENDIENTE` Seleccionar initramfs/rootfs y documentar requisitos.
- [ ] `PENDIENTE` Completar manifiesto de artefactos con hashes esperados de fuentes confiables.
- [ ] `PENDIENTE` Construir imagen candidata reproducible en PC.
- [ ] `PENDIENTE` Verificar estructura, particiones, integridad, formato y procedencia sin escribir en una unidad física.
- [ ] `PENDIENTE` Revisar plan de recuperación y registrar aprobación antes de cualquier prueba operativa.

## Fase 6 — Prueba en hardware
**Estado:** no iniciada; bloqueada por las fases previas.
- [ ] `BLOQUEADO` Autorizar explícitamente la prueba en consola.
- [ ] `BLOQUEADO` Ejecutar el primer arranque externo con criterios de aborto definidos.
- [ ] `PENDIENTE` Registrar logs, condiciones, versiones, hashes y comportamiento observado.
- [ ] `PENDIENTE` Verificar retorno al sistema original y ausencia de cambios no deseados en almacenamiento interno.
- [ ] `PENDIENTE` Clasificar cada resultado como éxito, fallo o inconcluso sin sobreinterpretar síntomas.

## Fase 7 — Caracterización funcional
**Estado:** pendiente de arranque Linux verificado.
- [ ] `PENDIENTE` Medir GPU, Mesa, OpenGL/Vulkan y aceleración disponible.
- [ ] `PENDIENTE` Probar audio, red, almacenamiento, periféricos y temperatura.
- [ ] `PENDIENTE` Medir estabilidad, consumo y límites térmicos en sesiones controladas.
- [ ] `PENDIENTE` Evaluar gaming y emulación con benchmarks reproducibles.
- [ ] `PENDIENTE` Evaluar LLM solo tras medir RAM disponible, soporte de GPU, backend y rendimiento real.

## Fase 8 — Publicación de resultados reproducibles
**Estado:** parcialmente preparada; no hay resultado funcional de arranque que publicar.
- [x] `IMPLEMENTADO` Publicar documentación de investigación, riesgos y herramientas.
- [ ] `PENDIENTE` Publicar reporte final del primer arranque, si se consigue.
- [ ] `PENDIENTE` Documentar limitaciones, pasos reproducibles y matriz de compatibilidad basada en pruebas propias.
- [ ] `PENDIENTE` Resolver licencias y avisos antes de publicar artefactos redistribuibles.

## Puertas de seguridad obligatorias

No avanzar a escritura de USB físico ni prueba de arranque hasta que se cumplan todas las condiciones aplicables: compatibilidad razonada con evidencia, procedencia/licencias revisadas, imagen auditada, destino identificado inequívocamente, recuperación preparada, tests aprobados y autorización explícita del mantenedor.

El proyecto puede progresar en auditoría, documentación y tests host-side mientras la prueba física permanece bloqueada.
