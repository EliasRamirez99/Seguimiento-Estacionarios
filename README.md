# Parte / Seguimiento de Equipos Estacionarios — OPS

Aplicación web para el seguimiento semanal de los equipos estacionarios de **OPS (Oilfield
Production Services)**, según un cronograma de cargas por día.

**Repositorio:** https://github.com/EliasRamirez99/Seguimiento-Estacionarios
**App online:** https://claude.ai/artifact/FAuKG35AiHLsnKhnUR7h1L

## Contenido del repositorio

| Archivo | Descripción |
|---|---|
| `index.html` | La aplicación (interfaz, lógica, estadísticas, informe PDF). La copia de esta carpeta tiene los datos embebidos para abrir con doble clic. |
| `equipos.json` | Lista base de los equipos estacionarios (datos de referencia). |
| `ops-logo.webp` | Logo de OPS. |
| `sync_api.py` | Script para sincronizar datos desde la API pública de OPS (ver estado más abajo). |
| `LEEME.txt` | Guía de uso rápida (en español). |
| `CHANGELOG.md` | Registro de cambios y modificaciones del sistema. |

## Dos formas de uso

1. **Local (doble clic):** se abre `index.html`; funciona en el navegador con los datos
   embebidos. Los cambios se guardan en ese navegador.
2. **App online (Claude Artifact):** `https://claude.ai/artifact/FAuKG35AiHLsnKhnUR7h1L`
   Los cambios se guardan en la cuenta y se sincronizan entre dispositivos; se puede compartir.

> Las dos formas guardan por separado. Para trabajo en conjunto, usar la versión online.

## Cronograma de cargas (vigente desde 25/11/2026)

| Día | Tarea |
|---|---|
| Lunes | Zapato Compactador |
| Martes | Chulengo |
| Miércoles | Motosoldadora y Motocompresores |
| Jueves | El resto de los equipos |
| Viernes | Generadores |

Cada equipo se marca **Al día / Corresponde hoy / Vencido / Programado** según su día y su
última actualización. Con el botón **"Sin cambios"** se confirma el registro de la semana sin
modificar los datos.

## Sincronización con la API de OPS

`sync_api.py` consulta `GET /api/public/v3/data/equipos-estacionarios` (host
`gestion.opssrlapp.com`, header `X-API-Key`). **La API key NO se versiona en este repositorio**
(ver `.gitignore`). Al momento de este commit, el endpoint devuelve HTTP 500 del lado del
proveedor; el script queda listo para cuando se rehabilite.

## Cómo registrar modificaciones

Cada cambio del sistema (código, datos de referencia, reglas del cronograma) se documenta en
`CHANGELOG.md` y queda en el historial de commits de este repositorio.
