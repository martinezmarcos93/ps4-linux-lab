# Seguridad y requisitos de futuras herramientas

## Principios
- Lectura/diagnóstico primero; escrituras explícitas, separadas y mínimas.
- Si el destino o formato no es identificable con seguridad, abortar.
- No seleccionar objetivo por orden de enumeración o sesión anterior.
- No ejecutar automáticamente código arbitrario para reparar el sistema.
- No registrar tokens, credenciales ni datos personales innecesarios.
- Ninguna utilidad del proyecto escribirá firmware de PS4 ni modificará automáticamente su almacenamiento interno.

## Diagnósticos
doctor, inspect-disks, verify-artifacts, inspect-image y collect-logs deben funcionar sin privilegios elevados cuando sea posible. Explicar requisitos de permisos.

## Construcción de imagen
- Directorio temporal único por ejecución.
- Rechazar rutas vacías, raíz y destinos fuera del workspace.
- No hacer limpieza global ni borrar rutas no creadas por el proceso.
- Verificar espacio/tamaño y errores de cada herramienta.
- Registrar versiones, entradas, hashes y salida.
- Limpiar solo temporales propios e identificados inequívocamente.

## Escritura a medio físico
No implementar/habilitar hasta superar pruebas con imágenes virtuales.
1. Advertir claramente la destrucción de datos.
2. Reenumerar el dispositivo justo antes de escribir.
3. Mostrar modelo, tamaño, bus, serial y particiones.
4. Rechazar discos de sistema/arranque y cualquier ambigüedad.
5. Exigir confirmación interactiva ligada a identificador único.
6. No añadir bypass genérico tipo --force que elimine confirmaciones.
7. Verificar escritura y guardar informe.
8. Probar con fixtures, nunca block devices reales.

Esto no autoriza por sí mismo una escritura USB real.

## Herramientas implementadas y su alcance (2026-10-15)
Todas son de **solo archivo**: no abren dispositivos de bloque, no montan, no escriben fuera del `.img` o del directorio temporal que ellas mismas crean, y se ejecutan sin root (las que construyen imágenes rechazan root). Detalle y tests en `docs/ROADMAP.md` Fase 4.
- `verify_boot_chain.py` (5 niveles; ver D-018), `verify_artifacts.py`, `inspect_image.py`: lectura.
- `payload_static.py`, `elf_audit.py`: análisis estático de lectura de blobs/ELF; nunca ejecutan ni desensamblan.
- `fat32_add_file.py`: escribe **solo** en una imagen regular, nunca sobrescribe entradas, rechaza dispositivos y symlinks; no es atómico (opera sobre copias).
- `build_usb_image.py`: construye un `.img` nuevo (no existente), con temporal `.nombre.img.parcial` y `os.replace` al final; ante fallo borra únicamente su temporal; rechaza rutas del sistema (`/dev`, `/proc`, `/sys`, `/run`, `/boot`, `/etc`, `/usr`, …), entradas no regulares, rootfs con archivos especiales y ejecución como root. `--dry-run` valida sin crear nada.
- **No existe** `write-usb-image` ni se implementará sin aprobación expresa de Marcos. Procedimiento manual propuesto para escribir una imagen ya verificada: (1) `lsblk -o NAME,MODEL,SERIAL,SIZE,TRAN,RM,MOUNTPOINTS` antes y después de conectar el pendrive; (2) identificar por modelo+serie+tamaño, nunca por `/dev/sdX`; (3) desmontar sus particiones; (4) `sudo dd if=<imagen> of=/dev/disk/by-id/<id-del-pendrive> bs=4M conv=fsync status=progress` solo tras confirmar que el `by-id` es el correcto y que no es un disco con datos; (5) `sync` y verificar con `cmp` o `sha256sum` de los primeros N bytes. Este texto describe el paso; **no lo autoriza**.

## Hallazgos sobre los scripts de la distribución (no se ejecutan ni se modifican)
`build-img.sh`: ruta fija `/root/psxitarch-usb.img` con `rm -f`, puntos de montaje fijos, sin `trap` de limpieza (un fallo deja loop y montajes activos), `sleep 2` como sincronización, destino `OUT` sin validar (un dispositivo recibiría la imagen). `write-img.ps1`: las comprobaciones de BusType/IsBoot/IsSystem/tamaño son incondicionales (`-Force` solo omite la reconfirmación), pero un disco USB externo de datos las supera y no se vuelve a enumerar entre la confirmación y la escritura. `install-psxitarch.sh` (initramfs): reparticiona por heurística un `/dev/sd?` y copia la clave del disco al rootfs. Detalle en `docs/UPSTREAM_CODE_MAP.md` §2.4, §2.5 y §2.9.

## Verificación de artefactos
Manifiesto: URL, release/tag/commit, nombre, tamaño, SHA-256 esperado, licencia, fecha y fuente del checksum. Un hash local detecta cambios futuros, pero no autentica el origen sin checksum confiable.

## Logs/privacidad
Registrar solo datos necesarios. Redactar usernames, rutas de hogar y seriales al compartir; nunca tokens. Separar reporte compartible del expediente local si hay identificadores sensibles.

## Calidad
Tests para entradas adversas/rutas/errores/códigos de salida; integración sobre imágenes virtuales; no declarar éxito si una etapa crítica falla; revisar OS antes de prometer compatibilidad multiplataforma.