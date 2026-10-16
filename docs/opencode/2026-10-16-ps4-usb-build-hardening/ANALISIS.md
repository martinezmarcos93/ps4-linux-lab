# Análisis del repositorio PS4-Linux-Lab

## Contexto y Estado
- **Stack**: Python 3, bash scripts para automatización, pytest para testing.
- **Convenciones**:
  - Verbos CRUD: `crear`, `obtener`, `listar`, `actualizar`, `eliminar`, `existe` (aunque el código actual usa nombres en inglés en las pruebas).
  - Estilo: Python 3.
  - El repositorio parece estar bajo un protocolo de seguridad bastante estricto (automatización en contenedores, verificaciones de firma, etc.).
- **Baseline**: 262 tests pasaron. Un test falló (`test_exit_codes` en `TestInspectImage` por archivo no encontrado, parece ser un problema en la ejecución de la prueba o una ruta mal definida). Hay una advertencia sobre `check_docs_links.py` inexistente.

## Zonas Sensibles (Alcance limitado)
- `tools/build_usb_image.py`: punto de entrada principal para construir la imagen.
- `scripts/check.sh`: script de chequeo.
- `tests/`: pruebas de todo lo anterior.

## Deuda Técnica
- Falta el archivo `tools/check_docs_links.py` que `check.sh` intenta llamar.
- Error en `tests/test_inspect_image.py` (test 59).
- La escritura de informes parece ser el foco principal del encargo (publicación no atómica).

## Roadmap

| ID | Tarea | Complejidad | Archivos | Verificación (oráculo) | Estado |
|----|-------|-------------|----------|------------------------|--------|
| 1 | Revisión de `check.sh` y corrección de `tools/check_docs_links.py` | 1 | `scripts/check.sh`, `tools/` | `check.sh` pasa | `pendiente` |
| 2 | Corrección de fallo en `test_exit_codes` | 2 | `tests/test_inspect_image.py` | `pytest` pasa | `pendiente` |
| 3 | Implementar atomicidad en escritura de informe JSON | 3 | `tools/build_usb_image.py` | Test nuevo de atomicidad | `pendiente` |
| 4 | Añadir pruebas de errores fsck, herramientas ausentes | 3 | `tests/test_build_usb_image.py` | Pruebas pasan | `pendiente` |
| 5 | Anonimización de rutas en manifiestos | 3 | `tools/build_usb_image.py` | Test de comparación de manifiestos | `pendiente` |
| 6 | Documentar procedimiento de construcción/QA | 1 | `docs/REPRODUCIBILIDAD.md` | Revisión manual | `pendiente` |

## Decisiones
- Se ignorará el `TestInspectImage` fallo momentáneamente para enfocarse en el encargo.
- Se corregirá `check.sh` primero para asegurar un entorno de validación base limpio.
