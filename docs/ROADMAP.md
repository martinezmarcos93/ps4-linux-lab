# Roadmap

Estados: PLANNED, IN_PROGRESS, BLOCKED, VERIFIED y REJECTED. Una puerta de salida requiere evidencia registrada; una declaración upstream no equivale a validación propia.

## Fase 0 — Inicialización y gobernanza
**Estado:** COMPLETADA en alcance inicial; mantenimiento continuo.
- [x] Crear repositorio privado martinezmarcos93/ps4-linux-lab.
- [x] Incorporar README y documentos base.
- [x] Registrar riesgos y prioridad de almacenamiento externo.
- [ ] Revisar enlaces/estados después de cada barrido.
- [ ] Definir política de protección de main y CI cuando existan checks automáticos.
- [ ] Definir retención y almacenamiento de logs/artefactos.
**Salida:** documentos de gobernanza coherentes; no implica soporte de hardware.

## Fase 1 — Identificación de consola
**Estado:** BLOCKED — no hay inventario de hardware propio.
- [ ] Registrar modelo CUH y revisión visible.
- [ ] Registrar firmware exacto sin actualizarlo.
- [ ] Registrar estado de arranque original y síntomas existentes.
- [ ] Determinar qué datos requieren respaldo.
- [ ] Clasificar identificación de southbridge como hecho, inferencia o desconocido.
**Salida:** ficha de hardware y procedencia de cada dato, sin acciones destructivas.

## Fase 2 — Auditoría upstream/licencias
**Estado:** IN_PROGRESS.
- [x] Leer README de ambos upstreams.
- [x] Inspección inicial de scripts de imagen y escritura USB en PS4-Linux.
- [x] Registrar límites de la revisión inicial.
- [ ] Inventariar scripts, dependencias y flujo de arranque completo.
- [ ] Fijar commits/tags exactos consultados.
- [ ] Revisar releases, hashes y cambios relevantes.
- [ ] Determinar licencias de cada componente candidato.
- [ ] Contrastar compatibilidad por firmware, southbridge, kernel y loader.
**Salida:** mapa de código y matriz citados con commit/tag y nivel de evidencia.

## Fase 3 — Selección de arranque
**Estado:** BLOCKED — depende de fases 1 y 2.
- [ ] Confirmar requisitos del método de carga para el firmware real.
- [ ] Confirmar kernel/initramfs/rootfs para la revisión de hardware.
- [ ] Investigar precedencia de rutas internas/USB.
- [ ] Documentar toda escritura interna y posibilidad de rollback.
- [ ] Preparar pasos y condiciones de aborto.
**Salida:** procedimiento específico y revisado para la consola real.

## Fase 4 — Herramientas USB seguras
**Estado:** PLANNED.
- [ ] Implementar doctor, inspect-disks, verify-artifacts e inspect-image.
- [ ] Crear manifiesto con origen, versión, hash y tamaño.
- [ ] Construir imágenes en directorio temporal único y limpiar solo archivos propios.
- [ ] Separar escritura física de inspección y volver a identificar destino justo antes.
- [ ] Añadir dry-run comprobable.
- [ ] Probar con fixtures e imágenes; no discos reales.
- [ ] Verificar escritura y capturar informe.
**Salida:** tests prueban abortos ante destino ambiguo, disco de sistema, tamaño insuficiente y confirmación ausente.

## Fase 5 — Preparación de medio externo
**Estado:** BLOCKED — depende de 1–4 y de procedencia/licencias.
- [ ] Construir imagen reproducible en PC.
- [ ] Verificar hashes, formato, particiones, etiquetas y espacio.
- [ ] Confirmar correspondencia kernel/initramfs/rootfs.
- [ ] Evitar kernels ambiguos según loader.
- [ ] Entender cambios internos del método de carga.
- [ ] Validar el procedimiento con imagen virtual.
**Salida:** artefacto USB reproducible y validado antes de conectar a consola.

## Fase 6 — Primer arranque Linux
**Estado:** BLOCKED — no hay consola identificada ni medio aprobado.
- [ ] Ejecutar solo procedimiento específico aprobado.
- [ ] Registrar vídeo, indicadores, tiempos y logs.
- [ ] Cambiar una variable por intento.
- [ ] Clasificar etapa del fallo.
- [ ] Verificar retorno al sistema original.
**Salida:** arranque externo reproducible y regreso comprobado.

## Fase 7 — Estabilidad/periféricos
**Estado:** PLANNED.
- [ ] Inventariar CPU, RAM, GPU, kernel, módulos y driver.
- [ ] Probar red, audio, USB, Bluetooth, HDMI y mandos por separado.
- [ ] Medir temperatura y estabilidad bajo carga progresiva.
- [ ] Documentar filesystem y modo rescate.
**Salida:** perfil estable durante una ventana definida.

## Fase 8 — GPU/juegos/emulación
**Estado:** PLANNED.
- [ ] Distinguir renderizado hardware/software.
- [ ] Capturar capacidades reales de OpenGL/Vulkan si están disponibles.
- [ ] Definir benchmarks breves y reproducibles.
- [ ] Probar cada aplicación individualmente.
- [ ] Registrar resolución, settings, FPS, temperatura, duración y fallos.
**Salida:** matriz basada en mediciones.

## Fase 9 — Compute/LLM
**Estado:** PLANNED; incertidumbre alta.
- [ ] Registrar baseline CPU/RAM/temperatura.
- [ ] Identificar APIs y backend realmente soportados.
- [ ] Elegir modelo pequeño cuantizado y fijar parámetros.
- [ ] Medir tokens/s, latencia, memoria, estabilidad y temperatura.
- [ ] Comparar CPU/GPU con condiciones equivalentes.
- [ ] Descartar aceleración si el coste técnico supera el beneficio.
**Salida:** benchmark reproducible y decisión documentada.

## Fase 10 — Diagnóstico/recuperación
**Estado:** PLANNED.
- [ ] Árbol de diagnóstico por síntoma.
- [ ] Herramientas de solo lectura y recolección de logs.
- [ ] Backup antes de editar; restauración atómica.
- [ ] Dry-run en acciones futuras con efectos secundarios.
- [ ] Tests de fallos inducidos en imágenes de laboratorio.
- [ ] Separar recuperación Linux de recuperación del firmware original.
**Salida:** cada reparación incluye precondiciones, aborto, verificación y rollback.

## Fase 11 — Decisión de uso final
**Estado:** PLANNED.
- [ ] Comparar utilidad como mini-PC, equipo de emulación, servidor o nodo de IA.
- [ ] Comparar consumo, ruido, limitaciones y mantenimiento contra alternativas.
- [ ] Identificar tareas que no justifican más investigación.
- [ ] Documentar limitaciones y conclusión.
**Salida:** decisión respaldada por evidencia, no expectativas.

## Dependencias críticas
- Fase 1 bloquea fases 3, 5 y 6.
- Fase 2 bloquea la selección/reutilización de componentes.
- Fase 4 puede avanzar en PC usando solo archivos/imágenes virtuales.
- Fases 8 y 9 esperan arranque y estabilidad reproducibles.
