# Selección del kernel para la PS4 Slim CUH-2115B (firmware 13.52)

Fecha de la investigación: 2026-10-16. Alcance: investigación documental y estática; **no se ejecutó Linux ni se probó ningún kernel en la consola**. El southbridge fue leído por el operador como Baikal B1 (`0x30201`) mediante GoldHEN v2.2.3; la captura original no está archivada, por lo que el nivel de evidencia permanece `OBSERVADO`. Este documento fija el procedimiento y los criterios; **no aprueba ningún kernel para arranque**.

Niveles de evidencia usados: **HECHO** (confirmado por una fuente que se consultó directamente, citada), **TERCEROS** (lo reporta alguien, sin reproducción nuestra), **INFERENCIA** (deducción nuestra), **PENDIENTE** (falta una comprobación), **FÍSICO** (exige intervención sobre la consola).

## 1. Conclusión técnica

**Estado vigente:** el operador informó una lectura directa de **Baikal B1 (`0x30201`)** (`LAB-001`; captura no archivada). El modelo CUH por sí solo no habría bastado para identificarlo. Esto permite mantener `bzImage-baikal-7.0.8` como candidato débil para revisión en PC, pero no demuestra que el kernel sea compatible ni que arranque. La auditoría de la cadena y el plan V0 siguen siendo obligatorios.

**Contexto histórico:** antes de la lectura reportada en `LAB-001`, no había evidencia suficiente para elegir una familia de kernel. La siguiente evidencia explica por qué el modelo CUH-2115B por sí solo no determina el southbridge:

> La wiki PS4 Developer (tabla *Hardware Info*, copia de Wayback del 2025-12-18) lista **tres filas** del modelo `CUH-2115` y **dos southbridges distintos para CUH-2115B**: `30201 (Baikal B1)` y `40100 (Belize2 A0)` (la CUH-2115A figura con `40100 (Belize2 A0)`). Las tablas de la página *Southbridge* (Wayback 2026-03-03) lo confirman por placa: el chasis 2100 usa **Belize 2** con las placas SAE-001/003 y **Baikal** con SAE-002/004.

Por tanto **el CUH-2115B no determina el southbridge**, y la elección de kernel depende de cuál de las dos variantes tenga esta unidad. Además, **ninguno** de los kernels disponibles localmente declara soporte para Belize 2.

## 2. Hechos, reportes de terceros e inferencias

| # | Afirmación | Nivel | Fuente (consultada 2026-10-16) |
|---|---|---|---|
| 1 | CUH-2115B figura con Baikal B1 (30201) **y** con Belize2 A0 (40100) en dos filas distintas; CUH-2115A con Belize2 A0 | HECHO (la wiki lo dice; la wiki es colaborativa y está marcada "for rewrite") | psdevwiki *Hardware Info*, `web.archive.org/web/20251218182117/https://www.psdevwiki.com/ps4/Hardware_Info`, tabla principal, columnas `[APU, SouthBridge SubSystem, hw_model (Serial Flash NVS)]` |
| 2 | Chasis 2100: SAE-001/003 → Belize 2 (fab. 2017-11..12); SAE-002/004 → Baikal (fab. 2017-06..12) | HECHO (wiki) | psdevwiki *Southbridge*, `web.archive.org/web/20260303210730/https://www.psdevwiki.com/ps4/Southbridge`, tabla "per chassis" |
| 3 | Una consola de fabricación 2017-06..10 sería Baikal; 2017-11..12 es ambiguo | INFERENCIA (de #2) | ídem |
| 4 | El acceso directo a psdevwiki devuelve HTTP 403 a clientes automáticos; se leyó la copia pública de Wayback, sin eludir ningún bloqueo | HECHO | pruebas de esta sesión |
| 5 | El southbridge se lee con `sysctlbyname("hw.sce_subsys_subid")`; IDs 0x10100-0x10300 Aeolia, 0x20100/0x20200 Belize, 0x30100-0x30201 Baikal, 0x40100 Belize2 | HECHO (código del loader `main-aio.c` líneas 324-338 y README de `tomfitzhenry/ps4-which-southbridge`) | loader@`f70f43a`; GitHub |
| 6 | Existe un payload de espacio de usuario (`ps4-which-southbridge`, 1 commit, 0 estrellas, sin licencia) que solo lee ese ID; "debe ejecutarse tras HEN" | HECHO (README) / seguridad del binario **no auditada** | https://github.com/tomfitzhenry/ps4-which-southbridge |
| 7 | GoldHEN ≥ 2.2.3 muestra "Southbridge info" | HECHO (CHANGELOG oficial); el GoldHEN para 13.52 es el binario no oficial de raw13g | `GoldHEN/GoldHEN` CHANGELOG; D-010 |
| 8 | La release `v5.4.247__baikal` (2025-08-29) del repositorio `feeRnt/ps4-linux-12xx` declara "CUH-71xx (CUH-7116B): Tested functional. **CUH-21xx (CUH-2115B): Tested functional.**" con un kernel **Baikal 5.4.247** | TERCEROS (autoría propia del mantenedor, sin logs; **firmware no indicado**, anterior a la existencia del exploit 13.52) | https://github.com/feeRnt/ps4-linux-12xx/releases (API) |
| 9 | Esa misma release contradice al README de `X-F1REBALL-X` (que usa el kernel **Belize** para CUH-7116B) y a la wiki (CUH-7116B → Belize2 A0) | HECHO (contradicción entre fuentes) | #8, README distribución, wiki |
| 10 | `feeRnt`: los kernels Baikal "dejaron de funcionar" al pasar de 5.4 a 5.15; 6.15.4 Baikal probado por alguien con LED blanco | TERCEROS | issue #3 de `feeRnt/ps4-linux-12xx` |
| 11 | Para CUH-2115B/2115 **no hay** issues ni PR en `ps4-linux-loader`, `X-F1REBALL-X/PS4-Linux` ni `feeRnt/ps4-linux-12xx` (búsqueda de "2115" = 0) | HECHO (búsqueda de la API) | GitHub Search |
| 12 | Un comentario de ps4linux.com afirma un kernel 5.15.15 funcionando en una "CUH-2112B belize2 A0" | TERCEROS **no verificado directamente** (lo vi solo en un resumen de búsqueda) | resumen de búsqueda; no usado como evidencia |
| 13 | El README de `X-F1REBALL` sugiere probar el otro kernel si la luz queda blanca | HECHO (README) — método de prueba y error, que exige ejecutar el payload en la consola | README distribución |
| 14 | Ningún kernel local (Baikal 7.0.8, Belize 7.1.7) declara soporte Belize 2: el README dice "Aeolia/Belize" y "Baikal" | HECHO | README distribución |

## 3. Cómo identificar el southbridge de forma fiable

| Método | ¿Requiere ejecutar código/abrir? | Fiabilidad | Estado |
|---|---|---|---|
| Número de modelo (CUH-2115B) | No | **Insuficiente**: dos southbridges posibles (HECHO #1) | Ya usado; agotado |
| Fecha de fabricación (¿figura en la etiqueta o la caja?) | No | Solo acota (INFERENCIA #3): antes de 2017-11 ⇒ Baikal; 2017-11/12 ambiguo | Opcional; ya existe una lectura de southbridge reportada en `LAB-001` |
| Código de placa SAE-00x impreso en la placa | **FÍSICO** (abrir la consola; sellos) | Alta (HECHO #2: cada placa tiene su southbridge) | No se hace: `LAB-000` prohíbe abrirla |
| Subsys ID por software (`ps4-which-southbridge` o GoldHEN "Southbridge info") | **Ejecuta código en la PS4** (exploit + payload) | Alta (es lo que el loader usa) | **Lectura realizada y reportada** en `LAB-001`; la captura no está archivada. Esta autorización no cubre escritura USB ni arranque Linux |
| `hw_model`/NVS del Serial Flash | Volcado de flash (hardware o exploit) | Alta pero invasiva | Fuera de alcance |
| Prueba y error con kernels (LED blanco ⇒ otro kernel) | Ejecuta el loader varias veces | **Baja** (un fallo no distingue SB incorrecto de otros fallos: exploit, offsets, vídeo) | Rechazado como método de identificación |

**Qué comprobar sin tocar la consola (acción de Marcos en su PC/casa):** (a) fotografiar la etiqueta y la caja buscando una fecha de fabricación; (b) registrar el resultado como dato nuevo en `LAB-000`. Con una fecha ≤ 2017-10 el candidato pasaría a Baikal por inferencia (aún no confirmación).

## 4. Procedimiento de selección del kernel

**Entradas disponibles:** modelo (CUH-2115B), firmware (13.52) y southbridge Baikal B1 (`0x30201`) reportado por lectura directa (`OBSERVADO`; captura no archivada). El catálogo de artefactos con hashes está en `manifests/arranque-catalogo.json`. La lectura del southbridge no sustituye la evidencia de compatibilidad del kernel.

**Paso 1 — Clasificar el dato de southbridge.**
- `CONFIRMADO` solo si proviene de lectura directa (ID por software autorizado o código de placa fotografiado). Una inferencia (fecha, analogía de modelo) es `INFERIDO` y **no habilita** una selección.

**Paso 2 — Criterios de ACEPTACIÓN** (todos deben cumplirse para considerar un kernel *candidato*):
1. southbridge `CONFIRMADO` y **contenido en el conjunto de southbridges que el kernel declara** (codename exacto: Belize ≠ Belize 2 mientras no haya evidencia que los equipare);
2. al menos un reporte de TERCEROS con **ese codename** y **firmware ≥ 13.xx** (idealmente 13.52) con detalle (versión del kernel y loader, síntoma observado), o una prueba de laboratorio propia;
3. el archivo está en el catálogo (sha256 + tamaño) y pasa `verify_boot_chain` (estructura, formato);
4. licencia y disponibilidad de fuentes registradas (`ARTIFACT_INVENTORY.md`); sin fuente ⇒ solo uso local, nunca redistribución;
5. no hay reporte negativo sin explicar para el mismo codename y versión.

**Paso 3 — Criterios de RECHAZO** (basta uno):
southbridge `INFERIDO` o desconocido; el kernel declara otro codename; evidencia solo de CUH vecinos o del mismo CUH con **otro** southbridge; reportes contradictorios sin resolver (p. ej. #9); firmware del reporte anterior al exploit 13.52 sin otra prueba; kernel sin hash en el catálogo; formato inválido.

**Paso 4 — Resultado por southbridge** (aplicación hoy, con la evidencia disponible):

| Southbridge confirmado | Kernel local candidato | Evidencia | Veredicto hoy |
|---|---|---|---|
| Baikal (0x30201) **← observado en esta consola (OPERADOR)** | `bzImage-baikal-7.0.8` | README: CUH-2116A FW 13.52 (TERCEROS débil); issue #10: CUH-2208B FW 13.52 con **otro** kernel (5.4.247); feeRnt: CUH-2115B con Baikal 5.4.247 (FW desconocido) | **Candidato débil**: cumple 1, 3, 4(parcial); el 2 solo con reportes sin logs y de otra versión de kernel. Habilitaría una **primera prueba de laboratorio autorizada**, no una afirmación de compatibilidad |
| Belize2 (0x40100) | ninguno | El README no declara Belize 2; sin reportes con SB confirmado | **Rechazado** (criterio 1): no hay kernel con soporte declarado |
| Belize (0x2xxxx) | `bzImage-belize-7.1.7` | CUH-7116B (pero la wiki da Belize2 para 7116B: contradicción #9); issue #11: Slim Belize con fallo inicial sin diagnóstico | **Rechazado hoy** por contradicción sin resolver |
| Aeolia | – | no aplica al CUH-2115B según la wiki | n/a |

**Paso 5 — Abortos y límites de la primera prueba de laboratorio (cuando exista autorización):** un solo cambio de variable por intento; máximo 3 intentos con la misma combinación; registrar LED, tiempos y logs; ante luz blanca > 20 s no encadenar kernels sin releer este documento; nunca escribir en el almacenamiento interno (D-008).

## 5. Qué componentes están validados, son candidatos o carecen de evidencia

| Componente | Estado | Qué significa |
|---|---|---|
| Loader `f70f43a` (código y compilación) | **Validado estáticamente** (compila, repetible, `fw_table` 13.52 presente) | No probado en hardware |
| Parche USB-only | **Validado estáticamente** (compila; sin rutas internas en el binario) | No probado en hardware |
| `bzImage-baikal-7.0.8` | **Candidato débil** (solo si SB = Baikal) | Formato OK, versión leída; sin prueba en CUH-2115B |
| `bzImage-belize-7.1.7` | **Sin evidencia suficiente** para esta consola | Sin soporte declarado para Belize 2; contradicción sobre 7116B |
| Kernels de `feeRnt/ps4-linux-12xx` (Baikal 5.4.247, Belize 5.15.15, Aeolia/Belize 6.15.4) | **No obtenidos**, no inventariados | Mencionan CUH-2115B solo la release Baikal 5.4.247 (TERCEROS, FW desconocido) |
| `initramfs.cpio.gz` (v0.9.1) y rootfs de la imagen publicada | **Validados estructuralmente** (cpio/gzip; FAT y ext4 sanos) | Contenido del rootfs sin auditar |
| Southbridge de la consola | **Baikal B1 (`0x30201`) observado** | Lectura reportada por el operador; captura no archivada, sin prueba de arranque |

## 6. Procedencia y condiciones de uso (resumen; detalle en `ARTIFACT_INVENTORY.md` §7)
Los kernels son derivados de Linux (GPL-2.0): quien los **redistribuye** debe ofrecer las fuentes. `X-F1REBALL-X/PS4-Linux` declara GPL-3.0 para guía/scripts (su `LICENSE` es un UTF-16 de 71 648 B, ilegible como texto plano sin convertirlo) y que kernel, initramfs y rootfs "mantienen sus licencias"; sin enlaces a las fuentes de los kernels. Los repositorios de kernels que inspeccioné (`feeRnt`, `codedwrench`, `crashniels`, `DFAUS-git`, `eeply`, `Ps3itaTeam`) son forks del kernel y la API de GitHub devuelve `NOASSERTION` (traen `COPYING` de Linux). `ps4-linux-loader` y `GoldHEN` no declaran licencia. Este laboratorio no redistribuye binarios (D-004); el uso privado de archivos ya descargados no se ve afectado, pero cualquier publicación de imágenes sí lo estaría.

## 7. Siguiente bloqueo y qué lo resuelve
**Bloqueo vigente:** el southbridge está observado, pero falta archivar la captura original y resolver la discrepancia R-23 sobre la versión del binario GoldHEN. El bloqueo técnico principal sigue siendo la procedencia/compatibilidad de la cadena kernel + initramfs + rootfs y la reproducción del loader parcheado.
1. **Sin tocar la consola:** buscar la fecha de fabricación en etiqueta/caja y registrarla (acota, no confirma).
2. **Con autorización expresa de Marcos:** leer el subsys ID con el procedimiento más pequeño disponible (hoy: payload de espacio de usuario tras el jailbreak; previa auditoría estática de ese binario y barrera de red D-016). Resultado → completar la tabla del Paso 4 y recién entonces preparar la imagen por la ruta A de `USB_ONLY_DESIGN.md` §8.
3. **Si el resultado es Belize2:** no hay kernel candidato; el siguiente trabajo sería buscar un kernel con soporte declarado para Belize 2 (investigación, no ejecución).
