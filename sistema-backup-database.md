# Sistema de Respaldo y Restauración de Base de Datos

## Descripción General

El sistema de respaldo y restauración de la base de datos proporciona una solución completa para crear copias de seguridad de todos los datos almacenados en la plataforma blockchain. Este sistema permite realizar respaldos completos de la base de datos PostgreSQL en formato JSON, lo que facilita la portabilidad y restauración de los datos en caso de ser necesario.

## Archivos del Sistema

El sistema consta de dos scripts principales:

1. **backup-database.js**: Script para crear copias de seguridad completas de la base de datos.
2. **restore-database.js**: Script para restaurar copias de seguridad previamente creadas.

## Ubicación de Respaldos

Los archivos de respaldo se almacenan en el directorio `backups/` en la raíz del proyecto. Cada archivo de respaldo sigue el formato de nomenclatura:

```
db_backup_YYYY-MM-DD_HH-MM.json
```

Donde `YYYY-MM-DD_HH-MM` representa la fecha y hora de creación del respaldo.

## Tablas Incluidas en el Respaldo

El sistema realiza respaldo de todas las tablas del sistema, incluyendo (pero no limitado a):

- users
- app_config
- position_history
- custom_pools
- position_preferences
- real_positions
- timeframe_adjustments
- leads
- referrals
- referred_users
- referral_commissions
- referral_apr_boosts
- referral_subscribers
- invoices
- billing_profiles
- managed_nfts
- custodial_wallets
- custodial_sessions
- custodial_recovery_tokens
- support_tickets
- ticket_messages
- legal_signatures
- landing_videos

## Uso del Sistema de Respaldo

### Crear un Respaldo

Para crear un respaldo completo de la base de datos, ejecute:

```bash
node backup-database.js
```

El script realizará las siguientes acciones:
1. Conectarse a la base de datos usando las credenciales almacenadas en las variables de entorno.
2. Recopilar datos de todas las tablas del sistema.
3. Guardar los datos en un archivo JSON en el directorio `backups/`.
4. Mostrar un resumen de las tablas respaldadas y la cantidad total de registros.

### Restaurar un Respaldo

Para restaurar un respaldo previamente creado, ejecute:

```bash
node restore-database.js
```

El script mostrará una lista interactiva de los respaldos disponibles, ordenados por fecha (más recientes primero). El usuario puede seleccionar el respaldo que desea restaurar.

⚠️ **ADVERTENCIA**: La restauración sobrescribirá los datos actuales en la base de datos. Este proceso no es reversible.

## Estructura del Archivo de Respaldo

El archivo de respaldo es un documento JSON con la siguiente estructura:

```json
{
  "tabla1": [
    { "id": 1, "campo1": "valor1", ... },
    { "id": 2, "campo1": "valor2", ... },
    ...
  ],
  "tabla2": [
    { "id": 1, "campo1": "valor1", ... },
    ...
  ],
  ...
}
```

Cada clave en el objeto principal representa una tabla de la base de datos, y su valor es un array de objetos donde cada objeto representa un registro en esa tabla.

## Requisitos

El sistema de respaldo y restauración requiere:

1. Node.js (versión 16 o superior)
2. Acceso a la base de datos PostgreSQL (mediante la variable de entorno `DATABASE_URL`)
3. Los siguientes paquetes npm:
   - dotenv
   - @neondatabase/serverless (o el cliente de PostgreSQL apropiado)
   - ws (para conexión WebSocket con Neon Database)

## Programación de Respaldos Automáticos

Para realizar respaldos automáticos periódicos, se recomienda utilizar un sistema de tareas programadas como cron. Por ejemplo, para realizar un respaldo diario a las 3:00 AM, podría agregar la siguiente línea a crontab:

```
0 3 * * * cd /ruta/a/la/aplicacion && node backup-database.js >> /logs/backup.log 2>&1
```

## Mejores Prácticas

- Realizar respaldos antes de ejecutar migraciones o hacer cambios importantes en la estructura de la base de datos.
- Almacenar copias de los respaldos en ubicaciones externas (como servicios de almacenamiento en la nube).
- Verificar periódicamente que los respaldos se puedan restaurar correctamente.
- Establecer un período de retención para los respaldos (por ejemplo, conservar respaldos diarios durante una semana, respaldos semanales durante un mes, etc.).

## Solución de Problemas

### Errores de Conexión

Si el script muestra errores de conexión a la base de datos, verifique:
- Que la variable de entorno `DATABASE_URL` esté correctamente configurada.
- Que el servidor de base de datos esté en funcionamiento y sea accesible.
- Que las credenciales proporcionadas tengan permisos suficientes.

### Errores de Restauración

Si encuentra problemas durante la restauración:
- Verifique que el archivo de respaldo no esté corrupto.
- Asegúrese de que el esquema de la base de datos coincida con el esquema del respaldo.
- Compruebe que tiene suficientes permisos para modificar todas las tablas.

## Consideraciones de Seguridad

- Los archivos de respaldo contienen datos sensibles. Asegúrese de protegerlos adecuadamente.
- Considere cifrar los archivos de respaldo, especialmente si se almacenan en ubicaciones externas.
- Restrinja el acceso a los scripts de respaldo y restauración solo a personal autorizado.