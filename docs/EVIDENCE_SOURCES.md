# Registro de fuentes y evidencia

Las URLs a ramas por defecto ayudan a descubrir contenido, no son referencias inmutables. Registrar commit/tag/release para decisiones importantes.

| ID | Fuente | Alcance revisado | Consulta | Límites |
|---|---|---|---|---|
| SRC-001 | https://github.com/X-F1REBALL-X/PS4-Linux | README, compatibilidad declarada, rutas tools/build-img.sh y tools/write-img.ps1, LICENSE | 2026-10-15 | revisión preliminar, no auditoría completa ni prueba en hardware |
| SRC-002 | https://github.com/ps4-linux/ps4-linux-loader | README sobre firmware/southbridge, rutas boot y VRAM | 2026-10-15 | revisión preliminar; no hallar LICENSE en la raíz consultada no demuestra ausencia de licencia aplicable |
| SRC-003 | https://github.com/martinezmarcos93/ps4-linux-lab | documentación del laboratorio | 2026-10-15 | describe plan, no valida hardware |

## Afirmaciones que requieren referencia inmutable
- Rango de firmware/southbridge del loader.
- Combinaciones consola/firmware declaradas probadas.
- Precedencia entre USB y almacenamiento interno.
- Valores/efectos de reserva VRAM.
- Particiones/formato de rootfs.
- Escrituras internas del loader/initramfs.
- Licencias de kernel, payloads, initramfs, rootfs y dependencias.
- Hashes publicados de artefactos.

## Tipos de evidencia
- PRIMARY-IMMUTABLE: commit/tag, release firmado o checksum verificable.
- PRIMARY-MUTABLE: README/rama default sin fijar commit.
- SECONDARY: issue/informe comunitario identificable.
- INFERENCE: deducción pendiente.
- LAB: experimento propio con condiciones y artefactos.

## Formato de alta
ID; afirmación; tipo (UPSTREAM-CLAIM/CODE-OBSERVATION/INFERENCE/HYPOTHESIS/LAB-VERIFIED); URL; commit/tag/release; ruta/línea; fecha; hash; límites; experimento que podría refutar/confirmar.

No elevar una afirmación a LAB-VERIFIED por repetir citas del mismo origen.