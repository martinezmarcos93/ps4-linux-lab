# Investigación GPU, gaming y LLM

## Objetivo y límite
Determinar si Linux ofrece aceleración gráfica o de cómputo utilizable en una PS4 concreta. No asumir que APIs o backends de GPU AMD de PC están disponibles.

## Gate 0 — Sistema base
Exigir arranque reproducible, kernel/módulos identificados, estabilidad bajo carga leve, salida de vídeo caracterizada y recuperación externa conocida. Hasta entonces, GPU/LLM queda BLOCKED.

## Inventario gráfico
Registrar versión de kernel, módulos, Mesa, renderer OpenGL/extensiones, capacidades Vulkan si están disponibles, resolución/compositor, errores, reserva de memoria/VRAM, memoria disponible y temperatura con método de medida. No instalar una pila completa solo para obtener una herramienta de inventario; anotar dependencias faltantes.

## Hardware vs software rendering
Un escritorio visible no demuestra aceleración hardware. Registrar renderer y logs/módulos; ejecutar carga breve controlada. Si la evidencia es insuficiente o contradictoria, clasificar INCONCLUSIVE.

## Gaming/emulación
Registrar aplicación/versión, procedencia, renderer, resolución, ajustes, escena reproducible, duración, FPS (método/distribución), temperatura, errores y estabilidad tras salir. Separar compatibilidad, rendimiento y estabilidad.

## Cómputo GPU
Antes de frameworks, confirmar API expuesta, driver/runtime compatible, paquetes disponibles, memoria y prueba mínima. No inferir soporte Vulkan/OpenCL/ROCm/CUDA por la marca de GPU.

## Protocolo LLM
**Baseline CPU:** modelo pequeño con licencia apropiada; registrar versión/hash, cuantización, backend, parámetros, prompt, latencia al primer token, tokens/s sostenidos, memoria pico, temperatura y errores.

**Candidato GPU:** solo tras validar backend; mantener escenario comparable y registrar capas offloadadas, memoria, fallbacks y errores.

**Continuar** solo si el backend funciona, se demuestra uso efectivo y la mejora justifica complejidad/consumo. Si es incompatible o no mejora el baseline, documentar descarte.

| Dimensión | Métrica |
|---|---|
| Rendimiento | tokens/s sostenidos y latencia |
| Memoria | RAM y memoria GPU/unificada pico |
| Temperatura | lectura, método, intervalo y duración |
| Correctitud | finalización, errores, fallbacks |
| Reproducibilidad | modelo/hash/backend/versiones/parámetros |
| Coste | dependencias, parches y mantenimiento |

**Estado actual:** sin mediciones propias, consola identificada, kernel elegido o backend LLM validado.