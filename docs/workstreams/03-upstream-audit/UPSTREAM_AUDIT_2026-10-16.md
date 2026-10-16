# Auditoría upstream — corte 2026-10-16

**Rama:** `workstream/03-upstream-audit`  
**Responsable:** ChatGPT; verificación local pendiente de Claude Code.  
**Método de esta iteración:** consulta de metadatos públicos de GitHub y lectura de README, LICENSE/NOTICE y rutas de licencia relevantes. No se descargaron ni ejecutaron binarios, no se compiló código y no se realizó prueba de consola. Esta nota complementa —no sustituye— la auditoría local fechada 2026-10-15.

## Resumen ejecutivo

1. **La distribución PS4-Linux v1.0 es una guía/empaquetado de un tercero, no una garantía de compatibilidad para la consola objetivo.** Su README declara dos modelos probados con firmware 13.52 (CUH-2116A/Baikal y CUH-7116B/Belize), pero deja otras filas sin probar. El equipo del laboratorio es CUH-2115B y su southbridge sigue desconocido.
2. **Existe una incompatibilidad de diseño con el requisito USB-only estricto:** la guía de PS4-Linux indica subir el kernel y el initramfs a rutas del almacenamiento interno de la consola (`/data/linux/boot/`). Su imagen raíz se prepara para USB, pero eso no demuestra que la cadena completa pueda arrancar sin escribir ni depender de archivos del disco interno.
3. **El loader declara soporte de firmware 5.05–13.52, pero etiqueta 13.02, 13.04, 13.50 y 13.52 con interrogantes en su README.** Es una afirmación del upstream, no una prueba para CUH-2115B.
4. **Licencias:**
   - `X-F1REBALL-X/PS4-Linux`: raíz con GPL-3.0 y NOTICE que atribuye guía/scripts a GPL-3.0, kernels a GPL-2.0 y afirma que payloads, initramfs e imagen Arch conservan licencias originales. El NOTICE no aporta un inventario completo por archivo; hace falta resolver cada artefacto antes de redistribuirlo.
   - `ps4-linux/ps4-linux-loader`: metadatos del repositorio indican `license: null` y no se encontró LICENSE en la raíz consultada. `linux/ps4-kexec-common/LICENSE` sí contiene BSD de dos cláusulas para ese subcomponente. Esto **no** demuestra que todo el loader esté en dominio público ni que carezca de derechos; mantener bloqueada la redistribución de código/binarios del loader hasta identificar las licencias de cada componente.
5. **No se aprueba ningún artefacto para redistribución en esta iteración.** Lectura de repositorio y coincidencia de hashes publicados no son prueba de seguridad, autoría criptográfica ni reproducibilidad.

## Fuentes fijadas en este corte

| ID | Fuente | Ref. consultada | Observación comprobada | Enlace |
|---|---|---|---|---|
| U-01 | Distribución PS4-Linux | `main` @ `66e21cb8c15f20189254e2608c6e9bf957eb8078`, commit fechado 2026-10-04 | README, LICENSE, NOTICE y scripts de imagen visibles en el árbol; la raíz declara `license: other / NOASSERTION` en la API de GitHub, pese al archivo LICENSE GPL-3.0 | https://github.com/X-F1REBALL-X/PS4-Linux |
| U-02 | Release de PS4-Linux | `v1.0`, publicado 2026-09-28 | GitHub expone assets binarios; esta auditoría no los descargó ni inspeccionó. No asumir que todos están cubiertos por la licencia del repositorio | https://github.com/X-F1REBALL-X/PS4-Linux/releases/tag/v1.0 |
| U-03 | Loader | `master` @ `f70f43a60a973b3662daeb29c1f115d95408db93`, commit fechado 2026-09-23 | README enumera familias de southbridge y firmwares; repo sin licencia raíz declarada en metadatos | https://github.com/ps4-linux/ps4-linux-loader |
| U-04 | Release del loader | `v25.1`, publicado 2026-09-25 | Metadatos de release consultados; los assets no se descargaron ni compararon | https://github.com/ps4-linux/ps4-linux-loader/releases/tag/v25.1 |
| U-05 | Loader, subcomponente kexec | archivo `linux/ps4-kexec-common/LICENSE` en `master` | Licencia BSD de dos cláusulas con avisos de shuffle2 y Hector Martin (“marcan”); aplicabilidad limitada a ese subcomponente | https://github.com/ps4-linux/ps4-linux-loader/tree/master/linux/ps4-kexec-common |
| U-06 | Reporte de compatibilidad de tercero | issue #10, abierto 2026-09-22, actualizado 2026-09-26 | Usuario reporta CUH-2208B/Baikal/FW 13.52 con loader v25 y kernel 5.4.247; no respalda los kernels 7.x de la distribución | https://github.com/ps4-linux/ps4-linux-loader/issues/10 |
| U-07 | Reporte negativo/diagnóstico incompleto | issue #11, cerrado 2026-09-26 | Un reporte Slim/Belize/FW 13.52 con LED blanca; el autor luego indica que arrancó desde USB. No establece causa raíz ni prueba de laboratorio independiente | https://github.com/ps4-linux/ps4-linux-loader/issues/11 |

**Integridad de referencias:** SHA de commit es un identificador de revisión de Git, no un hash criptográfico de cada archivo descargado. No se calculó en esta iteración un SHA-256 local de los assets de release. Los digests que GitHub publica para assets, cuando están disponibles, se deben registrar como valores de API y no etiquetar como hashes calculados localmente.

## Hallazgos técnicos relevantes para el laboratorio

### PS4-Linux

- El README describe una distribución Arch Linux/KDE para PS4, con imagen raíz comprimida, kernels por familia de southbridge y payloads ELF.
- La matriz upstream marca como “Works (FW 13.52, GoldHEN)” a CUH-2116A (Slim/Baikal, kernel 7.0.8) y CUH-7116B (Pro/Belize, kernel 7.1.7); otras filas se declaran no probadas.
- El README indica que el kernel debe residir en `/data/linux/boot/bzImage` y el initramfs en `/data/linux/boot/initramfs.cpio.gz`, y da instrucciones de subirlos por FTP. Por tanto, el procedimiento publicado **modifica/depende del almacenamiento interno** y no satisface por sí mismo el objetivo de preservarlo intacto.
- El README describe grabar la imagen en una unidad USB y advierte que se borra el dispositivo. No ejecutar el script de escritura ni seguir el procedimiento de instalación en esta etapa.
- La licencia de raíz es GPL-3.0, pero el NOTICE distingue kernels GPL-2.0 y artefactos de terceros con sus licencias originales. Se necesita una tabla por archivo/artefacto, avisos originales y procedencia antes de redistribuir.

### ps4-linux-loader

- El README se presenta como payload kexec para firmwares 5.05–13.52 y southbridges Aeolia, Belize(2) y Baikal. 13.02, 13.04, 13.50 y 13.52 aparecen con incertidumbre (`(?)`).
- El README explica que no es por sí mismo un exploit: necesita un mecanismo externo para inyectar código en el kernel de OrbisOS.
- Declara ruta interna por defecto `/data/linux/boot`, fallback a `/user/system/boot/` y prioridad de archivos de USB si se conecta uno. El README de la distribución usa deliberadamente el almacenamiento interno para el kernel/initramfs; no asumir que eso es USB-only.
- El release `v25.1` está publicado, pero la existencia de un release no prueba build reproducible ni equivalencia con el código de `master`. Se requiere comparar los assets con artefactos reconstruidos antes de confiar en ellos.
- La raíz no tiene licencia declarada en metadatos y el LICENSE localizado dentro de `linux/ps4-kexec-common/` cubre ese subcomponente, no automáticamente todo el repositorio. No copiar ni redistribuir el árbol completo hasta cerrar la trazabilidad de licencias, incluidos `lib/` y `freebsd-headers/`.

## Decisiones de uso

| Componente | Uso en investigación documental | Integración en cadena candidata | Redistribución | Estado |
|---|---|---|---|---|
| README/scripts de PS4-Linux | Sí, citar con revisión/fecha | No aprobar todavía; flujo publicado requiere archivos internos y no demuestra USB-only | Solo tras revisar alcance de GPL-3.0 y avisos de cada archivo | Condicionado |
| Kernels publicados por PS4-Linux | Inspección estática de metadatos únicamente | Bloqueado: southbridge local desconocido, fuente/config/build reproducible no cerrados | No redistribuir en esta etapa | Bloqueado |
| Payloads ELF de PS4-Linux | Inspección estática de manifiestos/hashes | Bloqueado: procedencia/build y compatibilidad para CUH-2115B sin demostrar | No redistribuir | Bloqueado |
| Loader fuente `ps4-linux-loader` | Sí, lectura/citas de código | Solo análisis estático; no ejecutar | Bloqueada hasta determinar licencias de todo el árbol | Bloqueado |
| Release binario `v25.1` del loader | Registrar metadatos públicos | No usar hasta comparar con fuente y revisar licencia/procedencia | No redistribuir | Bloqueado |
| Initramfs/rootfs de distribución | Revisar inventario y scripts sin montar/ejecutar | Bloqueado hasta mapear escritura/lectura y dependencias completas | No redistribuir sin licencias y avisos por componente | Bloqueado |

## Pendientes para cierre al 100 %

- Claude debe reproducir en el checkout los commits, hashes locales de fuentes ya presentes y rutas de archivos citadas; documentar discrepancias, sin ejecutar binarios.
- Completar licencias de `lib/`, `freebsd-headers/`, kernels, initramfs, rootfs y todos los assets de release.
- Comparar de manera reproducible los assets del release `v25.1` con un build limpio, si las dependencias/condiciones legales lo permiten; no publicar artefactos resultantes.
- Actualizar `ARTIFACT_INVENTORY.md`, `EVIDENCE_SOURCES.md`, `LICENSE_POLICY.md` y `UPSTREAM_AUDIT.md` en esta rama con los hallazgos validados.
- Mantener bloqueadas ejecución de payloads, escritura en USB físico, cambios de firmware y redistribución.
