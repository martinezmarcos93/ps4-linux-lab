# Workstream 05 — Imagen y cadena USB-only

**Responsable de implementación en esta iteración:** ChatGPT  
**Revisión independiente de arquitectura y seguridad:** ChatGPT  
**Prioridad:** 5 de 5 — mayor complejidad de las cinco categorías  
**Objetivo:** preparar y auditar una imagen candidata y demostrar mediante evidencia suficiente que el diseño propuesto no depende de escribir en el almacenamiento interno. No incluye aún el primer arranque físico.

## Dependencias previas

Depende de los workstreams 02 (tests), 03 (procedencia/licencias) y 04 (compatibilidad). Puede avanzar en revisión estática y dry-run, pero no seleccionar un artefacto final ni declarar compatibilidad si las dependencias están abiertas.

## Tareas hasta el 100 %

- [ ] I01 — Mapear el flujo completo desde el artefacto de entrada hasta el layout final de la imagen.
- [x] I02 — Enumerar las rutas de lectura del loader y referencias al almacenamiento interno. Evidencia: `USB_ONLY_CHAIN_REVIEW_2026-10-16.md`; análisis de runtime de initramfs/rootfs sigue pendiente.
- [x] I03 — Revisar fallback/mezcla de orígenes. El upstream mezcla por archivo; el parche USB-only evita rutas internas, pero se detectó un manejo incompleto de errores en archivos opcionales. Evidencia: `USB_ONLY_CHAIN_REVIEW_2026-10-16.md` y `PATCH_REVIEW_2026-10-16.md`.
- [x] I04 — Definir invariantes USB-only y pruebas negativas. Evidencia: `USB_ONLY_CHAIN_REVIEW_2026-10-16.md`.
- [ ] I05 — Revisar que los scripts de construcción operen solo sobre archivos/directorios de salida explícitos y no detecten ni escriban dispositivos automáticamente. Revisión estática inicial publicada en `IMAGE_TOOLING_REVIEW_2026-10-16.md`; corregido H-IMG-001 para impedir sobrescritura concurrente del destino, pendiente CI.
- [ ] I06 — Ejecutar preflight/dry-run con fixtures sintéticos; no usar dispositivos físicos. Se añadió `tools/strict_usb_preflight.py` y `tests/test_strict_usb_preflight.py`; pendiente ejecución real de la suite/CI.
- [ ] I07 — Verificar formato, estructura, tamaño, hashes y reproducibilidad de la imagen candidata en PC.
- [ ] I08 — Incorporar pruebas de seguridad para paths, symlinks, nombres de dispositivo ambiguos, sobrescritura de salidas y fallos parciales. Cobertura inicial de opcionales/symlinks en `tests/test_strict_usb_preflight.py` y publicación sin sobrescritura en `tests/test_build_usb_image.py`; faltan más casos de fallos de lectura y rutas.
- [ ] I09 — Confirmar que el manifiesto referencia fuentes confiables y artefactos permitidos por licencia. Auditoría documental inicial publicada en `ARTIFACT_PROVENANCE_LICENSE_AUDIT_2026-10-16.md`; resultado actual: NO-GO para artefactos críticos por fuente/licencia incompletas.
- [ ] I10 — Documentar recuperación, condiciones de aborto y criterios de aprobación previos a una prueba física.
- [ ] I11 — ChatGPT revisa de forma independiente el diseño, el diff, las rutas de escritura y los claims de seguridad. Revisión inicial publicada en `PATCH_REVIEW_2026-10-16.md`; nueva iteración de contención documentada en `R_USB_001_CONTAINMENT.md` y `USB_MINIMAL_CONFIG_TEST_PLAN.md`.
- [ ] I12 — Emitir informe final con propiedades demostradas, no demostradas, limitaciones y decisión go/no-go para una futura prueba física.
- [ ] I13 — Resolver R-USB-001: se adoptó como contención excluir `bootargs.txt`/`vram.txt` del candidato inicial y se añadió un preflight estricto; el defecto general de `read_file()` sigue abierto y requiere corrección/reconstrucción o exclusión formal de los opcionales en la configuración final. Evidencia: `R_USB_001_CONTAINMENT.md`.

## Criterios de aceptación

- El pipeline se ejecuta en modo host-side/dry-run sin acceso de escritura a dispositivos de bloque.
- Cada ruta de escritura está identificada y acotada a destinos de archivo explícitos.
- Los invariantes USB-only tienen evidencia de código y tests negativos; no se declara aislamiento absoluto basándose solo en intención de diseño.
- Artefactos y licencias cumplen las decisiones del workstream 03.
- La selección de kernel y loader respeta la matriz del workstream 04.
- El resultado puede ser “no-go” si hay rutas ambiguas o riesgos residuales.

## Restricciones

No editar `main` directamente. No escribir USB físico, no ejecutar payloads y no arrancar la consola. La autorización para prueba de hardware es un hito independiente y queda fuera de esta rama.

## Avance de esta iteración (2026-10-16)

- Añadido `tools/strict_usb_preflight.py`: comprueba la estructura y rechaza expresamente `bootargs.txt`/`vram.txt` presentes. Es un preflight host-side, no toca hardware.
- Añadido `tests/test_strict_usb_preflight.py`: cubre obligatorios ausentes, opcionales presentes/vacíos, directorio, symlink roto y directorio de entrada inválido.
- Añadidos `R_USB_001_CONTAINMENT.md` y `USB_MINIMAL_CONFIG_TEST_PLAN.md` para hacer explícita la política conservadora y sus límites.
- Estado de validación: los archivos están publicados en esta rama, pero todavía no se afirma que los tests pasen; se necesita ejecutar CI o la suite en un entorno host-side.
- No se modificó `main`, no se ejecutó payload ni se escribió un dispositivo físico.


- Revisión posterior: se corrigió la ubicación de un decorador de skip para que las pruebas de publicación sin sobrescritura no queden omitidas por las condiciones de las pruebas de construcción. Se endureció `_cadena()` para rechazar terminadores FAT inválidos y se validó la geometría BPB (tamaño de FAT suficiente, regiones dentro del volumen); las pruebas verifican rechazo y hash inalterado ante entradas corruptas. El run #45 pasó para el commit `dea17f6` (incluye el código y tests FAT); el run #46, sobre el commit documental `3e4f298`, sigue en curso al actualizar esta nota.

- [ ] H-FAT-001/H-FAT-002 — La corrección de cadena FAT y geometría BPB está implementada; CI #45 pasó con tests y documentación para `dea17f6`. Falta confirmar el run más reciente y revisar casos residuales.
- [ ] H-IMG-001 — Cerrar con CI la publicación atómica sin sobrescritura y confirmar tests host-side.


## Auditoría de procedencia/licencias — 2026-10-16

- [x] Se cruzaron `docs/ARTIFACT_INVENTORY.md`, `manifests/arranque-catalogo.json`, `docs/LICENSE_POLICY.md`, `docs/LOADER_BUILD_REPRO.md` y `docs/USB_ONLY_DESIGN.md`.
- [x] Se publicó `ARTIFACT_PROVENANCE_LICENSE_AUDIT_2026-10-16.md` con decisión conservadora por artefacto, nivel de confianza, limitaciones y puertas de aceptación.
- [ ] No se declara aprobado el kernel Baikal: hay hash y cabecera, pero no fuente exacta, `.config` ni build reproducible identificados.
- [ ] No se declara aprobado el initramfs: faltan inventario/licencias completas de binarios y firmware incluidos.
- [ ] No se declara aprobado el rootfs: faltan auditoría de paquetes, servicios, usuarios, scripts y acceso al almacenamiento interno.
- [ ] No se declara resuelta la licencia global del loader; la licencia BSD-2-Clause del subcomponente `ps4-kexec-common` no se extiende automáticamente al repositorio entero.
- **Decisión:** NO-GO para prueba física con el conjunto actual; GO para continuar análisis estático y pruebas sintéticas. No se descargaron ni ejecutaron binarios durante esta revisión.


- Revisión adicional del preflight (2026-10-16): detecté que la política de ausencia de `bootargs.txt`/`vram.txt` solo comprobaba nombres exactos. Para no depender de diferencias de mayúsculas entre el filesystem del host y FAT, `tools/strict_usb_preflight.py` ahora rechaza variantes de caso (`BOOTARGS.TXT`, `VRAM.TXT`) y symlinks rotos con esos nombres reservados. Se agregaron dos tests y se actualizó `USB_MINIMAL_CONFIG_TEST_PLAN.md`. Commits: `45c3302` (corrección) y `f988159` (tests). La consulta disponible de runs asociados al commit no devolvió ejecuciones; la suite sigue pendiente de validación CI, no se declara verde.
