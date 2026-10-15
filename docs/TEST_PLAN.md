# Plan de pruebas

Casos concretos, derivados de `docs/BOOT_FLOW.md`, `docs/TROUBLESHOOTING.md` y `docs/GPU_AND_LLM_RESEARCH.md`. Cada caso usa la plantilla de `docs/LAB_LOG_TEMPLATE.md` para su registro real; este documento solo define **qué** probar, **en qué orden**, con qué precondición y qué evidencia guardar — no sustituye al registro de ejecución.

Ningún caso de este plan se ha ejecutado todavía. Ninguno puede marcarse `VERIFIED` sin una entrada de log real con hashes y resultado observado.

## TP-01 — Identificación de hardware (precondición de todo lo demás)

- **Precondición:** consola disponible, apagada, se puede ver la etiqueta trasera sin desarmar nada.
- **Pasos:** fotografiar/anotar el modelo CUH exacto y su revisión si es visible; encender en modo normal y registrar el firmware en Ajustes → Sistema → Información del sistema; **no actualizar**.
- **Resultado esperado:** modelo CUH y firmware exactos registrados en `docs/LAB_LOG_TEMPLATE.md`.
- **Evidencia a guardar:** foto de la etiqueta (sin datos de cuenta visibles), captura de la versión de firmware.
- **Condición de aborto:** si la consola pide actualizar al encenderla, no aceptar — desconectar red si es necesario y registrar el bloqueo.

## TP-02 — Verificación de artefactos descargados (en la PC, sin consola)

- **Precondición:** TP-01 completo (para saber qué kernel/southbridge buscar).
- **Pasos:** descargar únicamente desde `Releases` de cada repositorio (ver `docs/EVIDENCE_SOURCES.md`); calcular SHA-256 de cada archivo y compararlo contra los valores de esta auditoría (`docs/UPSTREAM_CODE_MAP.md` §2.3) o contra el manifiesto que el propio `build-img.sh` imprime.
- **Resultado esperado:** todos los hashes coinciden; tamaños de archivo coinciden con los declarados en el README (`psxitarch.tar.xz` 2.8 GB, `kernel.zip` 36.4 MB, `payloads.zip` 185 KB, `tools.zip` 5 KB).
- **Condición de aborto:** cualquier hash o tamaño que no coincida — no continuar con ese archivo, volver a descargarlo desde la fuente oficial.

## TP-03 — Construcción de imagen USB (en la PC, sin consola)

- **Precondición:** TP-02 completo; entorno Linux o WSL disponible; USB de prueba de al menos 32 GB (recomendado) dedicado, sin datos importantes.
- **Pasos:** ejecutar `tools/build-img.sh` con los argumentos documentados en `docs/BOOT_FLOW.md` Fase 1; registrar el hash SHA-256 que el script imprime al final.
- **Resultado esperado:** archivo `.img` de ~12 GB generado, hash registrado.
- **Evidencia a guardar:** salida completa del script, hash final.
- **Condición de aborto:** cualquier error de `sfdisk`/`mkfs`/`tar` antes de llegar a `BUILD_IMG_OK` — no continuar a TP-04 con una imagen a medio construir.

## TP-04 — Escritura del USB (en la PC, Windows, sin consola)

- **Precondición:** TP-03 completo; disco USB físico identificado y confirmado como no-booteable/no-sistema vía `Get-Disk`.
- **Pasos:** ejecutar `tools/write-img.ps1` como Administrador, confirmando el número de disco manualmente (sin `-Force` en la primera vez).
- **Resultado esperado:** `WRITE_DONE_OK` en la salida; tamaño escrito igual al tamaño de la imagen.
- **Evidencia a guardar:** salida completa del script.
- **Condición de aborto:** el script mismo aborta si el disco no es USB o es de arranque/sistema — no hay override seguro para eso; si aborta, verificar el número de disco con `Get-Disk` de nuevo antes de reintentar.

## TP-05 — Decisión de ubicación del kernel (bloqueante, requiere autorización explícita)

- **Precondición:** TP-01 a TP-04 completos; **decisión D-008 de `docs/DECISION_LOG.md` resuelta** (Opción A: FTP a `/data/linux/boot/`, u Opción B: USB-only).
- **Este caso no tiene "pasos" todavía** — es el punto donde el roadmap se detiene hasta que Marcos decida, porque la Opción A modifica el almacenamiento interno de la consola (ver `docs/BOOT_FLOW.md` Fase 2).
- **Resultado esperado:** una decisión registrada, no una ejecución.

## TP-06 — Primer intento de arranque (en la consola, con USB)

- **Precondición:** TP-05 resuelto y ejecutado (kernel ubicado según la opción elegida); jailbreak/GoldHEN funcionando en la consola (fuera de alcance de este laboratorio, pero precondición dura).
- **Pasos:** conectar el USB antes de encender; jailbreak; enviar `payloads/linux-1024mb.elf` (tamaño recomendado para un primer intento, ver `docs/TROUBLESHOOTING.md` caso 2) vía el método elegido (PayLoader/`nc` o carpeta de GoldHEN); cronometrar el cambio de LED y el tiempo hasta video.
- **Resultado esperado:** LED pasa a azul/violeta en ~15 s; pantalla negra normal de hasta 2 minutos; login de KDE Plasma.
- **Evidencia a guardar:** tiempos exactos observados, fotos/video de la LED si es posible, cualquier mensaje visible.
- **Condición de aborto:** si la LED no cambia en 20+ segundos, seguir el árbol del caso 2 de `docs/TROUBLESHOOTING.md` — no reintentar la misma combinación sin cambiar una variable.
- **Variable única a cambiar en reintentos:** en este orden — (1) método de transferencia del payload, (2) verificar integridad del `.elf`, (3) ubicación del kernel (si la Opción A/B lo permite probar ambas).

## TP-07 — Validación de retorno al sistema original

- **Precondición:** TP-06 alcanzó al menos la Fase 4 de `BOOT_FLOW.md` (handoff ocurrió), independientemente de si llegó a escritorio.
- **Pasos:** reiniciar la consola y confirmar que arranca OrbisOS normalmente, sin errores, sin pedir restauración.
- **Resultado esperado:** la consola vuelve a su sistema original sin intervención adicional.
- **Condición de aborto/escalación:** si la consola no vuelve a arrancar normalmente, este deja de ser un problema de este laboratorio — es un Nivel 5 de `docs/RECOVERY_STRATEGY.md` (fuera de alcance de los scripts automáticos); detener todo intento adicional y documentar el estado exacto antes de buscar un procedimiento específico verificado.

## TP-08 — Inventario de hardware/drivers desde dentro de Linux

- **Precondición:** TP-06 exitoso (login alcanzado).
- **Pasos:** ejecutar la secuencia de la sección 2 de `docs/GPU_AND_LLM_RESEARCH.md` (`lspci -k`, `dmesg`, `glxinfo -B`, `vulkaninfo --summary`, `free -h`, lectura de VRAM del driver, temperatura si hay sensor).
- **Resultado esperado:** inventario completo registrado, incluyendo la confirmación de `GetSouthbridgeName()` si se pudo capturar el log temprano del payload (UART) — este es el dato que permitiría avanzar las filas "Untested" de `docs/COMPATIBILITY_MATRIX.md`.
- **Evidencia a guardar:** salida completa de cada comando.

## TP-09 — Prueba gráfica mínima reproducible

- **Precondición:** TP-08 completo, con renderizado por hardware confirmado (no `llvmpipe`).
- **Pasos:** correr `glmark2` y/o `vkmark`/`vkcube` dos veces en arranques separados.
- **Resultado esperado:** FPS/puntaje registrado con baja varianza entre corridas (coherente con el reloj de GPU fijo documentado en `GPU_AND_LLM_RESEARCH.md` §1); cualquier varianza alta se investiga antes de reportar un número.
- **Condición de aborto:** renderer software detectado — detener y resolver el driver antes de seguir con benchmarks.

## TP-10 — Baseline de inferencia LLM en CPU

- **Precondición:** TP-08 completo.
- **Pasos:** compilar `llama.cpp` sin ningún backend GPU; correr un modelo pequeño cuantizado (GGUF, ~1-3B parámetros, 4 bits) con un prompt fijo y reproducible.
- **Resultado esperado:** tokens/s de generación y de prompt processing registrados, con uso de RAM y temperatura.
- **Esto es el piso de comparación obligatorio antes de TP-11.**

## TP-11 — Exploración de backend GPU para LLM (exploratorio, puede terminar en descarte documentado)

- **Precondición:** TP-10 completo; investigación bibliográfica adicional sobre backends de cómputo para GCN1/GCN4 (fuera del alcance de código auditado en esta sesión).
- **Pasos:** según lo que la investigación previa encuentre — no se prescribe un backend concreto todavía.
- **Resultado esperado:** o bien una medición comparable contra TP-10, o bien una entrada en `docs/DECISION_LOG.md` documentando por qué se descarta, con la evidencia que lo sostiene.

## Orden de dependencia resumido

```text
TP-01 -> TP-02 -> TP-03 -> TP-04 -> TP-05 (decisión) -> TP-06 -> TP-07
                                                            |
                                                            v
                                                   TP-08 -> TP-09
                                                            |
                                                            v
                                                   TP-10 -> TP-11
```


## Resultados de ejecución host-side

| Fecha | Suite | Resultado | Alcance/límite |
|---|---|---|---|
| 2026-10-15 | `python -m unittest discover -v` sobre el primer verificador de artefactos | **11/11 PASS** en sandbox local | Incluye hashes, tamaño, archivo ausente/vacío, manifiesto inválido y rutas inseguras. No prueba dispositivos físicos ni arranque PS4. El resultado del workflow CI de GitHub debe comprobarse por separado. |
