# Diagnóstico del CI

**Última actualización:** 2026-10-16  
**Workflow:** `.github/workflows/tests.yml` (Host-side tests)

## Estado actual verificado

- El repositorio se reporta actualmente como **público** en los metadatos de GitHub. La afirmación histórica de que era privado ya no describe el estado observado.
- GitHub Actions está iniciando jobs y ejecutando pruebas. Por lo tanto, el bloqueo de facturación descrito abajo no es la explicación de los runs más recientes.
- El run 31, sobre `main` en el commit `9e9527d16329d20c041bce97927ecff3869aa9e7`, ejecutó 262 tests y falló en `tests.test_check_docs.TestDocumentacionReal.test_la_documentacion_del_repositorio_es_coherente`.
- El fallo encontró cinco enlaces relativos rotos en `docs/WORKSTREAMS.md`: los roadmaps están en ramas de trabajo, pero no existen en el árbol de `main`.
- La corrección está propuesta en el PR #2: https://github.com/martinezmarcos93/ps4-linux-lab/pull/2. La ejecución de CI de ese PR todavía debe concluir antes de confirmar que la corrección resuelve el fallo.
- El fallo observado es de consistencia documental; no debe atribuirse al loader ni a la compatibilidad de hardware.

## Diagnóstico histórico del 2026-10-15

En los runs inspeccionados el 15 de octubre, el workflow fallaba antes de iniciar el runner: `runner_id=0`, nombre de runner vacío y cero pasos. La anotación del check-run indicaba que el job no había arrancado por pagos recientes fallidos o por un límite de gasto que debía aumentarse.

En aquel momento:
- Actions aparecía habilitado (`enabled: true`, `allowed_actions: all`).
- La inferencia razonable era un problema de facturación o del límite de gasto, no un fallo del código.
- El estado real de pagos/límite no pudo verificarse mediante la API disponible.

Ese diagnóstico es histórico. No debe usarse para explicar los runs actuales, que sí tienen runner y pasos ejecutados.

## Comprobación local

`scripts/check.sh` ejecuta `compileall`, `unittest discover -v` y `tools/check_docs.py`. Los resultados deben registrarse con el comando exacto y la salida real del entorno en que se ejecuten.

No declarar CI resuelto hasta que un run posterior confirme el resultado. Un test aprobado tampoco demuestra que Linux arranque en la PS4.

## Nota de consolidación (merge a main, 2026-10-16)

`workstream/01-docs-governance` llevaba un diagnóstico histórico anterior al run 31 y al PR #2 (no conocía esos eventos). Se conserva la versión de arriba porque está mejor evidenciada; el checklist de próximas comprobaciones de esa rama sigue vigente como guía general:

1. Consultar el estado más reciente de GitHub Actions para `main` y para una rama de trabajo.
2. Confirmar si el job obtuvo runner y ejecutó pasos.
3. Registrar el resultado real de tests y documentación, no solo si el job arrancó.
4. No publicar un badge verde ni marcar CI como resuelto hasta ver una ejecución satisfactoria posterior al fix del PR #2.
