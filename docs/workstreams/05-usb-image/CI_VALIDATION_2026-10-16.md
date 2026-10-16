# Validación CI host-side — 2026-10-16

## Estado vigente

- Run #53: [resultado](https://github.com/martinezmarcos93/ps4-linux-lab/actions/runs/38926947822) — **success** para el commit `b6b46937e2c3799079517b28ec03f0c19811215a`.
- Run #58: [resultado](https://github.com/martinezmarcos93/ps4-linux-lab/actions/runs/38927608404) — **failure** por una aserción estática que coincidía también con líneas eliminadas del parche.
- Run #61: [resultado](https://github.com/martinezmarcos93/ps4-linux-lab/actions/runs/38927741956) — **success** para `ee1df08e47970314213d8cd063478490a1c01971`; las pruebas unitarias y la coherencia documental finalizaron correctamente.
- Run #62: [resultado](https://github.com/martinezmarcos93/ps4-linux-lab/actions/runs/38927771709) — **success** para el cambio documental posterior.
- Run #64: [resultado](https://github.com/martinezmarcos93/ps4-linux-lab/actions/runs/38928578354) — **success** para el commit `1355836a08e1e1ef92bbdf36dc66c2fb7c71975d`, que incluye el plan integrado de barridos y esta actualización del registro CI.

La falla #58 se corrigió para examinar solo las líneas añadidas del parche. La suite host-side está verde en #61, #62 y #64; el run #64 ejecutó los tests unitarios y la comprobación de coherencia documental. Esto no valida el código C upstream.

## Qué demuestra y qué no

La CI confirma que los tests configurados del laboratorio y la comprobación documental pasan en esos commits. Los tests de `loader-read-file-hardening-f70f43a.patch` validan el texto del diff, los contadores de hunks y algunas invariantes declaradas. **No** aplican el parche a un checkout limpio, no compilan el loader y no inyectan fallos de E/S.

Por lo tanto, la propuesta C sigue sin estar validada como código aplicable/compilable. El estado de la CI del repositorio no elimina las puertas pendientes de compatibilidad, procedencia/licencias, revisión de initramfs/rootfs y prueba de arranque.

## Decisión vigente

**GO** para análisis estático y pruebas sintéticas host-side. **NO-GO** para prueba física de la consola con el conjunto actual.

No se modificó `main`, no se fusionó ningún PR, no se ejecutaron payloads y no se escribieron dispositivos físicos ni almacenamiento interno.
