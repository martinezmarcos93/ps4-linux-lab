# Guía de solución de problemas

Guía para recopilar evidencia y aislar fallos, no un procedimiento universal de reparación. No improvisar operaciones destructivas ni de firmware.

## Antes de diagnosticar
Registrar ID de experimento, modelo/firmware, hashes de loader/kernel/initramfs/rootfs, medio, cambios recientes, duración de espera y síntomas. No actualizar firmware como diagnóstico.

## USB no detectado
1. Inspeccionar el medio en PC sin formatearlo.
2. Revisar capacidad, particiones, filesystem, etiquetas y hash.
3. Confirmar puerto/ruta con documentación del loader versionado.
4. Comparar con el manifiesto esperado.
No reescribir la imagen a ciegas.

## Loader/payload no inicia
Registrar firmware, versión/hash y mensaje; confirmar que la tabla de soporte corresponde a esa versión; revisar procedencia y requisitos. Si no hay evidencia de compatibilidad con el firmware real, detenerse en lugar de probar payloads aleatorios.

## Pantalla negra/sin señal
Registrar indicadores, señal previa y tiempo. No concluir “brick” solo por pantalla negra. Distinguir entre no saber si comenzó el payload, kernel sin vídeo, kernel sin rootfs y userspace sin compositor. Cambiar una variable por intento. Abortar si hay síntomas nuevos del sistema original o haría falta escribir firmware/almacenamiento interno sin procedimiento verificado.

## Kernel aparentemente inicia pero no monta rootfs
Revisar logs de montaje; inspeccionar imagen en PC sin escritura; confirmar UUID/etiquetas/formato y correspondencia kernel/initramfs/rootfs; consultar la versión exacta del initramfs. No reparar filesystem montado en escritura ni cambiar varias variables a la vez.

## Consola de texto pero no escritorio
Capturar logs, servicios, espacio y estado gráfico; confirmar que la consola responde; identificar sesión/compositor/driver antes de reinstalar paquetes; verificar renderer hardware/software.

## Red, Wi-Fi, Bluetooth, audio o mando ausentes
Registrar qué subsistemas funcionan, inventariar interfaces/módulos/logs, revisar limitaciones para modelo/southbridge y probar un periférico por vez. Ethernet puede ser alternativa diagnóstica si está soportada.

## Temperatura, cuelgues o apagados
Detener carga, registrar duración/lecturas y revisar externamente ventilación. No ejecutar otro benchmark para confirmar ni inventar umbrales térmicos sin fuente justificada. Repetir solo tras entender el síntoma.

## Filesystem corrupto/apagado brusco
Evitar montaje en escritura cuando pueda conservarse evidencia, preservar copia del medio, registrar errores y verificar cuidadosamente el dispositivo antes de usar herramienta específica de filesystem. Conservar backup.

## Informe de fallo
Usar `docs/LAB_LOG_TEMPLATE.md`; adjuntar logs, hashes, versiones y pasos mínimos. Redactar credenciales, tokens y datos personales innecesarios.