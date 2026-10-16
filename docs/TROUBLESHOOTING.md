# Diagnóstico y recuperación — árboles de decisión no destructivos

Complementa [`docs/RECOVERY_STRATEGY.md`](RECOVERY_STRATEGY.md) (niveles 0-5 generales) con árboles específicos para los síntomas de esta pila concreta (loader `ps4-linux-loader` + distribución `PS4-Linux`), basados en `docs/BOOT_FLOW.md`. Regla general de todos los árboles: **cambiar una sola variable por intento, nunca repetir a ciegas la acción que produjo el error.**

Cada caso: síntoma → en qué fase de `BOOT_FLOW.md` ocurre → evidencia a recolectar → comprobaciones seguras → causas plausibles (con nivel de confianza) → condición de aborto → rollback.

---

## 1. USB no detectado por el loader (antes de enviar el payload)

**No aplica si el síntoma aparece después de enviar el payload** — ver caso 3.

- **Evidencia a recolectar (en la PC, sin tocar la consola):** `lsblk -f` o `Get-Partition`/`Get-Volume` sobre el USB; confirmar que la partición 2 tiene la etiqueta exacta `psxitarch` (sensible a mayúsculas) y que la partición 1 es FAT32.
- **Comprobaciones seguras:** reconectar el USB a otro puerto; probar el USB en otra PC para descartar que la escritura haya fallado a mitad de camino; verificar el hash SHA-256 de la imagen `.img` contra el que `build-img.sh` imprimió al finalizar (línea 41 del script).
- **Causas plausibles:**
  - Escritura incompleta/corrupta (`write-img.ps1` reportó `WRITE_FAILED` o un tamaño escrito distinto al esperado) — confianza alta si el log de la escritura no dice `WRITE_DONE_OK`.
  - Puerto USB 2.0 muy lento combinado con un USB de baja calidad — confianza media, sin evidencia de upstream sobre esto específicamente.
  - USB de menos de 16 GB — el README de la distribución documenta 16 GB como mínimo estricto.
- **Condición de aborto:** si el hash del `.img` no coincide con el calculado al construirlo, no escribir — reconstruir la imagen primero.
- **Rollback:** ninguno necesario; nada se escribió en la consola todavía.

## 2. Payload enviado, LED permanece blanca fija ("no kexec handoff")

**Fase de `BOOT_FLOW.md`:** 3-4 (envío del payload / handoff a Linux). **Evidencia de upstream:** este es exactamente el síntoma del issue [#11](https://github.com/ps4-linux/ps4-linux-loader/issues/11) de `ps4-linux-loader` (REPORTADO-TERCEROS, cerrado como resuelto).

- **Evidencia a recolectar:** firmware exacto y southbridge de la consola (si ya se determinaron en un intento anterior vía log/UART); método usado para enviar el payload (FTP a `/data/GoldHEN/payloads/` vs. `nc` directo al puerto del PayLoader); tamaño de VRAM del payload enviado; integridad del archivo `.elf` (tamaño exacto contra `docs/EVIDENCE_SOURCES.md`).
- **Comprobaciones seguras (no destructivas, se hacen en la PC o reenviando el mismo payload):**
  1. Confirmar que el `.elf` enviado coincide en tamaño (320 936 bytes) y, si es posible, en hash con el original — un archivo truncado por una transferencia FTP en modo texto en vez de binario es una causa real documentada en issue #11 (el reportante confirmó explícitamente "integridad de archivo" como parte de su descarte).
  2. Reintentar con el payload de 1024 MB de VRAM en vez de uno de los payloads "server" (32-512 MB) — la comunidad (issue #11, comentario de `naxyiandpoxyi`) recomienda 1024 MB como el tamaño "seguro" para una primera instalación; no hay explicación técnica confirmada de por qué los tamaños bajos fallarían más, así que tratar esto como heurística, no causa probada.
  3. Si se venía instalando leyendo el kernel desde el almacenamiento interno (`/data/linux/boot/`), tener el kernel en la FAT del USB (política USB-only, `BOOT_FLOW.md` Fase 2) — en el issue #11, lo que resolvió el caso fue "arrancar desde el USB" en vez del flujo que venía usando (según un comentario de otro usuario, instalar desde el disco de la PS4 no funciona). Es evidencia de terceros de que el camino USB funciona en su consola, no una prueba de aislamiento.
  4. Apagado completo (mantener el botón de power, no solo reiniciar), esperar, rehacer el jailbreak, reintentar sin cambiar nada más que un solo parámetro a la vez.
- **Causas plausibles, por confianza:**
  - Alta: archivo del payload corrupto/truncado por el método de transferencia.
  - Media: el exploit de ejecución en kernel (GoldHEN) no completó correctamente antes de lanzar el payload — no es un problema de este laboratorio, es de la capa de jailbreak.
  - Media: offsets de firmware incorrectos si el firmware real detectado no coincide con el que se asumía (`fw_detect.c` lee el firmware real desde `libc.sprx`, así que un error de detección es poco probable salvo build corrupta, pero no se puede descartar sin log).
  - Baja/sin evidencia directa: tamaño de VRAM específico como causa raíz — es una correlación reportada por un usuario, no una causa confirmada en el código.
- **Condición de aborto:** si tras 3 intentos limpios (cada uno cambiando una sola variable) la luz nunca pasa de blanca, detener y registrar el caso como `BLOCKED` en `docs/LAB_LOG_TEMPLATE.md` en vez de seguir reintentando — podría ser un problema de la capa de jailbreak, no de este payload.
- **Rollback:** apagado y reinicio normal; ninguna escritura persistente ocurrió si no se llegó a la Fase 4 de `BOOT_FLOW.md`.

## 3. Kernel inicia (hay señal de video o UART) pero el rootfs no monta

**Fase de `BOOT_FLOW.md`:** 5. **Síntoma documentado:** shell de rescate con mensaje `mounting LABEL=psxitarch failed`.

- **Evidencia a recolectar:** confirmar si el USB estaba conectado **antes** de encender la consola y durante todo el proceso (el README de la distribución es explícito: reconectar y reiniciar no ayuda — "resume-boot does not help" — hay que apagar completamente).
- **Comprobaciones seguras:** verificar en la PC que la partición 2 del USB siga teniendo la etiqueta `psxitarch` exacta (`lsblk -f` o `blkid`); descartar que el USB se haya desconectado físicamente o que el puerto USB de la consola tenga un contacto defectuoso.
- **Causas plausibles:**
  - Alta (documentada en el propio README): el USB no estaba conectado antes del encendido o se desconectó.
  - Media: la etiqueta de la partición se perdió o cambió (por ejemplo, si se usó una herramienta de partición en la PC entre un intento y otro).
  - Baja: filesystem ext4 dañado — solo investigar esto si las dos causas anteriores se descartaron.
- **Condición de aborto:** no ejecutar `fsck`/`e2fsck` en modo escritura desde dentro de la shell de rescate sin antes copiar en la PC una imagen de respaldo de la partición, si se sospecha corrupción real.
- **Rollback:** apagado completo, reconectar el USB correctamente, reintentar desde la Fase 3 de `BOOT_FLOW.md`.

## 4. Pantalla negra prolongada sin otro síntoma

Distinguir de los casos 2 y 3 — ver `docs/RECOVERY_STRATEGY.md` Nivel 2, que ya cubre esta separación en términos generales. Aquí, lo específico de esta pila:

- El propio README de la distribución documenta pantalla negra de 1-2 minutos como **normal** antes de llegar al login de KDE. No declarar fallo antes de ese tiempo.
- Si supera los 2-3 minutos sin cambio: revisar primero si la LED pasó de blanca a azul/violeta (caso 2) — si nunca pasó, es un fallo de handoff, no de video. Si sí pasó, es más probable un problema en la Fase 5 (initramfs/rootfs/driver de video), no en el exploit.
- El cmdline por defecto fuerza `video=HDMI-A-1:1920x1080@60` — si el monitor conectado no soporta esa resolución/frecuencia exacta, podría no haber señal aun con el kernel funcionando correctamente. Probar con un `bootargs.txt` que fuerce una resolución que el monitor confirme soportar (ver `docs/BOOT_FLOW.md` Fase 5).

## 5. GPU/video sin señal o con artefactos — posible causa de firmware/EDID

**Hallazgo de código relevante:** `UPSTREAM_CODE_MAP.md` §1.5 documenta un bug real, ya corregido en el commit auditado, sobre el cálculo del tamaño del EDID (PR #9 de `ps4-linux-loader`). Si se usa una build **anterior** a ese fix (por ejemplo, un release descargado antes de 2026-07-18), un monitor con bloques de extensión EDID atípicos podría producir un EDID truncado o con overflow, afectando la detección de modos de video.

- **Evidencia a recolectar:** versión/release exacta del loader usado (comparar contra la fecha del fix, 2026-07-18); modelo de monitor y si tiene múltiples bloques de extensión EDID (monitores con HDR, múltiples entradas, o G-Sync/FreeSync suelen tenerlos).
- **Comprobación segura:** si el loader usado es anterior al fix, actualizar al release más reciente antes de seguir investigando el monitor.
- **Causa plausible:** build del loader anterior al PR #9, combinada con un monitor con EDID extendido — confianza media, es una hipótesis razonable pero no hay un reporte de issue que la confirme explícitamente como causa de un caso real.

## 6. Red, audio o periféricos ausentes tras llegar al escritorio

No hay, en los issues consultados, reportes específicos de fallas de red/audio como síntoma aislado (el issue #10 reporta Wi-Fi y audio HDMI funcionando en su combinación específica). El README de la distribución sí documenta limitaciones conocidas, no bugs:

- **Bluetooth:** se debe re-emparejar el control **en cada arranque** — esto es comportamiento esperado documentado, no una falla a diagnosticar.
- **Wi-Fi:** el propio README dice "todavía en pruebas" y recomienda preferir 2.4 GHz — tratar cualquier problema de Wi-Fi en 5 GHz como un límite conocido, no como algo a resolver con prioridad en las primeras fases.
- **Suspensión/hibernación:** viene deshabilitada deliberadamente en la imagen lista para usar (dañaría el sistema según el README: "Suspending the console breaks this Linux"). Si se construye un rootfs propio, el README indica el comando exacto para enmascarar los targets de systemd correspondientes (`docs/BOOT_FLOW.md` no lo repite; ver README original citado en `EVIDENCE_SOURCES.md`).
- Si aparece un síntoma de audio/red/periférico **distinto** a estos límites conocidos, recolectar `dmesg`, `lspci`, `lsusb` y registrar como caso nuevo en `docs/LAB_LOG_TEMPLATE.md` — no hay evidencia upstream previa que lo explique.

## 7. Temperatura excesiva, cuelgues o reinicios bajo carga

Sin evidencia específica de upstream sobre esto en los issues consultados (ninguno de los 11 issues de `ps4-linux-loader` trata temperatura). Aplican íntegramente los principios generales de `docs/RECOVERY_STRATEGY.md` Nivel 3 y el riesgo R-08 de `docs/RISK_REGISTER.md`: inspección física del sistema de refrigeración antes de cualquier prueba de carga sostenida, y pruebas cortas incrementales en vez de cargas largas desde el primer intento. Esto queda como **hipótesis general de hardware reutilizado**, no como hallazgo de código.

## 8. Diferenciar "falla del USB" vs. "falla del kernel" vs. "falla del rootfs" vs. "incompatibilidad de firmware" — tabla resumen

| Observable | USB (medio) | Kernel/exploit | Rootfs/initramfs | Firmware/southbridge |
|---|---|---|---|---|
| LED nunca pasa de blanca | Posible si el `.elf` no llegó a ejecutarse por archivo corrupto | **Más probable** (caso 2) | No aplica — no se llegó tan lejos | Posible si no hay entrada en `fw_offsets.h` para ese FW exacto (el payload debería alertarlo, no quedar en blanco silenciosamente) |
| LED pasa a azul/violeta, luego pantalla negra permanente | Poco probable solo | Posible (fallo tras el handoff, antes de video) | **Más probable** si hay timeout largo sin cambio | Posible si el kernel elegido no corresponde al southbridge real |
| Llega a shell de rescate con error de montaje | **Más probable** (caso 3) | Descartado — el kernel ya inició | Posible si el initramfs busca una etiqueta distinta | No aplica |
| Escritorio carga pero sin un periférico puntual | Descartado | Descartado | Posible (driver/módulo faltante) | Posible (southbridge con soporte parcial, ver §1.6 de `UPSTREAM_CODE_MAP.md` sobre Belize2) |
