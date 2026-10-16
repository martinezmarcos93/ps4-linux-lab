# Plan de recuperación y criterios de aborto

**Estado:** procedimiento documental; no ensayado en hardware.  
**Alcance:** preparación de imagen USB y diagnóstico de un intento autorizado de arranque Linux.  
**Regla principal:** preservar el sistema original y detenerse ante cualquier incertidumbre que pueda provocar escritura en el almacenamiento interno.

## 1. Límites de seguridad

- No escribir en el almacenamiento interno de la PS4 como parte de la preparación o del primer intento.
- No ejecutar un instalador de distribución que reparticione automáticamente el dispositivo.
- No usar un kernel si la compatibilidad con el southbridge confirmado no está respaldada por evidencia suficiente.
- No continuar si el procedimiento depende de rutas internas del loader o mezcla artefactos de distintos orígenes/releases.
- No conectar una imagen a un dispositivo físico para probarla: la validación host-side se hace sobre archivos de imagen.
- Toda acción sobre la consola requiere autorización explícita del operador y una revisión previa de los artefactos exactos.

## 2. Puertas previas a cualquier intento

Antes de autorizar un intento, registrar en el log de laboratorio:

1. Modelo CUH, firmware observado y método de identificación.
2. Southbridge y evidencia que lo respalda; si sigue desconocido, abortar la selección del kernel.
3. Hash SHA-256 y procedencia del loader/payload, kernel, initramfs, rootfs e imagen USB.
4. Evidencia de que kernel e initramfs pertenecen a una combinación compatible y no mezclan releases.
5. Resultado de las validaciones de estructura e integridad de la imagen.
6. Procedimiento exacto de arranque y procedimiento de retorno al estado original.
7. Estado previo del sistema original y observaciones relevantes.
8. Aprobación explícita para el intento físico concreto.

La ausencia de un dato crítico no se compensa con una suposición.

## 3. Criterios de aborto inmediato

Detener el procedimiento y no probar otra combinación a ciegas si ocurre cualquiera de estos casos:

- El southbridge no está confirmado.
- La procedencia o el hash de un artefacto no coincide con el registro aprobado.
- Falla una validación obligatoria o el informe de validación no se puede generar.
- Se detectan artefactos de distintas releases o rutas de carga ambiguas.
- El procedimiento intenta instalar, formatear, reparticionar o escribir en el almacenamiento interno.
- El loader, el payload o el kernel muestra un comportamiento distinto al previsto.
- Se pierde una condición necesaria para volver al sistema original.
- No se puede determinar si una operación escribe en almacenamiento persistente.

No improvisar comandos de recuperación sobre el disco interno.

## 4. Diagnóstico escalonado de un intento autorizado

Registrar cada etapa por separado, sin afirmar que una etapa posterior se alcanzó si no hay evidencia:

1. **Preparación del host:** imagen y USB identificados por hash.
2. **Carga del payload/loader:** resultado observable y log disponible.
3. **Handoff a kexec:** evidencia de que el kernel recibió el control.
4. **Inicialización del kernel:** log temprano, UART o mensaje observable, si está disponible.
5. **Inicio de initramfs:** evidencia de ejecución de su proceso inicial.
6. **Montaje del rootfs:** dispositivo y etiqueta identificados; no ejecutar scripts de instalación automática.
7. **Entorno de usuario:** consola, red, vídeo y periféricos comprobados.
8. **Integridad posterior:** registrar síntomas y verificar que no hubo cambios persistentes no autorizados.

Un LED blanco, pantalla negra o ausencia de vídeo no identifica por sí solo la etapa del fallo.

## 5. Paquete mínimo de diagnóstico

Por cada intento, conservar:

- Fecha/hora y operador.
- Modelo CUH, firmware y southbridge con fuente de evidencia.
- Hashes de todos los artefactos utilizados.
- Hash de la imagen USB antes del intento, si se puede obtener sin riesgo.
- Versión/commit del loader y parches aplicados.
- Comandos exactos y sus códigos de salida.
- Logs completos disponibles, recortados solo para presentarlos, no para reemplazar el original.
- Síntomas observados y etapa máxima demostrada.
- Resultado: ABORTADO, FALLIDO, PARCIAL o EXITOSO; no usar VERIFIED sin evidencia de laboratorio según la política del proyecto.

No incluir claves, credenciales, tokens ni datos personales innecesarios en los logs versionados.

## 6. Recuperación

- Si el intento no llega al kernel y no hay evidencia de escritura persistente, detenerse y revisar logs/artefactos en el host antes de otro intento.
- Si aparece un instalador, petición de particionado o escritura persistente, abortar sin confirmar la operación.
- Si el estado del almacenamiento interno es incierto, no seguir experimentando: preservar el estado y documentar el incidente.
- No proponer restauraciones, reinstalaciones o actualizaciones de firmware como primera respuesta.
- Toda acción correctiva que modifique el almacenamiento interno requiere análisis separado y autorización expresa.

## 7. Estado actual

Este documento no autoriza la ejecución de payloads ni una prueba física. La compatibilidad de kernel para la CUH-2115B sigue bloqueada hasta disponer de evidencia fiable del southbridge y de una combinación compatible. La validación host-side de una imagen no demuestra que la PS4 vaya a arrancar Linux.
