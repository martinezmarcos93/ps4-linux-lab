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

## D-008 — Ubicación del kernel/initramfs: priorizar USB-only
- **Fecha:** 2026-10-15 (resuelta como dirección de diseño; ejecución aún bloqueada por validación técnica).
- **Estado:** RESUELTA PARA PLANIFICACIÓN; NO AUTORIZA EJECUCIÓN EN LA CONSOLA.
- **Contexto (HECHO DOCUMENTADO + OBSERVACIÓN DE CÓDIGO):** el procedimiento oficial de `X-F1REBALL-X/PS4-Linux` (README) instruye subir por FTP el `bzImage` y `initramfs.cpio.gz` a `/data/linux/boot/` en el almacenamiento interno de la consola; el USB solo lleva el rootfs. El código del loader (`main-aio.c`, ver `docs/UPSTREAM_CODE_MAP.md` §1.3 y `docs/BOOT_FLOW.md` Fase 2) sí soporta leer ambos archivos desde el USB con prioridad sobre el almacenamiento interno — un flujo 100% externo es técnicamente posible pero no es el que documenta ni prueba la distribución elegida.
- **Opciones:**
  - **A.** Escribir en `/data/linux/boot/` por FTP. No se elige como ruta predeterminada: contradice el objetivo de preservar el almacenamiento interno y amplía el impacto de un error.
  - **B.** Investigar y adaptar el flujo USB-only, colocando el kernel correcto en la partición de arranque del medio externo. **Seleccionada como dirección de diseño**, pero aún no demostrada en hardware y sin asumir que funciona porque el loader lea desde USB.
- **Motivo:** preservar el almacenamiento interno y mantener el experimento reversible. Si la auditoría o una prueba virtual demuestra que USB-only no es viable, se documentará el bloqueo y se presentará la alternativa; no se cambiará a escritura interna automáticamente.
- **Condiciones antes de una prueba real:** identificación del modelo/southbridge cuando sea posible; binarios con procedencia revisada; script y hashes verificados; test sobre imagen virtual; aislamiento de internet/PSN; y confirmación específica antes de ejecutar el exploit/payload.

## D-009 — Numeración de versión del kernel "7.1.7"/"7.0.8": aclarar antes de citarla como versión de Linux
- **Fecha:** 2026-10-15.
- **Estado:** PENDIENTE DE VERIFICACIÓN, no bloqueante para avanzar el roadmap, pero sí para cualquier documento que cite una versión de kernel Linux real.
- **Contexto:** ver discrepancia D-B en `docs/EVIDENCE_SOURCES.md` §4. El archivo de configuración de la distribución se autodenomina "Linux/x86_64 7.1.7"; un reporte de comunidad (issue #10 del loader) describe "Kernel 5.4.247". Ambos no pueden ser literalmente la misma cifra de versión de Linux mainline.
- **Hipótesis de trabajo:** "7.1.7"/"7.0.8" son la numeración propia del fork "Strawberry" (rmuxnet), no la versión de Linux. No confirmada — el repositorio de ese kernel no fue identificado ni auditado en esta sesión.
- **Acción pendiente:** localizar el repositorio del kernel "Strawberry" (o la fuente que rmuxnet use) y confirmar la versión real de Linux mainline sobre la que está basado, antes de redactar cualquier documento que dependa de esa versión.

## D-014 — Delegación de decisiones técnicas en Claude
- **Fecha:** 2026-10-15. **Estado:** ACEPTADA.
- **Decisión:** Marcos delegó en Claude las decisiones técnicas intermedias ("las demás decisiones te las dejo a vos") para poder avanzar. **No** delega: ejecutar el exploit sobre la consola, escribir en su almacenamiento interno, ni el push de código que no sea documentación. Esos pasos requieren un "sí" puntual de Marcos en el momento.

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

## Preguntas abiertas

Las primeras cinco son bloqueos generales de fase; las tres últimas (Q-006 a Q-008) surgen de la auditoría de código de esta sesión y son más específicas.

- **Q-001:** ¿modelo CUH y firmware exactos de la consola objetivo? PARCIAL (2026-10-15): firmware 13.52 confirmado, familia Slim inferida, capacidad 861,4 GB. **CUH y southbridge siguen desconocidos** (sin etiqueta en la base). Ver `docs/lab-logs/LAB-000-identificacion-consola.md`.
- **Q-002:** ¿qué combinación loader/kernel/initramfs/rootfs es compatible? BLOCKED hasta Q-001 y la auditoría.
- **Q-003:** ¿qué cambios internos realiza el flujo de arranque elegido? Ver D-008 — ya tiene respuesta parcial (sí los hay, según el procedimiento oficial), falta la decisión de aceptarlos o evitarlos.
- **Q-004:** ¿qué licencia aplica a cada componente/artefacto? Pendiente por componente — ver `docs/UPSTREAM_CODE_MAP.md` §1.3/§2.8 y la lista de dependencias no auditadas en `docs/EVIDENCE_SOURCES.md` §5.
- **Q-005:** ¿qué API de cómputo y backend LLM son realmente utilizables? Posterior a validación gráfica — ver `docs/GPU_AND_LLM_RESEARCH.md` §4.
- **Q-006:** RESUELTA PARA PLANIFICACIÓN por D-008: no escribir en `/data/linux/boot/` como opción predeterminada; investigar primero USB-only. Si la vía USB-only resulta inviable, detenerse y documentar alternativas en lugar de cambiar automáticamente a escritura interna.
- **Q-007:** ¿existe tolerancia a repetir el ciclo de jailbreak varias veces en la misma sesión de prueba? El propio upstream documenta que 2-3 intentos son normales (ver `docs/TROUBLESHOOTING.md` caso 2) — afecta cuánto tiempo de sesión planificar, no es una decisión técnica.
- **Q-008:** ¿vale la pena, antes de tener la consola, investigar específicamente soporte ROCm/Vulkan-compute para GCN1-GCN4 (vacío identificado en `docs/GPU_AND_LLM_RESEARCH.md` §5) para no descubrir un descarte evitable recién en la Fase de compute/LLM? Es una pregunta de priorización de tiempo, no de autorización.

## D-010 — No ejecutar el payload 13.52 sin revisión estática adicional
- **Fecha:** 2026-10-15.
- **Estado:** ACEPTADA como gate de seguridad.
- **Decisión:** no ejecutar `goldhen.bin` en la consola mientras siga siendo un blob nativo sin fuente y sin desensamblado revisado. El análisis del JavaScript no valida el payload nativo.
- **Siguiente acción:** análisis offline con Rizin/objdump si ya están disponibles; documentar offsets, regiones no decodificables, llamadas/saltos relevantes y límites. No ejecutar el binario ni cargarlo en la PS4 durante esta etapa.
- **Revisión:** después de un informe reproducible de análisis estático y de evaluar la procedencia/hash del artefacto. La decisión de ejecutar en hardware seguirá siendo separada.
- **Actualización 2026-10-15:** el informe reproducible existe (`EXPLOIT_AUDIT_13.52.md`, segunda pasada): el cuerpo se descomprime (zlib), se identifica como GoldHEN v2.4b18.12, sin hosts ajenos a GoldHEN/GitHub/Google, con ~80 % de cadenas en común con el release oficial 2.4b18. **Límites:** sin revisión del código máquina del cuerpo, sin referencia oficial exacta y sin compilación reproducible. El gate pasa a **"informe completado, decisión de ejecución pendiente de Marcos"**; no se ejecuta nada hasta ese "sí".

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