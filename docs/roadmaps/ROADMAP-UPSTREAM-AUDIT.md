# Roadmap de categoría 3 — Auditoría upstream y licencias

**Rama:** `workstream/03-upstream-audit`  
**Responsable de ejecución:** Claude Code  
**Orden:** 3 de 5 — complejidad media  
**Objetivo:** cerrar la auditoría de las fuentes y dependencias necesarias para diseñar una cadena de arranque reproducible, con procedencia, licencias y límites explícitos.

## Criterio de 100 %

La categoría llega al 100 % cuando cada dependencia candidata del alcance tiene una fuente fijada, versión/commit, hash cuando corresponda, licencia y obligaciones identificadas, evaluación de confianza, rol técnico, decisión de uso/no uso y documentación reproducible. Si un componente no tiene licencia identificable, se marca no apto para redistribución; no se inventa una licencia.

## Tareas

- [ ] UA-01 Revisar inventario actual y reconciliarlo con todos los componentes realmente referenciados por scripts, manifiestos y documentación.
- [ ] UA-02 Enumerar dependencias directas e indirectas: loader, kernel, distribución, rootfs, initramfs, paquetes gráficos, skeletons, payloads, herramientas y fuentes de paquetes.
- [ ] UA-03 Fijar URL canónica, commit/tag/release, fecha de consulta y método de descarga por dependencia.
- [ ] UA-04 Verificar hashes desde una fuente confiable independiente cuando exista; distinguir hash calculado de autenticidad.
- [ ] UA-05 Identificar licencia por componente y avisos requeridos; diferenciar licencia del código, firmware, payload y marca.
- [ ] UA-06 Revisar scripts de instalación/compilación de dependencias por descargas flotantes, privilegios, escritura de disco y ejecución remota.
- [ ] UA-07 Comparar README, release y código del commit exacto; registrar divergencias.
- [ ] UA-08 Revisar si cada componente puede modificarse, usarse localmente y redistribuirse; separar las tres decisiones.
- [ ] UA-09 Emitir decisión por artefacto: `ACEPTAR PARA INVESTIGACIÓN`, `USO CONDICIONAL`, `NO REDISTRIBUIR`, `RECHAZADO` o `PENDIENTE`.
- [ ] UA-10 Actualizar inventario, fuentes de evidencia, política de licencias y mapa de código.
- [ ] UA-11 Revisar riesgo de incluir binarios, dumps, blobs comprimidos o material de procedencia incierta en el repositorio público.
- [ ] UA-12 Producir informe de cierre con tabla de dependencias cubiertas, exclusiones justificadas y bloqueos externos.

## Fuera de alcance

No ejecutar payloads ni exploit, no probar la consola y no declarar compatibilidad de hardware. La identificación de kernel adecuado se decide en la categoría 4 usando esta auditoría como entrada.

## Criterios de aceptación

1. No quedan dependencias candidatas sin inventariar.
2. Cada componente tiene procedencia y licencia verificadas o está bloqueado explícitamente.
3. Ningún hash se presenta como prueba de autenticidad sin una fuente de referencia confiable.
4. El repositorio no incorpora artefactos redistribuibles sin permisos comprobados.
5. Los documentos relacionados se actualizan de forma consistente.
6. Las incertidumbres quedan enumeradas; no se rellenan con inferencias presentadas como hechos.

## Registro de ejecución

| ID | Estado | Evidencia / commit | Observaciones |
|---|---|---|---|
| UA-01…UA-12 | PENDIENTE | — | Completar al ejecutar |

**Dependencia:** TT-01 puede revelar herramientas/dependencias adicionales; reconciliar antes de cerrar UA-01.