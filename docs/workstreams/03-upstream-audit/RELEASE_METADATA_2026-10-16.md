# Actualización de metadatos de releases — 2026-10-16

Esta nota actualiza la metadata pública consultada para los dos upstreams. Los valores `digest` se obtuvieron de la API de GitHub; **no son hashes calculados localmente en esta sesión**. No se descargó, ejecutó ni reconstruyó ningún asset.

## PS4-Linux `v1.0`

- Release: https://github.com/X-F1REBALL-X/PS4-Linux/releases/tag/v1.0
- Publicado: 2026-09-28T21:24:08Z
- Revisión declarada: `main`; commit observado en consulta: `66e21cb8c15f20189254e2608c6e9bf957eb8078` (2026-10-04).
- API de repositorio: `license.key = other`, `license.spdx_id = NOASSERTION`, aunque la raíz contiene un archivo `LICENSE` cuyo texto corresponde a GPL-3.0. Registrar esta discrepancia como metadata imperfecta; la licencia efectiva de cada asset depende también de su procedencia/avisos.

| Asset | Bytes | SHA-256 publicado por la API |
|---|---:|---|
| `bzImage-baikal-7.0.8` | 13,841,408 | `46c835f762e7b0b5400ea762b8daa1bcec638a1b769c7ec0905137bc565b1ba8` |
| `bzImage-belize-7.1.7` | 20,415,488 | `072113898347932c34888cfdc7556953ee27233c0727cc45f419a57119242480` |
| `initramfs.cpio.gz` | 4,102,011 | `3f373bd6c469e490eaf4e5cf4d2e8ed77cf7bb91449b6a18da6a6529d479169b` |
| `linux-1024mb.elf` | 320,936 | `623c3b68592437b612ede22a4fc1a6f1eef6b17c4b16a1270100ece04cb3c98f` |
| `psxitarch-usb.img.xz.part1` | 1,088,315,226 | `4063f3386c8fe4687c8768f0439ddb868b3bd3f01d4e5176558a277b219bf588` |
| `psxitarch-usb.img.xz.part2` | 1,088,315,226 | `e62aa04d0fff12979f3095d5371b8711af6ee04c600d7599913fdc460462df2d` |
| `SHA256SUMS` | 1,619 | `8d6fd2b42901e5a3425b0f7568a319058f860daf76cb5a054c55b23f8af4e54e` |
| `build-img.sh` | 2,147 | `3a9bfd6739dccc07a439dfa68996f129a8f46388802a414173c62f86271c12a2` |
| `write-img.ps1` | 4,808 | `893dc5ac05c80beb0f5ccabc62b8d80b40327830cafa22f78ba0acce80fe4868` |

El release también publica otros payloads ELF con VRAM variable y archivos de configuración. No descargar ni ensamblar la imagen dividida durante esta fase. La presencia de una imagen lista para USB no implica que el flujo sea USB-only: el README del release instruye colocar `bzImage` e `initramfs.cpio.gz` en `/data/linux/boot/` del almacenamiento interno.

## ps4-linux-loader `v25.1`

- Release: https://github.com/ps4-linux/ps4-linux-loader/releases/tag/v25.1
- Publicado: 2026-09-25T18:34:16Z.
- Revisión de código consultada: `master` @ `f70f43a60a973b3662daeb29c1f115d95408db93`, fechado 2026-09-23.
- Asset `ps4-linux-loader-v25.1.zip`: 363,871 bytes; digest API `sha256:7ee03018982cc25a6a6fcb44221b004406168cb33261dd62d82560144316da74`.
- API de repositorio: `license = null`; no se encontró LICENSE en la raíz consultada. El archivo `linux/ps4-kexec-common/LICENSE` contiene BSD-2-Clause, pero solo se debe atribuir a ese subcomponente y no automáticamente a todo el repositorio.

## Implicaciones

1. Los digests API sirven como referencias de integridad publicadas, no como verificación independiente ni como prueba de seguridad.
2. No se verificó si los assets del loader corresponden byte a byte a un build del commit consultado.
3. No se verificó un build reproducible de los kernels, payloads ni initramfs.
4. No redistribuir estos assets; mantener la investigación en metadatos y lectura estática.
5. Claude debe calcular hashes locales solo sobre archivos que ya existan en el checkout del laboratorio y reportar explícitamente el método, sin descargar o ejecutar binarios nuevos para esta tarea.
