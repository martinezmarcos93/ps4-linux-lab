# Procedimiento de Construcción y Validación de PS4 Linux USB

## 1. Requisitos
- Herramientas: `sfdisk`, `mkfs.vfat`, `mkfs.ext4`, `7z`, `debugfs`.
- Entorno: Linux con permisos de usuario normal (no requiere root).

## 2. Construcción
Ejecutar:
```bash
python3 tools/build_usb_image.py \
    --salida mi_imagen.img \
    --initramfs /ruta/a/initramfs.cpio.gz \
    --kernel /ruta/a/bzImage \
    --rootfs-dir /ruta/a/rootfs/
```
Esto creará `mi_imagen.img` y `mi_imagen.json` de forma atómica.

## 3. Validación
Correr suite completa:
```bash
bash scripts/check.sh
pytest tests/test_build_usb_image.py
```
El script `check.sh` verifica enlaces de la documentación y los tests básicos.
