#!/usr/bin/env bash
# Compila ps4-linux-loader (revisión fijada) dentro de un contenedor Docker sin red, sin dispositivos,
# con sistema de archivos raíz de solo lectura y sin capacidades. NO ejecuta ningún ELF resultante.
#
# Uso: scripts/build_loader_isolated.sh <dir-fuentes-limpio> <dir-salida> [--patch archivo.patch]
#   <dir-fuentes-limpio>  checkout del loader en la revisión fijada (se copia; el original no se modifica)
#   <dir-salida>          directorio NUEVO donde quedan fuentes copiadas, logs y artefactos
set -euo pipefail

IMAGEN=ps4lab-loader-build:1
REPO=$(cd "$(dirname "$0")/.." && pwd)
SRC=${1:?falta <dir-fuentes-limpio>}
OUT=${2:?falta <dir-salida>}
PARCHE=""
if [ "${3:-}" = "--patch" ]; then PARCHE=${4:?falta archivo.patch}; fi

[ -d "$SRC/linux" ] && [ -d "$SRC/lib" ] || { echo "ERROR: $SRC no parece el loader" >&2; exit 2; }
[ ! -e "$OUT" ] || { echo "ERROR: $OUT ya existe; use un directorio nuevo" >&2; exit 2; }
case "$(readlink -f "$OUT")" in /dev/*|/proc/*|/sys/*|/etc/*|/usr/*|/boot/*) echo "ERROR: salida en ruta del sistema" >&2; exit 2;; esac

mkdir -p "$OUT"
cp -a "$SRC" "$OUT/src"
rm -rf "$OUT/src/.git"
if [ -n "$PARCHE" ]; then
  (cd "$OUT/src" && git apply --check "$PARCHE" && git apply "$PARCHE")
  echo "parche aplicado: $PARCHE (sha256 $(sha256sum "$PARCHE" | cut -d' ' -f1))" | tee "$OUT/parche.txt"
fi
chmod a+rwx "$OUT"            # el usuario del contenedor (uid 10001) debe poder escribir logs
chmod -R a+rwX "$OUT/src"

docker image inspect "$IMAGEN" >/dev/null 2>&1 || {
  echo "Construyendo la imagen $IMAGEN (usa red solo para apt)..." >&2
  docker build -q -t "$IMAGEN" "$REPO/build-env/loader" >/dev/null
}

# lib/syscalls.asm está versionado: se marca como más nuevo que lib/syscalls.py para que make NO lo regenere.
# El contenedor no tiene red ni Python: si make intentara regenerarlo, la compilación fallaría en vez de descargar nada.
docker run --rm --network none --read-only --tmpfs /tmp:rw,exec,size=512m --cap-drop ALL \
  --security-opt no-new-privileges --pids-limit 512 --memory 2g --cpus 4 \
  -v "$OUT/src":/work/src:rw -v "$OUT":/out:rw \
  "$IMAGEN" bash -c '
    set -uo pipefail
    cd /work/src
    { gcc --version | head -1; ld --version | head -1; yasm --version | head -1; make --version | head -1; } > /out/versiones.txt 2>&1
    dpkg-query -W -f="\${Package} \${Version}\n" build-essential binutils gcc g++ make yasm libc6-dev > /out/paquetes.txt
    touch lib/syscalls.asm
    set +e
    ( time make -C linux -j4 ) > /out/build.log 2>&1
    echo "make exit=$?" >> /out/build.log
    exit 0
  '

echo "--- resumen"; tail -3 "$OUT/build.log"
if ls "$OUT"/src/linux/payloads/*.elf >/dev/null 2>&1; then
  (cd "$OUT/src/linux/payloads" && sha256sum *.elf *.bin) | tee "$OUT/artefactos.sha256"
else
  echo "SIN ARTEFACTOS: la compilación falló (ver $OUT/build.log)"
fi
