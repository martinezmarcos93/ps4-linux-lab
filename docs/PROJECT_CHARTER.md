# Acta del proyecto

**Fecha de inicio documental:** 2026-10-15  
**Estado:** propuesta inicial; pendiente de validar el hardware real.

## Propósito

Investigar si una PlayStation 4 en desuso puede convertirse, sin perder innecesariamente la capacidad de volver a su sistema original, en un sistema Linux experimental para escritorio, videojuegos/emulación y cargas de cómputo seleccionadas.

## Objetivos principales

1. Conseguir un arranque de Linux desde almacenamiento USB externo.
2. Evitar escrituras en el disco interno hasta que exista una justificación técnica explícita.
3. Identificar las limitaciones reales del modelo, firmware, southbridge, kernel y controladores.
4. Crear herramientas seguras para preparar medios, comprobar archivos, recopilar diagnósticos y recuperar configuraciones de Linux.
5. Evaluar la utilidad como equipo de juegos/emulación y como nodo experimental de inferencia local.

## Fuera de alcance inicial

- Sustituir o borrar el sistema original de la consola.
- Modificar firmware de manera irreversible.
- Automatizar escrituras destructivas sin confirmación.
- Distribuir payloads, kernels, rootfs o firmware de terceros sin comprobar licencias y procedencia.
- Prometer aceleración LLM por GPU antes de probar un backend compatible.

## Criterios de éxito

### Hito A — Preparación segura
- Modelo CUH y firmware registrados.
- Disco interno y datos importantes protegidos.
- Imagen USB, origen y hashes registrados.
- Ninguna modificación del disco interno.

### Hito B — Primer arranque
- Payload y kernel elegidos con evidencia para la combinación hardware/firmware.
- Linux llega a una consola o escritorio utilizable.
- Registro de vídeo/síntomas, periféricos y tiempos de arranque.
- Reinicio de vuelta al sistema original verificado.

### Hito C — Plataforma estable
- Temperatura, ventilación y estabilidad observadas durante pruebas progresivas.
- Almacenamiento, red, audio, USB y controladores documentados.
- Pruebas de integridad tras apagados controlados.

### Hito D — Usos finales
- Juegos y emuladores evaluados individualmente.
- GPU, OpenGL/Vulkan y cómputo verificados con herramientas concretas.
- LLM medidos con modelo, cuantización, backend, memoria, tokens/s y temperatura registrados.

## Principios operativos

- Evidencia antes de conclusiones.
- Un cambio relevante por iteración.
- `main` protegido hasta autorización explícita.
- Una sola rama temporal activa salvo necesidad justificada.
- No declarar tests ejecutados si solo fueron inspeccionados.
- Las hipótesis deben tener un experimento que pueda refutarlas.
