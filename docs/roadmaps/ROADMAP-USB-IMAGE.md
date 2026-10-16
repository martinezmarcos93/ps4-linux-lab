# Roadmap de categoría 5 — Imagen y cadena USB-only

**Rama:** `workstream/05-usb-image`  
**Responsable de ejecución:** Claude Code, con revisión de ChatGPT  
**Orden:** 5 de 5 — mayor complejidad de las cinco categorías de preparación  
**Objetivo:** completar el diseño, preflight y construcción reproducible de una imagen candidata sobre archivos en PC. No incluye escribir en una unidad física ni probar el arranque en PS4.

## Alcance del 100 %

El 100 % de esta rama significa que el flujo de construcción y validación de imagen está documentado, probado con fixtures/artefactos permitidos, reproducible en host, con checks de integridad y seguridad, y que los límites de USB-only están descritos con precisión. No significa que el arranque USB-only esté verificado en hardware.

## Tareas

- [ ] UI-01 Mapear el pipeline completo actual: entradas, scripts, artefactos intermedios, imagen final y salidas.
- [ ] UI-02 Definir el contrato de entradas/salidas y formato esperado para kernel, initramfs, rootfs, manifiestos y particiones.
- [ ] UI-03 Revisar cada ruta de escritura y demostrar que el modo de preparación host-side no toca dispositivos de bloque.
- [ ] UI-04 Auditar rutas temporales, permisos, symlinks, nombres de archivo, falta de espacio, interrupciones y limpieza.
- [ ] UI-05 Probar dry-run y planificación de imagen con fixtures ficticios; verificar que no se escribe una imagen final cuando no corresponde.
- [ ] UI-06 Construir imagen solo con componentes de procedencia/licencia aceptadas, si los artefactos necesarios están disponibles.
- [ ] UI-07 Validar estructura, tamaños, checksums, offsets, particiones y consistencia de manifiestos.
- [ ] UI-08 Comprobar reproducibilidad de build: misma entrada y entorno fijado producen resultado idéntico o diferencias explicadas.
- [ ] UI-09 Verificar que el loader no requiera rutas internas de PS4 para la ruta objetivo; registrar caminos alternativos y límites de evidencia.
- [ ] UI-10 Crear una matriz de seguridad del pipeline y pruebas negativas de entradas inválidas.
- [ ] UI-11 Definir checklist de preflight y criterios de aborto antes de cualquier prueba física futura.
- [ ] UI-12 Documentar plan de recuperación sin prometer que evita todos los fallos.
- [ ] UI-13 Ejecutar pruebas host-side y registrar logs, hashes y entorno.
- [ ] UI-14 Emitir informe final de preparación de imagen y estado del objetivo USB-only: demostrado por código, probado en host o pendiente de laboratorio.

## Fuera de alcance

No ejecutar escritura a USB/dispositivos de bloque, no modificar almacenamiento interno de PS4, no lanzar payloads, no intentar el primer arranque y no declarar USB-only `LAB`-verificado.

## Criterios de aceptación

1. Todo el flujo puede describirse desde entradas hasta salida con versiones y hashes.
2. Pruebas negativas confirman que entradas inválidas fallan de forma segura.
3. El pipeline de host no escribe dispositivos físicos.
4. La imagen solo se genera si hay componentes permitidos y los checks obligatorios pasan.
5. Las afirmaciones sobre USB-only se separan entre análisis estático, tests host y prueba física pendiente.
6. La revisión de categorías 2, 3 y 4 se incorpora o se registran sus bloqueos.
7. No hay merge automático a `main`.

## Registro de ejecución

| ID | Estado | Evidencia / commit | Observaciones |
|---|---|---|---|
| UI-01…UI-14 | PENDIENTE | — | Completar al ejecutar |

**Dependencias:** categoría 2 (herramientas), categoría 3 (artefactos/licencias), categoría 4 (compatibilidad). No generar una imagen final con kernel/artefactos seleccionados por suposición.