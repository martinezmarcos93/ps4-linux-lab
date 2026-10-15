# Diagnóstico del CI (2026-10-15)

## Hecho observado
- El workflow `.github/workflows/tests.yml` ("Host-side tests") falla en **todos** los runs de `main`, en 4-13 s, con `runner_id=0`, `runner_name=""` y **0 pasos**.
- La anotación del check-run (API `repos/.../check-runs/<job>/annotations`) dice textualmente: *"The job was not started because recent account payments have failed or your spending limit needs to be increased. Please check the 'Billing & plans' section in your settings"*.
- `actions/permissions`: Actions habilitado (`enabled: true`, `allowed_actions: all`). El repo es **privado**, y los repos privados consumen minutos de Actions facturables.
- Hay además un aviso informativo: `ubuntu-latest` migrará a Ubuntu 26 desde 2026-10-19 (no relacionado con el fallo).

## Conclusión (hecho + inferencia)
- **Hecho:** el job nunca arranca; no es un fallo del código ni de los tests. Los logs no existen (`BlobNotFound`) porque no hubo ejecución.
- **Inferencia razonable:** la causa es de facturación de la cuenta/límite de gasto de Actions, no del workflow.
- **No verificado:** el estado real de pagos/límite (el token de `gh` no tiene scope `user`, la API de billing devuelve 404/403).

## Qué falta y quién lo resuelve
Solo el titular puede revisar *GitHub → Settings → Billing & plans* (método de pago y *Spending limit* de Actions). Alternativas que no requieren eso: hacer el repo público (Actions es gratuito en repos públicos; **decisión de privacidad de Marcos, no tomada**) o usar un runner propio.

## Mitigación mientras tanto
- `scripts/check.sh` ejecuta localmente lo mismo que el workflow (`compileall` + `unittest discover -v`). El workflow **no se deshabilita ni se modifica**, para no ocultar el fallo.
- Nota: en esta máquina el comando es `python3` (no existe `python`).
