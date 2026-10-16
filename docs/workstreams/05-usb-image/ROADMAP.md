# Workstream 05 — Imagen y cadena USB-only

**Responsable principal:** Claude Code  
**Revisión independiente de arquitectura y seguridad:** ChatGPT  
**Prioridad:** 5 de 5 — mayor complejidad de las cinco categorías  
**Objetivo:** preparar y auditar una imagen candidata y demostrar mediante evidencia suficiente que el diseño propuesto no depende de escribir en el almacenamiento interno. No incluye aún el primer arranque físico.

## Dependencias previas

Depende de los workstreams 02 (tests), 03 (procedencia/licencias) y 04 (compatibilidad). Puede avanzar en revisión estática y dry-run, pero no seleccionar un artefacto final ni declarar compatibilidad si las dependencias están abiertas.

## Tareas hasta el 100 %

- [ ] I01 — Mapear el flujo completo desde el artefacto de entrada hasta el layout final de la imagen.
- [x] I02 — Enumerar las rutas de lectura del loader y referencias al almacenamiento interno. Evidencia: `USB_ONLY_CHAIN_REVIEW_2026-10-16.md`; análisis de runtime de initramfs/rootfs sigue pendiente.
- [x] I03 — Revisar fallback/mezcla de orígenes. El upstream mezcla por archivo; el parche USB-only evita rutas internas, pero se detectó un manejo incompleto de errores en archivos opcionales. Evidencia: `USB_ONLY_CHAIN_REVIEW_2026-10-16.md` y `PATCH_REVIEW_2026-10-16.md`.
- [x] I04 — Definir invariantes USB-only y pruebas negativas. Evidencia: `USB_ONLY_CHAIN_REVIEW_2026-10-16.md`.
- [ ] I05 — Revisar que los scripts de construcción operen solo sobre archivos/directorios de salida explícitos y no detecten ni escriban dispositivos automáticamente.
- [ ] I06 — Ejecutar preflight/dry-run con fixtures sintéticos; no usar dispositivos físicos.
- [ ] I07 — Verificar formato, estructura, tamaño, hashes y reproducibilidad de la imagen candidata en PC.
- [ ] I08 — Incorporar pruebas de seguridad para paths, symlinks, nombres de dispositivo ambiguos, sobrescritura de salidas y fallos parciales.
- [ ] I09 — Confirmar que el manifiesto referencia fuentes confiables y artefactos permitidos por licencia.
- [ ] I10 — Documentar recuperación, condiciones de aborto y criterios de aprobación previos a una prueba física.
- [ ] I11 — ChatGPT revisa de forma independiente el diseño, el diff, las rutas de escritura y los claims de seguridad. Revisión inicial del parche publicada en `PATCH_REVIEW_2026-10-16.md`; queda pendiente revisar la siguiente iteración tras resolver R-USB-001.
- [ ] I12 — Emitir informe final con propiedades demostradas, no demostradas, limitaciones y decisión go/no-go para una futura prueba física.
- [ ] I13 — Resolver R-USB-001: manejar errores parciales de lectura de `bootargs.txt`/`vram.txt` y probar archivos opcionales ausentes, vacíos, truncados o no regulares; o excluirlos de forma explícita del manifiesto candidato.

## Criterios de aceptación

- El pipeline se ejecuta en modo host-side/dry-run sin acceso de escritura a dispositivos de bloque.
- Cada ruta de escritura está identificada y acotada a destinos de archivo explícitos.
- Los invariantes USB-only tienen evidencia de código y tests negativos; no se declara aislamiento absoluto basándose solo en intención de diseño.
- Artefactos y licencias cumplen las decisiones del workstream 03.
- La selección de kernel y loader respeta la matriz del workstream 04.
- El resultado puede ser “no-go” si hay rutas ambiguas o riesgos residuales.

## Restricciones

No editar `main` directamente. No escribir USB físico, no ejecutar payloads y no arrancar la consola. La autorización para prueba de hardware es un hito independiente y queda fuera de esta rama.