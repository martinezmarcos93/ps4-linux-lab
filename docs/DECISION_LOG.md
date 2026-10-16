# Registro de decisiones

Las decisiones describen opciones aceptadas y condiciones para revisarlas; no transforman hipótesis en hechos.

## D-001 — Priorizar arranque externo
- **Fecha:** 2026-10-15
- **Estado:** ACEPTADA como estrategia inicial.
- **Decisión:** evaluar Linux desde USB y mantener intacto el almacenamiento interno durante las primeras fases.
- **Motivo:** reducir riesgo y facilitar el retorno al sistema original.
- **Revisión:** si el loader requiere persistencia interna, detenerse y estudiar ese efecto antes de ejecutar.

## D-002 — No inferir compatibilidad por categoría
- **Fecha:** 2026-10-15
- **Estado:** ACEPTADA.
- **Decisión:** registrar modelo CUH, firmware y southbridge/revisión mediante fuentes fiables.
- **Motivo:** Fat/Slim/Pro no identifican necesariamente toda la revisión del hardware.

## D-003 — Separar arranque, gráficos y LLM
- **Fecha:** 2026-10-15
- **Estado:** ACEPTADA.
- **Decisión:** no instalar frameworks de IA hasta validar kernel, driver y APIs de cómputo.
- **Motivo:** evitar invertir en un backend no compatible.

## D-004 — No copiar binarios por defecto
- **Fecha:** 2026-10-15
- **Estado:** ACEPTADA.
- **Decisión:** preferir releases upstream verificables; copiar código solo tras resolver licencia, atribución y procedencia.

## D-005 — Repositorio privado inicializado
- **Fecha:** 2026-10-15
- **Estado:** COMPLETADA.
- **Decisión:** usar `martinezmarcos93/ps4-linux-lab` (privado, rama por defecto `main`) como repositorio de trabajo.
- **Evidencia:** repositorio creado y disponible en `https://github.com/martinezmarcos93/ps4-linux-lab`; metadata de GitHub consultada durante la sesión; se verificaron permisos de administración/escritura del propietario.

## D-006 — Escritura documental directa a main
- **Fecha:** 2026-10-15
- **Estado:** ACEPTADA para la fase documental inicial.
- **Decisión:** trabajar en `main` por autorización explícita del propietario.
- **Límite:** no autoriza force-push, borrados masivos, acciones destructivas sobre hardware ni cambios irreversibles en la consola.

## D-007 — No destructivo primero
- **Fecha:** 2026-10-15
- **Estado:** ACEPTADA.
- **Decisión:** comenzar por doctor/inspect/verify/diagnose y tests sobre archivos de prueba, nunca sobre discos reales ni sobre la consola, hasta superar esa etapa.

## D-008 — Ubicación del kernel/initramfs: USB-only es la arquitectura objetivo
- **Fecha:** 2026-10-15 (elección de diseño); cerrada y reconciliada el 2026-10-15 tras la auditoría del historial del loader.
- **Estado:** DECIDIDA como política de diseño. **NO VALIDADA** como propiedad técnica del flujo completo. No autoriza ejecutar nada en la consola.
- **Decisión:** `bzImage`, `initramfs.cpio.gz` y los archivos opcionales (`bootargs.txt`, `vram.txt`) viven en la partición FAT del USB. **No se escribe nada en el almacenamiento interno de la consola.** La escritura en `/data/linux/boot/` no es una opción ni un fallback automático. Si USB-only resultara inviable, se detiene el trabajo, se documenta el bloqueo exacto y cualquier alternativa exige una decisión nueva y explícita de Marcos. Las "opciones A/B" de versiones anteriores de este registro quedan retiradas: la elección ya se hizo.
- **Qué NO significa:** que el loader upstream sea USB-only. Busca cada archivo por separado en `/mnt/usb0/`, `/mnt/usb1/`, `/data/linux/boot/` y `/user/system/boot/` (`main-aio.c` @ `f70f43a`, líneas 375-389). Una búsqueda prioritaria en USB **no** es aislamiento: si falta un archivo en el USB, el loader toma el del almacenamiento interno sin avisar y puede combinar orígenes (kernel del USB con initramfs del interno).
- **Qué está demostrado** (ver `UPSTREAM_CODE_MAP.md` §1.8-1.9 y `USB_ONLY_DESIGN.md` §2): ningún commit del historial del loader (71) contiene código que cree o escriba archivos; el ELF distribuido por la distribución no contiene literales de escritura y su tabla de offsets coincide con el código fuente fijado; el `init` del initramfs monta solo `LABEL=psxitarch`; el `fstab` del rootfs está vacío.
- **Qué NO está demostrado:** (1) que los releases publicados del loader se compilen desde ese código (el CI no publica los releases; el ELF de la distribución se compiló con otro compilador y no se pudo reproducir bit a bit, ver D-021); (2) que, una vez en Linux, ningún componente monte o escriba el disco interno; (3) que el flujo arranque en hardware real.
- **Condiciones antes de una prueba real (sin cambios):** modelo/southbridge identificados cuando sea posible; binarios con procedencia revisada y hashes en el catálogo; imagen verificada en la PC; aislamiento de internet/PSN (D-012/D-016); y confirmación específica de Marcos antes de ejecutar el exploit/payload (D-014).
- **Bloqueo exacto y solución técnica:** `USB_ONLY_DESIGN.md` §4-§5. En síntesis: aplicar la verificación previa de `tools/verify_boot_chain.py`, usar el catálogo de procedencia, construir la imagen con `tools/build_usb_image.py` (bzImage dentro de la FAT) y, para convertir la política en propiedad del binario, compilar y revisar el parche `patches/loader-usb-only-f70f43a.patch` (pendiente de entorno de compilación y de aprobación de Marcos para su uso).

## D-009 — Numeración de versión del kernel "7.1.7"/"7.0.8"
- **Fecha:** 2026-10-15. **Estado:** RESUELTA (observación directa, 2026-10-15).
- **Observación:** la cabecera del protocolo de arranque x86 de cada `bzImage` incluye la cadena de versión (`kernel_version`, offset indicado en 0x20E). `bzImage-baikal-7.0.8`: `7.0.8-Strawberry-FullLTO-Baikal-+ (pask@pask-MacBookPro16-1) #1 SMP PREEMPT_DYNAMIC Tue Sep 8 03:09:52 CEST 2026`. `bzImage-belize-7.1.7`: `7.1.7-Strawberry-General-FullLTO+ (runner@runnervmgx7h7) #1 SMP PREEMPT_DYNAMIC Tue Aug 25 18:56:41 UTC 2026`. Son versiones reales de Linux 7.0.8 y 7.1.7 con la etiqueta de compilación "Strawberry"; **la hipótesis anterior de una numeración propia del fork queda refutada**.
- **Consecuencia:** el "Kernel 5.4.247" del issue #10 es otra compilación (rama LTR 5.4). Ese reporte **no** respalda los kernels 7.x del catálogo; solo respalda la combinación hardware/firmware/southbridge para la que se hizo.
- **Límite:** la versión leída no prueba que el binario se haya compilado de las fuentes publicadas ni que arranque; el repositorio del kernel "Strawberry" sigue sin auditarse. Reproducible con `python3 tools/verify_boot_chain.py <dir>`.

## D-010 — No ejecutar el payload 13.52 sin revisión estática adicional
- **Fecha:** 2026-10-15.
- **Estado:** ACEPTADA como gate de seguridad.
- **Decisión:** no ejecutar `goldhen.bin` en la consola mientras siga siendo un blob nativo sin fuente y sin desensamblado revisado. El análisis del JavaScript no valida el payload nativo.
- **Siguiente acción:** análisis offline con Rizin/objdump si ya están disponibles; documentar offsets, regiones no decodificables, llamadas/saltos relevantes y límites. No ejecutar el binario ni cargarlo en la PS4 durante esta etapa.
- **Revisión:** después de un informe reproducible de análisis estático y de evaluar la procedencia/hash del artefacto. La decisión de ejecutar en hardware seguirá siendo separada.
- **Actualización 2026-10-15:** el informe reproducible existe (`EXPLOIT_AUDIT_13.52.md`, segunda pasada): el cuerpo se descomprime (zlib), se identifica como GoldHEN v2.4b18.12, sin hosts ajenos a GoldHEN/GitHub/Google, con ~80 % de cadenas en común con el release oficial 2.4b18. **Límites:** sin revisión del código máquina del cuerpo, sin referencia oficial exacta y sin compilación reproducible. El gate pasa a **"informe completado, decisión de ejecución pendiente de Marcos"**; no se ejecuta nada hasta ese "sí".
- **Actualización 2026-10-15 (reproducción):** `tools/payload_static.py` reproduce las cifras del informe (cuerpo zlib en `0x6900`, 636 760 bytes, sha256 `4e2864fb…91abee`) y añade el solapamiento de ventanas de 16 bytes con el `goldhen.bin` oficial 2.4b18 (≈65 %; ver `EXPLOIT_AUDIT_13.52.md` §1.4). El **estado de la auditoría estática** (informe hecho, límites documentados) está separado del **estado de autorización de ejecución** (cerrado, a la espera del "sí" de Marcos): completar una no desbloquea la otra.

## D-011 — Posponer REA y no instalar herramientas de agente todavía
- **Fecha:** 2026-10-15.
- **Estado:** ACEPTADA.
- **Decisión:** preferir herramientas locales de análisis binario ya instaladas. No ejecutar `npx rea-agents setup` ni modificar configuración de agentes hasta auditar su paquete y demostrar que agrega valor frente a Rizin/Ghidra directamente.
- **Motivo:** reducir la superficie de confianza y evitar instalar infraestructura que todavía no necesitamos.

## D-012 — Aislamiento de red antes de cualquier prueba de exploit
- **Fecha:** 2026-10-15.
- **Estado:** ACEPTADA como precondición, todavía no completada.
- **Decisión:** mantener desactivadas las actualizaciones automáticas y no iniciar sesión en PSN para pruebas. Antes de una eventual ejecución, verificar una barrera reversible que permita el acceso local necesario pero impida salida de la PS4 a internet/PSN.
- **Límite:** este registro no afirma que la consola ya esté aislada; sigue figurando conectada por Wi-Fi según LAB-000 y la auditoría del exploit.

## D-013 — Priorizar herramientas de PC no destructivas
- **Fecha:** 2026-10-15.
- **Estado:** ACEPTADA.
- **Decisión:** avanzar en verificación de artefactos, inspección de imágenes y tests con fixtures mientras el binario y el hardware permanezcan bloqueados.
- **Motivo:** producir resultados verificables sin depender de identificar el CUH ni ejecutar código en la consola.

## D-014 — Delegación de decisiones técnicas en Claude
- **Fecha:** 2026-10-15. **Estado:** ACEPTADA.
- **Decisión:** Marcos delegó en Claude las decisiones técnicas intermedias ("las demás decisiones te las dejo a vos") para poder avanzar. **No** delega: ejecutar el exploit sobre la consola, escribir en su almacenamiento interno, ni el push de código que no sea documentación. Esos pasos requieren un "sí" puntual de Marcos en el momento.
- **Actualización 2026-10-15 (encargo "barrido resolutivo"):** Marcos autorizó expresamente resolver conflictos, implementar correcciones, tests y documentación e **integrar en `main`** lo que pase las verificaciones locales. Sigue sin autorizar: ejecutar `goldhen.bin` u otro payload, lanzar el exploit, modificar el almacenamiento interno, escribir una imagen en un dispositivo físico, pruebas destructivas, hacer público el repositorio, ni eliminar ramas/commits con trabajo no integrado.

## D-015 — Conciliación con las decisiones D-008, D-010 a D-013 (sesión paralela)
- **Fecha:** 2026-10-15. **Estado:** ACEPTADA.
- **Contexto:** mientras se trabajaba aquí, otra sesión subió a `main` D-008 (USB-only por defecto) y D-010 a D-013. Una versión previa de este registro (no publicada) contenía otras D-010 a D-013 con numeración colisionante; se retiran y se concilian así:
  - **D-008:** prevalece la versión publicada (USB-only; si es inviable, detenerse y documentar, **sin** pasar automáticamente a escritura interna).
  - **D-010 (gate del payload):** prevalece. Se retira mi propuesta de "aceptar el payload no auditable con mitigaciones": el gate sigue activo. Hallazgo nuevo que la informa: >90 % del blob tiene entropía ≈ 8 (`EXPLOIT_AUDIT_13.52.md`), así que la revisión estática exigida deberá empezar por el stub de descompresión (salto `0x0` → `0xe3b`). Si resultara no concluyente, la decisión de ejecutar en hardware será de Marcos, informada, y separada.
  - **D-011 y D-013:** coinciden con lo que se había decidido aquí (sin REA por ahora; herramientas de PC no destructivas).
  - **D-012:** se concreta en D-016.

## D-016 — Barrera de red: DNS manual + alojamiento local (implementa D-012)
- **Fecha:** 2026-10-15. **Estado:** PROPUESTA, sin verificar.
- **Método:** en la PS4, DNS manual a una IP sin servicio (p. ej. `127.0.0.1`), sin sesión de PSN; el exploit se serviría desde la PC con `tools/ps4lab.py serve` (solo lectura, lista blanca, solo IP privada). Reversible, no toca el router.
- **Pendiente:** comprobar que la PS4 deja de resolver dominios de Sony con ese DNS (p. ej. observando el tráfico en la PC) antes de dar la barrera por efectiva. Las descargas automáticas de actualización ya fueron desactivadas por Marcos (2026-10-15).

## D-017 — Qué se pudo y qué no se pudo demostrar sobre la "copia automática" a la interna
- **Fecha:** 2026-10-15. **Estado:** ACEPTADA como conclusión de la investigación (resultado: **DESCONOCIDO** para el componente que copia; evidencia faltante listada).
- **Hechos (ver `UPSTREAM_CODE_MAP.md` §1.8):** la frase "Automatic boot files placement … copied automatically to /data/linux/boot" entró en `README.md` en el commit `8a1468f` (2025-09-26, solo README); el matiz "from the external fat32 partition" en `7280a37` (2026-04-02, solo README). En todo el historial (71 commits) ningún archivo fuente no-markdown contiene `O_CREAT`/`O_WRONLY` fuera del commit inicial `d55dd2c` (2022, utilidad de prueba en `acpi.c`), ni `creat(`, ni `time=`. El ELF `linux-1024mb.elf` de la distribución no tiene literales ni símbolos de copia. El `init` del initramfs v0.9.1 y sus `functions.sh` no copian a `/data/linux/boot` (no hay directorio `/hooks`).
- **Conclusión:** no puede demostrarse que **ningún componente que hayamos podido inspeccionar** realice esa copia. La afirmación del README no tiene respaldo en el código disponible; tampoco "la refutamos" para binarios que no tenemos.
- **Evidencia que faltaría para cerrarlo:** (a) el código fuente real de los releases del loader (`ArabPixel/ps4-linux-payloads`, mismo repositorio tras un renombre; el workflow no publica releases); (b) una compilación reproducible que dé los mismos hashes que los ELF de la distribución; (c) captura de `strace`-equivalente o logs de un arranque real (solo posible en laboratorio con autorización).
- **Regla derivada:** no usar la "copia automática" en ningún procedimiento y verificar siempre, antes de arrancar, que `/data/linux/boot/` y `/user/system/boot/` no contengan archivos ajenos (hoy solo comprobable con acceso FTP de GoldHEN, es decir, en una fase con ejecución autorizada).

## D-018 — El verificador de arranque separa cinco niveles y no promete lo que no comprueba
- **Fecha:** 2026-10-15. **Estado:** ACEPTADA e implementada (`tools/verify_boot_chain.py`, 59 tests).
- **Decisión:** estructura, integridad, formato, compatibilidad y arranque son niveles independientes con estados `OK`/`FALLO`/`NO_EVALUADO`. Un conjunto de bytes arbitrarios no pasa el nivel de formato; el nivel de compatibilidad no se evalúa si el southbridge es desconocido (D-002); el nivel de arranque solo acepta un registro de laboratorio cuyos hashes coincidan y se declara basado en ese registro, no en la herramienta. Los mensajes describen lo comprobado ("cabecera x86 coherente"), nunca "arranque válido".
- **Fuente de los criterios de formato:** protocolo de arranque x86 del kernel Linux (firma 0xAA55, "HdrS", LOADED_HIGH) y formato cpio "newc". No se validan firmas de publicador, porque no existen.

## D-019 — Arquitectura recomendada para convertir USB-only en una propiedad verificable
- **Fecha:** 2026-10-15. **Estado:** ACEPTADA como recomendación de diseño; implementación parcial (ver `USB_ONLY_DESIGN.md` §3-§5).
- **Decisión:** defensa en capas, de menor a mayor acoplamiento: (1) verificación previa de la cadena en la PC con catálogo y detección de mezclas; (2) imagen construida con bzImage dentro de la FAT del USB; (3) variante auditada del loader sin rutas internas (parche revisable; compilado y verificado estáticamente el 2026-10-16, D-021; no ejecutado); (4) precondición de laboratorio: confirmar por FTP de solo lectura que las rutas internas están vacías antes de cada intento. Ninguna capa sola basta; la (3) es la única que convierte la política en propiedad del binario.

## D-020 — Taxonomía de estados del roadmap
- **Fecha:** 2026-10-15. **Estado:** ACEPTADA (aplicada en `ROADMAP.md`).
- **Decisión:** cada tarea lleva una etiqueta de evidencia: `IMPLEMENTADO`, `TESTS`, `CÓDIGO`, `TERCEROS`, `LAB`, `PENDIENTE` o `BLOQUEADO`. Solo `LAB` (prueba propia en hardware con registro y hashes) puede sostener un `VERIFIED` de fase. Documentación, código escrito o un reporte de terceros nunca bastan. La selección de kernel para esta consola no se marca como resuelta mientras CUH y southbridge sigan sin confirmar.

## D-021 — Compilación aislada del loader (original y parcheado): resultados, defectos corregidos y límites
- **Fecha:** 2026-10-16. **Estado:** ACEPTADA (resultados registrados; sin ejecución de binarios).
- **Autorización:** Marcos autorizó compilar `f70f43a` con y sin `patches/loader-usb-only-f70f43a.patch` en un entorno aislado; no autorizó ejecutar nada ni integrar a `main`. Rama `claude/2026-10-16-compilacion-aislada-loader`. Desde esta fecha Marcos dejó de usar OpenCode y coordina con ChatGPT mediante informes.
- **Hallazgo previo:** `lib/syscalls.py` consulta dos URLs sin integridad en origen (una por HTTP) pero solo **imprime ensamblador**; `syscalls.asm` está versionado y regenerarlo sin red con las fuentes descargadas da una salida byte-idéntica. La compilación usa el `.asm` versionado, con contenedor sin red ni Python.
- **Defectos del primer script, corregidos:** (1) registraba el código de `make` y luego hacía `exit 0`, y daba por buena una compilación con solo algún ELF → ahora se propaga el código real y se exige el conjunto completo (9 ELF, 9 BIN, 20 `kexec.bin`, sin vacíos, duplicados ni inesperados), verificado por `tools/verify_loader_build.py`; (2) `chmod a+rwx` globales → el contenedor corre con el uid/gid del anfitrión; (3) la imagen base y `apt` no estaban fijados → digest + snapshot + `paquetes.lock` con comparación obligatoria; (4) el parche con ruta relativa fallaba tras un `cd` (fallaba en seguro, ahora se resuelve a ruta absoluta). Cubierto con 15 pruebas de inyección de fallos (23 en el archivo de pruebas) y 6 mutaciones detectadas.
- **Resultado:** ambas variantes compilan (GCC 13.3.0, ld 2.42, yasm 1.3.0), son repetibles en el entorno fijado y sus hashes coinciden con el manifiesto; **no** se reproduce bit a bit el ELF de la distribución (GCC 16.2.1). La variante parcheada no contiene literales de rutas internas y su selección de carpeta está confirmada en el desensamblado.
- **Visible y pendiente:** 30 avisos de pila ejecutable y 20 de segmento RWX del enlazador por variante (R-20); no se silenciaron.
- **No demuestra:** que el loader arranque, que USB-only esté garantizado en ejecución, ni compatibilidad de hardware. Detalle: `docs/LOADER_BUILD_REPRO.md`.

## D-022 — Inventario local cerrado; no se construye imagen mientras el kernel no pueda elegirse
- **Fecha:** 2026-10-16. **Estado:** ACEPTADA.
- **Hechos:** CUH-2115B confirmado por Marcos (LAB-000); southbridge desconocido; 0 reportes del modelo exacto en los repositorios upstream consultados. Inventario real de 20 archivos en `manifests/inventario-local-2026-10-16.json` (sin descargas nuevas). Hallazgo R-IMG-01 de `docs/REVIEW_BUILD_USB_IMAGE.md` confirmado y corregido.
- **Decisión:** no se selecciona kernel por analogía con CUH vecinos ni se construye una imagen "de demostración" con un kernel arbitrario. La imagen se prepara por la ruta A de `USB_ONLY_DESIGN.md` §8 cuando el southbridge esté resuelto.
- **Límite:** el inventario prueba qué archivos hay y sus hashes, no que sean auténticos ni compatibles.

## Preguntas abiertas

Las primeras cinco son bloqueos generales de fase; las tres últimas (Q-006 a Q-008) surgen de la auditoría de código de esta sesión y son más específicas.

- **Q-001:** ¿modelo CUH y firmware exactos de la consola objetivo? PARCIAL (2026-10-15): firmware 13.52 **observado**, familia Slim **inferida** de una foto, capacidad 861,4 GB **observada**. **CUH y southbridge siguen desconocidos**: la selección de kernel NO está resuelta. Ver `docs/lab-logs/LAB-000-identificacion-consola.md` y `COMPATIBILITY_MATRIX.md` §7.
- **Q-002:** ¿qué combinación loader/kernel/initramfs/rootfs es compatible? BLOCKED hasta Q-001 y la auditoría.
- **Q-003:** ¿qué cambios internos realiza el flujo de arranque elegido? RESPUESTA PARCIAL: el procedimiento de la distribución sube kernel e initramfs por FTP a `/data/linux/boot/` (D-008: **no se acepta**); el código del loader no escribe archivos (D-017). Falta demostrar que el flujo USB-only completo no toca el disco interno en runtime.
- **Q-004:** ¿qué licencia aplica a cada componente/artefacto? Pendiente por componente — ver `docs/UPSTREAM_CODE_MAP.md` §1.3/§2.8 y la lista de dependencias no auditadas en `docs/EVIDENCE_SOURCES.md` §5.
- **Q-005:** ¿qué API de cómputo y backend LLM son realmente utilizables? Posterior a validación gráfica — ver `docs/GPU_AND_LLM_RESEARCH.md` §4.
- **Q-006:** CERRADA por D-008: la escritura en `/data/linux/boot/` no es una opción. La pregunta vigente pasa a ser si USB-only es demostrable (`USB_ONLY_DESIGN.md` §4).
- **Q-007:** ¿existe tolerancia a repetir el ciclo de jailbreak varias veces en la misma sesión de prueba? El propio upstream documenta que 2-3 intentos son normales (ver `docs/TROUBLESHOOTING.md` caso 2) — afecta cuánto tiempo de sesión planificar, no es una decisión técnica.
- **Q-008:** RESPUESTA PARCIAL (rama `chatgpt/research-audits`, integrada): la investigación bibliográfica de `GPU_AND_LLM_RESEARCH.md` §5 concluye que ROCm no tiene soporte oficial para Liverpool/PS4 en la matriz consultada y que Vulkan/RADV con `llama.cpp` es un candidato experimental, todo `INFERENCE` sin prueba en la consola. Pregunta original: ¿vale la pena, antes de tener la consola, investigar específicamente soporte ROCm/Vulkan-compute para GCN1-GCN4 (vacío identificado en `docs/GPU_AND_LLM_RESEARCH.md` §5) para no descubrir un descarte evitable recién en la Fase de compute/LLM? Es una pregunta de priorización de tiempo, no de autorización.
