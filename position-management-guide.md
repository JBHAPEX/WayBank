# Guía de Gestión de Posiciones en WayPool

## Índice
1. [Introducción](#introducción)
2. [Conceptos Básicos](#conceptos-básicos)
3. [Ciclo de Vida de una Posición](#ciclo-de-vida-de-una-posición)
4. [Temporalidades y Renovación](#temporalidades-y-renovación)
5. [Liquidación de Beneficios](#liquidación-de-beneficios)
6. [Cierre de Posiciones](#cierre-de-posiciones)
7. [Estrategias Delta Neutral](#estrategias-delta-neutral)
8. [Métricas y Seguimiento](#métricas-y-seguimiento)
9. [Preguntas Frecuentes](#preguntas-frecuentes)

## Introducción

WayPool es una plataforma que optimiza la gestión de posiciones de liquidez en Uniswap V4. Este documento explica en detalle cómo funcionan las posiciones, sus temporalidades, la renovación, la liquidación de beneficios y el cierre de posiciones dentro del ecosistema WayPool.

Las posiciones de liquidez en Uniswap permiten a los usuarios proporcionar liquidez a pares de tokens y recibir comisiones a cambio. WayPool mejora este proceso mediante estrategias delta neutral que minimizan el riesgo de pérdida impermanente y optimizan los rendimientos.

## Conceptos Básicos

### ¿Qué es una posición de liquidez?

Una posición de liquidez representa capital depositado en un pool de Uniswap que facilita el intercambio de tokens. Cuando los usuarios realizan swaps en Uniswap, pagan comisiones que se distribuyen entre los proveedores de liquidez proporcionalmente a su participación en el pool.

### Tipos de posiciones en WayPool

1. **Posiciones Activas**: Posiciones que actualmente están generando comisiones.
2. **Posiciones Cerradas**: Posiciones que han finalizado su ciclo y cuyo capital ha sido retirado.
3. **Posiciones Finalizadas**: Posiciones que han completado su ciclo de vida pero cuyos activos aún no han sido retirados completamente.

### Representación de posiciones como NFTs

Cada posición de liquidez se representa como un NFT (Non-Fungible Token) que contiene toda la información sobre la posición, incluyendo:

- Par de tokens (ej. USDC/ETH)
- Rango de precios
- Cantidad de liquidez proporcionada
- Comisiones acumuladas
- Fecha de creación
- Fecha de la última recolección de comisiones
- Estado (Activo, Cerrado, Finalizado)

## Ciclo de Vida de una Posición

### 1. Creación de una Posición

Para crear una posición de liquidez en WayPool:

1. El usuario selecciona una estrategia (Conservadora, Moderada o Agresiva)
2. Deposita el capital (en USDC generalmente)
3. WayPool implementa automáticamente la estrategia delta neutral, distribuyendo el capital entre múltiples pools de Uniswap
4. Se genera un NFT que representa la posición

### 2. Acumulación de Comisiones

Una vez creada, la posición comienza a generar comisiones de trading. Estas comisiones se acumulan dentro de la posición y aumentan el valor de los activos sin necesidad de reinversión manual.

### 3. Recolección de Comisiones

Periódicamente, las comisiones pueden ser recolectadas (harvested) siguiendo las reglas de temporalidad establecidas. Las comisiones recolectadas pueden ser:
- Reinvertidas en la posición
- Retiradas como beneficio
- Una combinación de ambas opciones

### 4. Cierre de Posición

Al finalizar el ciclo de vida de una posición, el usuario puede cerrarla, lo que implica:
- Retirar todo el capital inicial
- Recolectar todas las comisiones acumuladas
- Convertir los activos a USDC (o el token original de entrada)

## Temporalidades y Renovación

### Períodos de Temporalidad

Las posiciones en WayPool tienen diferentes temporalidades que determinan cuándo se pueden realizar ciertas acciones:

#### Período de Cooldown para Recolección de Comisiones

- **Posiciones Estándar**: 30 días de cooldown entre recolecciones de comisiones
- **Posiciones Premium**: 7 días de cooldown entre recolecciones

Esto significa que después de realizar una recolección de comisiones, debe esperar el período de cooldown correspondiente antes de poder realizar otra recolección.

#### Período de Bloqueo de Capital

- **Posiciones Estándar**: 12 meses de bloqueo del capital inicial
- **Posiciones Premium**: 6 meses de bloqueo del capital inicial

Durante este período, el capital inicial no puede ser retirado completamente, aunque las comisiones pueden seguir siendo recolectadas según el período de cooldown.

### Renovación de Posiciones

Al finalizar el período de bloqueo, el usuario tiene dos opciones:

1. **Renovación Automática**: La posición continúa activa con los mismos parámetros por un nuevo período. Esta opción es adecuada para usuarios que desean mantener el rendimiento sin intervención.

2. **Renovación Manual**: El usuario puede modificar los parámetros de la posición antes de renovarla, como:
   - Cambiar la estrategia (Conservadora, Moderada, Agresiva)
   - Aumentar o disminuir el capital
   - Ajustar los rangos de precios manualmente

La renovación puede configurarse desde la página de detalles de posición, en la sección "Configuración de renovación".

## Liquidación de Beneficios

### Proceso de Recolección de Comisiones (Harvesting)

El harvesting o recolección de comisiones es el proceso de extraer las comisiones acumuladas en una posición. Este proceso implica:

1. Acceder a la posición desde el dashboard
2. Seleccionar la opción "Recolectar comisiones"
3. Elegir el porcentaje de comisiones a recolectar (25%, 50%, 75% o 100%)
4. Confirmar la transacción

#### Restricciones de Recolección

- Solo se puede realizar una recolección después de que haya pasado el período de cooldown desde la última recolección
- El estado de la recolección se muestra en la interfaz, indicando cuántos días faltan para poder realizar la próxima
- El mínimo de comisiones acumuladas para realizar una recolección es de 50 USDC equivalente

### Destino de los Beneficios

Las comisiones recolectadas pueden tener varios destinos:

1. **Retirada a Wallet**: Las comisiones se envían directamente a la wallet del usuario en forma de USDC
2. **Reinversión**: Las comisiones se reinvierten en la misma posición, aumentando el capital y potencialmente los rendimientos futuros
3. **Recompensas Compuestas**: Sistema automático que reinvierte un porcentaje de las comisiones (configurable desde 0% a 100%)

### Cálculo de Comisiones y APR

El sistema calcula automáticamente:

- **Comisiones Diarias**: Promedio de comisiones generadas cada día
- **APR (Tasa Anual de Rendimiento)**: Porcentaje anualizado de rendimiento basado en el capital invertido
- **Comisiones Totales**: Suma de todas las comisiones generadas desde la creación de la posición
- **Comisiones Recolectadas**: Total de comisiones que han sido retiradas

## Cierre de Posiciones

### Proceso de Cierre

Para cerrar completamente una posición:

1. Acceder a la posición desde el dashboard
2. Seleccionar la opción "Cerrar posición"
3. Confirmar la acción
4. Los fondos (capital inicial + comisiones acumuladas) se convierten a USDC y se transfieren a la wallet del usuario

### Restricciones de Cierre

- El cierre completo solo está disponible después del período de bloqueo de capital
- Durante el período de bloqueo, solo se pueden recolectar comisiones, pero no el capital principal

### Cierre Parcial

Algunas posiciones premium permiten cierre parcial:

1. Seleccionar la opción "Cierre parcial"
2. Especificar el porcentaje de la posición a cerrar (25%, 50% o 75%)
3. Confirmar la transacción

El cierre parcial permite liberar parte del capital manteniendo el resto activo en la posición.

## Estrategias Delta Neutral

WayPool implementa estrategias delta neutral para minimizar el riesgo de pérdida impermanente. Estas estrategias distribuyen el capital en múltiples pools con exposiciones complementarias.

### Tipos de Estrategias

1. **Conservadora (5% de riesgo)**
   - 70% en pools estables (USDC/USDT, USDC/DAI)
   - 30% en pools volátiles (ETH/USDC, BTC/USDC)
   - Adecuada para usuarios con baja tolerancia al riesgo

2. **Moderada (15% de riesgo)**
   - 50% en pools estables
   - 50% en pools volátiles
   - Balance entre seguridad y rendimiento

3. **Agresiva (25% de riesgo)**
   - 30% en pools estables
   - 70% en pools volátiles
   - Mayor potencial de rendimiento pero mayor exposición a volatilidad

### Rebalanceo Automático

El sistema realiza rebalanceos automáticos en dos casos:

1. **Rebalanceo Periódico**: Cada 30 días para mantener la distribución óptima
2. **Rebalanceo por Condición de Mercado**: Cuando hay movimientos significativos de precio que alteran la distribución ideal

## Métricas y Seguimiento

### Métricas Principales

En el dashboard de WayPool, cada posición muestra métricas clave:

- **Valor Total**: Capital + Comisiones acumuladas
- **APR Actual**: Rendimiento anualizado basado en el rendimiento reciente
- **Comisiones Generadas**: Total de comisiones desde la creación
- **Próxima Recolección Disponible**: Fecha en que se puede realizar la próxima recolección
- **Tiempo Restante de Bloqueo**: Días restantes hasta poder retirar el capital
- **Estado del Rango**: Indica si la posición está dentro o fuera del rango óptimo de precios

### Seguimiento Histórico

La sección de Analytics permite ver el rendimiento histórico:

- Gráficos de rendimiento diario/semanal/mensual
- Comparación entre posiciones
- Análisis de eficiencia de la estrategia
- Historial de recolecciones y reinversiones

## Preguntas Frecuentes

**¿Puedo retirar mi capital antes del período de bloqueo?**

No, el capital inicial está bloqueado durante el período establecido (6 o 12 meses según el tipo de posición). Solo las comisiones pueden ser recolectadas durante este período.

**¿Con qué frecuencia se recolectan las comisiones automáticamente?**

WayPool no recolecta comisiones automáticamente. El usuario debe iniciar manualmente el proceso de recolección respetando los períodos de cooldown.

**¿Qué sucede si el precio sale del rango de mi posición?**

Si el precio sale del rango, la posición deja temporalmente de generar comisiones. Sin embargo, la estrategia delta neutral de WayPool está diseñada para minimizar este riesgo mediante la distribución del capital en diferentes rangos.

**¿Cómo se calculan exactamente las comisiones?**

Las comisiones se calculan basándose en:
- El porcentaje de comisión del pool (0.01%, 0.05%, 0.3% o 1%)
- La cantidad de liquidez proporcionada por el usuario
- El volumen de operaciones en el rango de precios de la posición

**¿Qué sucede cuando finaliza el período de bloqueo?**

Al finalizar el período de bloqueo, recibirás una notificación. Puedes elegir renovar la posición (automática o manualmente) o cerrarla y retirar todos los fondos.

**¿Cómo afecta la volatilidad del mercado a mis posiciones?**

La estrategia delta neutral está diseñada para minimizar el impacto de la volatilidad. En períodos de alta volatilidad, algunas posiciones pueden salir del rango, pero otras compensarán esas pérdidas manteniendo un rendimiento estable general.

**¿Puedo cambiar mi estrategia a mitad del período de bloqueo?**

No es posible cambiar completamente la estrategia durante el período de bloqueo, pero los usuarios premium pueden realizar ajustes menores en los rangos de precio dentro de los límites de su estrategia seleccionada.