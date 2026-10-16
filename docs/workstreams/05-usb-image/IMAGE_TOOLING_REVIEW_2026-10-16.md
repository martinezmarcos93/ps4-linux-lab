# Revisión host-side de herramientas de imagen — iteración 1

**Fecha:** 2026-10-16  
**Alcance:** lectura estática de `tools/build_usb_image.py`, `tools/fat32_add_file.py`, `tools/plan_usb_image_build.py` y pruebas existentes. No se creó una imagen candidata ni se accedió a dispositivos físicos.

## Resultado

Las herramientas están diseñadas para trabajar sobre archivos de imagen, sin montar ni escribir directamente a dispositivos de bloque. La revisión confirma controles importantes, pero encontró una condición de carrera en la publicación de la imagen construida.

### H-IMG-001 — posible sobrescritura concurrente del destino

**Severidad:** media.  
**Archivo:** `tools/build_usb_image.py`, función `construir()`.

`planificar()` rechaza un destino que ya exista y `construir()` crea un temporal exclusivo. Sin embargo, la publicación final usaba `os.replace(parcial, destino)`. Si otro proceso crea el destino después de la validación inicial y antes de la publicación, `os.replace` puede reemplazar ese archivo, contradiciendo el contrato “no sobrescribir”.

**Corrección aplicada en esta rama:** se reemplazó la publicación final por `_publicar_sin_sobrescribir()`, que crea un enlace duro desde el temporal al destino. La creación falla atómicamente si el nombre de destino ya existe; solo tras publicar se elimina el nombre temporal. El temporal y destino están en el mismo directorio, por lo que pertenecen al mismo filesystem. Se agregaron tests para publicación normal y destino que ya existe.

**Estado:** corrección implementada; pendiente resultado de CI del commit actualizado. La revisión no afirma todavía que el build completo se haya ejecutado en esta sesión.

### Controles existentes observados

- La salida debe ser un archivo `.img`, su directorio padre debe existir y no se permiten rutas bajo varios directorios críticos del sistema.
- Se rechazan destinos que ya existen durante la planificación.
- Kernel e initramfs deben ser archivos regulares, no vacíos y no enlaces simbólicos.
- Se rechaza ejecutar el constructor como root.
- La imagen se arma en un archivo temporal con creación exclusiva y se elimina ante errores intermedios.
- La herramienta de inspección abre imágenes con modo de solo lectura y rechaza entradas que no sean archivos regulares.
- El editor FAT opera sobre un archivo de imagen y acota lecturas/escrituras al tamaño de la partición declarada.

### Riesgos residuales

1. Los controles de ruta y los cálculos de espacio son verificaciones de preflight; no sustituyen la validación de la imagen resultante.
2. `tools/fat32_add_file.py` modifica la imagen de trabajo in situ. Debe usarse únicamente sobre una copia descartable, no sobre el único original de una imagen.
3. La presencia de enlaces simbólicos dentro del rootfs puede ser legítima; el comportamiento efectivo de `mkfs.ext4 -d` debe verificarse con fixtures antes de usar un rootfs real.
4. No se ha demostrado que la imagen candidata concreta contenga los artefactos finales aprobados por procedencia/licencia.
5. Nada de esta auditoría demuestra que el kernel/initramfs/rootfs no accedan al almacenamiento interno de la PS4 durante runtime.

## Próximas verificaciones

- [ ] CI verde para la corrección H-IMG-001.
- [ ] Añadir o confirmar pruebas negativas de salida parcial, symlink de destino, temporal preexistente y limpieza tras fallos.
- [ ] Construir una imagen mínima solo con fixtures ficticios en un directorio temporal, si las herramientas requeridas están disponibles en CI.
- [ ] Inspeccionar la imagen generada sin montarla y verificar hashes del kernel/initramfs extraídos.
- [ ] Mantener NO-GO para prueba física hasta completar procedencia/licencias, revisión de rootfs y autorización expresa separada.
