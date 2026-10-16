# Auditoría de recursos externos y replanteo del proyecto PS4 Linux
Fecha de consulta: 2026-10-16
Repositorio: `martinezmarcos93/ps4-linux-lab`
Objetivo: documentar las fuentes propuestas para arrancar Linux en PS4 Slim CUH-2115B, firmware 13.52, southbridge reportado Baikal B1 (`0x30201`), priorizando arranque USB y sin escrituras al disco interno.

## Resumen ejecutivo

1. **Cambio importante de selección de kernel:** la guía actual de DionKill distingue los kernels por southbridge. El kernel de feeRnt `6.15.4-crashnt-4.8.3` se publica explícitamente para Aeolia/Belize; no es candidato para nuestra Baikal B1. La guía lista un kernel Baikal `7.0.8` como espejo FullLTO, y un kernel `7.1.7` recomendado para Aeolia/Belize y también para Baikal en su perfil Server. El candidato `bzImage-baikal-7.0.8` ya registrado en el laboratorio debe seguir como candidato, no como artefacto validado.
2. **Loader:** upstream `ps4-linux-loader` v25 declara soporte para FW 13.52; v25.1 corrige un offset de detección de GPU para 13.02. El README mantiene rutas internas `/data/linux/boot/` y `/user/system/boot/`, y dice que USB tiene prioridad, no exclusividad. El código de v25.1 busca kernel, initramfs y archivos de configuración en USB y luego en ambas rutas internas. No cumple el requisito USB-only sin parche.
3. **Instalación y rootfs:** la guía de DionKill distingue almacenamiento interno y externo; indica que Baikal no tiene instalación interna fiable y recomienda unidad externa. Esto no equivale a probar que un initramfs/rootfs concreto no accede al HDD interno durante la ejecución.
4. **Initramfs:** la guía enlaza un initramfs-ps4 más reciente y advierte que el initramfs antiguo no debe usarse. También indica una salvedad de scripts para kernels 7.x. Debemos identificar y auditar el artefacto exacto, no elegirlo por nombre.
5. **MediaFire:** las URLs proporcionadas para los archivos del video y el initramfs están truncadas (`.../file/aibvor...`, `.../file/wziaiu...`). No se pudo identificar de forma inequívoca el archivo, autor, versión, hash ni contenido. No descargarlos ni usarlos hasta obtener las URL completas y verificar su procedencia.
6. **Herramientas:** Rufus sirve para crear medios USB arrancables, pero no demuestra que una imagen genérica sea apropiada para el método PS4. 7-Zip es útil para inspeccionar archivos comprimidos. FileZilla sirve para transferencias FTP; la guía advierte usar modo binario al transferir por FTP con GoldHEN.
7. **Decisión actual: NO-GO para ejecución física.** Sí se autoriza continuar análisis estático, inventario, pruebas sintéticas de host y preparación de un candidato aislado. No ejecutar payload, no escribir USB físico ni almacenamiento interno, y no ejecutar instaladores que particionen/formateen dispositivos.

## Inventario de fuentes y hallazgos

### A. Kernel PS4 de feeRnt
Fuentes:
- Repositorio: https://github.com/feeRnt/ps4-linux-12xx
- Releases: https://github.com/feeRnt/ps4-linux-12xx/releases
- Release más reciente observado al 2026-10-16: https://github.com/feeRnt/ps4-linux-12xx/releases/tag/v6.15.4__crashnt-4.8.3
- Asset publicado: `bzImage`, SHA-256 informado por GitHub: `e4639c29fea7ec46fac0cb09c328fbf672a843879ddd0980d56c931bd4e09d2c`, tamaño 18,088,960 bytes.
- Rama por defecto: `6.15.4-aeolia-belize-crashniels`. El repositorio se describe como fork de `codedwrench/ps4-linux` con parches adicionales para periféricos en CUH-12xx y otros modelos.

Hallazgos:
- La release v6.15.4-crashnt-4.8.3 está rotulada explícitamente **AEOLIA/BELIZE**. Aunque el nombre del repositorio mencione CUH-12xx y la release incluya mejoras de USB-Bluetooth, USB audio/MIDI, webcam/media y firmware inalámbrico, eso no la convierte en compatible con Baikal.
- La release anterior v6.15.4-crashnt-4.7 también se etiqueta Aeolia/Belize y ofrece builds FullLTO/ThinLTO; no seleccionar una de esas variantes para Baikal por inferencia.
- GitHub muestra licencia `NOASSERTION`/“Other”; revisar el LICENSE y la procedencia de los parches antes de redistribuir artefactos. La existencia del código fuente no demuestra que el binario publicado sea reproducible.
- El archivo publicado es un kernel, no una distribución completa ni un initramfs. Necesita una combinación compatible de payload, initramfs y rootfs.

Decisión:
- **Descartar la release actual de feeRnt como candidato de arranque para Baikal B1**, salvo evidencia posterior explícita del autor que amplíe su compatibilidad.
- Conservarla como referencia para historial de parches y mejoras periféricas, no como kernel de prueba.

### B. Guía de DionKill
Fuentes:
- Guía: https://dionkill.github.io/ps4-linux-tutorial/
- Sección de archivos: https://dionkill.github.io/ps4-linux-tutorial/files.html
- Preparación: https://github.com/DionKill/ps4-linux-tutorial/blob/main/docs/setup.md
- Instalación: https://github.com/DionKill/ps4-linux-tutorial/blob/main/docs/installation.md
- Información de compatibilidad: https://github.com/DionKill/ps4-linux-tutorial/blob/main/docs/information.md
- Post-instalación: https://dionkill.github.io/ps4-linux-tutorial/postinstall.html
- Código de la guía (MIT): https://github.com/DionKill/ps4-linux-tutorial

Hallazgos de la sección de kernels, consultada el 2026-10-16:
- La guía indica que la comunidad pasó de 6.15 a kernels 7.x en Aeolia/Belize, y que Baikal fue portado a 7.0.8 después de años en 5.4.
- Kernel 7.1.7: recomendado para Aeolia/Belize en uso general; también aparece un perfil Server compatible con Aeolia, Belize y Baikal. Perfiles indicados: General, Server, SlopMax (general + KVM) y Slopium (server + KVM).
- Kernel 7.1.3: Aeolia/Belize.
- Kernel 7.0.8: Baikal; la página lo describe como espejo del build FullLTO para Baikal.
- Kernel 6.15.4: Aeolia/Belize.
- Kernel 5.4.247: Baikal específico; la guía indica no usarlo en otras consolas.
- Para uso como servidor, la guía recomienda un kernel Server y payload con VRAM de 128 MB, pero nuestro objetivo debe definirse antes de elegir perfil. Para escritorio/uso gráfico, no trasladar automáticamente esa recomendación.
- La guía recomienda distros basadas en Arch por la disponibilidad de actualizaciones de drivers, pero aclara que cada distro necesita versiones específicas de drivers. Esto aumenta el costo de mantenimiento y obliga a fijar versiones.
- La página de archivos lista CachyOS Light y otras distros; afirma compatibilidad de las distros listadas con revisiones/southbridges, pero la combinación kernel/initramfs/loader sigue siendo un requisito separado.
- La sección de preparación señala que se debe anotar firmware, southbridge y versión de GoldHEN/ps4hen. También advierte no usar GoldHEN v2.4b18.8 por un problema de arranque y recomienda usar la versión actual. Verificar la versión instalada antes de cualquier prueba, sin ejecutar todavía el payload.
- La guía advierte que para FileZilla se use modo binario al transferir archivos porque el FTP de GoldHEN puede fallar en transferencias.
- La guía de instalación indica que Baikal no tiene una instalación interna fiable y recomienda almacenamiento externo; además describe métodos de instalación que particionan o preparan unidades. Esos pasos no se deben ejecutar en esta fase.
- La guía es una referencia comunitaria viva, no una prueba de que la configuración concreta de este laboratorio ya arrancó. Debemos registrar fecha/commit/artefacto de cada selección.

Decisión:
- Usar la guía como índice de compatibilidad y fuente de selección, no copiar una receta completa sin separar los pasos que escriben o particionan dispositivos.
- Investigar 7.0.8 Baikal como candidato principal y 7.1.7 Server como candidato alternativo, descargando e inspeccionando hashes/configuración sin ejecutar. Comparar contra el hash del kernel Baikal ya registrado y explicar cualquier diferencia antes de reemplazarlo.

### C. PS4 Linux Loader / Payloads
Fuentes:
- Releases: https://github.com/ps4-linux/ps4-linux-loader/releases
- v25: https://github.com/ps4-linux/ps4-linux-loader/releases/tag/v25
- v25.1: https://github.com/ps4-linux/ps4-linux-loader/releases/tag/v25.1
- Comparación v24 → v25: https://github.com/ps4-linux/ps4-linux-loader/compare/v24...v25
- Comparación v25 → v25.1: https://github.com/ps4-linux/ps4-linux-loader/compare/v25...v25.1
- README v25.1: https://github.com/ps4-linux/ps4-linux-loader/blob/v25.1/README.md

Hallazgos:
- v25 declara soporte para FW 13.52 e incorpora entradas de offsets y blob kexec para 13.50/13.52, además de cambios de firmware/EDID.
- v25.1 solo cambia README y un offset `kern_off_gpu_devid_is_9924` para FW 13.52 (de `0x4AC5A0` a `0x4AC5B0`) según la comparación entre etiquetas.
- El ZIP v25.1 publica SHA-256 `7ee03018982cc25a6a6fcb44221b004406168cb33261dd62d82560144316da74`.
- El README afirma que el almacenamiento interno predeterminado es `/data/linux/boot`, con respaldo `/user/system/boot/`; también dice que USB tiene prioridad. La prioridad de USB no es exclusividad.
- En `linux/main-aio.c` de v25.1, la macro de lectura intenta `/mnt/usb0/`, `/mnt/usb1/`, `/data/linux/boot/` y `/user/system/boot/` de manera independiente para `bzImage`, `initramfs.cpio.gz`, `bootargs.txt` y `vram.txt`. Esto permite que distintos archivos procedan de ubicaciones diferentes y no satisface el requisito USB-only.
- La función `read_file()` no comprueba correctamente todos los errores de `lseek()` y `mmap()`, ni libera todos los recursos ante cada fallo de lectura. Sigue siendo necesario endurecerla y probarla.
- El código de `ps4-kexec-common/firmware.c` empaqueta `key/eap_hdd_key.bin` en el initramfs generado en el handoff. Esto demuestra que el material de clave se incorpora al initramfs de transferencia; no demuestra por sí solo que Linux monte o escriba el HDD interno.
- El README describe copia automática de kernel e initramfs al almacenamiento interno desde una partición FAT32 externa. El comportamiento efectivo debe confirmarse en el código exacto; mientras tanto, esa receta no se considera compatible con la política del laboratorio.
- El release es útil como nueva base de compatibilidad para FW 13.52, pero no es directamente aceptable como payload USB-only sin modificar y compilar.

Decisión:
- Fijar v25.1 como referencia de análisis de loader para firmware 13.52.
- Crear un parche de aislamiento basado en esa etiqueta, no sobre el commit antiguo `f70f43a...` sin reconciliar diferencias.
- El parche debe forzar una única carpeta de arranque USB, rechazar fallback interno, validar archivos de forma segura y tener pruebas de fallo. Aplicar `git apply --check`, compilar reproduciblemente y revisar el binario antes de considerar un ensayo.

### D. Payload Guest / HB Store
Fuente: https://pkg-zone.com/details/AZIF00003

Hallazgos:
- El listado identifica Payload Guest, autor AlAzif, Title ID `AZIF00003`, versión PS4 0.98, firmware de reproducción 5.05+ y actualización publicada el 2025-01-07.
- La descripción lo presenta como una aplicación para lanzar payloads desde USB; la instalación del HB Store requiere HEN y carga de la tienda desde la PS4.
- Es una vía de entrega/ejecución, no un payload Linux validado por sí mismo. Antes de usarlo hay que identificar qué payload concreto se cargaría y verificar su hash/procedencia.
- No instalar ni ejecutar durante la fase de auditoría.

### E. Distros en PS4Linux.com
Fuente: https://ps4linux.com/downloads/

Limitación:
- El sitio devolvió error al abrirse directamente en esta consulta. La guía de DionKill sí se pudo consultar y mantiene una sección de archivos/distro.
- No declarar verificados los archivos de PS4Linux.com ni asumir que sus instrucciones coinciden con el requisito USB-only.
- Pendiente: inventariar cada distro propuesta, fecha, URL final, hash, arquitectura, initramfs requerido, southbridge, método de instalación y licencia.

### F. Enlaces MediaFire del video
Fuentes proporcionadas por el usuario:
- “Used in video”: URL incompleta `https://www.mediafire.com/file/aibvor...`
- “Initramfs”: URL incompleta `https://www.mediafire.com/file/wziaiu...`

Hallazgos:
- Las URLs están truncadas en el mensaje original. La búsqueda pública no permitió identificar inequívocamente los archivos usando solo esos fragmentos.
- Sin URL completa, nombre, uploader, tamaño, fecha y hash, no hay trazabilidad suficiente para descargar o usar esos artefactos.
- Un archivo MediaFire no es confiable por el mero hecho de aparecer en un video. Hay que obtenerlo desde una fuente con versión identificable y, si existe, contrastarlo con el repo/código del autor.

Decisión:
- Estado: **pendiente por falta de URL completa**. No inventar URLs ni seleccionar artefactos similares por coincidencia parcial.

### G. Rufus
Fuente oficial: https://rufus.ie/en/

Hallazgos:
- Rufus es una herramienta de Windows para crear medios USB arrancables y formatear memorias.
- No es un instalador de Linux para PS4 ni garantiza que una ISO genérica funcione con el método de payload/kexec de PS4.
- La documentación de este laboratorio ya contempla herramientas propias para crear/editar imágenes de forma controlada. Antes de escribir un USB físico, debe decidirse si Rufus tiene un papel real; no utilizarlo por defecto ni escribir medios durante esta fase.
- Para descargas, usar únicamente el sitio oficial y verificar firma/hash cuando estén disponibles.

### H. FileZilla
Fuente oficial: https://filezilla-project.org/download.php?type=client

Hallazgos:
- Cliente FTP útil para transferencias desde el host a un PS4 con servidor FTP habilitado.
- La guía de DionKill advierte usar modo binario con el FTP de GoldHEN debido a posibles errores de transferencia.
- Es irrelevante para el flujo actual si todos los artefactos se preparan en el host y se usa un medio externo; además, la transferencia al almacenamiento interno contradice el principio de no escribirlo.
- No realizar transferencias al PS4 durante la fase de auditoría.

### I. 7-Zip
Fuente oficial: https://www.7-zip.org/download.html

Hallazgos:
- Herramienta de compresión/descompresión con soporte para ZIP, gzip, XZ, TAR y CPIO, formatos relevantes para inspección de artefactos.
- Puede servir para inspeccionar contenedores, pero la extracción no valida contenido, integridad ni seguridad. Verificar hashes antes y después de extraer y no ejecutar archivos incluidos.
- Preferir la versión oficial actual para el sistema operativo utilizado.

### J. Recursos comunitarios
Fuentes:
- https://ps4linux.com/forums/
- https://dionkill.github.io/ps4-linux-tutorial/

Hallazgos:
- El foro PS4Linux.com no se pudo abrir directamente durante esta consulta; queda como recurso comunitario pendiente de revisión.
- La guía de DionKill es una documentación estructurada, con repositorio fuente público bajo MIT, secciones de kernels, initramfs, distros, instalación y post-instalación.
- Las guías y foros sirven para generar hipótesis y encontrar artefactos; no reemplazan la verificación por commit, hash y pruebas del laboratorio.

## Matriz de decisión para nuestra consola

| Componente | Candidato/estado | Decisión actual |
|---|---|---|
| Firmware / southbridge | FW 13.52; Baikal B1 `0x30201` reportado por operador | Registrar como observación; volver a verificar solo por método ya autorizado, sin repetir payload innecesariamente |
| Loader | `ps4-linux-loader v25.1` | Base de auditoría; NO ejecutar sin parche USB-only validado |
| Kernel feeRnt 6.15.4 crashnt-4.8.3 | Aeolia/Belize | Descartar para Baikal B1 |
| Kernel Baikal 7.0.8 | Listado por DionKill como Baikal; hash previo del laboratorio `46c835f762e7b0b5400ea762b8daa1bcec638a1b769c7ec0905137bc565b1ba8` | Candidato, no validado; cotejar fuente, release y configuración |
| Kernel 7.1.7 Server | La guía lo lista compatible con Baikal en perfil Server | Alternativa de investigación; definir si el objetivo es servidor/headless antes de preferirlo |
| Initramfs | Nuevo `initramfs-ps4` enlazado por DionKill | Identificar artefacto exacto, hash, script de init y accesos a almacenamiento antes de selección |
| Rootfs/distro | No seleccionado de forma cerrada | Elegir tras kernel/initramfs; auditar scripts, servicios, paquetes, montajes y licencia |
| USB-only | Loader upstream tiene fallback interno | Bloqueante: parche + pruebas + auditoría runtime |
| Payload Guest | PS4 0.98, FW 5.05+ listado | Solo transporte/launcher potencial; no validado ni instalado |
| Rufus/FileZilla/7-Zip | Utilidades genéricas | No son gates de compatibilidad; usar solo donde aporten valor |

## Curso de acción replanteado

### Fase 1 — Congelar y consolidar evidencia
1. Mantener como política que no se ejecuta payload, no se escribe USB físico y no se escribe el almacenamiento interno.
2. Añadir URLs completas, commit/tag, fecha de consulta, hash, tamaño, licencia y southbridge soportado a cada artefacto.
3. Resolver las dos URLs MediaFire truncadas con el usuario o el autor del video; no adivinar.

### Fase 2 — Selección de kernel Baikal
1. Obtener de la fuente oficial los metadatos y hashes del kernel Baikal 7.0.8 que lista DionKill.
2. Comparar con el hash ya anotado en el laboratorio; si difiere, mantener ambos candidatos con procedencia separada.
3. Investigar el kernel 7.1.7 Server solo como alternativa y evaluar el tradeoff servidor/headless vs escritorio/gráficos. No sustituir sin evidencia.
4. Inspeccionar configuración y metadatos del kernel; la compatibilidad declarada no equivale a arranque demostrado.

### Fase 3 — Loader USB-only basado en v25.1
1. Fijar commit exacto v25.1 y registrar su hash/árbol.
2. Auditar rutas de lectura, escritura, llamadas de handoff, uso de `eap_hdd_key.bin`, y cualquier copia al disco interno.
3. Preparar un parche que use exclusivamente un directorio USB explícito y falle cerrado si no están kernel e initramfs requeridos.
4. Corregir la gestión de errores en `read_file()`; añadir pruebas para seek/map/read/close fallidos, archivos vacíos, directorios, symlinks y archivos parciales.
5. Aplicar el parche a un checkout limpio de v25.1, correr `git apply --check`, compilar y conservar logs/hashes. No basta con tests estáticos que inspeccionan el texto del parche.

### Fase 4 — Auditoría initramfs y rootfs
1. Obtener el initramfs-ps4 exacto recomendado por DionKill y registrar URL, commit/tag y SHA-256.
2. Listar el CPIO sin ejecutar nada; inspeccionar `init`, scripts/hook, `fstab`, servicios, módulos, montajes, particiones, `cryptsetup`, LVM, `eap_hdd_key.bin` y llamadas a block devices.
3. Inspeccionar la distro elegida en modo estático; buscar scripts de instalación, montaje del HDD interno y cualquier escritura/format.
4. Rechazar instaladores que automaticen particionado o formato para la primera prueba USB-only.

### Fase 5 — Ensayos de host y puerta de autorización
1. Ejecutar pruebas unitarias/sintéticas, reproducir la compilación y revisar CI del HEAD exacto.
2. Verificar que el candidato USB no contiene configuración opcional que fuerce rutas internas y que el preflight rechaza entradas no autorizadas.
3. Completar matriz de compatibilidad y revisión de licencias/procedencia.
4. Solo después preparar un protocolo separado de prueba física con criterios de parada, rollback y autorización explícita. Hasta entonces, NO-GO.

## Preguntas bloqueantes para cerrar el inventario

- URLs completas de los dos archivos MediaFire.
- ¿El objetivo inmediato del primer arranque es escritorio con HDMI y gráficos, o servidor/headless? Esta decisión cambia la selección entre kernel general y perfil Server.
- Versión exacta de GoldHEN/ps4hen disponible en la consola, para documentar compatibilidad sin ejecutar un payload adicional.

## Referencias consultadas

- feeRnt kernel source/release: https://github.com/feeRnt/ps4-linux-12xx ; https://github.com/feeRnt/ps4-linux-12xx/releases
- PS4 Linux Loader: https://github.com/ps4-linux/ps4-linux-loader/releases ; https://github.com/ps4-linux/ps4-linux-loader/compare/v24...v25 ; https://github.com/ps4-linux/ps4-linux-loader/compare/v25...v25.1
- DionKill guide: https://dionkill.github.io/ps4-linux-tutorial/ ; https://dionkill.github.io/ps4-linux-tutorial/files.html
- PS4Linux downloads/forum: https://ps4linux.com/downloads/ ; https://ps4linux.com/forums/
- Payload Guest/HB Store: https://pkg-zone.com/details/AZIF00003
- Rufus: https://rufus.ie/en/
- FileZilla: https://filezilla-project.org/download.php?type=client
- 7-Zip: https://www.7-zip.org/download.html

Este documento distingue los datos observados de las declaraciones de terceros y de los aspectos aún no verificados. Ninguna fuente consultada demuestra que la combinación concreta loader + kernel + initramfs + rootfs arranque correctamente en esta consola.
