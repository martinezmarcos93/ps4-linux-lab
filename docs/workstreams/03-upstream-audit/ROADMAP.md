# Workstream 03 — Auditoría upstream y licencias

**Responsable principal:** ChatGPT  
**Verificación de reproducibilidad en el checkout:** Claude Code  
**Prioridad:** 3 de 5  
**Objetivo:** cerrar la trazabilidad del código y artefactos de terceros necesarios para una evaluación responsable.

## Alcance

Repositorios upstream, commits fijados, dependencias transitivas, kernel, loader, initramfs/rootfs, paquetes gráficos, payloads y herramientas. La auditoría no autoriza por sí sola ejecución o redistribución.

## Tareas hasta el 100 %

- [ ] U01 — Confirmar la lista completa de dependencias y fuentes candidatas desde ARTIFACT_INVENTORY y EVIDENCE_SOURCES.
- [ ] U02 — Fijar para cada fuente URL canónica, propietario, commit/tag/release, fecha de consulta y hash.
- [ ] U03 — Separar repositorios inspeccionados de los que solo aparecen mencionados por terceros.
- [ ] U04 — Inspeccionar código y scripts que afectan kernel, bootloader, initramfs/rootfs, rutas de almacenamiento y escritura.
- [ ] U05 — Identificar licencia exacta por componente y archivos de avisos; registrar componentes sin licencia como no autorizados para redistribución.
- [ ] U06 — Revisar procedencia de artefactos binarios y que los hashes esperados procedan de una fuente confiable.
- [ ] U07 — Detectar diferencias entre release oficial, forks, commits no etiquetados y artefactos que declaran versiones ambiguas.
- [ ] U08 — Registrar vulnerabilidades, riesgos de cadena de suministro y límites de inspección, sin exagerar conclusiones.
- [ ] U09 — Actualizar ARTIFACT_INVENTORY, EVIDENCE_SOURCES, LICENSE_POLICY y UPSTREAM_AUDIT con referencias exactas.
- [ ] U10 — Claude reproduce localmente los comandos/hash checks no destructivos citados y reporta discrepancias.
- [ ] U11 — Revisar que el README no prometa redistribución, compatibilidad o soporte que no esté probado.
- [ ] U12 — Emitir informe de cierre con dependencias auditadas, no auditadas, licencias inciertas y recomendación por componente.

## Criterios de aceptación

- Cada dependencia crítica tiene estado de procedencia, versión, hash, licencia y decisión de uso.
- Toda afirmación se clasifica como observación de código, afirmación upstream, inferencia o prueba propia.
- Los componentes sin licencia clara quedan bloqueados para redistribución.
- No se ejecutan payloads ni se redistribuyen binarios como parte de la auditoría.
- Los cambios de esta rama se pueden revisar con fuentes y diffs verificables.

## Restricciones

No editar `main` directamente. ChatGPT lidera el análisis de fuentes y documentación; Claude verifica en el checkout. No confundir lectura estática con prueba funcional.