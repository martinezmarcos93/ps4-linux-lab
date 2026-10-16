# Revisión independiente de OpenCode — hardening USB

- Fecha: 2026-10-16
- Rama revisada: `opencode/ps4-usb-build-hardening`
- Base comparada: `main` en `e8c4b4e45f0ba7dce2da53afac96f1aea15fea40`
- Resultado de comparación: rama divergida; 6 commits por delante y 5 por detrás de `main`; merge base `de7a9931d78069464c3852248bdd20220e840c6b`.
- Método: revisión estática de archivos publicados por GitHub. No ejecuté los tests ni descargué el repositorio a un entorno de ejecución. El total de 265 tests es reportado por OpenCode y no está verificado independientemente en esta revisión.

## Resumen

El cambio parece mantener la intención de construir un archivo de imagen y no escribir directamente en dispositivos físicos. Sin embargo, la publicación del informe JSON no es segura en todos los escenarios de colisión/ruta. **No recomiendo integrar esta rama todavía.**

## Hallazgo OCH-001 — publicación JSON puede sobrescribir un informe previo o seguir un symlink

**Severidad: alta para integridad de archivos. Estado: bloqueante antes de integrar.**

En `tools/build_usb_image.py`, `validar_salida()` rechaza que exista el archivo `.img`, pero no comprueba si ya existe el destino `*.json`. En `construir()`, el informe temporal se crea con `open(parcial_json, "w")`, que no usa `O_EXCL`/`O_NOFOLLOW`, y después `os.replace(parcial_json, informe_json)` puede reemplazar un JSON previo aunque la imagen destino no exista.

Consecuencias posibles:
- Una salida `nombre.img` nueva puede reemplazar silenciosamente un `nombre.json` preexistente.
- Si `nombre.json.parcial` ya es un symlink, abrirlo en modo `w` puede truncar el archivo al que apunta, en lugar de rechazar el temporal.
- La comprobación de temporal existente se aplica a la imagen parcial, no a la parcial JSON.

Corrección recomendada:
1. Validar antes de construir que no existan `destino`, `informe_json`, `parcial_img` ni `parcial_json`; fallar sin modificar nada si cualquiera existe.
2. Crear el temporal JSON con `os.open(..., O_CREAT | O_EXCL | O_WRONLY | O_NOFOLLOW, 0o600)` y escribir mediante el descriptor.
3. Publicar ambos artefactos con una estrategia de transacción recuperable. El sistema de archivos no ofrece una transacción atómica de dos archivos: documentar y probar el comportamiento si falla el segundo `os.replace`.
4. Añadir pruebas para JSON final preexistente, symlink en `.json.parcial`, archivo temporal JSON previo y fallos inyectados en cada paso de publicación.

## Hallazgo OCH-002 — la prueba con rootfs real sigue sin ejecutarse

**Severidad: media. Estado: pendiente por alcance.**

Los tests de construcción mostrados usan un kernel, initramfs y rootfs ficticios; validan el pipeline de archivo, no la imagen final de la consola. El propio código documenta que, sin `fakeroot`, propietarios y grupos del rootfs pueden quedar incorrectos. No construir con el rootfs real hasta que Claude termine la auditoría de artefactos/licencias y se apruebe el conjunto exacto de entradas.

## Aspectos positivos observados

- La salida se restringe a un archivo `.img` y se rechazan directorios bajo rutas críticas como `/dev`, `/proc`, `/sys` y `/boot`.
- Se rechazan entradas que no sean archivos regulares para kernel/initramfs y archivos especiales dentro del rootfs.
- La construcción usa una imagen temporal regular y no un dispositivo de bloque.
- Hay pruebas de fallos simulados y limpieza de temporales.
- `inspect_image.py` abre con `O_RDONLY`, rechaza symlinks y valida que la entrada sea un archivo regular.

## Integración y pruebas

- Rama publicada: confirmada.
- Diferencia respecto de `main`: 6 commits ahead / 5 behind; no integrar directamente sin reconciliar la base.
- Tests: 265 aprobados según reporte de OpenCode; no ejecutados independientemente por ChatGPT.
- PR: no confirmado por la búsqueda disponible.
- Decisión: solicitar a OpenCode corregir OCH-001, rebasar o actualizar la rama desde `main` sin perder sus cambios, volver a ejecutar `bash scripts/check.sh` y `python3 -m unittest discover tests`, y entregar diff actualizado.
- No hacer merge a `main` sin autorización expresa de Marcos.

## Alcance no cubierto

Esta revisión no demuestra que el kernel Baikal 7.0.8 arranque en CUH-2115B, ni que el flujo completo sea USB-only, ni que la combinación kernel/initramfs/rootfs sea compatible. No se escribió USB físico ni se modificó la consola.