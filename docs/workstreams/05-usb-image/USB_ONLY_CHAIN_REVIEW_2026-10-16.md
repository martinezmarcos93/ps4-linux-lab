# Revisión independiente: cadena de carga USB-only

**Fecha:** 2026-10-16  
**Rama:** `workstream/05-usb-image`  
**Revisor:** ChatGPT  
**Upstream fijado:** `ps4-linux/ps4-linux-loader` commit `f70f43a60a973b3662daeb29c1f115d95408db93`; `X-F1REBALL-X/PS4-Linux` commit `66e21cb8c15f20189254e2608c6e9bf957eb8078`.  
**Método:** lectura estática de código/README y metadatos; sin compilar ni ejecutar artefactos.

## Conclusión

**NO-GO para ejecución en la PS4 por ahora; GO para continuar pruebas sintéticas en PC.** El código del loader busca los archivos de arranque primero en USB, pero aplica el fallback a almacenamiento interno **por archivo y de forma independiente**. Por tanto, si falta un archivo en USB, puede combinar kernel/initramfs/argumentos procedentes de medios distintos. No existe en el flujo auditado una garantía estricta de “todo desde USB o abortar”.

Esta revisión no encontró en el fragmento auditado una escritura directa de archivos al almacenamiento interno: las rutas examinadas son argumentos de `read_file()`. Eso no constituye una auditoría exhaustiva de todo el payload ni demuestra que la cadena completa no escriba al disco; sí permite afirmar que el riesgo visible en este punto es el **fallback/mezcla de fuentes**, además del parcheo de kernel en memoria.

## Evidencia estática

### 1. Selección de los archivos en `main-aio.c`

La macro `L(name, where, wheresz, is_fatal)` intenta estas rutas en este orden:

1. `/mnt/usb0/<nombre>`
2. `/mnt/usb1/<nombre>`
3. `/data/linux/boot/<nombre>`
4. `/user/system/boot/<nombre>`

Se usa para cargar por separado:

- `bzImage` — obligatorio.
- `initramfs.cpio.gz` — obligatorio.
- `bootargs.txt` — opcional; si no se encuentra, se utiliza una línea de comandos por defecto.
- `vram.txt` — opcional; si no se encuentra o no es válido, se utiliza el valor por defecto del payload.

El resultado es que los cuatro elementos no se resuelven como un conjunto atómico. Ejemplo de fallo: el USB tiene `bzImage` pero no `initramfs.cpio.gz`; el kernel puede proceder de USB y el initramfs de `/data/linux/boot/`. La misma mezcla puede ocurrir con `bootargs.txt` y `vram.txt`.

**Fuente fijada:** [`main-aio.c` en el commit auditado](https://github.com/ps4-linux/ps4-linux-loader/blob/f70f43a60a973b3662daeb29c1f115d95408db93/linux/main-aio.c), funciones `main()`, `get_sb_id()` y macro `L`; el bloque de carga se encuentra aproximadamente en la zona de líneas 370–430 de esa revisión. Confirmar números exactos en el checkout local antes de citarlos como líneas definitivas.

### 2. Comportamiento posterior

Después de cargar los archivos, el payload llama a `kexec(kernel_main, ...)`, parchea el kernel de Orbis en memoria y arma el handoff a Linux. El código auditado también altera configuración de memoria/GPU y transfiere control al kernel Linux. No es una simple utilidad de copia ni una operación reversible ordinaria.

El loader consulta `hw.sce_subsys_subid` y mapea `0x30201` a `Baikal B1`. Marcos informó que la pantalla de información mostraba ese valor para la consola objetivo. Esto permite que el kernel Baikal sea un **candidato documental**, pero no demuestra que el kernel seleccionado arranque en esa consola.

### 3. Distribución PS4-Linux

El README de la distribución indica renombrar el kernel como `bzImage` y colocarlo junto con `initramfs.cpio.gz` en `/data/linux/boot/`. Eso utiliza el almacenamiento interno de la consola. La imagen USB lista para usar no convierte automáticamente el procedimiento completo en USB-only.

El script `tools/build-img.sh` crea una imagen de disco y no instala por defecto `bzImage` en la partición FAT de arranque; la revisión anterior de código indica que coloca `initramfs.cpio.gz` y, opcionalmente, kernels de repuesto con nombres que el loader ignora. Antes de usar esa imagen como candidata, hay que demostrar cómo se ubicarán ambos archivos de arranque sin usar el disco interno.

Fuentes:
- [README de PS4-Linux, revisión fijada](https://github.com/X-F1REBALL-X/PS4-Linux/blob/66e21cb8c15f20189254e2608c6e9bf957eb8078/README.md)
- [`tools/build-img.sh`, revisión fijada](https://github.com/X-F1REBALL-X/PS4-Linux/blob/66e21cb8c15f20189254e2608c6e9bf957eb8078/tools/build-img.sh)

## Invariantes requeridos para nuestra propia cadena

La implementación candidata —no el upstream sin modificar— debe demostrar:

1. **All-or-nothing:** resolver todos los artefactos obligatorios desde un único origen USB antes de comenzar la transición; si falta uno, abortar. No hacer fallback de cada archivo individual al disco interno.
2. **USB-only explícito:** no consultar rutas internas en el modo estricto. Si no se puede configurar esta propiedad en el loader elegido, registrar el bloqueo y no ejecutar.
3. **Manifiesto cerrado:** kernel, initramfs, argumentos de boot y configuración VRAM quedan ligados a una revisión/manifiesto y hashes esperados; no mezclar archivos de versiones distintas.
4. **Raíz correcta:** los argumentos de kernel apuntan al rootfs de la imagen USB prevista; verificar el initramfs y su lógica de montaje sin ejecutarlos.
5. **Fail closed:** si falta un archivo, el hash no coincide, la partición esperada no está presente o el layout no coincide, no iniciar el handoff.
6. **Sin escrituras en disco interno:** inventariar todas las llamadas de escritura y almacenamiento en el loader, payload externo, initramfs y scripts. La revisión parcial actual no prueba esta propiedad para toda la cadena.
7. **Pruebas sintéticas:** cubrir USB0 completo, USB1 completo, kernel ausente, initramfs ausente, archivos divididos entre USB y HDD, configuración opcional ausente, hash incorrecto, rutas duplicadas y fallo de lectura. Estas pruebas se hacen con fixtures en PC, nunca con la consola.
8. **Separación de etapas:** primero inspección estática y dry-run; después aprobación de artefactos y licencia; solo en un hito separado puede considerarse una prueba física.

## Plan de cierre para I01–I04

- [ ] I01 — Dibujar la cadena artefacto → imagen → montaje USB → lectura de kernel/initramfs → rootfs.
- [x] I02 — Identificar en el loader el orden de rutas de kernel/initramfs/bootargs/vram y el fallback por archivo.
- [x] I03 — Identificar el riesgo de mezclar artefactos de USB y HDD; la recuperación no es fail-closed.
- [x] I04 — Proponer invariantes de USB-only y pruebas negativas.
- [ ] I05–I10 — Esperar resultados de Claude sobre herramientas, fixtures, reproducibilidad, path handling, manifiesto y recuperación.
- [ ] I11 — Revisar el diff del workstream 05 cuando Claude lo publique.
- [ ] I12 — Emitir decisión final después de integrar evidencia de workstreams 02–04.

## Decisión y límites

No se ha ejecutado código en la PS4 ni se ha escrito en USB físico o almacenamiento interno. No se recomienda seguir las instrucciones upstream que copian kernel/initramfs a `/data/linux/boot/`. La siguiente tarea útil es demostrar con pruebas host-side que nuestra herramienta puede producir y validar un layout USB completo, y decidir cómo se impondrá el modo fail-closed. Si eso requiere modificar el loader upstream, primero debe realizarse una revisión de código/licencia y pruebas aisladas; no parchear ni ejecutar sobre el dispositivo como experimento exploratorio.
