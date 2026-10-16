# Estado integrado y plan de barridos — 2026-10-16

## Resumen ejecutivo

**Avance estimado de preparación técnica: ~50 % (confianza moderada). Arranque real en PS4: no demostrado.** El porcentaje mide preparación, auditoría, herramientas y documentación; no es una probabilidad de éxito de boot ni una medida lineal de riesgo.

La CI host-side del workstream 05 pasó en runs #61, #62 y #64 (run #64: commit `1355836a08e1e1ef92bbdf36dc66c2fb7c71975d`). El parche C propuesto para el loader sigue sin aplicarse a un checkout limpio ni compilarse. Se mantiene **NO-GO para prueba física**.

La lectura cruzada de WS03/WS04 encontró una discrepancia documental: `COMPATIBILITY_DECISION_2026-10-16.md` registra el southbridge reportado por Marcos como Baikal B1 (`0x30201`), mientras que `UPSTREAM_AUDIT_2026-10-16.md` aún dice que sigue desconocido y que el equipo es CUH-2115B. La referencia integrada debe tratar Baikal B1 como observación reportada por el operador, no como verificación independiente; el bloqueo de compatibilidad sigue siendo el artefacto exacto y la cadena USB-only, no repetir la identificación.

## Estado por frente

| Frente | Estimación | Hecho verificable | Pendiente dominante |
|---|---:|---|---|
| WS01 — documentación y gobernanza | 90 % | Estructura de coordinación y reglas de cambios documentadas | Consolidar el estado de PR/ramas y evitar referencias documentales obsoletas |
| WS02 — herramientas y tests host-side | 40 % | Verificador de artefactos, utilidades de imagen y tests; cobertura de FAT32/preflight ampliada | Ejecución completa reproducible fuera de CI, pruebas de fallos y auditoría integral de herramientas |
| WS03 — auditoría upstream/procedencia | 45 % | Mapa estático del loader/distro, rutas, referencias al almacenamiento interno y primer análisis de licencias | Procedencia exacta del kernel, inventario de initramfs/rootfs, licencia global del loader y evidencia runtime |
| WS04 — compatibilidad | 40 % | Decisión de compatibilidad y límites documentados | Evidencia reproducible de compatibilidad de kernel/loader para la consola y revisión de artefactos exactos |
| WS05 — cadena USB-only/imagen | 35 % | Preflight estricto, hardening de editor FAT32/publicación, pruebas sintéticas, revisión de procedencia y parche propuesto | Aplicabilidad/compilación del parche C, prueba del flujo completo, imagen reproducible y prueba runtime aislada |
| Primer arranque real | 0 % demostrado | Ninguna evidencia de boot Linux en la consola | Requiere cerrar puertas técnicas y autorización separada |

Los porcentajes por frente son estimaciones de gestión, no métricas automatizadas. La preparación media aproximada ronda el 50 %, pero el objetivo de primer arranque sigue sin acreditarse.

## Barrido 1 — cerrar el loader USB-only de punta a punta

1. Obtener un checkout limpio de `ps4-linux/ps4-linux-loader@f70f43a60a973b3662daeb29c1f115d95408db93`.
2. Aplicar primero `patches/loader-usb-only-f70f43a.patch` y luego `patches/loader-read-file-hardening-f70f43a.patch`; ejecutar `git apply --check` antes de cada aplicación.
3. Registrar salidas, versiones de compilador/toolchain, flags, hashes de fuente y ELF. No afirmar reproducibilidad si el toolchain no coincide con el artefacto publicado.
4. Si aplica, compilar en entorno aislado; revisar warnings y símbolos/offsets contra la referencia conocida.
5. Añadir pruebas de fallos de E/S para la rutina endurecida: seek fallido, mmap fallido, lecturas parciales, EOF prematuro, cierre fallido y archivo vacío. Mantener claro qué se prueba en host y qué no.
6. Verificar por análisis del diff que kernel e initramfs salen de una misma carpeta USB y que no quedan fallbacks internos en el loader.
7. Actualizar R-USB-001 y la decisión del WS05 solo después de evidencia reproducible.

**Bloqueo actual:** el entorno de trabajo anterior no pudo resolver GitHub por DNS. Se recuperó el código fuente fijado mediante el conector GitHub y se confirmó que el `read_file()` upstream sigue sin validar fallos de `lseek`, `mmap` y reinicio, y retorna sin cerrar recursos ante lectura fallida. También se confirmó que el parche USB-only elimina los fallbacks internos y selecciona una carpeta con ambos archivos obligatorios. Esto permite revisar el contexto del diff, pero no sustituye `git apply --check` ni la compilación. Si el entorno sigue sin red, pedir a Codex que ejecute el bloque de verificación en su entorno con acceso y entregue logs completos, sin ejecutar payloads.

## Barrido 2 — inventario y aceptación de artefactos

Crear un manifiesto único que relacione cada artefacto candidato con:
- nombre, tamaño y SHA-256;
- URL/origen exacto, commit/tag/fecha y método de descarga;
- licencia y alcance de la licencia;
- evidencia de compatibilidad con firmware 13.52 y el southbridge reportado;
- estado: candidato, verificado, rechazado o bloqueado;
- si se puede redistribuir y bajo qué condiciones.

Cerrar explícitamente kernel Baikal, initramfs, rootfs y loader. No reemplazar evidencia faltante con la presencia de un hash: integridad no equivale a autenticidad, licencia ni compatibilidad. No publicar binarios cuya licencia/procedencia no esté clara.

## Barrido 3 — auditoría runtime del initramfs/rootfs

1. Enumerar archivos y scripts de arranque del initramfs y rootfs; revisar `init`, servicios, `fstab`, reglas udev, scripts de montaje y configuración de swap.
2. Buscar referencias a HDD interno, particiones, `/data`, `/dev/sd*`, `eap_hdd_key.bin`, montaje, fsck, reparticionado, swap y escrituras persistentes.
3. Clasificar cada acceso como lectura, montaje solo lectura, montaje escritura, modificación de particiones o no determinado.
4. Trazar el origen de cada archivo crítico desde el medio USB hasta el montaje final.
5. Producir pruebas negativas/estáticas y un informe de rutas no resueltas. Si los artefactos no se pueden inspeccionar, dejar el punto como bloqueado; no inferir seguridad por ausencia de evidencia.

## Barrido 4 — pipeline host-side reproducible y seguro

- Ejecutar toda la suite en un entorno limpio y registrar comando, versión de Python, dependencias, sistema operativo, resultado y commit.
- Añadir casos adversariales para rutas, symlinks, archivos truncados, tamaños extremos, nombres ambiguos, fallos de lectura/escritura, destinos existentes y fallos durante la publicación.
- Verificar que ninguna herramienta escribe automáticamente a dispositivos de bloque, usa `sudo`, autodetecta discos físicos o modifica la consola.
- Construir una imagen sintética de prueba, inspeccionarla y reconstruirla para comparar hashes; documentar si la reproducibilidad es exacta o solo estructural.
- Mantener un manifiesto de salida y modo dry-run por defecto.

## Barrido 5 — matriz de compatibilidad y gate de prueba

Consolidar en una sola matriz:
- consola: PS4 Slim CUH-2115B, firmware 13.52;
- southbridge reportado y evidencia de identificación;
- loader, offsets/firmware soportados y método de entrada requerido;
- kernel exacto, initramfs y rootfs;
- periféricos, salida de vídeo y limitaciones conocidas;
- requisitos previos, riesgos, plan de recuperación y criterios de aborto.

No declarar compatibilidad solo porque el firmware aparezca en una tabla del loader. Exigir evidencia para la combinación exacta de hardware, firmware y artefactos. El gate de prueba física es independiente y requiere autorización explícita; no ejecutar payloads ni escribir USB/discos mientras siga cerrado.

## Orden de ejecución recomendado

1. **Primero:** obtener y validar el parche C en un checkout limpio; es un bloqueo concreto y acotado.
2. **En paralelo:** pedir a los dos agentes Codex resultados con evidencia del inventario de artefactos y auditoría de initramfs/rootfs, evitando duplicar tareas.
3. **Después:** ejecutar el pipeline host-side completo y ampliar tests adversariales.
4. **Luego:** consolidar matriz de compatibilidad, manifiesto de artefactos y checklist de recuperación.
5. **Finalmente:** emitir un informe de gate GO/NO-GO con evidencia por criterio. La prueba física no se inicia por completar documentación: requiere autorización explícita aparte.

## Reglas de cambio

- No fusionar PR #2 o PR #3, ni cambiar `main`, sin autorización explícita.
- No borrar ramas de workstream o temporales durante esta fase.
- No ejecutar payloads, no escribir medios físicos y no escribir en el almacenamiento interno de la consola.
- Cada afirmación de validación debe apuntar a commit, comando, log o artefacto verificable.
- Si una tarea depende de acceso de red, hardware o artefactos ausentes, registrar el bloqueo y delegar una comprobación reproducible; no simular el resultado.
