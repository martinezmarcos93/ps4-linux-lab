# Flujo de arranque y puntos de diagnóstico

**Estado:** modelo conceptual, no procedimiento aprobado para ninguna consola concreta.

## Secuencia de alto nivel
1. Identificar modelo CUH, firmware y revisión/southbridge mediante evidencia fiable.
2. Confirmar requisitos del método de carga para ese firmware.
3. Confirmar loader/payload, procedencia, hash y versión.
4. Determinar selección del kernel y precedencia USB/interno para el commit exacto.
5. Iniciar kernel/initramfs y clasificar los mensajes disponibles.
6. Montar rootfs externo, verificando formato, etiqueta/UUID e integridad.
7. Iniciar userspace y escritorio si corresponde.
8. Validar kernel, módulos, driver gráfico, temperatura, periféricos y estabilidad.
9. Salir de forma controlada y comprobar el retorno al sistema original.

## Etapas y síntomas

| Etapa | Síntoma posible | Evidencia útil | Hipótesis, no conclusión |
|---|---|---|---|
| Método de carga | sin señal visible | firmware, método, hora, mensaje | método no activado o incompatible |
| Loader/payload | error/retorno inmediato | versión/hash, error | artefacto/requisito incorrecto |
| Selección de kernel | pantalla negra/bloqueo temprano | rutas y hashes | kernel ausente o equivocado |
| Kernel/initramfs | salida parcial/panic | logs, tiempos, hashes | driver, initramfs o configuración |
| Rootfs | kernel inicia pero no avanza | logs de montaje, UUID/etiqueta | rootfs no encontrado/incompatible |
| Userspace | consola sí, escritorio no | journal, servicios, espacio | servicio o stack gráfico |
| GPU/compositor | lentitud/artefactos | renderer, módulos, Mesa, temperatura | renderizado software o driver |
| Periféricos | función ausente | inventario, módulos, logs | soporte/configuración incompleta |

## Reglas
- Una pantalla negra no distingue por sí sola falta de señal, kernel bloqueado, rootfs ausente o fallo anterior al kernel.
- Cambiar una variable por intento y guardar hashes.
- Si el loader puede escribir en almacenamiento interno, detenerse hasta entender qué cambia y cómo revertirlo.
- Registrar cada intento con `docs/LAB_LOG_TEMPLATE.md`.

## Pendiente
La secuencia exacta, precedencia de rutas, tiempos y mecanismo de retorno deben confirmarse con código versionado o experimento registrado, no por inferencia.