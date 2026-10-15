# Plan de pruebas

Ningún test se considera ejecutado por estar documentado.

## Estados
`NOT_RUN` = definido; `PASS` = cumple; `FAIL` = no cumple; `BLOCKED` = faltan precondiciones; `NOT_APPLICABLE` = motivo registrado. Guardar entorno, versiones, entradas/hashes, comando, salida, fecha y operador. Un test virtual no demuestra seguridad sobre un disco físico.

## Documentación e integridad

| ID | Caso | Precondición | Resultado esperado | Abortar si |
|---|---|---|---|---|
| DOC-01 | Enlaces Markdown internos | checkout | todo enlace local resuelve | validador intenta modificar archivos |
| DOC-02 | Consistencia roadmap | docs actuales | tareas terminadas no quedan pendientes sin motivo | depende de hardware desconocido |
| INT-01 | Verificación SHA-256 | manifiesto confiable | hash exacto | origen/hash no verificable |
| INT-02 | Artefacto truncado | fixture | error claro, código no-cero | se usa artefacto real único sin copia |
| INT-03 | Hash esperado incorrecto | fixture | falla sin alterar archivo | el verificador silencia discrepancia |

## Imágenes/dispositivos simulados

| ID | Caso | Resultado esperado | Abortar si |
|---|---|---|---|
| IMG-01 | Imagen de prueba válida | informa formato/tamaño sin tocar discos | intenta escribir block device |
| IMG-02 | Imagen inválida | error legible y código no-cero | altera fixture |
| DISK-01 | Destino ambiguo | no selecciona automáticamente | elige implícitamente un destino |
| DISK-02 | Disco de sistema/arranque | rechaza destino | ofrece bypass genérico |
| DISK-03 | Capacidad insuficiente | no empieza escritura | tamaño necesario desconocido |
| WRITE-01 | Dry-run | muestra plan sin escribir medios físicos | intenta escritura real |

## Hardware (BLOCKED hasta inventario y método aprobados)

| ID | Prueba | Evidencia requerida | Criterio |
|---|---|---|---|
| HW-01 | Identificar consola | ficha de hardware | CUH/firmware confirmados |
| HW-02 | Método de carga | artefactos, hashes, mensajes | etapa del resultado identificada |
| HW-03 | Kernel | kernel/initramfs hashes y salida | etapa clasificada con evidencia |
| HW-04 | Rootfs | UUID/etiquetas/formato/logs | rootfs esperado montado |
| HW-05 | Retorno a sistema original | procedimiento y observaciones | arranque original comprobado |
| HW-06 | Estabilidad térmica | carga, duración, lecturas | criterio de parada respetado |
| HW-07 | Periféricos | pruebas aisladas | resultado por subsistema |

## GPU/LLM (BLOCKED hasta arranque reproducible)
- GPU-01: kernel, módulos, Mesa, renderer y API disponibles.
- GPU-02: distinguir hardware/software rendering con evidencia corroborante.
- GPU-03: carga breve, duración, temperatura, memoria y errores.
- LLM-01: modelo, cuantización, parámetros, tokens/s, latencia, RAM/temperatura en CPU.
- LLM-02: mismo escenario con backend GPU, registrando runtime, memoria, errores y fallbacks.
- LLM-03: comparación comparable y decisión documentada.

Abortar ante destino ambiguo, hash discrepante, escritura interna no prevista, anomalía térmica, error filesystem o evidencia insuficiente.