# Autorización y procedimiento para identificar el southbridge

- Fecha: 2026-10-16.
- Consola objetivo: PS4 Slim CUH-2115B, firmware 13.52.
- Autorización: Marcos autoriza expresamente todas las acciones técnicas necesarias para descubrir el kernel compatible, incluida la identificación del southbridge por software mediante GoldHEN o lectura de `hw.sce_subsys_subid`, y la ejecución del exploit/payload necesario para esa lectura. Esta autorización no autoriza escribir en el almacenamiento interno, escribir físicamente una imagen USB, ni arrancar Linux: esos son pasos distintos y no necesarios para leer el southbridge.
- Estado de ejecución: no se ha ejecutado nada en la consola desde esta autorización; requiere acción física local de Marcos, pues ChatGPT no tiene control remoto de la consola.

## Orden de preferencia para la identificación

1. **GoldHEN UI, si ya está disponible y funcional:** revisar `Ajustes → Sistema → Información del sistema` y buscar `Southbridge`. GoldHEN documenta la opción “Southbridge Info” desde la versión 2.2.3. Registrar el nombre/código exactamente como aparece y fotografiar la pantalla si es posible. No inferir el resultado.
2. **Lectura directa del ID por software:** si la interfaz no expone el dato, auditar primero el artefacto lector y su procedencia/hash. El método documentado consulta `hw.sce_subsys_subid`; registrar el ID hexadecimal crudo además del nombre decodificado. No usar un binario de procedencia desconocida sin inspección.
3. **Validación cruzada:** comparar el resultado con la tabla de IDs del loader y con la documentación de hardware. Si nombre e ID no coinciden, detener la selección y resolver la discrepancia.

## Mapeo de IDs documentado por el código del loader

- `0x10100–0x10300`: Aeolia.
- `0x20100 / 0x20200`: Belize.
- `0x30100–0x30201`: Baikal.
- `0x40100`: Belize2.

Los valores deben registrarse como lectura observada, no como inferencia. No confundir Belize con Belize2.

## Puertas posteriores

- Si el resultado es **Baikal B1 / 0x30201**, revisar primero los kernels Baikal existentes y la evidencia específica para CUH-2115B + firmware 13.52. El kernel 7.0.8 disponible es solo candidato débil hasta confirmar procedencia y compatibilidad.
- Si el resultado es **Belize2 A0 / 0x40100**, no seleccionar el kernel Belize 7.1.7 por semejanza de nombre: la evidencia actual no declara soporte explícito para Belize2. Buscar un kernel con soporte Belize2 documentado y revisar fuentes/hashes.
- Si el resultado es **Belize** u otro ID, cotejarlo contra el modelo y las fuentes antes de escoger.
- No construir una imagen final, ejecutar Linux ni escribir medios físicos como consecuencia automática de identificar el southbridge. Primero actualizar el registro de laboratorio y la matriz de compatibilidad.

## Evidencia pública consultada

- GoldHEN / ConsoleMods Wiki: la función “Southbridge Info” se documenta en GoldHEN 2.2.3 y muestra el codename en Ajustes → Sistema → Información del sistema: https://consolemods.org/wiki/PS4:GoldHEN
- Loader: el proyecto declara soporte de payload para firmware 5.05–13.52 y documenta detección runtime de southbridge: https://github.com/ps4-linux/ps4-linux-loader
- Reporte de terceros para firmware 13.52 y Baikal: https://github.com/ps4-linux/ps4-linux-loader/issues/10. Ese reporte prueba únicamente la combinación que el autor ensayó (CUH-2208B, Baikal, kernel 5.4.247), no esta CUH-2115B ni los kernels locales 7.x.

## Registro de resultado

- Southbridge/código leído: PENDIENTE.
- Método empleado y versión exacta de GoldHEN/lector: PENDIENTE.
- Evidencia (captura/log): PENDIENTE.
- Kernel seleccionado: NO SELECCIONADO.
