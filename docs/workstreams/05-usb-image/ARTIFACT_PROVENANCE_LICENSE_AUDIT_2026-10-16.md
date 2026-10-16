# Auditoría de procedencia, integridad y licencias de artefactos candidatos

**Fecha:** 2026-10-16  
**Rama de trabajo:** `chatgpt/05-usb-only-hardening`  
**Alcance:** revisión documental cruzada del inventario, catálogo de arranque, política de licencias, documentación de compilación y diseño USB-only. No se descargaron ni ejecutaron artefactos en esta revisión. No se modificó hardware ni se escribieron dispositivos físicos.

## Decisión ejecutiva

**NO-GO para una prueba física con el conjunto de artefactos actual. GO para continuar auditoría estática y pruebas sintéticas en host.**

El repositorio ya registra hashes locales para un kernel Baikal, un kernel Belize y un initramfs comunitarios. Esos hashes permiten reconocer exactamente los archivos examinados, pero no autentican al autor ni demuestran que el contenido sea seguro. El kernel Baikal candidato carece de fuente identificada, configuración de compilación y build reproducible; el initramfs contiene binarios y firmware que no tienen auditoría completa; y el rootfs no ha sido auditado por paquetes, servicios, usuarios o comportamiento de almacenamiento.

No se encontró evidencia suficiente para declarar una licencia clara y completa del conjunto de binarios candidato. La licencia GPL-3.0 de la distribución no debe interpretarse como licencia global de todos los kernels, initramfs, firmware, payloads y paquetes incluidos. La ausencia de licencia identificada se trata como **no autorizado para redistribución** hasta resolverla.

## Inventario de decisiones por artefacto

| ID del inventario | Artefacto | Integridad / procedencia | Licencia | Decisión |
|---|---|---|---|---|
| A-01 | Fuente de `ps4-linux-loader` en commit `f70f43a60a973b3662daeb29c1f115d95408db93` | Revisión de fuente fijada y leída; compilación local descrita en `docs/LOADER_BUILD_REPRO.md`. No se ha ejecutado el ELF. | No se identificó licencia en la raíz en la ruta revisada; el subdirectorio `ps4-kexec-common` tiene licencia BSD-2-Clause, que no licencia automáticamente todo el repositorio. | No redistribuir el conjunto de fuente/ELF como si tuviera una licencia global confirmada. Resolver licencias por archivo y dependencias. |
| B-02 | ELF del loader incluido por la distribución | Coherente con la fuente en tabla de offsets, rutas y símbolos, pero no reproducido bit a bit con el compilador observado en la distribución. | Depende de la licencia del código incorporado y de cada componente. | No tratar como reproducción autenticada del release. Preferir build propio documentado tras cerrar revisión legal/técnica. |
| B-03 | Kernel Baikal `bzImage-baikal-7.0.8` | SHA-256 registrado: `46c835f762e7b0b5400ea762b8daa1bcec638a1b769c7ec0905137bc565b1ba8`; tamaño registrado: 13,841,408 bytes. Hash coincide con los valores publicados por la misma distribución; no se identificó fuente ni build reproducible. | La distribución declara kernels GPL-2.0 en su NOTICE, pero no se localizó la fuente exacta ni el paquete de cumplimiento de fuente de esta variante. | Candidato documental únicamente. No redistribuir ni seleccionar como kernel aprobado. Requiere fuente exacta, configuración, versión de toolchain, avisos y correspondencia con el binario. |
| B-04 | Kernel Belize `bzImage-belize-7.1.7` | SHA-256 registrado: `072113898347932c34888cfdc7556953ee27233c0727cc45f419a57119242480`; sin fuente/build reproducible verificados. No es el candidato para Baikal. | Igual incertidumbre documental sobre fuente correspondiente. | Mantener fuera del candidato Baikal. No redistribuir. |
| B-05 | `initramfs.cpio.gz` de Psxitarch | SHA-256 registrado: `3f373bd6c469e490eaf4e5cf4d2e8ed77cf7bb91449b6a18da6a6529d479169b`; gzip/cpio y 48 entradas fueron inspeccionados según el inventario. Binarios y firmware incluidos no están auditados por completo. | La cabecera de `init` indica BSD-3 para better-initramfs, pero eso no determina las licencias de busybox, dropbear, cryptsetup, LVM, firmware y demás contenido. | No aprobar para arranque hasta inventariar componentes, licencias, hashes y scripts; no redistribuir el archivo completo. |
| B-06 | Imagen/rootfs Arch + KDE de Psxitarch | Imagen leída estáticamente; no montada para ejecución. El rootfs no ha sido auditado integralmente y carece de verificación reproducible de origen/paquetes. | Licencias mixtas de Arch y paquetes; no existe una conclusión de cumplimiento para la imagen completa. | No aprobar para arranque ni redistribuir. Auditar manifiesto de paquetes, servicios, usuarios, scripts de inicio y comportamiento de montaje. |
| B-01 | Releases binarios del loader | Los assets de release no se descargaron ni compararon con la compilación propia. | La licencia general del repositorio sigue sin aclararse. | No utilizar como sustituto de un build propio auditado. |

## Hallazgos relevantes para USB-only

1. El parche del loader limita la selección de kernel e initramfs a una sola carpeta USB y elimina las rutas literales internas del código compilado, según la evidencia existente en `docs/LOADER_BUILD_REPRO.md`. Esto reduce el riesgo de mezcla de fuentes en la etapa del loader; no demuestra que el kernel, initramfs o rootfs no lean o escriban el disco interno en runtime.
2. La documentación indica que el handoff puede incluir `eap_hdd_key.bin` en RAM. Por lo tanto, no debe afirmarse aislamiento del almacenamiento interno basándose solo en un `fstab` vacío o en la ausencia de rutas de montaje obvias.
3. El hash no es autenticación. Cuando el hash publicado y el hash local provienen del mismo distribuidor, la comparación detecta discrepancias respecto de esa publicación, pero no aporta una segunda fuente de confianza.
4. Los hashes registrados en el catálogo identifican artefactos históricos; no significan que el artefacto esté aprobado, sea compatible con CUH-2115B, ni que sea seguro.

## Puertas de aceptación pendientes

- [ ] **P-ART-01 — Kernel:** identificar fuente exacta del kernel Baikal, commit/tag, `.config`, toolchain, instrucciones de compilación y avisos de licencia. Si no se puede, conservar el estado BAJA confianza y bloquear su selección.
- [ ] **P-ART-02 — Initramfs:** extraer inventario de paquetes/binarios, versiones, licencias y hashes; revisar `init`, scripts de inicio, módulos, firmware, claves y puntos de montaje. Hacerlo en archivos de análisis, sin ejecutar el initramfs.
- [ ] **P-ART-03 — Rootfs:** obtener manifiesto reproducible de paquetes y versiones, licencias, usuarios/servicios habilitados y scripts que detecten/monten discos. No montar con ejecución ni arrancar servicios.
- [ ] **P-ART-04 — Loader:** resolver licencia por archivos y dependencias; documentar avisos y obligaciones para la variante compilada. No confundir la licencia BSD-2-Clause de un subcomponente con la licencia del repositorio entero.
- [ ] **P-ART-05 — Catálogo:** añadir al manifiesto el estado de confianza y el estado de licencia por artefacto, manteniendo separados `hash verificado`, `procedencia verificada`, `licencia aclarada` y `compatibilidad demostrada`.
- [ ] **P-ART-06 — USB-only runtime:** auditar estáticamente scripts y configuración de initramfs/rootfs para localizar escrituras, montajes automáticos, acceso al disco interno y uso de la clave HDD. La ausencia de hallazgos estáticos no sustituye la prueba de laboratorio.
- [ ] **P-ART-07 — Publicación:** no incorporar al repositorio kernels, initramfs, rootfs ni payloads de terceros hasta que la licencia y el derecho de redistribución estén documentados.

## Criterio de salida

El hito no se cierra por tener todos los hashes. Para cada artefacto obligatorio deben estar documentados: origen identificable, revisión exacta, integridad, versión, licencia/obligaciones, superficie de runtime examinada y limitaciones. Si una pieza crítica no puede verificarse, el resultado debe seguir siendo NO-GO y el bloqueo debe expresarse claramente.

## Fuentes internas

- `docs/ARTIFACT_INVENTORY.md`
- `manifests/arranque-catalogo.json`
- `docs/LICENSE_POLICY.md`
- `docs/LOADER_BUILD_REPRO.md`
- `docs/USB_ONLY_DESIGN.md`
- `docs/workstreams/05-usb-image/USB_ONLY_CHAIN_REVIEW_2026-10-16.md`

Esta auditoría es una evaluación técnica/documental del material del repositorio, no asesoramiento jurídico ni certificación de seguridad.
