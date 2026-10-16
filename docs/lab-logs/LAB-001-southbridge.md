# Registro de laboratorio — LAB-001: southbridge

- Fecha: 2026-10-16
- Operador: Marcos
- Consola: PS4 Slim CUH-2115B
- Firmware: 13.52
- GoldHEN: v2.2.3, observado en pantalla About GoldHEN
- Método: navegador PS4 → WebKitty → GoldHEN; luego Ajustes → Sistema → Información del sistema.
- Resultado observado y comunicado por el operador: Southbridge Baikal B1, ID 0x30201.
- Evidencia: observación directa reportada en esta conversación. La captura original no está incorporada al repositorio ni tiene hash de archivo; conservar esta limitación.
- Kernel: no seleccionado formalmente ni ejecutado. Baikal 7.0.8 queda como candidato prioritario para revisión, no como kernel verificado.
- Initramfs/rootfs: combinación aún no validada para esta consola.
- USB físico: no escrito.
- Almacenamiento interno: no se hizo ninguna modificación intencional.
- Linux: no arrancado.
- Estado: IDENTIFICACIÓN DE SOUTHBIDGE COMPLETADA; selección y validación de kernel pendientes.

## Siguientes controles
1. Confirmar hashes, procedencia y versión real de los artefactos Baikal.
2. Auditar compatibilidad de kernel, initramfs y rootfs como una cadena indivisible.
3. Confirmar que el flujo de arranque sea estrictamente USB-only, sin fallback interno.
4. Revisar el diff de la rama opencode/ps4-usb-build-hardening y ejecutar sus pruebas en el commit exacto.
5. No escribir el USB físico ni iniciar Linux sin autorización específica posterior.