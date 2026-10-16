# Manifiestos de artefactos

El manifiesto registra la procedencia y la integridad esperada de archivos utilizados en el laboratorio. El verificador es de solo lectura: no descarga, instala, ejecuta, repara ni escribe en dispositivos.

## Formato

El esquema actual usa JSON con schema_version igual a 1 y una lista no vacía artifacts. Cada entrada requiere una ruta relativa segura y un SHA-256 de 64 caracteres hexadecimales. size_bytes es opcional pero recomendado.

\`\`\`json
{
  "schema_version": 1,
  "artifacts": [
    {
      "path": "artifacts/kernel.bin",
      "sha256": "REEMPLAZAR_POR_64_CARACTERES_HEXADECIMALES",
      "size_bytes": 123456
    }
  ]
}
\`\`\`

Las rutas se resuelven dentro del directorio raíz y no pueden usar rutas absolutas, segmentos .., separadores Windows ni enlaces simbólicos. Los archivos deben ser regulares.

## Uso

Desde la raíz del repositorio:

\`\`\`bash
python3 tools/verify_artifacts.py --manifest /ruta/a/tu-manifiesto.json --root .
python3 -m unittest discover -v
\`\`\`

Códigos de salida:
- 0: todos los artefactos pasaron.
- 1: al menos un archivo no coincide, falta o no es regular.
- 2: manifiesto inválido o ilegible.

## Límites de seguridad

- Un hash solo confirma igualdad con el valor del manifiesto; no autentica por sí solo al publicador ni la procedencia.
- El manifiesto debe obtener su hash esperado de una fuente confiable e independiente. Reemplazá la ruta de ejemplo del comando por el archivo JSON que creaste; el archivo manifests/artifacts.example.json contiene valores ficticios y no debe usarse como evidencia.
- El verificador no acepta dispositivos de bloques como artefactos normales y nunca abre archivos para escritura.
- No usar el manifiesto de ejemplo como evidencia: contiene valores ficticios.

## Catálogo de arranque (`manifests/arranque-catalogo.json`)

`tools/verify_boot_chain.py` usa un catálogo distinto del manifiesto de rutas: describe **qué archivos conocidos existen** (por hash) y a qué *release* pertenecen, para detectar mezclas de versiones y asociar un kernel con un southbridge documentado.

```json
{
  "schema_version": 1,
  "artefactos": [
    {"id": "...", "rol": "kernel|initramfs", "sha256": "<64 hex>", "size_bytes": 123,
     "release": "<identificador de la release de origen>",
     "southbridges": ["belize"], "evidencia_compatibilidad": "texto honesto del nivel de evidencia"}
  ]
}
```

Reglas: `schema_version` entero 1 (no booleano); `sha256` en minúsculas de 64 caracteres; `id` único; kernel e initramfs de `release` distinta se rechazan como mezcla; un southbridge desconocido deja la compatibilidad en `NO_EVALUADO`. Un hash del catálogo prueba igualdad con el valor registrado, no autenticidad ni que el artefacto arranque. El catálogo del repositorio solo contiene valores recalculados localmente (ver `docs/ARTIFACT_INVENTORY.md`).
