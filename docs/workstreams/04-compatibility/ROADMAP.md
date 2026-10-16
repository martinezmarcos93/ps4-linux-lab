# Workstream 04 — Identificación y compatibilidad

**Responsable principal:** ChatGPT  
**Verificación de datos locales y artefactos:** Claude Code  
**Prioridad:** 4 de 5  
**Objetivo:** producir una decisión de compatibilidad auditable para la consola objetivo y reducir incertidumbre antes de seleccionar una cadena de arranque.

## Baseline conocido

- Modelo reportado/registrado: PS4 Slim CUH-2115B.
- Firmware registrado: 13.52.
- Capacidad observada: 861,4 GB.
- Southbridge: desconocido.
- Arranque Linux propio: no verificado.
- USB-only: objetivo de diseño, no propiedad demostrada.

## Tareas hasta el 100 %

- [ ] C01 — Auditar el log de identificación y clasificar cada dato como confirmado, observado, inferido o desconocido.
- [ ] C02 — Determinar qué métodos no invasivos permiten identificar revisión de placa/southbridge y documentar riesgos y requisitos.
- [ ] C03 — Reunir fuentes primarias por modelo, firmware, southbridge, exploit/payload, loader y kernel; fijar versiones y fechas.
- [ ] C04 — Crear una matriz de compatibilidad cruzada, no una lista aislada de compatibilidad por firmware.
- [ ] C05 — Separar compatibilidad reportada por terceros, inferida por código y probada en esta consola.
- [ ] C06 — Revisar las condiciones de firmware y evitar recomendar actualizaciones o acciones irreversibles.
- [ ] C07 — Definir qué evidencia mínima permite elegir candidato de kernel/loader y qué evidencia lo descarta.
- [ ] C08 — Identificar bloqueos irresolubles por documentación pública y describir la siguiente observación necesaria.
- [ ] C09 — Actualizar COMPATIBILITY_MATRIX, LAB-000 y ROADMAP sin convertir hipótesis en hechos.
- [ ] C10 — Revisar independientemente las conclusiones de upstream audit y documentar discrepancias.
- [ ] C11 — Emitir una decisión técnica: candidato viable, no viable o indeterminado, con justificación por fila.
- [ ] C12 — Dejar el plan de laboratorio separado; este workstream no autoriza ejecución en hardware.

## Criterios de aceptación

- Cada fila crítica incluye fuente, versión/fecha, nivel de evidencia, limitaciones y estado.
- No se elige kernel por analogía con otro modelo sin evidencia.
- Si el southbridge no se puede determinar sin ejecutar un payload, queda explícitamente bloqueado y se especifica la razón.
- La salida final puede concluir “indeterminado”; no se fuerza un 100 % artificial cuando falta evidencia externa.
- No hay instrucciones de modificación destructiva de firmware o almacenamiento.

## Restricciones

No editar `main` directamente. ChatGPT lidera investigación y matriz; Claude valida los datos del checkout y la reproducibilidad de fuentes. No realizar pruebas físicas.