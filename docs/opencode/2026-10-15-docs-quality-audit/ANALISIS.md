# Análisis — barrido de calidad documental (2026-10-15)

## Qué dice la documentación vs qué hay
- El repo es un laboratorio de documentación + herramientas de solo lectura (Python stdlib, sin dependencias).
- `scripts/check.sh` corre `compileall` + `unittest discover` sobre `tools/` y `tests/`. No hay control de enlaces documentales.
- Hay 20+ docs Markdown en `docs/` más `README.md`/`CONTRIBUTING.md` en la raíz. Los enlaces relativos entre docs usan estilos mixtos: `ARCHITECTURE.md` (desde docs/) y `docs/ARCHITECTURE.md` (desde raíz). Existe un subdirectorio `docs/lab-logs/`.

## Hallazgos rápidos (grep dirigido)
- Enlaces relativos apuntan a archivos existentes en su mayoría (verificado con `ls`), pero no hay verificador automatizado: riesgo de rotura silenciosa al renombrar.
- Estilos de enlace mixtos (relativo al archivo vs relativo a raíz) funcionan hoy porque GitHub resuelve rutas relativas al archivo; un verificador debe hacer lo mismo.
- No se detectaron referencias a scripts inexistentes en los docs revisados por grep (tools/verify_boot_chain.py, tools/inspect_image.py, tools/verify_artifacts.py, tools/ps4lab.py, tools/build-img.sh citados — todos existen o son upstream).
- `docs/DECISION_LOG.md`, `docs/BOOT_FLOW.md`, `docs/ROADMAP.md` y `tools/verify_boot_chain.py` están RESERVADOS por el encargo: no editar (solo leer).

## Stack y convenciones
- Python 3 stdlib solamente (prohibido instalar dependencias). Tests con `unittest` en `tests/test_*.py`.
- Herramientas de solo lectura; mensajes en español; encoding utf-8 explícito; sin `except: pass`.
- Conventional Commits en español.

## Zonas sensibles (fuera de alcance)
- Ninguna de auth/pagos/deploy. El riesgo aquí es documental: no debilitar reglas de seguridad ya escritas (RISK_REGISTER, SAFETY_AND_TOOLING) y no tocar archivos reservados.

## Deuda visible
- Sin verificador de enlaces; sin doc que explique controles de calidad documental.
- `scripts/check.sh` no incluye el control nuevo (hay que integrarlo).

## Alcance de esta tanda
1. `tools/check_docs_links.py` (solo lectura, stdlib).
2. `tests/test_check_docs_links.py` (dir temporales, datos sintéticos).
3. Integración en `scripts/check.sh` (no bloquear si hay solo advertencias).
4. `docs/DOCS_QUALITY_CHECKS.md` + actualización mínima de README si corresponde.
