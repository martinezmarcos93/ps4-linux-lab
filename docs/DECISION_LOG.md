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

## D-008 — Ubicación del kernel/initramfs: ¿almacenamiento interno (FTP) o USB-only? **[BLOQUEANTE, PENDIENTE]**
- **Fecha:** 2026-10-15 (abierta por la auditoría de código de upstream de esta sesión).
- **Estado:** PENDIENTE — requiere decisión explícita de Marcos antes de ejecutar la Fase 3/5 del roadmap.
- **Contexto (HECHO DOCUMENTADO + OBSERVACIÓN DE CÓDIGO):** el procedimiento oficial de `X-F1REBALL-X/PS4-Linux` (README) instruye subir por FTP el `bzImage` y `initramfs.cpio.gz` a `/data/linux/boot/` en el almacenamiento interno de la consola; el USB solo lleva el rootfs. El código del loader (`main-aio.c`, ver `docs/UPSTREAM_CODE_MAP.md` §1.3 y `docs/BOOT_FLOW.md` Fase 2) sí soporta leer ambos archivos desde el USB con prioridad sobre el almacenamiento interno — un flujo 100% externo es técnicamente posible pero no es el que documenta ni prueba la distribución elegida.
- **Opciones:**
  - **A.** Seguir el procedimiento oficial (escribir en `/data/linux/boot/`). Modificación acotada y reversible (borrar una carpeta), pero contradice literalmente el Hito A del `PROJECT_CHARTER.md` ("ninguna modificación del disco interno") y el principio "el almacenamiento interno se considera solo lectura" de `ARCHITECTURE.md`.
  - **B.** Adaptar `tools/build-img.sh` para colocar el `bzImage` correcto en la partición de arranque del USB (hoy el script lo evita deliberadamente, renombrándolo, para permitir compartir un USB entre consolas de southbridge distinto). Mantiene el principio original pero no tiene ningún reporte de terceros que la haya probado así.
- **Motivo de que esté bloqueando:** no se puede ejecutar TP-05/TP-06 de `docs/TEST_PLAN.md` sin esta decisión. No es una pregunta retórica — cambia qué script se ejecuta y qué se le pide a Marcos que autorice.
- **Revisión:** se resuelve antes de la Fase 1 real sobre hardware, aunque puede decidirse antes de tener la consola identificada.

## D-009 — Numeración de versión del kernel "7.1.7"/"7.0.8": aclarar antes de citarla como versión de Linux
- **Fecha:** 2026-10-15.
- **Estado:** PENDIENTE DE VERIFICACIÓN, no bloqueante para avanzar el roadmap, pero sí para cualquier documento que cite una versión de kernel Linux real.
- **Contexto:** ver discrepancia D-B en `docs/EVIDENCE_SOURCES.md` §4. El archivo de configuración de la distribución se autodenomina "Linux/x86_64 7.1.7"; un reporte de comunidad (issue #10 del loader) describe "Kernel 5.4.247". Ambos no pueden ser literalmente la misma cifra de versión de Linux mainline.
- **Hipótesis de trabajo:** "7.1.7"/"7.0.8" son la numeración propia del fork "Strawberry" (rmuxnet), no la versión de Linux. No confirmada — el repositorio de ese kernel no fue identificado ni auditado en esta sesión.
- **Acción pendiente:** localizar el repositorio del kernel "Strawberry" (o la fuente que rmuxnet use) y confirmar la versión real de Linux mainline sobre la que está basado, antes de redactar cualquier documento que dependa de esa versión.

## D-010 — Delegación de decisiones técnicas
- **Fecha:** 2026-10-15
- **Estado:** ACEPTADA.
- **Decisión:** Marcos delegó en Claude las decisiones técnicas intermedias ("las demás decisiones te las dejo a vos") para poder avanzar. **No** delega: ejecutar el exploit sobre la consola, escribir en su almacenamiento interno, ni el push de código que no sea documentación. Esos pasos requieren un "sí" puntual de Marcos en el momento.

## D-008 — RESUELTA (2026-10-15) por delegación D-010: Opción B primero, A solo como respaldo
- **Decisión:** el primer intento usa flujo **solo-USB** (Opción B): sin escribir en `/data/linux/boot/`. Respeta el Hito A de la Carta y el principio de almacenamiento interno solo lectura. Se apoya en que el loader lee `bzImage`/`initramfs` desde el USB con prioridad (CÓDIGO, `UPSTREAM_CODE_MAP.md` §1.3).
- **Contra:** ningún reporte de terceros lo probó así; puede fallar por razones del procedimiento, no del hardware. Eso se trata como hallazgo, no como bloqueo.
- **Respaldo (Opción A):** solo si B falla de forma reproducible, y **requiere confirmación puntual de Marcos** antes de escribir (modificación acotada: una carpeta, reversible borrándola). Resuelve Q-006 de forma condicional.

## D-011 — Aceptar el payload nativo no auditable, con mitigaciones y un "go" final
- **Fecha:** 2026-10-15. **Estado:** ACEPTADA CON CONDICIONES.
- **Contexto:** `goldhen.bin` está empaquetado (>90 % entropía ≈ 8), no es auditable estáticamente (`EXPLOIT_AUDIT_13.52.md`). No hay otra vía para 13.52. Un jailbreak por navegador es **no persistente** (un reinicio limpia el estado en RAM) y no toca el almacenamiento por sí mismo.
- **Decisión:** continuar con el plan, pero ejecutar solo si: (1) los artefactos pasan `ps4lab verify` contra el manifiesto fijado; (2) se sirven desde la PC en la LAN, sin internet; (3) PSN cortado (D-012); (4) sin sesión de PSN iniciada; (5) Marcos da el "go" explícito justo antes del primer intento.
- **Riesgo residual aceptado:** el binario podría hacer cosas no observables mientras corre; mitigado por no persistencia, falta de internet y ausencia de cuenta.

## D-012 — Corte de PSN por DNS manual + alojamiento local
- **Decisión:** en la PS4, DNS manual a una IP sin servicio (p. ej. `127.0.0.1`), más desactivar descargas automáticas de actualización. El exploit se sirve desde la PC con `tools/ps4lab.py serve`. Reversible, no toca el router. Cortar por MAC en el router queda como refuerzo opcional.

## D-013 — REA no se instala por ahora
- **Decisión:** no se ejecuta `npx rea-agents setup`. Si se decide analizar el stub de `goldhen.bin`, se instala solo un proveedor (Rizin/Ghidra) y REA pasaría antes por `dependency-auditor`. Ver `REA_EVALUATION.md`.

## Preguntas abiertas

Las primeras cinco son bloqueos generales de fase; las tres últimas (Q-006 a Q-008) surgen de la auditoría de código de esta sesión y son más específicas.

- **Q-001:** ¿modelo CUH y firmware exactos de la consola objetivo? PARCIAL (2026-10-15): firmware 13.52 confirmado, familia Slim inferida, capacidad 861,4 GB. **CUH y southbridge siguen desconocidos** (sin etiqueta en la base). Ver `docs/lab-logs/LAB-000-identificacion-consola.md`.
- **Q-002:** ¿qué combinación loader/kernel/initramfs/rootfs es compatible? BLOCKED hasta Q-001 y la auditoría.
- **Q-003:** ¿qué cambios internos realiza el flujo de arranque elegido? Ver D-008 — ya tiene respuesta parcial (sí los hay, según el procedimiento oficial), falta la decisión de aceptarlos o evitarlos.
- **Q-004:** ¿qué licencia aplica a cada componente/artefacto? Pendiente por componente — ver `docs/UPSTREAM_CODE_MAP.md` §1.3/§2.8 y la lista de dependencias no auditadas en `docs/EVIDENCE_SOURCES.md` §5.
- **Q-005:** ¿qué API de cómputo y backend LLM son realmente utilizables? Posterior a validación gráfica — ver `docs/GPU_AND_LLM_RESEARCH.md` §4.
- **Q-006 [RESUELTA condicionalmente por D-008]** (ex-pregunta 1 de esta sesión):** ¿se autoriza, en principio, la Opción A de D-008 (escritura acotada en `/data/linux/boot/`) si no hay otra forma documentada y probada de lograr un primer arranque exitoso? Sin esta respuesta, la Fase 3 no puede ejecutarse aunque todo lo demás esté listo.
- **Q-007:** ¿existe tolerancia a repetir el ciclo de jailbreak varias veces en la misma sesión de prueba? El propio upstream documenta que 2-3 intentos son normales (ver `docs/TROUBLESHOOTING.md` caso 2) — afecta cuánto tiempo de sesión planificar, no es una decisión técnica.
- **Q-008:** ¿vale la pena, antes de tener la consola, investigar específicamente soporte ROCm/Vulkan-compute para GCN1-GCN4 (vacío identificado en `docs/GPU_AND_LLM_RESEARCH.md` §5) para no descubrir un descarte evitable recién en la Fase de compute/LLM? Es una pregunta de priorización de tiempo, no de autorización.
