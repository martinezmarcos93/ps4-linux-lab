#!/usr/bin/env bash
# Se ejecuta DENTRO del contenedor (montado de solo lectura). Propaga el código de salida real de make.
# Variables (solo para pruebas en el anfitrión): PS4LAB_SRC (por defecto /work/src), PS4LAB_OUT (por defecto /out).
set -u
SRC=${PS4LAB_SRC:-/work/src}
OUT=${PS4LAB_OUT:-/out}
cd "$SRC" || { echo 1 > "$OUT/make.exit"; exit 1; }
rm -f "$OUT/make.exit"
{
  gcc --version | head -1
  ld --version | head -1
  yasm --version | head -1
  make --version | head -1
} > "$OUT/versiones.txt" 2>&1 || true
dpkg-query -W -f='${Package}=${Version}\n' 2>/dev/null | LC_ALL=C sort > "$OUT/paquetes.txt" || true
# lib/syscalls.asm está versionado: se marca más nuevo que lib/syscalls.py para que make NO intente regenerarlo.
# Sin red ni Python en el contenedor, un intento de regenerarlo haría fallar la compilación en vez de descargar nada.
touch lib/syscalls.asm
make -C linux -j4 > "$OUT/build.log" 2>&1
rc=$?
echo "$rc" > "$OUT/make.exit"
echo "make exit=$rc" >> "$OUT/build.log"
exit "$rc"
