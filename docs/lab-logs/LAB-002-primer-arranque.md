# Registro de laboratorio — LAB-002: primer intento de arranque Linux USB-only

- Fecha: 2026-10-18
- Operador: Marcos. **Autorización explícita del primer arranque dada por Marcos en la sesión del 2026-10-18**, con las condiciones de red de abajo.
- Consola: PS4 Slim CUH-2115B, FW 13.52, Baikal B1 (`0x30201`, `OBSERVADO`).
- Imagen en el pendrive: `candidata-baikal.img` sha256 `1b3330f1f1cba0ee8d165b6f0d58c12c16112516a30ba5071de62f583ca85a9f`, releída del dispositivo tras grabar y coincidente (pendrive STORE N GO, 14,9 GB). Manifiesto: `manifests/candidata-baikal-2026-10-17.json`.
- Kernel: `bzImage-baikal-7.0.8` `46c835f7…565b1ba8`. Initramfs `3f373bd6…9169b`.
- Payload a enviar: `linux-1024mb.elf` USB-only `a0d1eadb962bcde701a74285182c2426493789c6e0677a49d2a7c0e5b29ddbde`.
- Exploit servido: raw13g@9ba2f07, `goldhen.bin` `df3f27c1…ea12`, verificado contra manifiesto antes de servir (`tools/ps4lab.py serve`).
- Red (desviación aceptada por Marcos respecto al plan de cable directo): PS4 en Wi-Fi con DNS manual `127.0.0.1`; sin aislamiento comprobable. Apagado completo, sin modo reposo. Servidor en 192.168.1.69:8080. Log del servidor: `PS4-Linux-artefactos/logs/serve-2026-10-18.log`.
- Criterios de aborto: la PS4 pide actualizar o conectarse a PSN; cualquier escritura/formateo del disco interno; hash distinto; comportamiento imprevisto. Luz: blanco→azul en ~15 s indica arranque del kernel; blanco >20 s: apagar y reintentar una vez.

## Resultado
(pendiente: se completa con lo observado)
