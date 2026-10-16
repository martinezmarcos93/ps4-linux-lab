# Workstream 05 — Imagen y cadena USB-only

**Responsable principal:** Claude Code  
**Revisión independiente de arquitectura y seguridad:** ChatGPT  
**Prioridad:** 5 de 5 — mayor complejidad de las cinco categorías  
**Objetivo:** preparar y auditar una imagen candidata y demostrar mediante evidencia suficiente que el diseño propuesto no depende de escribir en el almacenamiento interno. No incluye aún el primer arranque físico.

## Dependencias previas

Depende de los workstreams 02 (tests), 03 (procedencia/licencias) y 04 (compatibilidad). Puede avanzar en revisión estática y dry-run, pero no seleccionar un artefacto final ni declarar compatibilidad si las dependencias están abiertas.

## Tareas hasta el 100 %

- [ ] I01 — Mapear el flujo completo desde el artefacto de entrada hasta el layout final de la imagen.
- [ ] I02 — Enumerar cada ruta de lectura/escritura del loader, initramfs y scripts de preparación; identificar referencias al almacenamiento interno.
- [ ] I03 — Revisar el flujo de error, fallback y recuperación para evitar que mezcle artefactos USB e internos.
- [ ] I04 — Definir invariantes USB-only y pruebas negativas para cada invariante.
- [ ] I05 — Revisar que los scripts de construcción operen solo sobre archivos/directorios de salida explícitos y no detecten ni escriban dispositivos automáticamente.
- [ ] I06 — Ejecutar preflight/dry-run con fixtures sintéticos; no usar dispositivos físicos.
- [ ] I07 — Verificar formato, estructura, tamaño, hashes y reproducibilidad de la imagen candidata en PC.
- [ ] I08 — Incorporar pruebas de seguridad para paths, symlinks, nombres de dispositivo ambiguos, sobrescritura de salidas y fallos parciales.
- [ ] I09 — Confirmar que el manifiesto referencia fuentes confiables y artefactos permitidos por licencia.
- [ ] I10 — Documentar recuperación, condiciones de aborto y criterios de aprobación previos a una prueba física.
- [ ] I11 — ChatGPT revisa de forma independiente el diseño, el diff, las rutas de escritura y los claims de seguridad.
- [ ] I12 — Emitir informe final con propiedades demostradas, no demostradas, limitaciones y decisión go/no-go para una futura prueba física.

## Criterios de aceptación

- El pipeline se ejecuta en modo host-side/dry-run sin acceso de escritura a dispositivos de bloque.
- Cada ruta de escritura está identificada y acotada a destinos de archivo explícitos.
- Los invariantes USB-only tienen evidencia de código y tests negativos; no se declara aislamiento absoluto basándose solo en intención de diseño.
- Artefactos y licencias cumplen las decisiones del workstream 03.
- La selección de kernel y loader respeta la matriz del workstream 04.
- El resultado puede ser “no-go” si hay rutas ambiguas o riesgos residuales.

## Restricciones

No editar `main` directamente. No escribir USB físico, no ejecutar payloads y no arrancar la consola. La autorización para prueba de hardware es un hito independiente y queda fuera de esta rama.