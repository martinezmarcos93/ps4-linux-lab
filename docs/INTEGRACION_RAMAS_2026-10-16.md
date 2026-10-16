# Integración de ramas y estado de consolidación — 2026-10-16

Repositorio: `martinezmarcos93/ps4-linux-lab`
Objetivo declarado: consolidar el trabajo en `main` y dejar el repositorio listo para retirar ramas temporales, sin perder hallazgos ni introducir regresiones.

## Estado real

La consolidación se ejecutó de forma mixta: merges squash cuando GitHub los aceptó, y portado manual de archivos únicos cuando las ramas divergentes tenían conflictos. **No se debe interpretar “consolidado” como “todas las ramas eliminadas” ni como validación funcional en PS4.**

### Merges completados

- PR #2 — correcciones de enlaces de documentación/CI; squash merge en `main`.
- PR #3 — preflight USB estricto, endurecimiento de imagen/FAT32, auditoría de procedencia/licencias y revisión parcial initramfs/rootfs; squash merge en `main`. La propuesta de parche C sigue sin aplicar/compilar.
- PR #8 — roadmap de herramientas/tests; squash merge.
- PR #9 — auditoría upstream y metadatos de releases; squash merge.
- PR #10 — análisis de compatibilidad y evidencia de southbridge; squash merge.

### Portado manual a main desde las ramas de auditoría

Se añadieron los siguientes artefactos desde `opencode/v0-kernel-inspect-hardening`:
- `tools/kernel_inspect.py` y `tests/test_kernel_inspect.py`
- `tools/inventariar_artefactos.py` y `tests/test_inventariar_artefactos.py`
- `manifests/inventario-local-2026-10-16.json`
- `docs/REVIEW_KERNEL_INSPECT_ZSTD_2026-10-16.md`
- `docs/PLAN_VALIDACION_BAIKAL.md`
- `docs/AUDITORIA_CADENA_BAIKAL.md`
- `docs/KERNEL_SELECTION.md`
- `docs/CROSS_DOC_AUDIT_2026-10-16.md`
- `docs/RECOVERY_PLAN.md`
- `docs/PROGRESS_2026-10-16.md`
- `docs/BRANCH_REVIEW_CLAUDE_2026-10-16.md`
- `docs/AUTHORIZATION_KERNEL_IDENTIFICATION_2026-10-16.md`
- `docs/OPENCODE_REVIEW_2026-10-16.md`
- `docs/lab-logs/LAB-001-southbridge.md`

Se integró también la licencia MIT para el código propio (`LICENSE`), el roadmap de gobernanza documental y la política de licencias. Se añadieron las decisiones D-022 (autorización de publicación), D-023 (licencia MIT para código propio) y D-025 (arquitectura candidata USB-only, diseño aceptado, implementación pendiente).

**No se copió la versión de `docs/lab-logs/LAB-000-identificacion-consola.md` que contiene identificadores de red privados.** El repositorio es público; ese contenido requiere sanitización antes de cualquier integración.

## PRs que no se pudieron fusionar tal como estaban

### PR #4 — inspección de kernel y auditoría Baikal
URL: https://github.com/martinezmarcos93/ps4-linux-lab/pull/4

GitHub reportó conflictos. Los archivos únicos de inspección estática y auditoría se portaron manualmente. No se fusionó la rama completa porque modifica también `tools/build_usb_image.py`, `tests/test_build_usb_image.py`, documentación compartida y un log que contiene identificadores de red privados. Se requiere revisión de las diferencias restantes y un nuevo CI sobre el HEAD integrado.

### PR #5 — endurecimiento del pipeline de imagen de OpenCode
URL: https://github.com/martinezmarcos93/ps4-linux-lab/pull/5

GitHub reportó conflictos. No se debe fusionar tal cual: su implementación termina publicando con `os.replace(parcial_img, destino)`; aunque valida que el destino no exista durante la planificación, una creación concurrente del destino después del preflight puede ser sobrescrita. La implementación integrada en WS05 tiene una publicación final no-clobber con `os.link` y se conserva como opción más segura. Se pueden portar tests/documentación no conflictivos tras reconciliar el diseño, pero no reemplazar el código seguro por la variante con carrera TOCTOU.

### PR #6 — roadmap de auditoría/recuperación
URL: https://github.com/martinezmarcos93/ps4-linux-lab/pull/6

GitHub reportó conflictos en archivos compartidos (README, decisiones, matriz, roadmap y logs). Los documentos únicos se portaron manualmente. Los cambios restantes requieren fusión de contenido, no sobrescritura ciega de archivos más recientes.

### PR #7 — gobernanza documental
URL: https://github.com/martinezmarcos93/ps4-linux-lab/pull/7

GitHub reportó conflictos en archivos compartidos. Se integraron manualmente `LICENSE`, `docs/workstreams/01-docs-governance/ROADMAP.md`, la política de licencias y la decisión D-023. Las correcciones de enlaces de PR #2 ya están integradas; no se sobrescribieron por una versión antigua de la rama.

## CI después de la integración

Los commits directos a `main` dispararon GitHub Actions. Algunas ejecuciones iniciales fallaron en `tests.test_check_docs.TestDocumentacionReal.test_la_documentacion_del_repositorio_es_coherente` porque los documentos importados referían D-022, D-023 y D-025 sin entradas en el registro de decisiones. D-023, D-022 y D-025 se añadieron a `docs/DECISION_LOG.md`; el workflow del commit posterior debe revisarse antes de declarar CI verde.

Último HEAD conocido al redactar este documento: consultar el commit `main` y la ejecución más reciente de Actions. No asumir que una ejecución en curso terminó con éxito.

## Ramas

El listado previo a la integración contenía ramas `chatgpt/*`, `claude/*`, `opencode/*` y `workstream/*`. Algunos commits fueron squash-mergeados, por lo que sus ramas no necesariamente quedan como ancestros directos de `main`. La integración de archivos no convierte automáticamente cada rama divergente en una rama fusionada.

La interfaz de GitHub disponible en esta sesión permite leer refs y moverlas, pero no expone una operación segura de borrado de ramas. Por eso **no se borraron ramas**. No se debe mover una rama a `main` con force para simular un borrado: eso destruye la referencia de trabajo sin garantizar que todos los cambios estén integrados. Una vez revisados los PRs restantes, borrar ramas ya integradas desde GitHub UI o con `git push origin --delete <rama>`.

## Puertas de seguridad que siguen vigentes

- No ejecutar payloads.
- No escribir imágenes en USB físico.
- No escribir ni modificar el almacenamiento interno de la PS4.
- No ejecutar instaladores que particionen/formateen dispositivos.
- No afirmar compatibilidad de la combinación loader/kernel/initramfs/rootfs sin evidencia.
- **NO-GO para prueba física** hasta fijar loader v25.1, aplicar y compilar el parche USB-only, auditar initramfs/rootfs, verificar procedencia/licencias y obtener autorización específica para la prueba.

## Próxima secuencia

1. Confirmar resultado del CI del HEAD actual y corregir cualquier fallo.
2. Revisar los cambios restantes de PR #4–#7; no fusionar la versión de `build_usb_image.py` que reintroduce la carrera de sobrescritura.
3. Actualizar el inventario y matriz con loader v25.1 y kernel Baikal 7.0.8 como candidato (no validado); descartar el kernel feeRnt 6.15.4 Aeolia/Belize para Baikal.
4. Obtener las URLs completas de los dos enlaces MediaFire truncados; no inferir artefactos.
5. Reconciliar diferencias restantes, verificar CI, y entonces retirar ramas ya integradas.
