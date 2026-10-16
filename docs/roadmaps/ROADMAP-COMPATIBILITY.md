# Roadmap de categoría 4 — Identificación y compatibilidad

**Rama:** `workstream/04-compatibility`  
**Responsable de ejecución:** Claude Code, con revisión de ChatGPT  
**Orden:** 4 de 5 — complejidad media/alta  
**Objetivo:** resolver toda la investigación de compatibilidad posible sin usar la consola ni afirmar una verificación de laboratorio que no ocurrió.

## Alcance del 100 %

El 100 % de esta rama corresponde al **paquete de decisión previo al laboratorio**: identificación disponible, hipótesis de compatibilidad comparadas, fuentes fijadas, matriz sin contradicciones, criterio de selección o rechazo de kernel y lista precisa de datos que solo pueden obtenerse en hardware. No equivale a compatibilidad funcional ni sustituye la futura categoría de prueba en hardware.

## Estado de partida conocido

- PS4 Slim CUH-2115B.
- Firmware registrado: 13.52.
- Capacidad observada: 861,4 GB.
- Southbridge: desconocido.
- Arranque Linux propio: no verificado.
- USB-only: objetivo arquitectónico, no propiedad demostrada.

## Tareas

- [ ] CP-01 Consolidar la evidencia del modelo y firmware; distinguir dato observado, dato declarado e inferencia.
- [ ] CP-02 Determinar qué revisión de placa/southbridge corresponde al CUH-2115B sin asumir que el modelo basta.
- [ ] CP-03 Identificar las rutas técnicas documentadas para conocer el southbridge y clasificar cuáles requieren ejecutar código en la consola.
- [ ] CP-04 Comparar candidatos de kernel por ABI, configuración, offsets, memoria, firmware y dependencias del payload/loader.
- [ ] CP-05 Contrastar reportes de terceros con código, releases y commits exactos; etiquetar cada afirmación por nivel de evidencia.
- [ ] CP-06 Reconciliar todas las filas de `COMPATIBILITY_MATRIX.md` con las fuentes actuales.
- [ ] CP-07 Crear tabla de compatibilidad por combinación de modelo, firmware, southbridge, loader, kernel y método de arranque.
- [ ] CP-08 Definir un criterio de selección reproducible: aceptar, candidato condicional, rechazar o insuficiente evidencia.
- [ ] CP-09 Documentar qué incertidumbres son resolubles desde PC y cuáles requieren laboratorio.
- [ ] CP-10 Emitir una recomendación técnica fundamentada y un árbol de decisión para el siguiente paso.
- [ ] CP-11 Actualizar roadmap general, registro de decisiones y riesgos con los resultados.
- [ ] CP-12 Revisión cruzada de ChatGPT: consistencia lógica, fuentes, nivel de certeza y ausencia de saltos inferenciales.

## Fuera de alcance de esta rama

No ejecutar payloads ni exploits, no actualizar firmware, no escribir en almacenamiento interno, no conectar una imagen experimental para arrancar y no declarar `LAB`/compatibilidad confirmada. Las pruebas físicas pertenecen a una fase posterior separada.

## Criterios de aceptación

1. Cada conclusión relevante cita evidencia verificable y su nivel.
2. La matriz no contiene contradicciones conocidas sin resolver o explicar.
3. La selección de kernel tiene razonamiento reproducible; si no se puede elegir, se documenta exactamente el bloqueo.
4. El dato southbridge no se inventa ni se infiere solo del CUH.
5. El paquete previo al laboratorio tiene un checklist de entrada y salida.
6. Revisión de ChatGPT completada y registrada.

## Registro de ejecución

| ID | Estado | Evidencia / commit | Observaciones |
|---|---|---|---|
| CP-01…CP-12 | PENDIENTE | — | Completar al ejecutar |

**Dependencias:** categoría 3 para procedencia/licencias; categoría 2 para estado real de herramientas.