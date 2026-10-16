# Diagnóstico del CI

**Última revisión documental:** 2026-10-16  
**Estado:** diagnóstico histórico pendiente de nueva ejecución verificable.

## Observación histórica (2026-10-15)

- El workflow `.github/workflows/tests.yml` (`Host-side tests`) no iniciaba jobs: `runner_id=0`, nombre de runner vacío y cero pasos.
- La anotación del check-run reportó que el job no arrancaba debido a pagos recientes fallidos o al límite de gasto de la cuenta.
- En ese momento, el repositorio se describía como privado. **Ese dato quedó obsoleto: el repositorio ahora es público.**
- El workflow usa `ubuntu-latest`; la advertencia de migración de imagen de runner observada en ese momento no explicaba el fallo de facturación.

## Conclusión y límites

- **Hecho histórico:** el job no llegó a ejecutar tests en la observación del 15 de octubre.
- **Inferencia histórica:** la causa probable era la facturación/límite de Actions, no el código del workflow.
- **Estado actual:** no se ha verificado en esta revisión que el problema siga presente o esté resuelto tras hacer público el repositorio. No reutilizar la observación histórica como estado actual.
- La publicación del repositorio cambia una de las condiciones que se consideraban alternativas, pero no demuestra por sí sola que un nuevo workflow haya corrido con éxito.

## Próximas comprobaciones

1. Consultar el estado más reciente de GitHub Actions para `main` y para una rama de trabajo.
2. Confirmar si el job obtuvo runner y ejecutó pasos.
3. Si el job arranca, registrar el resultado real de tests y documentación.
4. Si no arranca, conservar el mensaje de error actual y clasificarlo como bloqueo externo o problema de workflow según la evidencia.
5. No publicar un badge verde ni marcar CI como resuelto hasta ver una ejecución satisfactoria.

## Mitigación local

`scripts/check.sh` ejecuta `compileall`, `unittest discover -v` y `tools/check_docs.py`. Ejecutarlo localmente permite validar el estado host-side, pero no sustituye la comprobación del runner remoto. Registrar los comandos y resultados exactos; no afirmar ejecución local si solo se inspeccionó el script.
