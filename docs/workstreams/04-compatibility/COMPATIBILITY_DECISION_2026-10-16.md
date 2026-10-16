# Decisión de compatibilidad — corte 2026-10-16

**Rama:** `workstream/04-compatibility`  
**Responsable:** ChatGPT; verificación local pendiente de Claude Code.  
**Equipo objetivo:** PS4 Slim CUH-2115B, firmware 13.52, capacidad observada 861,4 GB; southbridge reportado como Baikal B1 (`0x30201`) en la pantalla de información consultada por Marcos.  
**Decisión actual:** **INDETERMINADO / NO-GO para seleccionar o ejecutar una cadena de arranque.** La evidencia pública justifica continuar la investigación, pero no elegir kernel ni afirmar compatibilidad con esta unidad.

## 1. Evidencia actual

| Afirmación | Fuente / revisión | Nivel | Qué permite concluir | Qué no permite concluir |
|---|---|---|---|---|
| PS4-Linux declara dos modelos probados con FW 13.52: CUH-2116A/Baikal y CUH-7116B/Belize | [README upstream](https://github.com/X-F1REBALL-X/PS4-Linux/blob/66e21cb8c15f20189254e2608c6e9bf957eb8078/README.md), commit `66e21cb8c15f20189254e2608c6e9bf957eb8078` (2026-10-04) | README-UPSTREAM | El autor de la distribución afirma esos dos casos | No prueba CUH-2115B ni que todos los CUH-21xx compartan southbridge |
| El README recomienda kernel Baikal para CUH-2116A y kernel Belize para CUH-7116B | Misma fuente | README-UPSTREAM | La selección publicada es específica por fila | No permite extrapolar por cercanía numérica a CUH-2115B |
| Loader enumera soporte para Aeolia, Belize(2), Baikal y FW hasta 13.52; los firmwares 13.02, 13.04, 13.50 y 13.52 llevan `(?)` | [README loader](https://github.com/ps4-linux/ps4-linux-loader/blob/f70f43a60a973b3662daeb29c1f115d95408db93/README.md), commit `f70f43a60a973b3662daeb29c1f115d95408db93` (2026-09-23) | README-UPSTREAM | El proyecto afirma que existen offsets/payloads para esa gama | No es una prueba reproducida ni valida el modelo de consola |
| Usuario reportó CUH-2208B, Baikal, FW 13.52 con loader v25 y kernel 5.4.247 | [issue #10](https://github.com/ps4-linux/ps4-linux-loader/issues/10), creado 2026-09-22, actualizado 2026-09-26 | REPORTADO-TERCEROS; mantenedor agradece el detalle | Evidencia anecdótica detallada de una configuración Baikal/13.52 | No respalda los kernels 7.0.8/7.1.7 de PS4-Linux ni prueba CUH-2115B |
| Usuario reportó fallo inicial en PS4 Slim/Belize/FW 13.52 con loader v25 y después dijo que funcionó arrancando desde USB | [issue #11](https://github.com/ps4-linux/ps4-linux-loader/issues/11), cerrado 2026-09-26 | REPORTADO-TERCEROS, causa no establecida | El resultado depende de más variables que firmware/modelo; el reporte es incompleto | No permite afirmar incompatibilidad ni establecer causa raíz |
| La consola del laboratorio es CUH-2115B, FW 13.52, capacidad observada 861,4 GB | Registro local `docs/lab-logs/LAB-000-identificacion-consola.md` | OBSERVADO/COMUNICADO, según el campo | Define el baseline de investigación | No identifica revisión de placa ni southbridge |
| No se ha probado un arranque Linux propio en la consola | Registro del laboratorio y README del proyecto | LAB-PENDIENTE | La compatibilidad propia sigue sin probar | No debe etiquetarse como compatible ni incompatible |

## 2. Matriz cruzada de decisión

| Modelo objetivo | Firmware | Southbridge | Loader | Kernel candidato | USB-only estricto | Decisión |
|---|---|---|---|---|---|---|
| CUH-2115B | 13.52 | Baikal B1 (`0x30201`, reportado por el operador) | v25.1 / código fijado pendiente de revisión final | `bzImage-baikal-7.0.8` es candidato documental, no aprobado | No demostrado; la distribución consultada indica almacenar kernel/initramfs en el disco interno y el loader tiene fallback a rutas internas | **Candidato técnico identificado; NO-GO hasta cerrar USB-only y gate de artefactos** |
| CUH-2116A (caso publicado) | 13.52 | Baikal (según distribución) | loader asociado a PS4-Linux v1.0 | `bzImage-baikal-7.0.8` (declarado por el distribuidor) | No; instrucciones publicadas requieren kernel/initramfs internos | Solo afirmación upstream, no transferible al objetivo |
| CUH-7116B (caso publicado) | 13.52 | Belize (según distribución) | loader asociado a PS4-Linux v1.0 | `bzImage-belize-7.1.7` (declarado por el distribuidor) | No; instrucciones publicadas requieren kernel/initramfs internos | Solo afirmación upstream, no transferible al objetivo |
| CUH-2208B (reporte comunitario) | 13.52 | Baikal (reportado) | v25 | Kernel 5.4.247 Baikal (reportado; no es el 7.0.8 de la distribución) | No establecido por el issue | Evidencia de tercero; no usar como equivalencia |

## 3. Bloqueo principal: southbridge

El CUH-2115B por sí solo no identifica el southbridge; sin embargo, Marcos reportó una lectura de información del sistema que muestra `Baikal B1`, ID `0x30201`. En el código upstream auditado, `GetSouthbridgeName()` asigna explícitamente `0x30201` a `Baikal B1`. Esto eleva el dato a **REPORTADO-OBSERVADO por el operador**, no a una medición repetida e independiente en esta sesión. La tabla comunitaria de PS4 Developer Wiki presenta filas contradictorias para el identificador de modelo, pero esa ambigüedad general no invalida automáticamente la lectura de runtime de esta unidad. No volver a ejecutar un payload solo para repetir una observación ya registrada.

Siguiente observación admisible, sin intervención en la consola:
1. Buscar documentación primaria fiable que relacione **CUH-2115B exacto** y revisión de placa/southbridge; registrar URL, fecha y qué identifica realmente.
2. Revisar el registro de identificación existente y las fotos/documentos del usuario, si están disponibles en el checkout, distinguiendo dato leído directamente de inferencias.
3. Si la identificación exige abrir la consola, leer información interna o ejecutar un payload, dejarlo bloqueado para una fase física futura y describir el requisito; no improvisar una inspección ni pedir desmontaje ahora.
4. No usar números de serie, región comercial, capacidad del disco o semejanza de modelo como sustitutos del southbridge.

## 4. USB-only: criterio de exclusión independiente

El README de PS4-Linux ordena subir kernel e initramfs a `/data/linux/boot/` en el almacenamiento interno. Aunque la imagen raíz resida en USB, esta configuración **no cumple el requisito estricto de no tocar ni depender del disco interno**. El loader documenta también rutas internas por defecto y fallback. Para considerar una cadena USB-only viable, hace falta una ruta demostrada en la que:
- kernel e initramfs se obtengan del USB;
- el proceso de arranque no escriba automáticamente esos archivos al disco interno;
- no se dependa de archivos internos preexistentes;
- todos los accesos de lectura/escritura estén identificados estáticamente y probados primero con fixtures/simulaciones;
- la política de imagen y las herramientas impidan escribir a dispositivos físicos en la fase actual.

La documentación upstream menciona prioridad de USB para los archivos de boot si hay USB conectado, pero eso no prueba que el flujo completo sea USB-only ni que ningún otro componente escriba al disco interno. El comportamiento debe verificarse en código de una revisión fijada, sin ejecutar payloads.

## 5. Qué permitiría revisar la decisión

- Identificación fiable de la revisión de placa/southbridge de CUH-2115B, con fuente y método explícitos.
- Matriz cruzada modelo + revisión de placa + firmware + loader/tag/commit + kernel exacto + método de carga + origen de kernel/initramfs/rootfs.
- Trazabilidad del kernel candidato: versión real en la cabecera, fuente, configuración, hash, licencia y posibilidad de reconstrucción.
- Código fijado del loader auditado, licencia resuelta y análisis estático de todas las rutas de almacenamiento y escritura.
- Flujo USB-only verificado mediante tests no destructivos con imágenes sintéticas; no es necesario ni está autorizado probar la consola para cerrar esta etapa documental.
- Evidencia positiva de terceros clasificada como tal, sin convertirla en prueba del laboratorio.

## 6. Límites y conclusión

No actualizar firmware, no ejecutar payloads, no escribir una imagen en un USB físico, no modificar el disco interno y no probar en hardware. La recomendación presente es **no seleccionar kernel todavía**. El bloqueo restante ya no es principalmente la identificación del southbridge: es demostrar la cadena USB-only, fijar y validar artefactos exactos, resolver licencias/procedencia y revisar riesgos del payload de entrada. No se ha demostrado arranque Linux propio en CUH-2115B. Esto no significa que Linux sea imposible en esta consola; significa que la documentación actual no basta para decidir con rigor.

Pendiente para cerrar el workstream: Claude debe contrastar localmente el log de identificación, las fuentes y commits, y la matriz existente; registrar cualquier discrepancia antes de marcar tareas como completadas.
