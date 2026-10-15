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

## Verificación de artefactos
Manifiesto: URL, release/tag/commit, nombre, tamaño, SHA-256 esperado, licencia, fecha y fuente del checksum. Un hash local detecta cambios futuros, pero no autentica el origen sin checksum confiable.

## Logs/privacidad
Registrar solo datos necesarios. Redactar usernames, rutas de hogar y seriales al compartir; nunca tokens. Separar reporte compartible del expediente local si hay identificadores sensibles.

## Calidad
Tests para entradas adversas/rutas/errores/códigos de salida; integración sobre imágenes virtuales; no declarar éxito si una etapa crítica falla; revisar OS antes de prometer compatibilidad multiplataforma.