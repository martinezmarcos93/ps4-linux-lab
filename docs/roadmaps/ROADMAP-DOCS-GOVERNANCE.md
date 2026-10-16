# Roadmap de categoría 1 — Gobernanza y documentación

**Rama:** `workstream/01-docs-governance`  
**Responsable de ejecución:** ChatGPT  
**Orden:** 1 de 5 — menor complejidad relativa  
**Objetivo:** llevar la categoría de documentación/gobernanza al 100 % dentro del alcance documental y de publicación. No implica validar el arranque de Linux.

## Criterio de 100 %

La categoría se considera al 100 % cuando el estado público es veraz y consistente, los documentos tienen navegación y referencias coherentes, las reglas de contribución y evidencia son inequívocas, los metadatos públicos están especificados y la auditoría documental automatizada queda ejecutada con resultados registrados. La revisión de secretos y licencias debe tener evidencia; no alcanza con escribir que se hizo.

## Tareas

- [ ] DG-01 Inventariar todos los documentos Markdown, scripts, manifiestos y workflows que describan estado, comandos o política del proyecto.
- [ ] DG-02 Detectar contradicciones entre README, roadmap general, decisión log, matriz de compatibilidad, riesgos, CI y estado público.
- [ ] DG-03 Verificar enlaces relativos y rutas mencionadas en documentación; corregir los rotos y registrar excepciones legítimas.
- [ ] DG-04 Normalizar vocabulario de estado y evidencia: `IMPLEMENTADO`, `CÓDIGO`, `TESTS`, `TERCEROS`, `LAB`, `PENDIENTE`, `BLOQUEADO`.
- [ ] DG-05 Confirmar que ningún documento describe como privado el repositorio ni como verificado un arranque no probado.
- [ ] DG-06 Revisar las instrucciones de contribución, flujo de ramas, criterios de aceptación y requisitos de evidencia.
- [ ] DG-07 Proponer descripción de About, topics de GitHub, política de licencia del código propio y badges solo si su estado puede verificarse.
- [ ] DG-08 Ejecutar los chequeos documentales disponibles y registrar comandos/salida real; no simular ejecución.
- [ ] DG-09 Revisar los archivos publicados en busca de secretos o datos sensibles con herramientas disponibles; registrar alcance y límites del escaneo.
- [ ] DG-10 Crear un informe de auditoría documental con hallazgos, cambios, excepciones y riesgos residuales.
- [ ] DG-11 Actualizar README y documentación de índice solo después de verificar las rutas finales.
- [ ] DG-12 Cerrar el roadmap con evidencias vinculadas a cada tarea.

## Fuera de alcance

No declarar compatibilidad de hardware, no ejecutar payloads, no escribir unidades físicas y no declarar verificado el arranque Linux. La auditoría integral de licencias de dependencias es responsabilidad de la categoría 3.

## Criterios de aceptación

1. Cada tarea cerrada incluye evidencia o referencia a un commit/resultado.
2. Los tests se ejecutaron realmente y su salida está registrada.
3. No hay enlaces internos rotos sin explicación.
4. No hay afirmaciones públicas que excedan la evidencia.
5. Las tareas no resueltas quedan explícitamente bloqueadas o pendientes.
6. La rama no se integra a `main` automáticamente; se entrega para revisión.

## Registro de ejecución

| ID | Estado | Evidencia / commit | Observaciones |
|---|---|---|---|
| DG-01…DG-12 | PENDIENTE | — | Completar al ejecutar |

**Definición de avance:** 0 % inicial; actualizar por tareas aceptadas, no por volumen de texto.