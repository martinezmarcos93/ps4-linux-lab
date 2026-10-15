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
- **Decisión:** usar martinezmarcos93/ps4-linux-lab como repositorio privado de trabajo.
- **Evidencia:** metadata de GitHub consultada durante la sesión; rama predeterminada main.
- **Nota:** se verificaron permisos de administración/escritura del propietario.

## D-006 — Escritura documental directa a main
- **Fecha:** 2026-10-15
- **Estado:** ACEPTADA para la fase documental inicial.
- **Decisión:** trabajar en main por autorización explícita del propietario.
- **Límite:** no autoriza force-push, borrados masivos, acciones destructivas sobre hardware ni cambios irreversibles en la consola.

## D-007 — No destructivo primero
- **Fecha:** 2026-10-15
- **Estado:** ACEPTADA.
- **Decisión:** comenzar por doctor/inspect/verify/diagnose y tests sobre archivos de prueba.

## Preguntas abiertas
- Q-001: ¿modelo CUH y firmware exactos de la consola objetivo? BLOCKED.
- Q-002: ¿qué combinación loader/kernel/initramfs/rootfs es compatible? BLOCKED hasta Q-001 y auditoría.
- Q-003: ¿qué cambios internos realiza el flujo de arranque elegido? Investigar antes de usar.
- Q-004: ¿qué licencia aplica a cada componente/artefacto? Pendiente por componente.
- Q-005: ¿qué API de cómputo y backend LLM son realmente utilizables? Posterior a validación gráfica.
