# Revisión independiente del parche USB-only

**Fecha:** 2026-10-16  
**Artefacto revisado:** `patches/loader-usb-only-f70f43a.patch`  
**Fuente objetivo:** `ps4-linux/ps4-linux-loader@f70f43a60a973b3662daeb29c1f115d95408db93`  
**Método:** inspección estática del parche y del `read_file()` original. No se compiló en esta revisión ni se ejecutó el ELF. La compilación aislada ya está registrada en `docs/LOADER_BUILD_REPRO.md`; debe tomarse como evidencia previa del proyecto y volver a comprobarse en checkout antes de un gate final.

## Veredicto

**La idea principal del parche es correcta para P1/P2 (origen USB y carpeta única), pero el parche todavía no basta para aprobar la ejecución.** La revisión detecta una ruta de error en la carga de configuración opcional que debe resolverse o excluirse mediante una condición explícita y comprobable antes de considerar el loader candidato.

## Propiedades que sí aborda

- Elimina las dos rutas internas de boot (`/data/linux/boot/` y `/user/system/boot/`) del flujo de selección.
- Selecciona una carpeta USB que contenga ambos archivos obligatorios, `bzImage` e `initramfs.cpio.gz`.
- Carga los archivos obligatorios desde esa carpeta seleccionada y aborta si falla su lectura.
- Los opcionales `bootargs.txt` y `vram.txt` se buscan únicamente en la misma carpeta; no se intenta fallback a otra unidad o al almacenamiento interno.
- El código agregado usa `open(..., O_RDONLY)` en la comprobación de legibilidad y no agrega llamadas de escritura a archivos.

Estas observaciones no prueban la integridad de los archivos, que pertenezcan a la misma release ni que Linux en ejecución no monte/escriba el almacenamiento interno.

## Hallazgo R-USB-001 — errores de lectura de opcionales no tratados

**Severidad:** media; puede elevarse si se decide permitir archivos opcionales de configuración no validados.  
**Ubicación:** bloque añadido en `main-aio.c` por el parche, llamadas `load_from(boot_dir, "bootargs.txt", ...)` y `load_from(boot_dir, "vram.txt", ...)`; helper original `read_file()`.

El parche ignora el valor de retorno de las dos cargas opcionales. El `read_file()` original puede fallar después de abrir el archivo (por ejemplo, error de `lseek`, `mmap` o lectura parcial) y no valida todos esos resultados antes de devolver. Si falla tras haber modificado `ptr`/`sz`, el llamador puede recibir un puntero/tamaño que no representa un archivo completamente leído. En el caso de `bootargs.txt`, el código posterior puede recorrer y usar ese buffer como línea de comandos; para `vram.txt`, `my_atoi()` puede leer datos parciales.

La ruta habitual de “archivo opcional ausente” probablemente funciona porque `open()` falla antes de asignar el puntero; eso no cubre el caso distinto de “existe pero no se pudo leer por completo”.

### Corrección requerida antes de ejecutar

Elegir una de estas políticas y probarla:
1. **Más simple y conservadora:** no distribuir `bootargs.txt` ni `vram.txt` en la imagen candidata; comprobar en el manifiesto y en preflight que no están presentes, y usar únicamente los valores por defecto. Esto reduce el alcance, pero no corrige por sí solo el defecto general del helper.
2. **Fail-closed en el loader:** si un archivo opcional existe y su lectura falla, abortar antes de `kexec`; si no existe, usar defaults. Hacer que `read_file()` valide `lseek`, tamaño no cero, `mmap != MAP_FAILED`, lectura completa y cierre en todas las rutas de error; no publicar el puntero/tamaño al llamador hasta terminar correctamente.
3. Añadir pruebas host-side para archivo opcional ausente, vacío, directorio en vez de archivo, lectura truncada/error simulado y archivo válido sin salto de línea; verificar que no se use un buffer parcial.

No modificar el upstream ni ejecutar el binario durante esta revisión. Cualquier cambio al parche debe ir en una rama de trabajo, con diff revisable, compilación aislada y pruebas reproducibles.

## Hallazgo R-USB-002 — la selección de carpeta no valida contenido ni versión

**Severidad:** alta como requisito de preflight, no necesariamente un defecto del parche.

`file_readable()` solo comprueba que `open(O_RDONLY)` tenga éxito. No valida tamaño, tipo, hash, cabecera del kernel ni correspondencia entre kernel e initramfs. Eso debe quedar fuera del loader y en la herramienta de preflight/manifiesto, que tiene que ejecutarse sobre la carpeta exacta que luego se copia a la USB.

**Control exigido:** preflight exitoso para `bzImage` e `initramfs.cpio.gz`, hashes registrados, manifiesto que fije release/fuente, y revisión de la imagen tras agregar el kernel. La comprobación no debe escribir en dispositivos físicos.

## Hallazgo R-USB-003 — propiedad no cubierta: no escribir en disco interno en runtime

**Severidad:** bloqueo de diseño para el objetivo de preservación del almacenamiento interno.

El parche limita las rutas de lectura de los archivos de arranque, pero no demuestra que el kernel Linux, initramfs, servicios o rootfs no accedan al almacenamiento interno una vez iniciado el sistema. La evidencia estática actual sobre el initramfs y rootfs es parcial. Mantener P4/P5 de `USB_ONLY_DESIGN.md` pendientes; no convertir “el loader no escribe archivos” en “el sistema Linux no modificará el disco”.

## Acciones siguientes

- [ ] Claude reproduce la compilación y verifica los hashes del ELF original y parcheado contra `docs/LOADER_BUILD_REPRO.md` y `manifests/loader-f70f43a-build.json`.
- [ ] Claude incorpora tests para los casos R-USB-001 en el modelo host-side o justifica cómo se excluyen los opcionales y valida el contrato del loader.
- [ ] Verificar el preflight y la imagen candidata como archivos temporales, sin montar ni escribir dispositivos físicos.
- [ ] ChatGPT revisa el diff corregido y las evidencias de tests.
- [ ] Mantener NO-GO físico hasta completar procedencia/licencias, revisar runtime de rootfs y obtener autorización específica de Marcos para ese hito.
