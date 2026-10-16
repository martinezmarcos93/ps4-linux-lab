# Validación CI host-side — 2026-10-16

## Resultado

- Workflow: **Host-side tests**
- Run: [#53](https://github.com/martinezmarcos93/ps4-linux-lab/actions/runs/38926947822)
- Commit consultado: `b6b46937e2c3799079517b28ec03f0c19811215a`
- Estado del run: `completed`
- Conclusión: `success`
- Job: `unittest`, concluido correctamente.

Los pasos reportados como exitosos fueron:
1. Checkout del repositorio.
2. Configuración de Python.
3. Ejecución de pruebas unitarias.
4. Comprobación de coherencia documental.

## Alcance y límites

Este resultado confirma que los pasos configurados en ese workflow terminaron correctamente para el commit consultado. No equivale a una prueba de arranque en PS4, no valida el comportamiento real del loader/kernel y no demuestra que el sistema en ejecución evite el almacenamiento interno.

Tampoco demuestra por sí solo que los artefactos candidatos tengan procedencia/licencia suficiente. La decisión del workstream 05 sigue siendo **NO-GO para prueba física** hasta cerrar las puertas de compatibilidad, procedencia/licencias y auditoría de initramfs/rootfs.

## Corrección de estado documental

Esta nota supersede las menciones anteriores en los documentos del workstream que indican que la CI de los cambios de endurecimiento seguía pendiente. No se modificó `main`, no se fusionó ningún PR y no se usaron dispositivos físicos.

## Incidente posterior — run #58

La ampliación de pruebas de contrato del parche tuvo un fallo de test: la aserción buscaba llamadas a archivos opcionales en todo el texto del parche, por lo que también coincidía con las líneas eliminadas del upstream. Se corrigió para examinar únicamente las líneas añadidas por el parche. Este cambio corrige el test, no altera el código C propuesto.

- Run fallido: [#58](https://github.com/martinezmarcos93/ps4-linux-lab/actions/runs/38927608404).
- La validación del commit que contiene la corrección debe confirmarse en una ejecución posterior; hasta entonces, el estado de CI del último head queda pendiente.
- El parche C sigue sin aplicarse ni compilarse en un checkout upstream. 
