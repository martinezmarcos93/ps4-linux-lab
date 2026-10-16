# Contribuir al laboratorio público

Este repositorio documenta investigación experimental sobre Linux en PlayStation 4. Las contribuciones deben priorizar seguridad, procedencia, reproducibilidad y honestidad sobre el estado real.

## Flujo de trabajo

1. Leer `docs/ROADMAP.md`, `docs/RISK_REGISTER.md`, `docs/LICENSE_POLICY.md` y `docs/PUBLICATION_AUDIT.md`.
2. Trabajar en una rama temporal y mantener cada cambio acotado a una unidad coherente.
3. No modificar `main` directamente salvo autorización explícita del mantenedor para una operación concreta.
4. Registrar fuente, versión/commit, licencia, hash y método de obtención de cada artefacto externo.
5. No probar scripts destructivos sobre dispositivos reales durante el desarrollo.
6. Añadir pruebas de regresión y casos de seguridad para cada cambio en herramientas.
7. Registrar los comandos de test ejecutados y sus resultados reales; no afirmar que un test pasó si no se ejecutó.
8. No marcar una tarea como `VERIFIED` sin prueba reproducible en hardware, registro de condiciones y hashes.
9. No subir dumps, claves, datos personales, tokens, credenciales, logs sensibles ni artefactos grandes sin revisar y redactar.
10. No incorporar ni redistribuir payloads, kernels, imágenes, rootfs o binarios de terceros sin revisar sus licencias.
11. Actualizar README, roadmap, registro de decisiones e inventario cuando cambie el estado técnico.
12. Distinguir claramente `IMPLEMENTADO`, `TESTS`, `CÓDIGO`, `TERCEROS` y `LAB`; no confundir pruebas host-side con pruebas de consola.

## Evidencia

Cada hallazgo técnico debe indicar la fuente y el alcance de lo observado. Usar estas categorías:

- `UPSTREAM-CLAIM`: afirmación de un proyecto o usuario externo.
- `CODE-OBSERVATION`: observación derivada de inspeccionar código o binarios.
- `INFERENCE` / `HYPOTHESIS`: conclusión tentativa, con incertidumbre explícita.
- `TESTS`: test automatizado ejecutado en el equipo anfitrión.
- `LAB-VERIFIED`: prueba propia en la consola, con condiciones y resultados registrados.

## Seguridad

La arquitectura de referencia es USB-only y el almacenamiento interno debe permanecer intacto en las primeras fases. Ninguna contribución puede dar por probado ese aislamiento sin evidencia. Un hash no acredita el origen por sí solo; debe existir una fuente confiable para el valor esperado.

## Alcance y expectativas

El repositorio es público y acepta revisión técnica, correcciones documentales y tests. La publicación no implica soporte oficial, garantía de funcionamiento ni autorización para reutilizar componentes de terceros.
