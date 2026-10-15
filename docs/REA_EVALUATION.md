# Evaluación de REA (`morluto/rea`)

- **Fecha de auditoría:** 2026-10-15. Repo clonado en carpeta aislada, solo lectura (commit abreviado registrado como `6183544`). La fecha `2026-10-16` que figuraba junto a ese commit es posterior a la fecha de auditoría y queda pendiente de verificar; no se usa como hecho confirmado. No se instaló nada ni se ejecutó `npx rea-agents setup`.
- **Qué es:** servidor MCP de ingeniería inversa que conecta un agente con Ghidra, Hopper o IDA (y herramientas de binarios, JavaScript/Electron, APK, firmware, capturas, etc.). Licencia MIT. Análisis local, según su README.
- **Instalación:** `npx rea-agents setup` **modifica la configuración de los agentes** (registra el servidor MCP y un skill, con backups). Requiere Node 22+/24+/26+ (hay Node 24.20 local).

## Requisitos para nuestro caso (desensamblar `goldhen.bin`)
- Un proveedor nativo: **Ghidra, Hopper o IDA**. En esta máquina **no hay Ghidra ni Java instalados** (verificado con `which`). Habría que instalarlos: Ghidra necesita JDK. Alternativas más ligeras que REA soporta con "caller-supplied": `objdump` GNU y Rizin.
- Un `.bin` crudo x86-64 sin cabecera: hay que indicar arquitectura y dirección base manualmente. REA no lo resuelve solo.

## Utilidad real
| Uso | Valor |
|---|---|
| Desensamblar/leer `goldhen.bin` y ver qué parchea del kernel, si abre sockets o toca el disco | **Alto**, pero el valor viene de Ghidra/Rizin, no de REA. REA añade comodidad para que un agente consulte el desensamblado con evidencia. |
| Análisis estático de `jb.js` (JavaScript) | Bajo: ya está leído a mano; son archivos chicos y sin ofuscar. |
| Analizar el firmware de la PS4 | **No aplica**: no tenemos el firmware. |
| Identificar el CUH/southbridge | **No aplica**: es un dato de hardware. |

## Riesgos / consideraciones
- **Superficie de confianza:** es un paquete grande (366 KB de CHANGELOG, árbol `third_party`, `install.sh`) que se registra como herramienta de un agente con permisos. Habría que auditarlo antes de dar acceso, como cualquier dependencia (ver skill `dependency-auditor`: necesidad, licencia, mantenimiento, seguridad, peso).
- **Su propio DISCLAIMER** excluye eludir protecciones técnicas, tamperar servicios online y cheats. Auditar un payload de terceros para entender qué hace en nuestra propia consola es un uso de análisis/seguridad, pero cualquier uso para evadir protecciones de Sony queda fuera.
- Es un proyecto muy joven y cambia rápido (commits diarios), no hay estabilidad que citar.

## Veredicto
**Se puede usar, pero no hace falta todavía y no es lo primero.** Para auditar `goldhen.bin` alcanza con Ghidra o Rizin directamente, sin dar a un agente un servidor MCP nuevo. REA se justifica si se quiere que el agente haga el análisis iterativo con evidencia. Recomendación: decidir primero (a) si vale la pena auditar el binario o descartar esta ruta, y (b) en ese caso instalar solo el proveedor (Rizin o Ghidra) y pasar REA por `dependency-auditor` antes de `npx rea-agents setup`.
