# Política de licencias y procedencia

## Regla general

No asumir que un repositorio, release o paquete tiene una única licencia aplicable a todos sus componentes. Revisar cada script, kernel, payload, initramfs, rootfs, tema, paquete y dependencia.

## Inventario mínimo por componente

- Nombre y función.
- URL del proyecto y release/tag/commit.
- Autor/mantenedor.
- Archivo de licencia o cabecera.
- Hash SHA-256.
- Si se modifica o redistribuye.
- Obligaciones de atribución, entrega de fuente y avisos.
- Fecha de revisión.

## Licencia del código propio

El código y la documentación propios de este repositorio (`tools/`, `tests/`, `scripts/`, `docs/`, `README.md`) se publican bajo **MIT** (ver `LICENSE` en la raíz, decisión `D-023` en `docs/DECISION_LOG.md`). Esta licencia **no se extiende** a componentes de terceros (loaders, kernels, payloads, rootfs, parches o binarios upstream): cada uno conserva su propia licencia y condiciones, según el inventario de esta política y de `docs/ARTIFACT_INVENTORY.md`.

## Política inicial de este repositorio

- Documentación y scripts propios se identificarán como propios.
- No subir imágenes completas de Linux, kernels ni payloads de terceros por defecto.
- Preferir instrucciones que descarguen desde la fuente original y verifiquen hashes.
- No copiar código de un upstream sin confirmar la licencia del archivo y sus dependencias.
- Mantener avisos de copyright y archivos de licencia requeridos.
- Marcar modificaciones y procedencia.
- Consultar antes de redistribuir artefactos cuya licencia sea ausente, ambigua o incompatible.

## Hallazgo inicial

`X-F1REBALL-X/PS4-Linux` tiene `LICENSE` con GPL-3. No se encontró `LICENSE` en la raíz de `ps4-linux/ps4-linux-loader` en la ruta comprobada. Esto es una observación preliminar, no una conclusión de que el segundo proyecto no tenga derechos o licencias aplicables.
