# Entorno DESECHABLE de compilación del loader (solo toolchain; sin Python; se ejecuta sin red).
#
# Fijado:
#  - imagen base por digest (índice multi-arquitectura; se usa la variante linux/amd64);
#  - repositorios apt por snapshot con fecha (snapshot.ubuntu.com), no por "latest";
#  - versiones exactas de los paquetes de compilación;
#  - lista completa de paquetes de la imagen final comparada con paquetes.lock: si difiere, la construcción FALLA.
# La construcción de la imagen necesita red (solo snapshot.ubuntu.com; la imagen base no trae ca-certificates, así que TLS no se verifica y la integridad la da la firma GPG de apt sobre InRelease/Packages). La compilación se ejecuta con --network none.
FROM ubuntu:24.04@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55
ARG SNAPSHOT=20261016T040000Z
RUN printf 'Types: deb\nURIs: https://snapshot.ubuntu.com/ubuntu/%s\nSuites: noble noble-updates noble-security\nComponents: main universe\nSigned-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg\n' "$SNAPSHOT" > /etc/apt/sources.list.d/ubuntu.sources \
 && printf 'Acquire::Check-Valid-Until "false";\nAcquire::https::Verify-Peer "false";\nAcquire::https::Verify-Host "false";\n' > /etc/apt/apt.conf.d/99snapshot \
 && apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential=12.10ubuntu1 binutils=2.42-4ubuntu2.10 make=4.3-4.1build2 yasm=1.3.0-4 \
      gcc=4:13.2.0-7ubuntu1 gcc-13=13.3.0-6ubuntu2~24.04.1 libc6-dev=2.39-0ubuntu8.9 \
 && rm -rf /var/lib/apt/lists/*
COPY paquetes.lock /tmp/paquetes.lock
RUN dpkg-query -W -f '${Package}=${Version}\n' | LC_ALL=C sort > /tmp/instalados.txt \
 && diff -u /tmp/paquetes.lock /tmp/instalados.txt \
 && rm /tmp/paquetes.lock /tmp/instalados.txt
RUN useradd --create-home --uid 10001 builder
USER 10001:10001
WORKDIR /work
