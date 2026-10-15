# PS4 Linux Lab

Laboratorio privado para estudiar, documentar y probar el arranque de Linux en PlayStation 4, con prioridad en la seguridad del dispositivo, la reproducibilidad y la trazabilidad de las pruebas.

**Estado:** planificación e investigación. No hay todavía una PS4 identificada ni una combinación modelo/firmware validada en este laboratorio.

## Objetivos

- Determinar el método de arranque compatible con el modelo, firmware y southbridge de la consola.
- Evaluar referencias comunitarias sin asumir que sus instrucciones son universalmente aplicables.
- Preparar un medio USB externo de prueba y mantener intacto el almacenamiento interno de la PS4.
- Desarrollar diagnósticos no destructivos, verificaciones de integridad y procedimientos de recuperación.
- Medir soporte real de GPU, Mesa, OpenGL/Vulkan, audio, red, temperatura y estabilidad.
- Evaluar juegos y emulación; investigar inferencia LLM solo después de validar el stack gráfico y de cómputo.
- Registrar resultados reproducibles y separar los hechos verificados de las hipótesis.

## Referencias upstream

- [X-F1REBALL-X/PS4-Linux](https://github.com/X-F1REBALL-X/PS4-Linux)
- [ps4-linux/ps4-linux-loader](https://github.com/ps4-linux/ps4-linux-loader)

Consultar [`docs/UPSTREAM_AUDIT.md`](docs/UPSTREAM_AUDIT.md) antes de reutilizar archivos o código. No se copian binarios, kernels, payloads ni imágenes de terceros a este repositorio por defecto.

## Principios de seguridad

1. **No actualizar el firmware antes de registrar la versión actual.**
2. **No escribir en el disco interno de la PS4 durante las primeras fases.**
3. Identificar discos por modelo, tamaño, bus y número de serie; nunca confiar solo en `/dev/sdX` o un número de disco guardado.
4. Toda operación destructiva debe mostrar el objetivo y exigir confirmación interactiva explícita.
5. Verificar hashes y procedencia de imágenes y payloads.
6. No ejecutar scripts descargados de upstream sin revisarlos.
7. Mantener un registro de cada prueba, resultado, cambio y criterio de rollback.
8. No considerar una pantalla negra como prueba suficiente de brick; diagnosticar antes de repetir acciones.

## Estado actual

- [x] Fuentes de referencia iniciales identificadas.
- [x] Riesgos preliminares documentados.
- [ ] Crear repositorio privado y cargar este esqueleto.
- [ ] Identificar modelo CUH, firmware y estado de almacenamiento.
- [ ] Confirmar licencia de cada componente que se pretenda reutilizar.
- [ ] Elegir un camino de arranque según evidencia específica del hardware.
- [ ] Preparar y validar el USB en una PC, sin conectarlo aún a la consola.
- [ ] Primer arranque Linux sin modificar el disco interno.
- [ ] Validar GPU, temperatura y estabilidad.

## Documentos

- [`docs/PROJECT_CHARTER.md`](docs/PROJECT_CHARTER.md): alcance, objetivos y criterios de éxito.
- [`docs/ROADMAP.md`](docs/ROADMAP.md): fases, entregables y puertas de decisión.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md): arquitectura objetivo y flujo de arranque.
- [`docs/UPSTREAM_AUDIT.md`](docs/UPSTREAM_AUDIT.md): lectura inicial de los repositorios de referencia.
- [`docs/RISK_REGISTER.md`](docs/RISK_REGISTER.md): riesgos y mitigaciones.
- [`docs/RECOVERY_STRATEGY.md`](docs/RECOVERY_STRATEGY.md): estrategia de diagnóstico y reparación.
- [`docs/LICENSE_POLICY.md`](docs/LICENSE_POLICY.md): reglas para reutilización de código y binarios.
- [`docs/DECISION_LOG.md`](docs/DECISION_LOG.md): decisiones y supuestos.
- [`docs/LAB_LOG_TEMPLATE.md`](docs/LAB_LOG_TEMPLATE.md): plantilla de experimentos.

## Regla de estado

Usar `PLANNED`, `IN_PROGRESS`, `BLOCKED`, `VERIFIED` o `REJECTED`. Solo usar `VERIFIED` con evidencia registrada, modelo/firmware identificados y procedimiento reproducible.
