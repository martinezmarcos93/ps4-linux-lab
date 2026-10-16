# Registro de laboratorio — LAB-001: southbridge

- Fecha: 2026-10-16
- Operador: Marcos
- Consola: PS4 Slim CUH-2115B
- Firmware: 13.52
- GoldHEN: v2.2.3, observado en pantalla About GoldHEN
- Método: navegador PS4 → WebKitty → GoldHEN; luego Ajustes → Sistema → Información del sistema.
- Resultado observado y comunicado por el operador: Southbridge Baikal B1, ID 0x30201.
- Evidencia: observación directa reportada en esta conversación. La captura original no está incorporada al repositorio ni tiene hash de archivo; conservar esta limitación.
- **Nota de consolidación:** una versión anterior de este registro (rama `chatgpt/ps4-audit-roadmap`) afirmaba GoldHEN `v2.4b18.12` y hashes SHA-256 concretos de capturas. Esa cifra de versión y esos hashes no están respaldados por evidencia verificable en este repositorio y contradicen lo que `docs/AUDITORIA_CADENA_BAIKAL.md` §3.7 (riesgo R-23) documenta como pendiente ("capturar la pantalla *About* y calcular el hash del archivo realmente cargado"). Se descartan esos datos no verificados; ver R-23 para la inconsistencia de versión real conocida.
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
4. Resolver R-23: capturar la pantalla *About* de GoldHEN y calcular el hash del binario realmente cargado (la versión reportada en pantalla no coincide con la que se autodeclara en el binario de raw13g).
5. No escribir el USB físico ni iniciar Linux sin autorización específica posterior.

## Límites de evidencia
- La pantalla confirma la identificación que reporta GoldHEN, pero no demuestra que el kernel candidato arranque en esta unidad.
- La presencia de soporte Baikal en el kernel es un indicador de compatibilidad potencial, no una prueba de funcionamiento.
- La seguridad USB-only requiere revisar loader, kernel, initramfs y rootfs; no se infiere solo de que la imagen se cree en la PC.
- No se ha escrito ningún USB físico ni ejecutado un nuevo payload como parte de este trabajo.

## Referencias
- `docs/AUDITORIA_CADENA_BAIKAL.md`
- `docs/PLAN_VALIDACION_BAIKAL.md`
- `docs/USB_ONLY_DESIGN.md`
