# Hallazgo transversal: datos de red en documentación pública

**Fecha:** 2026-10-16  
**Archivo revisado:** `docs/lab-logs/LAB-000-identificacion-consola.md` en la rama pública `main`.  
**Clasificación:** revisión de privacidad/publicación; no es una credencial ni una vulnerabilidad de ejecución.

El registro de identificación contiene identificadores de red del equipo/consola, hostname local y dirección IP privada. No son necesarios para justificar el modelo CUH, firmware o estado de compatibilidad; su publicación aumenta la huella identificable del entorno doméstico.

## Acción recomendada

1. En la rama de gobernanza, sustituir estos valores por marcadores neutros (por ejemplo, `[MAC LAN redactada]`, `[MAC Wi-Fi redactada]`, `[hostname local redactado]`, `[IP privada redactada]`) y conservar solo la metodología y los resultados que importan al laboratorio.
2. Buscar si los mismos valores aparecen en otros documentos, capturas, logs, commits o manifests; no copiar los valores en el informe de auditoría.
3. No publicar capturas de pantalla con esos identificadores visibles.
4. Recordar que editar el archivo en un commit nuevo no elimina el contenido de commits históricos. No reescribir historial ni borrar referencias sin autorización expresa del propietario y evaluación de enlaces/colaboradores.
5. Verificar el resultado en el diff público y dejar constancia de qué se redactó, sin volver a incluir los valores originales en el reporte.

**Estado:** pendiente de corrección por el responsable de `workstream/01-docs-governance`. Esta nota no modifica `main` ni el log original.
