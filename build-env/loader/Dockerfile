# Entorno DESECHABLE de compilación del loader (solo toolchain; sin Python, sin red en ejecución).
# Construcción de la imagen: requiere red SOLO para apt (repositorios firmados de Ubuntu).
# Ejecución de la compilación: siempre con --network none (ver scripts/build_loader_isolated.sh).
FROM ubuntu:24.04
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential binutils make yasm \
 && rm -rf /var/lib/apt/lists/* \
 && useradd --create-home --uid 10001 builder
USER 10001:10001
WORKDIR /work
