# Gate previo a la primera prueba en PS4

**Corte:** 2026-10-16  
**Consola:** PS4 Slim CUH-2115B, firmware 13.52, southbridge Baikal B1 (`0x30201`) reportado por Marcos.  
**Kernel candidato documental:** `bzImage-baikal-7.0.8` (SHA-256 publicado/local previamente registrado: `46c835f762e7b0b5400ea762b8daa1bcec638a1b769c7ec0905137bc565b1ba8`).  
**Decisión:** **todavía NO-GO para ejecución física**. Este documento define el camino más corto verificable para llegar a una decisión, no autoriza el intento.

## Por qué todavía no estamos en el dispositivo

Ya no hace falta bloquear el avance por la identificación del southbridge: el valor `0x30201` fue reportado por el operador y el código upstream mapea ese valor a Baikal B1. Eso permite tratar el kernel Baikal como candidato.

Los bloqueos reales que quedan son:
1. La cadena del loader permite fallback por archivo desde USB a rutas del almacenamiento interno; puede mezclar kernel/initramfs/argumentos de orígenes distintos. El modo estricto USB-only no está demostrado.
2. El procedimiento de PS4-Linux publica la colocación de kernel e initramfs en `/data/linux/boot/`, en el almacenamiento interno. No se adoptará ese procedimiento.
3. El payload/loader, el kernel, el initramfs y el rootfs necesitan procedencia, licencia y revisión estática suficientes. Un hash correcto no demuestra que el artefacto sea seguro.
4. Las herramientas host-side necesitan una ejecución completa y resultados reproducibles, incluidos tests negativos para escritura a dispositivos, sobrescritura y rutas ambiguas.
5. La imagen USB debe inspeccionarse y validarse sin montarla en escritura ni grabarla en una unidad física.

## Gates de salida

### G0 — Baseline y trazabilidad
- [x] Modelo CUH-2115B y firmware 13.52 registrados.
- [x] Southbridge reportado como Baikal B1 (`0x30201`); no volver a ejecutar payload para repetirlo.
- [x] Kernel Baikal 7.0.8 identificado como candidato documental, no como compatibilidad probada.
- [x] Inventario inicial del kernel Baikal e initramfs en `manifests/arranque-catalogo.json`; hashes locales ya calculados y comparados con los digests API publicados.
- [x] Compilación aislada del loader original y parcheado documentada en `docs/LOADER_BUILD_REPRO.md`; artefactos de build no ejecutados.
- [ ] Cerrar manifiesto final con loader/payload, kernel, initramfs y rootfs exactos; separar hash local, digest API y hash del propio publicador.
- [ ] Resolver licencia/procedencia de loader, kernel, initramfs y rootfs por componente; excluir lo que siga sin licencia/procedencia suficiente.

**Salida G0:** lista cerrada de candidatos y artefactos que se excluyen.

### G1 — Herramientas host-side y pruebas
- [ ] Claude termina workstream 02: suite completa en entorno limpio, regresiones y CI diagnosticada. Existen pruebas locales previas para verificadores/inspección, pero falta un resultado actual de suite completa en esta sesión.
- [x] Herramientas host-side de verificación/inspección y modelo de loader existen en el repo (`verify_boot_chain.py`, `inspect_image.py`, `loader_model.py`).
- [ ] Preflight rechaza rutas de dispositivos y no escribe ni monta unidades físicas.
- [ ] Tests negativos cubren symlinks, path traversal, archivo existente, salida parcial, interrupción y hash incorrecto.
- [ ] Se registra el comando exacto, versión de herramientas, salida real y estado de cada test.

**Salida G1:** tests verdes o bloqueos externos documentados con evidencia; no se acepta “debería pasar”.

### G2 — Cadena USB-only e imagen sintética
- [ ] Verificar independientemente el parche USB-only ya compilado y sus hashes/build logs; confirmar que la salida revisada corresponde al parche y al commit exactos. El registro existente afirma compilación repetible; la revisión independiente detectó R-USB-001 para el manejo de errores de archivos opcionales.
- [ ] Definir una disposición donde kernel, initramfs, configuración y rootfs correspondan al mismo manifiesto.
- [ ] El diseño debe fallar cerrado si falta cualquier artefacto; nunca tomar silenciosamente un archivo del disco interno.
- [x] Inspección inicial de la imagen publicada registrada en `docs/PLAN_INMEDIATO.md` y `docs/USB_ONLY_DESIGN.md`: particiones/layout leídos sin montar en escritura; el contenido de arranque actual no incluye `bzImage` con nombre exacto ni el kernel Baikal.
- [ ] Inspeccionar una copia de imagen candidata tras agregar el kernel Baikal en la FAT, sin montar en escritura ni modificar dispositivos físicos.
- [ ] Validar tamaño, estructura y hashes con fixtures sintéticos y salidas temporales explícitas.
- [ ] Verificar por lectura estática los argumentos de arranque y cómo el initramfs localiza la raíz USB; la revisión existente del initramfs/rootfs es parcial y no prueba que Linux no acceda al disco interno.
- [ ] Documentar recuperación y límites de lo que no puede probarse sin hardware.

**Salida G2:** imagen candidata reproducible/inspeccionada en PC y evidencia de que el diseño no depende de las rutas internas. Si la variante parcheada no pasa revisión o no se puede vincular a sus fuentes/build, mantener el NO-GO y corregir/reconstruirla en entorno aislado; no sustituirla por el loader upstream sin parche.

### G3 — Revisión independiente y autorización
- [ ] ChatGPT revisa el diff final de Claude, manifiesto, resultados de tests y rutas de lectura/escritura.
- [ ] Cerrar o aceptar explícitamente cada riesgo crítico del registro de riesgos.
- [ ] Emitir informe go/no-go que distinga hechos probados en PC de propiedades aún no probadas en PS4.
- [ ] Marcos revisa la propuesta concreta de prueba física y decide explícitamente si autoriza ese hito.

**Salida G3:** solo una propuesta revisada, con lista exacta de artefactos, riesgos residuales, rollback y criterios de aborto. La aprobación documental no equivale a una orden de ejecutar.

## Condiciones de aborto para cualquier futura prueba

Abortar si el loader requiere copiar archivos al almacenamiento interno, si el origen de algún archivo no puede identificarse, si el hash no coincide, si la imagen está incompleta, si se necesita actualizar firmware, si aparece una ruta de escritura no explicada, o si no se puede determinar qué resultado observable marcaría éxito o fallo.

## Alcance excluido de esta etapa

No se ejecuta payload ni exploit en esta fase; no se escribe una unidad USB física; no se altera el almacenamiento interno; no se actualiza firmware; no se declara éxito por pantalla blanca, LED o ausencia de error sin un criterio observable previamente definido.

**Próximo movimiento concreto:** Claude completa workstream 02 y avanza el dry-run del workstream 05; en paralelo, se resuelve la procedencia/licencia del candidato y se termina la auditoría estática del loader. No hace falta esperar a terminar toda la documentación general, pero sí cerrar estos gates técnicos antes de proponer la primera ejecución.
