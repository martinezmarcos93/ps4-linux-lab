# Roadmap

Estados: `PLANNED`, `IN_PROGRESS`, `BLOCKED`, `VERIFIED`, `REJECTED`.

## Fase 0 — Inicialización del proyecto
**Estado:** IN_PROGRESS

- [ ] Crear `martinezmarcos93/ps4-linux-lab` como repositorio privado.
- [ ] Añadir este esqueleto en un commit inicial revisable.
- [ ] Proteger `main` y usar una rama temporal para cambios posteriores.
- [ ] Añadir plantillas de incidencias y un registro de decisiones.
- [ ] Definir política para artefactos grandes: no versionar imágenes USB ni rootfs.

**Puerta de salida:** repositorio privado creado, estructura revisada y referencias documentadas.

## Fase 1 — Inventario de la consola
**Estado:** BLOCKED — falta identificar la consola.

- [ ] Fotografiar la etiqueta de modelo CUH y registrar revisión visible.
- [ ] Consultar y registrar firmware exacto sin actualizarlo.
- [ ] Registrar si la consola arranca normalmente y si el lector/disco funcionan.
- [ ] Registrar síntomas de temperatura, ruido, apagados y conectores.
- [ ] Identificar capacidad y estado del almacenamiento sin borrarlo.
- [ ] Decidir si hace falta preservar partidas o datos.

**Puerta de salida:** ficha de hardware completa; sin acciones destructivas.

## Fase 2 — Auditoría de upstream y licencias
**Estado:** IN_PROGRESS

- [x] Leer los README de PS4-Linux y ps4-linux-loader.
- [x] Inspeccionar scripts de construcción de imagen y escritura USB.
- [ ] Revisar historial/release exactos que coincidan con la guía.
- [ ] Identificar licencia por repositorio y por componente.
- [ ] Comparar soporte declarado por firmware, southbridge y kernel.
- [ ] Registrar hashes y versiones de los artefactos elegidos.
- [ ] No reutilizar código sin confirmar la licencia aplicable.

**Puerta de salida:** matriz de compatibilidad con fuente y nivel de confianza.

## Fase 3 — Selección del método de arranque
**Estado:** BLOCKED — requiere fase 1.

- [ ] Confirmar si existe un exploit/payload compatible con el firmware registrado.
- [ ] Confirmar requisitos y riesgos del método seleccionado.
- [ ] Elegir kernel según revisión/southbridge; no inferir solo por “Fat/Slim/Pro”.
- [ ] Definir ruta de rollback para cada paso.
- [ ] Registrar qué cambios persisten en el sistema original, si los hubiera.
- [ ] Ensayar el procedimiento documentalmente antes de ejecutarlo.

**Puerta de salida:** procedimiento específico revisado; no genérico.

## Fase 4 — Herramientas seguras de preparación USB
**Estado:** PLANNED

- [ ] `inspect-host`: sistema operativo, herramientas disponibles, espacio y permisos.
- [ ] `verify-artifacts`: SHA-256, tamaño, formato y manifiesto.
- [ ] `inspect-disks`: lista discos con modelo, tamaño, bus, serial y particiones.
- [ ] `build-usb-image`: construcción en entorno temporal; no borrar archivos arbitrarios.
- [ ] `write-usb-image`: modo seguro, reidentificación del disco, doble confirmación.
- [ ] `verify-usb-image`: lectura de muestra o verificación completa posterior a escritura.
- [ ] `collect-diagnostics`: empaqueta logs sin secretos ni identificadores innecesarios.
- [ ] Tests con dispositivos virtuales/archivos de imagen; nunca con discos reales por defecto.

**Puerta de salida:** tests automáticos demuestran que los casos ambiguos o peligrosos abortan.

## Fase 5 — Preparación y primer arranque externo
**Estado:** BLOCKED — depende de fases 1–4.

- [ ] Crear imagen USB en una PC.
- [ ] Verificar hashes y estructura de particiones.
- [ ] Comprobar etiqueta de rootfs e initramfs.
- [ ] Confirmar ausencia de kernels ambiguos que puedan ser seleccionados por error.
- [ ] Ejecutar payload según procedimiento validado.
- [ ] Registrar indicador luminoso, pantalla, tiempos y resultado.
- [ ] Si falla, cambiar una sola variable por intento.
- [ ] Verificar reinicio normal a OrbisOS.

**Puerta de salida:** arranque Linux reproducible desde USB y retorno al sistema original.

## Fase 6 — Diagnóstico y estabilización
**Estado:** PLANNED

- [ ] Inventario de CPU, RAM, GPU, kernel, módulos y firmware.
- [ ] Probar Ethernet, Wi-Fi, Bluetooth, USB, audio HDMI y mando.
- [ ] Medir temperaturas y comportamiento de ventiladores.
- [ ] Desactivar suspensión/hibernación si el kernel no la soporta.
- [ ] Verificar integridad del filesystem tras apagado controlado.
- [ ] Definir perfiles de carga y límites térmicos conservadores.
- [ ] Documentar recuperación desde consola/rescue shell.

**Puerta de salida:** sesión estable y periféricos esenciales caracterizados.

## Fase 7 — Rendimiento gráfico y videojuegos
**Estado:** PLANNED

- [ ] Identificar driver y versión de Mesa.
- [ ] Capturar `glxinfo -B`, `vulkaninfo --summary` si aplica, `dmesg` y módulos.
- [ ] Confirmar si el render es hardware o software.
- [ ] Ejecutar pruebas gráficas breves y reproducibles.
- [ ] Probar emuladores/juegos individualmente, con FPS, resolución, temperatura y estabilidad.
- [ ] Distinguir compatibilidad del juego, rendimiento y estabilidad del sistema.

**Puerta de salida:** matriz de resultados; no asumir compatibilidad por tener escritorio.

## Fase 8 — GPU compute y LLM
**Estado:** PLANNED; investigación de alto riesgo técnico.

- [ ] Identificar APIs de cómputo realmente disponibles en la GPU.
- [ ] Comprobar compatibilidad de Vulkan/OpenCL/ROCm u otros backends sin asumir soporte.
- [ ] Evaluar primero inferencia CPU como baseline.
- [ ] Probar un modelo pequeño cuantizado con parámetros registrados.
- [ ] Medir tokens/s, RAM disponible, VRAM reservada, latencia, temperatura y errores.
- [ ] Comparar GPU frente a CPU; abandonar aceleración GPU si el coste de compatibilidad supera el beneficio.
- [ ] No instalar toolchains pesadas antes de validar la base gráfica.

**Puerta de salida:** benchmark reproducible y conclusión basada en mediciones.

## Fase 9 — Automatización de reparación
**Estado:** PLANNED

- [ ] Árbol de diagnóstico por síntoma.
- [ ] Modo `--dry-run` obligatorio en utilidades de reparación.
- [ ] Backups antes de editar configuración.
- [ ] Restauración atómica de archivos.
- [ ] Recolección de logs con redacción de datos sensibles.
- [ ] Pruebas de fallo inducido sobre imágenes de laboratorio.
- [ ] Runbook de pantalla negra, kernel incorrecto, USB no detectado, rescue shell, red y filesystem.
- [ ] Separar recuperación de Linux de recuperación del firmware de PS4.

**Puerta de salida:** cada reparación tiene precondiciones, validación posterior y rollback.

## Fase 10 — Decisión de uso final
**Estado:** PLANNED

- [ ] Comparar utilidad real como mini-PC, consola de emulación y servidor headless.
- [ ] Comparar coste/consumo/ruido con hardware alternativo disponible.
- [ ] Definir si vale la pena mantenerlo permanentemente en Linux o usar arranque ocasional.
- [ ] Documentar limitaciones no resueltas y tareas descartadas.
