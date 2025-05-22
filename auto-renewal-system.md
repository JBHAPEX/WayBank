# Sistema de Autorenovación Automática

## Resumen

El sistema de autorenovación automática en WayPool está diseñado para maximizar los rendimientos de los usuarios a través del interés compuesto, garantizando que las posiciones de liquidez continúen generando beneficios incluso cuando el usuario no toma acción al finalizar su período.

## Características principales

- **Período de contrato fijo**: Todas las posiciones tienen un período de contrato fijo de 365 días.
- **Timeframes flexibles**: Los usuarios pueden seleccionar timeframes de 30, 90 o 365 días según sus preferencias de visualización y seguimiento.
- **Renovación automática**: Las posiciones que finalicen su período de contrato y no sean recolectadas en 24 horas se renuevan automáticamente.

## Funcionamiento detallado

### Creación de posiciones

1. Al crear una posición, el sistema establece automáticamente:
   - Un período de contrato de 365 días (fijo para todas las posiciones)
   - El timeframe seleccionado por el usuario (30, 90 o 365 días)

2. El período de bloqueo del capital se determina según el tipo de posición:
   - **Posiciones premium** (≥ 20,000 USDC): 180 días de bloqueo
   - **Posiciones estándar** (< 20,000 USDC): 365 días de bloqueo

### Proceso de autorenovación

Cuando una posición llega al final de su período de contrato:

1. El sistema monitorea si el usuario recolecta o cierra la posición.
2. Si después de 24 horas no se ha realizado ninguna acción:
   - La posición se renueva automáticamente por otros 365 días
   - La fecha de inicio se actualiza al día actual
   - Se mantiene el timeframe original seleccionado por el usuario
   - Se registra la renovación en las notas de la posición

### Beneficios para el usuario

- **Interés compuesto automático**: Permite que las ganancias se acumulen sin interrupciones
- **Maximización de rendimientos a largo plazo**: Aprovecha el poder del interés compuesto para aumentar significativamente los beneficios
- **Comodidad y tranquilidad**: No es necesario estar pendiente de fechas de vencimiento
- **Flexibilidad mantenida**: El usuario puede seguir recolectando fees o cerrar la posición en cualquier momento

## Consideraciones importantes

- La autorenovación ocurre solo después de que el período de contrato ha finalizado y han pasado más de 24 horas
- Esta funcionalidad es compatible con todos los tipos de posiciones, independientemente del timeframe seleccionado
- Los usuarios pueden seguir monitorizando sus posiciones y controlando cuando recolectar fees o cerrar posiciones