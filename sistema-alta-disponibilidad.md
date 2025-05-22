# Sistema de Alta Disponibilidad para Base de Datos

## Descripción General

El sistema de alta disponibilidad es una solución que permite la continuidad del servicio en caso de fallas en la base de datos principal. Implementa un mecanismo de conmutación por error (failover) automático que detecta problemas en la conexión a la base de datos principal y redirige el tráfico a una base de datos secundaria ubicada en una región geográfica diferente.

## Características Principales

- **Redundancia Geográfica**: Base de datos principal en US-East y secundaria en Europa
- **Detección Automática de Fallos**: Monitoreo continuo del estado de ambas bases de datos
- **Conmutación Automática**: Cambio transparente a la base de datos secundaria en caso de fallo
- **Recuperación Automática**: Retorno automático a la base de datos principal cuando se recupera
- **APIs de Monitoreo**: Endpoints para verificar el estado del sistema en tiempo real
- **Sincronización de Datos**: Herramientas para mantener sincronizadas ambas bases de datos

## Arquitectura del Sistema

```
┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │
│  Base de Datos  │     │  Base de Datos  │
│    Principal    │◄───►│   Secundaria    │
│    (US-East)    │     │    (Europa)     │
│                 │     │                 │
└────────▲────────┘     └────────▲────────┘
         │                       │
         │                       │
         │     ┌─────────────────▼─────────────────┐
         │     │                                   │
         └────►│  Sistema de Failover Automático   │
               │                                   │
               └─────────────────▲─────────────────┘
                                 │
                                 │
                       ┌─────────▼─────────┐
                       │                   │
                       │    Aplicación     │
                       │                   │
                       └───────────────────┘
```

## Componentes del Sistema

### 1. Módulo de Failover (`server/failover-db.js`)

Este componente es el corazón del sistema de alta disponibilidad y se encarga de:

- Monitorear continuamente ambas bases de datos
- Detectar fallos en las conexiones
- Cambiar automáticamente a la base de datos secundaria cuando es necesario
- Gestionar la recuperación y retorno a la base de datos principal
- Mantener un registro del estado del sistema

### 2. Integración con la Base de Datos (`server/db.ts`)

Modifica la forma en que la aplicación se conecta a la base de datos:

- Inicializa el sistema de failover
- Proporciona una interfaz unificada para el acceso a la base de datos
- Gestiona las configuraciones de conexión
- Maneja el estado de disponibilidad de cada base de datos

### 3. Sincronización de Datos (`db-sync.js`)

Herramienta para mantener sincronizadas ambas bases de datos:

- Realiza copias de seguridad entre bases de datos
- Sincroniza todas las tablas y registros
- Verifica la integridad de los datos
- Permite la ejecución manual o programada

### 4. APIs de Monitoreo (`server/health-routes.ts`)

Endpoints REST para monitorear el estado del sistema:

- `/api/status`: Información básica sobre el estado de las bases de datos
- `/api/health/detailed`: Información detallada para administradores

## Configuración

### Variables de Entorno Requeridas

| Variable | Descripción |
|----------|-------------|
| `DATABASE_URL` | URL de conexión a la base de datos principal (US-East) |
| `SECONDARY_DATABASE_URL` | URL de conexión a la base de datos secundaria (Europa) |

### Parámetros Configurables

En el archivo `server/failover-db.js` se pueden ajustar los siguientes parámetros:

- `maxFailedAttempts`: Intentos fallidos necesarios para cambiar de base de datos (por defecto: 3)
- `recoveryCheckInterval`: Intervalo entre verificaciones de recuperación (por defecto: 60000ms)
- `recoveryGracePeriod`: Tiempo antes de volver a la primaria tras recuperación (por defecto: 300000ms)

## Uso del Sistema

### Monitoreo del Estado

#### Verificación Básica

```bash
curl http://localhost:5000/api/status
```

Respuesta de ejemplo (sistema saludable):
```json
{
  "status": "healthy",
  "message": "Sistema funcionando correctamente (base de datos principal)",
  "details": {
    "primary": true,
    "secondary": true,
    "activeDb": "primary",
    "lastCheck": "2025-05-19T16:05:23.456Z"
  }
}
```

Respuesta de ejemplo (sistema en failover):
```json
{
  "status": "degraded",
  "message": "Sistema funcionando en modo de respaldo (base de datos secundaria)",
  "details": {
    "primary": false,
    "secondary": true,
    "activeDb": "secondary",
    "lastPrimaryFailure": "2025-05-19T16:00:12.345Z",
    "primaryRecovered": null,
    "lastSwitchTime": "2025-05-19T16:01:10.123Z",
    "lastCheck": "2025-05-19T16:05:23.456Z"
  }
}
```

#### Verificación Detallada (Solo Administradores)

```bash
curl http://localhost:5000/api/health/detailed
```

### Sincronización Manual de Bases de Datos

Para verificar el estado de ambas bases de datos:
```bash
node db-sync.js --status
```

Para sincronizar la base de datos secundaria con la principal:
```bash
node db-sync.js --sync
```

## Flujo de Trabajo en Caso de Fallo

1. El sistema detecta que la base de datos principal no responde después de 3 intentos
2. Automáticamente cambia a la base de datos secundaria (Europa)
3. La aplicación continúa funcionando normalmente con la base de datos secundaria
4. El sistema verifica periódicamente si la base de datos principal se ha recuperado
5. Cuando la principal se recupera, el sistema espera un periodo de gracia (5 minutos)
6. Si la principal se mantiene estable, el sistema retorna automáticamente a ella

## Recomendaciones de Uso

1. **Sincronización Regular**: Programar la sincronización entre bases de datos al menos una vez al día
2. **Monitoreo Continuo**: Implementar alertas basadas en el endpoint `/api/status`
3. **Pruebas Periódicas**: Realizar pruebas controladas de failover para verificar el funcionamiento
4. **Revisión de Logs**: Analizar los logs del sistema para detectar posibles problemas

## Limitaciones

- El sistema no garantiza la sincronización en tiempo real entre las bases de datos
- Durante el failover puede haber un breve periodo (segundos) de indisponibilidad
- Las escrituras realizadas en la base de datos secundaria durante el failover necesitarán ser sincronizadas manualmente con la principal

## Solución de Problemas

### La aplicación no puede conectarse a ninguna base de datos

1. Verificar que ambas URLs de conexión estén correctamente configuradas en las variables de entorno
2. Comprobar que los servidores de base de datos estén activos y accesibles
3. Revisar los logs de la aplicación para identificar errores específicos

### El sistema no regresa a la base de datos principal

1. Verificar que la base de datos principal esté realmente accesible
2. Comprobar los valores de `recoveryGracePeriod` y `recoveryCheckInterval`
3. Revisar los logs para identificar posibles problemas en la detección de recuperación

## Conclusión

El sistema de alta disponibilidad proporciona una capa adicional de protección contra fallos en la base de datos, asegurando que el servicio permanezca disponible incluso ante problemas en la infraestructura principal. La redundancia geográfica entre US-East y Europa ofrece una garantía adicional contra fallos regionales, mientras que los mecanismos automáticos de failover y recuperación minimizan la intervención manual necesaria.