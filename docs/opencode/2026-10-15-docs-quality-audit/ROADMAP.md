# RoadMap — docs/quality-audit

| ID | Tarea | Complejidad | Archivos | Verificación (oráculo) | Estado |
|----|-------|-------------|----------|------------------------|--------|
| 1 | `tools/check_docs_links.py` (v1) | 3 | tools/ | `python3 tests/test_check_docs_links.py` | pendiente |
| 2 | `tests/test_check_docs_links.py` | 3 | tests/ | `bash scripts/check.sh` | pendiente |
| 3 | Integrar `check.sh` | 1 | scripts/check.sh | `bash scripts/check.sh` | pendiente |
| 4 | Doc: `DOCS_QUALITY_CHECKS.md` | 1 | docs/ | (leer el archivo) | pendiente |

*Tareas complejas 1/2: el verificador debe resolver rutas relativas estilo GitHub, manejar anclas, no usar red, diferenciar error/warn. Complejidad 3 por manejo de PATH y regex.*
