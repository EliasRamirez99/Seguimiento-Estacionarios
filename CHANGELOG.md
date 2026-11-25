# Registro de cambios — Parte Equipos Estacionarios OPS

Formato: fecha · descripción del cambio / carga de datos.

## 2026-11-25

- Versión inicial del sistema puesta bajo control de versiones (GitHub).
- Lista base de 977 equipos estacionarios (17 tareas; martillos hidráulicos clasificados
  desde percutores).
- Cronograma de cargas por día (Lun Zapato · Mar Chulengo · Mié Motosoldadora y
  Motocompresores · Jue resto · Vie Generadores), vigente desde el 25/11/2026.
- App con: filtros (buscar, día de carga, estado de registro, tarea, propietario,
  estado operativo, **obra**, familia), edición por equipo con fecha de última
  actualización, botón "Sin cambios", informe PDF en hoja vertical con branding OPS,
  y estadísticas (incluida **estadística por obra**).
- Tabla ordenada: Seguimiento · Código · Ubicación · Estado · Tarea · Marca y Modelo · Propietario.
- Campo **Obra** estandarizado (desplegable) en la edición, en lugar de texto libre.
- Datos de prueba de revisiones borrados; se comienza a operar el 26/11/2026.
- `sync_api.py` listo para sincronizar desde la API de OPS cuando el endpoint v3 vuelva a responder.

<!-- Agregar aquí cada nueva carga de datos o modificación, con su fecha. -->
