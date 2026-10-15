# Arquitectura objetivo

## Capas

1. **Consola original:** firmware, exploit/homebrew compatible y almacenamiento interno. No modificar durante el arranque inicial.
2. **Cargador/payload:** entrega control a un kernel Linux preparado para el hardware PS4.
3. **Kernel + initramfs:** soporte de southbridge, memoria reservada para GPU, salida de vídeo, buses y montaje del sistema raíz.
4. **Medio externo:** USB con partición de arranque e imagen/rootfs Linux.
5. **Sistema operativo:** distribución basada en Arch/PSXITArch u otra opción que la auditoría justifique.
6. **Stack gráfico:** kernel DRM/amdgpu adaptado, Mesa, OpenGL/Vulkan y compositor.
7. **Cargas de trabajo:** escritorio, emulación/juegos, servidor y experimentos LLM.

## Flujo conceptual

```text
PS4 + firmware identificado
        |
        v
Método de jailbreak compatible
        |
        v
Payload Linux compatible
        |
        v
Kernel + initramfs correctos para la revisión
        |
        v
Rootfs en USB externo
        |
        v
Diagnóstico de hardware y drivers
       / \
      v   v
Juegos  Inferencia LLM (solo si el backend funciona)
```

## Regla de separación

La selección de exploit/firmware y la selección de kernel/southbridge son problemas distintos. No elegir kernel solo a partir de “PS4 Fat”, “Slim” o “Pro”. Registrar la fuente exacta y el nivel de confianza de cada afirmación.

## Memoria y VRAM

El payload puede reservar una porción de memoria unificada para la GPU. Menos memoria reservada puede ayudar a tareas de servidor/CPU; más puede ser necesaria para gráficos. Esto es un parámetro experimental y no equivale a una GPU de PC con VRAM dedicada. Toda prueba debe registrar la reserva usada y la memoria restante.

## Persistencia y rollback

- Prioridad inicial: todos los artefactos Linux en almacenamiento externo.
- El almacenamiento interno se considera solo lectura desde la perspectiva del proyecto.
- Si un método de carga copia archivos de arranque al almacenamiento interno, documentar ese comportamiento y detenerse hasta evaluar si es aceptable.
- Cada experimento debe tener un procedimiento de retorno al sistema original.

## Telemetría mínima por prueba

- Modelo CUH y firmware.
- Revisión/southbridge conocido o hipótesis.
- Hash y versión del payload, kernel, initramfs e imagen.
- Perfil de VRAM reservada.
- Puerto de salida de vídeo, pantalla y HDCP si es relevante.
- Tiempo hasta señal de vídeo/escritorio.
- `dmesg`, versión de kernel, módulos, driver Mesa, temperaturas.
- Resultado, fallo observado y siguiente variable a modificar.
