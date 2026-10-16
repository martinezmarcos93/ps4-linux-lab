# Auditoría estática de construcción y escritura de imagen USB

**Fecha:** 2026-10-16  
**Tipo de evidencia:** inspección estática de fuentes públicas; no se ejecutaron los scripts.  
**Alcance:** `X-F1REBALL-X/PS4-Linux`, herramientas `tools/build-img.sh` y `tools/write-img.ps1`.  
**Fuente:** https://github.com/X-F1REBALL-X/PS4-Linux  
**Referencia de distribución consultada:** release `v1.0`, commit abreviado `26a6451` (28-09-2026).  
**Política:** no ejecutar el escritor ni conectar/escribir dispositivos físicos durante esta auditoría.

## Resumen ejecutivo

El flujo de construcción y escritura contiene salvaguardas útiles en el escritor de Windows, pero no es seguro asumir que el proceso de construcción siempre limpia sus recursos o que cualquier ruta de salida es inocua. Antes de reutilizar estos scripts en el laboratorio, se recomienda aislar la construcción en un directorio temporal dedicado, garantizar limpieza mediante `trap`, evitar borrar una ruta fija y verificar el resultado antes de permitir una escritura física.

Esta auditoría no demuestra que el script haya dañado datos ni que el resultado sea incorrecto; identifica rutas de fallo visibles en el código.

## Hallazgos

### BLD-001 — Borrado de una ruta fija antes de construir

**Severidad:** alta para datos existentes en esa ruta; impacto condicionado al entorno.

`build-img.sh` fija `IMG=/root/psxitarch-usb.img` y luego ejecuta `rm -f "$IMG"` sin preguntar ni comprobar si el archivo existente fue creado por esta ejecución.

**Consecuencia:** una ejecución puede eliminar una imagen previa o un archivo no relacionado que use exactamente esa ruta.

**Corrección recomendada:**
- construir en un directorio temporal único, creado explícitamente por la ejecución;
- nunca borrar un archivo preexistente de ruta fija;
- exigir que el destino final no exista o pedir una opción explícita de reemplazo;
- comprobar que el destino final no coincide con ningún input.

### BLD-002 — Limpieza de loop devices y montajes no garantizada ante errores

**Severidad:** media; puede dejar recursos del host montados o asociados.

El script usa `losetup -Pf --show`, monta ambas particiones y las desmonta al final del flujo normal. No instala un `trap` de limpieza. Con `set -e`, un fallo en `mkfs`, `mount`, `tar`, `cp`, `e2fsck` u otro comando puede terminar la ejecución antes de ejecutar `umount` y `losetup -d`.

**Consecuencia:** montajes residuales o loop devices ocupados, complicando reintentos y limpieza manual.

**Corrección recomendada:**
- registrar el loop device y cada punto de montaje solo después de crearlos correctamente;
- añadir un `trap` idempotente para EXIT/INT/TERM que desmonte en orden inverso y libere únicamente el loop device creado por esa ejecución;
- no usar `umount -l` como solución automática para ocultar un montaje ocupado;
- registrar los fallos de limpieza sin ocultar el código de salida original.

### BLD-003 — Puntos de montaje globales compartidos

**Severidad:** media en hosts con ejecuciones concurrentes o montajes preexistentes.

El script usa `/mnt/psx` y `/mnt/psxboot` mediante `mkdir -p`, sin comprobar si ya están montados ni si otra ejecución los está usando.

**Consecuencia:** una ejecución puede interactuar con un montaje preexistente o entrar en conflicto con otra construcción.

**Corrección recomendada:** crear puntos de montaje exclusivos bajo un directorio temporal propio; comprobar con `mountpoint` y registrar explícitamente qué montó esta ejecución antes de desmontar.

### BLD-004 — Validación de entradas insuficiente para una herramienta ejecutada como root

**Severidad:** media.

Se verifica que los inputs sean archivos regulares mediante `-f`, pero no se comprueba explícitamente que el archivo de salida sea distinto de los inputs, que el destino de salida no sea un enlace simbólico ni que haya espacio suficiente para la copia final. El script crea una imagen de 12 GiB y después copia esa imagen al destino, lo que requiere espacio adicional.

**Corrección recomendada:**
- resolver rutas canónicas y rechazar colisiones entre entradas y salida;
- rechazar enlaces simbólicos como destino;
- comprobar espacio para la imagen temporal y la salida;
- validar que el tar sea legible y que el initramfs tenga el formato esperado usando herramientas disponibles, sin ejecutarlo;
- fallar antes de crear dispositivos loop si cualquier precondición no se cumple.

### BLD-005 — La escritura física es destructiva por diseño

**Severidad:** crítica si se elige el disco incorrecto; mitigada parcialmente por las comprobaciones existentes.

`write-img.ps1` ejecuta `Clear-Disk -RemoveData -RemoveOEM -Confirm:$false` sobre el disco seleccionado cuando tiene particiones y luego abre `\\.\PHYSICALDRIVE$DiskNumber` para escritura directa. El script exige administrador, comprueba `BusType -eq USB`, `IsBoot`, `IsSystem`, tamaño y confirmación del número, salvo que se use `-Force`.

**Fortalezas observadas:** las comprobaciones de bus, disco de arranque/sistema y capacidad preceden al borrado. La confirmación interactiva reduce errores de selección.

**Riesgos residuales:**
- `-Force` omite la confirmación manual, por lo que no debe usarse en el procedimiento del laboratorio;
- el número de disco puede cambiar entre identificación y uso;
- el script no vuelve a consultar y comparar identidad/serie del disco inmediatamente antes de `Clear-Disk` y de abrir el dispositivo;
- un fallo durante la escritura puede dejar el USB parcialmente escrito, lo que es esperable en un escritor raw.

**Corrección recomendada antes de adoptar el escritor:** no usar `-Force`; capturar modelo, serie, tamaño y bus en una vista previa; volver a consultar el disco justo antes de cualquier operación destructiva y abortar si cambió cualquiera de esos atributos; pedir confirmación explícita de un identificador estable además del número. El laboratorio debe probar estas salvaguardas con mocks o pruebas estáticas, nunca escribiendo un disco real.

## Qué falta verificar

- No se ejecutó `build-img.sh` ni `write-img.ps1`.
- No se ha comprobado el comportamiento en todas las versiones de PowerShell, WSL o utilidades de Linux.
- No se ha validado la integridad del rootfs, kernel o initramfs distribuidos; esta auditoría es sobre el ciclo de construcción/escritura, no sobre su contenido.
- El checksum publicado de una release solo es útil si se obtiene por un canal confiable y se compara con el archivo exacto descargado.

## Plan de corrección propuesto

1. Escribir un constructor propio de laboratorio que use un directorio temporal único, no borre rutas fijas y tenga limpieza garantizada.
2. Separar construcción de imagen y escritura física en herramientas distintas; la construcción no debe requerir escribir dispositivos.
3. Añadir pruebas unitarias y de integración sobre archivos temporales e imágenes dispersas, incluyendo fallos inyectados en cada fase.
4. Implementar un modo de simulación que muestre rutas, espacio requerido, loop devices y montajes previstos, sin ejecutar `mkfs`, `mount`, `Clear-Disk` ni escribir dispositivos.
5. Mantener el escritor físico fuera del flujo normal hasta que las pruebas de identidad y confirmación estén demostradas.

## Estado de las correcciones propuestas (2026-10-15)

Cruce con el barrido resolutivo (los hallazgos BLD-001 a BLD-005 coinciden con `UPSTREAM_CODE_MAP.md` §2.4-2.5, que añade: destino `OUT` sin validar, `sleep 2` como sincronización, `"${SPARE[@]}"` bajo `set -u`, y que `BusType=USB` admite discos USB externos de datos):

| Hallazgo | Mitigación en el laboratorio | Estado |
|---|---|---|
| BLD-001 (ruta fija + `rm -f`) | `tools/build_usb_image.py`: salida nueva obligatoria, temporal `.<nombre>.parcial` + `os.replace`, sin borrar nada ajeno | `TESTS` |
| BLD-002 (sin `trap`, loops/montajes residuales) | No usa loop devices ni montajes (`mkfs.ext4 -d`, `sfdisk`, FAT32 propia sobre archivo); `finally` borra solo su temporal | `TESTS` (fallos inyectados) |
| BLD-003 (montajes globales) | No monta nada | `TESTS` |
| BLD-004 (entradas/salida sin validar) | Rechazo de symlinks, no regulares, vacíos, colisión de rutas, rutas del sistema, espacio insuficiente y root; formato de kernel/initramfs verificado antes de construir | `TESTS` |
| BLD-005 (escritura física destructiva) | No se implementa `write-usb-image`; procedimiento manual propuesto en `SAFETY_AND_TOOLING.md` | `BLOQUEADO` por límite del encargo |

La limitación declarada en el criterio de cierre sigue vigente: los tests del constructor no cierran el riesgo de la escritura física.

## Criterio de cierre

El riesgo de construcción puede considerarse mitigado cuando las pruebas demuestren que los fallos inducidos no dejan montajes/loop devices residuales, que ningún archivo preexistente se elimina silenciosamente, que inputs y salida no pueden colisionar y que el modo de simulación no realiza escrituras. El riesgo de escritura física requiere una verificación separada y no queda cerrado por los tests del constructor.
