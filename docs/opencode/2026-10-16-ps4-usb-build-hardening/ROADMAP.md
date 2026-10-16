| ID | Tarea | Complejidad | Archivos | Verificación (oráculo) | Estado |
|----|-------|-------------|----------|------------------------|--------|
| 1 | Revisión de `check.sh` y corrección de `tools/check_docs.py` | 1 | `scripts/check.sh`, `tools/` | `check.sh` pasa | `hecha` |
| 2 | Corrección de fallo en `test_exit_codes` | 2 | `tests/test_inspect_image.py`, `tools/inspect_image.py` | `pytest` pasa | `hecha` |
| 3 | Implementar creación y atomicidad de informe JSON en `build_usb_image.py` | 3 | `tools/build_usb_image.py` | Test de creación de informe | `pendiente` |
| 4 | Añadir pruebas de errores fsck, herramientas ausentes | 3 | `tests/test_build_usb_image.py` | Pruebas pasan | `pendiente` |
| 5 | Anonimización de rutas en manifiestos | 3 | `tools/build_usb_image.py` | Test de comparación de manifiestos | `pendiente` |
| 6 | Documentar procedimiento de construcción/QA | 1 | `docs/REPRODUCIBILIDAD.md` | Revisión manual | `pendiente` |
