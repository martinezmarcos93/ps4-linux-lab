# Plan de trabajo vigente — PS4 Linux Lab

**Actualizado:** 2026-10-16  
**Repositorio:** `martinezmarcos93/ps4-linux-lab`  
**Base integrada:** `main`  
**Estado:** los cinco workstreams originales ya se integraron a `main`. Este documento reemplaza el plan de ejecución basado en ramas que ya no existen.

## Objetivo

Completar la preparación técnica reproducible en PC y reunir evidencia suficiente para decidir si procede una prueba controlada en hardware. La meta no es llegar al 100 % documental: es producir una cadena de arranque auditada y no presentar como probado lo que todavía no se ejecutó.

## Distribución de responsabilidades

| Trabajo | Responsable principal | Revisión |
|---|---|---|
| Baseline local, suite completa y compilación del loader original/parcheado | OpenCode | ChatGPT revisa logs, hashes y diferencias |
| Auditoría estática de herramientas críticas y seguridad de publicación | ChatGPT | OpenCode reproduce los hallazgos en el entorno local |
| Fuentes, procedencia, hashes y licencias de artefactos locales | ChatGPT investiga fuentes públicas; OpenCode inspecciona archivos locales | Revisión cruzada con evidencia |
| Compatibilidad de kernel/initramfs/rootfs | Compartido: análisis de evidencia por ChatGPT; inspección local por OpenCode | No aprobar por inferencia |
| Construcción y validación de imagen virtual | OpenCode | ChatGPT revisa diseño, informe y riesgos |
| Prueba en PS4, escritura USB física y ejecución de payloads | No asignada en este ciclo | Requiere autorización específica posterior de Marcos |

## Secuencia y criterios de aceptación

### 1. Baseline y compilaciones

- Confirmar la relación del checkout local con `origin/main` y registrar SHA.
- Ejecutar `bash scripts/check.sh` sin ocultar fallos.
- Compilar el loader upstream fijado y la variante USB-only parcheada.
- Registrar dependencias, versiones, comandos, códigos de salida, logs y hashes.
- Diferenciar compilación funcional de reproducibilidad bit a bit.

**Cierre:** ambas variantes tienen resultados de compilación verificables o un bloqueo reproducible con causa documentada.

### 2. Auditoría de artefactos

- Identificar el kernel Baikal 7.0.8 y verificar su hash contra el catálogo.
- Solicitar acceso legítimo a las fuentes/configuración de Strawberry si el acceso a releases sigue restringido.
- Auditar initramfs y rootfs reales, incluidos scripts de inicio, servicios, módulos, firmware, paquetes y posibles montajes automáticos.
- Registrar licencias, fuentes disponibles y restricciones de redistribución.
- Mantener en evaluación los componentes cuya procedencia no pueda demostrarse.

**Cierre:** cada artefacto tiene estado, hash, fuente, licencia y límite de evidencia; los bloqueos están explícitos.

### 3. Construcción de imagen virtual

- Usar únicamente artefactos catalogados y aprobados para el experimento.
- Construir la imagen como archivo regular, sin abrir dispositivos de bloque, montar medios físicos ni escribir un USB.
- Verificar las estructuras FAT y ext4, el contenido esperado, los hashes y el informe de construcción.
- Probar que archivos finales o temporales preexistentes y symlinks no se sobrescriben ni se siguen.
- Verificar que el modo de fallo no deja artefactos finales parciales o elimina archivos preexistentes.

**Cierre:** imagen y manifiesto verificables, resultado de filesystem checks explícito y pruebas de regresión aprobadas.

### 4. Revisión previa al laboratorio

- Revisar en conjunto loader, kernel, initramfs, rootfs y parámetros de arranque.
- Confirmar que el diseño no depende de rutas internas como fallback.
- Documentar qué riesgos USB-only son mitigados por diseño y cuáles solo pueden evaluarse en hardware.
- Definir precondiciones de red, recuperación y criterios de aborto.

**Cierre:** informe de decisión con bloqueos residuales y alcance exacto de cualquier eventual prueba.

### 5. Validación en hardware (fuera del ciclo automático)

No se autoriza por este plan la escritura del USB físico, la ejecución de payloads ni el arranque de Linux. Cualquier prueba requiere autorización específica de Marcos para los artefactos y la etapa identificados. Si se autoriza posteriormente, comenzar por la shell de rescate, mantener un solo cambio de variable por intento y documentar evidencia con hashes.

## Protocolo de trabajo

1. Trabajar en ramas separadas de `main`, con commits pequeños y coherentes.
2. No sobrescribir ni eliminar cambios locales ajenos.
3. No marcar tests como ejecutados si no se corrieron.
4. No declarar una compilación reproducible sin evidencia de reproducción.
5. No llamar `VERIFIED` a un resultado basado solo en documentación, código o tests host-side.
6. Al terminar cada tarea, entregar archivos cambiados, SHA inicial/final, comandos, salidas reales, tests, hashes, riesgos y siguiente paso.
7. Integrar a `main` solo después de revisión y autorización explícita de Marcos.

## Fuera del alcance inmediato

- Escritura de USB físico.
- Ejecución de payloads o exploit en la consola.
- Modificación del almacenamiento interno.
- Primer arranque Linux.
- Mediciones de GPU, juegos, emulación, temperatura y LLM.

Estas actividades se reconsideran solo después de cerrar las etapas de PC y la revisión de seguridad correspondiente.
