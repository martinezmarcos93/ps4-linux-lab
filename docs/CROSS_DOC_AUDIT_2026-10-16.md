# Auditoría cruzada de documentación — 2026-10-16

**Rama:** `chatgpt/ps4-audit-roadmap`  
**Base comparada:** `main` en `e8c4b4e45f0ba7dce2da53afac96f1aea15fea40` al iniciar esta revisión.  
**Alcance:** lectura estática de roadmap, plan de pruebas, flujo de arranque, diseño USB-only, estrategia de recuperación, seguridad de herramientas y registro de decisiones.  
**No realizado:** ejecución de tests, descarga/inspección de artefactos locales, escritura USB, ejecución de payload ni prueba en PS4.

## Hallazgos corregidos

### A-001 — El plan de pruebas recomendaba el constructor upstream

**Hallazgo:** TP-03 recomendaba ejecutar `tools/build-img.sh`, aunque la documentación de seguridad identifica riesgos concretos en el script upstream (ruta de salida no validada, eliminación en ruta fija, limpieza incompleta y puntos de montaje fijos). La recomendación tampoco coincidía con la arquitectura de herramientas de solo archivo del proyecto.

**Cambio:** TP-03 ahora exige el generador auditado `tools/build_usb_image.py`, primero en `--dry-run`, con un kernel compatible y procedencia validada como precondiciones. Se aclara que el resultado host-side no prueba el arranque.

### A-002 — El plan de pruebas trataba la escritura física como paso operativo inmediato

**Hallazgo:** TP-04 indicaba ejecutar `tools/write-img.ps1` como administrador. La existencia de esa instrucción podía leerse como autorización operativa, aunque la política del laboratorio separa preparación de imagen y escritura destructiva.

**Cambio:** TP-04 queda explícitamente bloqueado hasta autorización concreta de Marcos, revisión de la imagen y confirmación inequívoca del dispositivo. No se ejecutó ninguna escritura.

### A-003 — D-008 describía como pendiente una compilación ya documentada

**Hallazgo:** el registro de decisiones seguía diciendo que compilar el parche USB-only estaba pendiente, mientras que `docs/LOADER_BUILD_REPRO.md` y `docs/USB_ONLY_DESIGN.md` documentan una compilación y revisión estática del 2026-10-16.

**Cambio:** D-008 ahora distingue compilación/revisión estática completadas de identidad bit a bit, ejecución en hardware y aislamiento en runtime aún no demostrados.

### A-004 — Alcance contradictorio de la inspección del initramfs

**Hallazgo:** `USB_ONLY_DESIGN.md` describía una inspección estática del `init` de better-initramfs 0.9.1, mientras que `BOOT_FLOW.md` decía que no se había auditado el script.

**Cambio:** `BOOT_FLOW.md` ahora registra la inspección estática parcial y sus límites; la imagen final todavía necesita verificación de hash/procedencia y no hay prueba de ejecución.

## Archivos modificados

- `docs/TEST_PLAN.md`
- `docs/DECISION_LOG.md`
- `docs/BOOT_FLOW.md`
- `docs/ROADMAP.md`
- `docs/RECOVERY_PLAN.md`

## Bloqueos que siguen vigentes

1. El southbridge de la CUH-2115B sigue desconocido.
2. No hay base suficiente para seleccionar un kernel para esa consola.
3. La compatibilidad exacta de kernel, initramfs y rootfs para el hardware concreto no está demostrada.
4. El aislamiento USB-only en runtime y la ausencia de escrituras al almacenamiento interno no están probados en la consola.
5. La auditoría estática del payload no equivale a una autorización para ejecutarlo.
6. No se ha construido una imagen final para la CUH-2115B.
7. No se ha escrito un USB físico ni realizado un intento de arranque.
8. Los cambios de esta rama son documentales; no se ejecutó `bash scripts/check.sh` ni otra suite de tests.

## Revisión antes de integrar

- Comparar este diff con los cambios simultáneos de Claude y OpenCode.
- Resolver conflictos por contenido, no mediante sobrescritura.
- Verificar las pruebas host-side en la máquina de desarrollo.
- Mantener las puertas de autorización de payload y escritura física independientes.
- No marcar ninguna tarea como `LAB` o `VERIFIED` sin un registro real de hardware con hashes y resultados observados.
