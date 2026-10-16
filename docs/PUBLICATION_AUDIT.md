# Auditoría de publicación pública

**Fecha:** 2026-10-16  
**Repositorio:** https://github.com/martinezmarcos93/ps4-linux-lab  
**Visibilidad comprobada:** pública  
**Rama principal:** `main`

## Objetivo

Adaptar el repositorio a una audiencia pública sin presentar investigación como funcionamiento demostrado, sin exponer información sensible y sin confundir la publicación del código propio con permiso para redistribuir componentes upstream.

## Hallazgos del barrido

- El README describía el laboratorio como “privado”; se actualizó para describirlo como proyecto público.
- El estado de consola se unificó en PS4 Slim CUH-2115B, firmware 13.52, capacidad observada 861,4 GB y southbridge desconocido.
- El estado funcional queda explícito: no hay arranque Linux propio verificado.
- USB-only se presenta como objetivo de diseño; el aislamiento completo no está demostrado.
- La investigación y los tests host-side no se anuncian como compatibilidad real.
- La política de licencias se mantiene por componente; la publicación no cambia derechos sobre código o binarios de terceros.
- Se actualizaron README, guía de contribución y roadmap.
- La descripción y los topics del campo About de GitHub requieren una revisión de configuración separada si no se dispone de una acción autorizada para modificar metadatos.
- CI y tests necesitan estado actual verificable; el diagnóstico anterior puede quedar obsoleto.

## Checklist de publicación

- [x] README orientado a público y con estado funcional explícito.
- [x] Instrucciones de contribución adaptadas a un repositorio público.
- [x] Roadmap reestructurado con fases, bloqueos y puertas de seguridad.
- [x] Informe de estado y estimación de avance.
- [ ] Revisión automatizada de todos los enlaces internos y referencias de ruta.
- [ ] Inspección completa de archivos publicados para detectar secretos, datos personales y logs sensibles.
- [ ] Confirmar la licencia del propio repositorio y añadir un archivo de licencia solo tras decidir qué licencia aplicar al código propio.
- [ ] Configurar descripción y topics en GitHub About.
- [ ] Confirmar CI ejecutándose correctamente y publicar un badge solo cuando sea veraz.
- [ ] Revisión de dependencias y avisos de licencia antes de distribuir binarios.

## Descripción sugerida para GitHub About

`Researching Linux on PS4 with a USB-only goal, static audits, reproducible tooling, and hardware compatibility studies. Experimental; boot not yet verified.`

## Topics sugeridos para GitHub

Usar topics normalizados, en minúsculas y sin `#`:
`ps4-linux`, `playstation-4`, `linux`, `homebrew`, `reverse-engineering`, `hardware-research`, `reproducible-research`, `gaming`, `llm`.

## Hashtags temáticos para README y promoción

`#PS4Linux` `#PlayStation4` `#Linux` `#Homebrew` `#ReverseEngineering` `#Cybersecurity` `#OpenSource` `#HardwareResearch` `#ReproducibleResearch` `#Gaming` `#LLM`

## Limitaciones

Este documento registra los cambios documentales y los controles pendientes. No certifica que todos los archivos históricos hayan pasado un análisis de secretos, que el CI funcione o que la consola sea compatible. Esos controles requieren ejecución y evidencia propia.
