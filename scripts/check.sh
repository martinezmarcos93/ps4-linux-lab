#!/usr/bin/env bash
# Sustituto local del CI mientras GitHub Actions no pueda arrancar jobs
# (ver docs/CI_DIAGNOSIS.md). Ejecuta lo mismo que .github/workflows/tests.yml
# (tests + validación de documentación).
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PYTHON:-python3}
"$PY" -m compileall -q tools tests
"$PY" -m unittest discover -v
"$PY" tools/check_docs.py .
echo "CHECK_OK"
