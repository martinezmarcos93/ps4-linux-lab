#!/usr/bin/env bash
# Compila ps4-linux-loader (revisión fijada) dentro de un contenedor Docker sin red, sin dispositivos,
# con raíz de solo lectura y sin capacidades. NO ejecuta ningún ELF resultante.
#
# Uso: scripts/build_loader_isolated.sh <dir-fuentes-limpio> <dir-salida> [--patch archivo.patch ...] [--manifiesto m.json --variante original|parcheado]
# Código de salida: 0 SOLO si make terminó con 0 Y el conjunto completo de artefactos (9 ELF, 9 BIN, 20 kexec.bin)
# existe, no está vacío y no tiene duplicados/inesperados. Cualquier otra cosa: distinto de 0, con los logs conservados.
# Variable DOCKER (por defecto "docker"): solo para pruebas con un docker simulado.
set -uo pipefail

IMAGEN=ps4lab-loader-build:2
DOCKER=${DOCKER:-docker}
REPO=$(cd "$(dirname "$0")/.." && pwd)

falla() { echo "FALLO: $1" >&2; exit "${2:-1}"; }

SRC=${1:-}; OUT=${2:-}
if [ -z "$SRC" ] || [ -z "$OUT" ]; then falla "uso: $0 <dir-fuentes-limpio> <dir-salida> [--patch f] [--manifiesto m --variante v]" 2; fi
shift 2
PARCHEES=(); MANIFIESTO=""; VARIANTE=""
while [ $# -gt 0 ]; do
  case "$1" in
    --patch) PARCHE=${2:?falta archivo.patch}; [ -f "$PARCHE" ] || falla "el parche $PARCHE no existe" 2; PARCHEES+=("$(readlink -f "$PARCHE")"); shift 2;;
    --manifiesto) MANIFIESTO=${2:?falta manifiesto}; shift 2;;
    --variante) VARIANTE=${2:?falta variante}; shift 2;;
    *) falla "argumento desconocido: $1" 2;;
  esac
done

{ [ -d "$SRC/linux" ] && [ -d "$SRC/lib" ]; } || falla "$SRC no parece el loader" 2
[ ! -e "$OUT" ] || falla "$OUT ya existe; use un directorio nuevo" 2
case "$(readlink -f "$OUT")" in /dev/*|/proc/*|/sys/*|/etc/*|/usr/*|/boot/*) falla "salida en ruta del sistema" 2;; esac

mkdir -m 700 "$OUT" || falla "no se pudo crear $OUT" 2
cp -a "$SRC" "$OUT/src" || falla "no se pudo copiar las fuentes" 2
rm -rf "$OUT/src/.git"
if [ "${#PARCHEES[@]}" -gt 0 ]; then
  : > "$OUT/parches.txt"
  for PARCHE in "${PARCHEES[@]}"; do
    # Validar y aplicar en orden: cada parche posterior puede depender del anterior.
    (cd "$OUT/src" && git apply --check "$PARCHE" && git apply "$PARCHE") || falla "el parche no aplica limpio: $PARCHE" 2
    echo "parche aplicado: $PARCHE (sha256 $(sha256sum "$PARCHE" | cut -d' ' -f1))" | tee -a "$OUT/parches.txt"
  done
fi

if ! "$DOCKER" image inspect "$IMAGEN" >/dev/null 2>&1; then
  echo "Construyendo la imagen $IMAGEN (usa red solo para el snapshot de apt)..." >&2
  "$DOCKER" build -q -t "$IMAGEN" "$REPO/build-env/loader" >/dev/null || falla "no se pudo construir la imagen (¿el lock de paquetes cambió?)" 3
fi
{ echo "arquitectura_anfitrion=$(uname -m)"; echo "imagen=$IMAGEN"; \
  echo "imagen_id=$("$DOCKER" image inspect "$IMAGEN" --format '{{.Id}}' 2>/dev/null || echo desconocido)"; } > "$OUT/entorno.txt"

# El contenedor corre con el uid/gid del anfitrión: no se cambian permisos globales y nada queda escribible por terceros.
"$DOCKER" run --rm --platform linux/amd64 --network none --read-only --tmpfs /tmp:rw,exec,size=512m --cap-drop ALL \
  --security-opt no-new-privileges --pids-limit 512 --memory 2g --cpus 4 \
  --user "$(id -u):$(id -g)" -e HOME=/tmp \
  -v "$OUT/src":/work/src:rw -v "$OUT":/out:rw \
  -v "$REPO/build-env/loader/inner_build.sh":/inner_build.sh:ro \
  "$IMAGEN" bash /inner_build.sh
RC_CONTENEDOR=$?
echo "$RC_CONTENEDOR" > "$OUT/contenedor.exit"

VERIF=("$REPO/tools/verify_loader_build.py" "$OUT")
[ -z "$MANIFIESTO" ] || VERIF+=(--manifiesto "$MANIFIESTO" --variante "$VARIANTE")
python3 "${VERIF[@]}"
RC_VERIF=$?

echo "--- resumen: contenedor/make=$RC_CONTENEDOR verificación=$RC_VERIF (logs en $OUT/build.log, $OUT/verificacion.json)"
if [ "$RC_CONTENEDOR" -ne 0 ]; then
  falla "la compilación NO terminó bien (código $RC_CONTENEDOR). Los resultados parciales se conservan en $OUT sin modificar." "$RC_CONTENEDOR"
fi
[ "$RC_VERIF" -eq 0 ] || falla "make terminó con 0 pero el conjunto de artefactos no es válido (ver $OUT/verificacion.json)" 1
echo "OK: compilación y conjunto de artefactos verificados. Ningún binario se ejecutó."
