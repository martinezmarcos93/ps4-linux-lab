# GPU, gaming y LLM — protocolo de evaluación, sin conclusiones adelantadas

Este documento define **cómo medir**, no afirma rendimiento. Ninguna cifra de este documento proviene de una medición propia (no tenemos hardware identificado todavía) salvo que se cite explícitamente una fuente de terceros con su nivel de confianza. Ver `docs/COMPATIBILITY_MATRIX.md` para qué combinaciones tienen evidencia de arranque exitoso.

## 1. Lo que ya sabemos por código, no por benchmark

Documentado con cita exacta en `docs/UPSTREAM_CODE_MAP.md` §1.4:

- El reloj y power-gating de la GPU se fijan **manualmente en el payload** (`kexec.c`, función `sys_kexec`), con valores distintos para PS4 Pro vs Fat/Slim, **antes** de que Linux arranque.
- El cmdline por defecto desactiva `radeon.dpm=0 amdgpu.dpm=0` — sin gestión dinámica de frecuencia por parte de ningún driver Linux.
- **Consecuencia directa para cualquier benchmark:** el reloj de GPU observado es el que fijó el payload en el exploit, no uno que Linux/amdgpu puedan subir o bajar en caliente. Si se quisiera otro reloj, habría que modificar esos valores en el payload (`kexec.c` líneas 136-164) y recompilar — no es un parámetro de arranque de Linux.
- La VRAM es una partición real de memoria unificada, reconfigurada a nivel de registros del controlador de memoria (`configure_vram()`, `linux_boot.c`), parametrizable entre 32 MB y 4096 MB vía `vram.txt`. Memoria total del sistema: 8 GB GDDR5 unificados (dato de hardware conocido de la PS4/PS4 Pro, no específico de este código) menos la VRAM reservada.

## 2. Qué determinar primero, en orden, antes de cualquier prueba de IA

No instalar ningún framework de IA (`llama.cpp`, Ollama, PyTorch, etc.) antes de completar esta secuencia — ver D-003 en `docs/DECISION_LOG.md`.

1. **Identificar GPU y driver de kernel real.**
   - `lspci -k` (clase VGA/3D, kernel driver en uso: `amdgpu` o `radeon`).
   - `dmesg | grep -i drm` / `dmesg | grep -i amdgpu` para errores de inicialización del driver.
   - `cat /sys/class/drm/card0/device/uevent` y `/sys/kernel/debug/dri/*/amdgpu_firmware_info` (si `debugfs` está montado) para confirmar qué firmware cargó realmente (recordar que el firmware se inyecta en runtime desde la propia consola — ver `UPSTREAM_CODE_MAP.md` §1.5 — así que confirmar que **cargó**, no asumirlo).
2. **Confirmar stack Mesa y versión.**
   - `glxinfo -B` (requiere `mesa-utils`): renderer, versión de OpenGL, si el renderizado es por hardware o por software (`llvmpipe`/`softpipe` en el renderer indica software — invalida cualquier medición de "aceleración").
   - El README de la distribución atribuye los paquetes de Mesa parcheados a "centi07 y DionKill" — **no auditados en esta sesión**; registrar la versión exacta instalada.
3. **Confirmar soporte real de Vulkan, si corresponde.**
   - `vulkaninfo --summary` (requiere `vulkan-tools`).
   - El issue #10 de `ps4-linux-loader` (REPORTADO-TERCEROS, ver `COMPATIBILITY_MATRIX.md`) menciona "AMD RADV LIVERPOOL, Vulkan 1.2.145" con un Mesa 20.3.5 con parches "Liverpool" — es la única mención de Vulkan funcionando que encontramos, y es de un tercero, no verificado por nosotros.
4. **Medir memoria disponible real, no nominal.**
   - `free -h` (RAM visible a Linux, ya neta de la VRAM reservada).
   - `cat /sys/class/drm/card0/device/mem_info_vram_total` y `..._vram_used` si existen, para confirmar que la reserva de `vram.txt` se refleja en el driver.
5. **Medir temperatura y estabilidad antes de cualquier carga sostenida.**
   - `sensors` si hay soporte, o la fuente de temperatura que el kernel/driver expongan; si no hay ninguna, registrar explícitamente "sin lectura de temperatura disponible" en vez de omitir el dato.

## 3. Evaluación gráfica y gaming — qué medir y cómo no engañarse

- **Confirmar renderizado por hardware antes de cualquier FPS.** Un `glxinfo`/`vulkaninfo` que muestre un renderer software invalida la medición — descartar esa corrida, no reportarla como rendimiento de GPU.
- **Reproducibilidad:** correr cada benchmark/juego al menos 2 veces en sesiones de arranque distintas antes de registrar un número, porque el reloj de GPU fijo (sección 1) hace esperable baja varianza entre corridas — una varianza alta inesperada es en sí misma un hallazgo a investigar, no a promediar y ocultar.
- **Herramientas sugeridas (a confirmar su disponibilidad en el rootfs real, no asumida):** `vkcube`/`vkmark` para un piso mínimo de Vulkan, `glmark2` para OpenGL, y los juegos/emuladores concretos que se quieran evaluar — cada uno con su propia entrada en `docs/TEST_PLAN.md`.
- **Qué registrar por prueba:** resolución, FPS (mínimo/promedio si la herramienta lo da), renderer confirmado, VRAM reservada (`vram.txt`), temperatura al inicio y al final, y si hubo cuelgue/reinicio.
- **Un solo reporte de terceros (issue #10) menciona** Proton 10 + DXVK + "R.E.P.O." y "Portal 2 a 60 FPS en configuración alta" sobre CUH-2208B con 3072 MB de VRAM. Esto es **ACEPTADO-MANTENEDOR**, no reproducido por nosotros — no usarlo como expectativa de rendimiento propia hasta repetirlo con hardware y configuración propios y registrarlo en `LAB_LOG_TEMPLATE.md`.

## 4. Inferencia LLM — cuellos de botella a caracterizar, no a asumir

**No prometemos aceleración por GPU para LLM en ningún punto de este documento.** La arquitectura GCN de la PS4/PS4 Pro (2013-2016) no tiene ningún reporte, en las fuentes auditadas en esta sesión, de soporte de backends de cómputo modernos (ROCm, Vulkan compute para inferencia, CUDA — que no aplica, es AMD). Esto es **DESCONOCIDO/PENDIENTE**, no "no funciona": no se buscó evidencia específica de backends de cómputo GPU para GCN1/GCN4 en esta sesión; sería trabajo adicional de investigación antes de siquiera intentar una prueba.

### 4.1 Orden de evaluación obligatorio

1. **Baseline en CPU, siempre primero.** La CPU es un AMD Jaguar de 8 núcleos a baja frecuencia (dato de hardware conocido, no de este código) — es razonable esperar que sea un cuello de botella serio incluso sin GPU, y medirlo da el punto de comparación real.
   - Herramienta: `llama.cpp` compilado solo para CPU (sin ningún backend GPU), con un modelo pequeño cuantizado (p. ej. una variante GGUF de pocos miles de millones de parámetros a 4 bits).
   - Métrica: tokens/segundo en generación y en prompt processing, uso de RAM, temperatura durante la corrida.
2. **Solo después del baseline, investigar si existe algún backend de cómputo GPU disponible.**
   - Comprobaciones seguras: `vulkaninfo` buscando extensiones de cómputo (`VK_KHR_compute` es parte del core de Vulkan 1.0, así que su presencia no es suficiente — buscar límites de cómputo reales: `maxComputeWorkGroupCount`, soporte de tipos de datos de 16 bits si se quisiera cuantización agresiva); `clinfo` si hubiera OpenCL disponible (no confirmado que exista en este stack); revisar si `llama.cpp`/otro backend tienen siquiera un camino Vulkan-compute o CLBlast compatible con GCN de esta generación — **esto es investigación bibliográfica adicional, no cubierta por la auditoría de código de esta sesión**.
   - No instalar ROCm: no hay ninguna evidencia en las fuentes auditadas de que ROCm soporte esta GPU (su soporte oficial de AMD típicamente empieza en generaciones GCN más recientes o posteriores); confirmarlo o descartarlo con una búsqueda específica antes de invertir tiempo instalándolo.
3. **Si aparece un backend GPU candidato, probarlo con el mismo modelo del baseline, no con uno distinto**, para que la comparación sea válida.

### 4.2 Qué registrar por prueba de LLM

Modelo (nombre, parámetros, cuantización exacta), backend usado (CPU puro / Vulkan-compute / OpenCL / otro), tokens/s de generación y de prompt, RAM usada, VRAM reservada (`vram.txt`) y si el backend la usó o no, temperatura, y errores exactos si el backend GPU falla al inicializar (no solo "no funcionó").

### 4.3 Criterio de descarte explícito

Descartar la aceleración por GPU para LLM en este hardware si: (a) no existe ningún backend de cómputo mantenido que soporte esta generación de GCN con el driver `amdgpu`/Mesa disponibles en este rootfs, o (b) existiendo, el tiempo de desarrollo/parcheo necesario para hacerlo funcionar supera el valor de la mejora esperada frente al baseline de CPU. Documentar la decisión en `docs/DECISION_LOG.md` con la evidencia que la sostiene, sea cual sea el resultado.

## 5. Investigación bibliográfica de backends LLM (2026-10-16)

**Conclusión provisional:** ROCm no es una ruta oficial demostrada para la GPU de PS4; Vulkan es una ruta experimental plausible, pero la evidencia disponible no demuestra que funcione en el rootfs concreto ni que sea suficientemente estable o rápida para inferencia.

### 5.1 ROCm

La matriz oficial vigente de ROCm describe las GPU soportadas y advierte que una GPU no incluida no tiene soporte oficial. La matriz consultada enumera familias AMD modernas (Instinct, Radeon recientes y Ryzen recientes), pero no identifica la GPU personalizada Liverpool de PS4. Por tanto:

- **Estado:** NO SOPORTE OFICIAL CONFIRMADO para Liverpool/PS4 en la matriz consultada.
- **No equivale a:** prueba de imposibilidad técnica o ausencia de forks comunitarios.
- **Decisión:** no invertir en instalar ROCm ni adaptar HIP para esta consola mientras no aparezca una referencia primaria y reproducible que incluya explícitamente esta GPU.

Fuentes:
- AMD, matriz ROCm 10.1.0 (publicada 2026-08-25): https://rocm.docs.amd.com/en/latest/compatibility/compatibility-matrix.html
- AMD, requisito de hardware soportado: https://rocm.docs.amd.com/projects/install-on-linux/en/latest/reference/system-requirements.html

### 5.2 Vulkan / RADV / llama.cpp

La discusión técnica del proyecto `ggml-org/llama.cpp` sobre RADV señala que RADV se usa con GPU AMD soportadas por `amdgpu`, incluidas generaciones GCN; también advierte que GCN1/GCN2 puede requerir parámetros de kernel para forzar el driver `amdgpu` en lugar del driver antiguo `radeon`. Esto hace que Vulkan sea una hipótesis razonable para investigar, pero no prueba compatibilidad con el kernel modificado, firmware inyectado ni Mesa parcheado de PS4 Linux.

La misma discusión identifica límites relevantes para esta generación: FP16 no está disponible en todas las GPU GCN antiguas, y las capacidades reales deben leerse del backend, no deducirse solo de que `vulkaninfo` funcione. Además, hay reportes recientes de errores/crashes en hardware GCN antiguo; por tanto, incluso una inicialización correcta no basta para declarar estabilidad.

Fuentes:
- `ggml-org/llama.cpp`, guía comunitaria de depuración RADV, 2026-05-18: https://github.com/ggml-org/llama.cpp/discussions/23295
- `ggml-org/llama.cpp`, reporte de crash Vulkan en GCN 1.0 con RADV (caso de otra GPU, no PS4): https://github.com/ggml-org/llama.cpp/issues/19610

### 5.3 Evaluación y decisión actual

| Ruta | Evaluación documental | Decisión |
|---|---|---|
| ROCm/HIP | La GPU PS4 no figura como soportada oficialmente en la matriz consultada | No invertir en instalación; reconsiderar solo con evidencia específica |
| Vulkan/RADV en `llama.cpp` | Backend existente y casos GCN reportados, pero sin prueba específica reproducible para PS4 Linux | Candidato experimental, condicionado a que el sistema arranque y exponga Vulkan estable |
| OpenCL/CLBlast | No se encontró evidencia primaria suficiente para el rootfs ni la GPU de PS4 | No priorizar hasta hallar una distribución/runtime verificable |
| CPU-only `llama.cpp` | No depende del backend GPU, pero rendimiento real desconocido | Baseline obligatorio si se alcanza un arranque estable |

No instalar paquetes ni compilar frameworks todavía. Una vez logrado un arranque externo reproducible, la secuencia mínima será: identificar GPU/driver; registrar versiones de kernel, Mesa y Vulkan; ejecutar una prueba Vulkan pequeña; confirmar resultados correctos y estabilidad; recién entonces compilar `llama.cpp` con Vulkan y comparar el mismo modelo contra CPU-only.

### 5.4 Límite de la investigación

Esta investigación es bibliográfica y no equivale a un test sobre la PS4 del laboratorio. El southbridge de la consola sigue sin identificar, no se ha validado el rootfs candidato y no hay arranque Linux propio. La conclusión debe mantenerse como `INFERENCE` respaldada por fuentes externas, no como `LAB-VERIFIED`.
