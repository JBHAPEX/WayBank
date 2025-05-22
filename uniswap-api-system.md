# Documentación del Sistema de API para Pools de Uniswap

## Resumen

Este documento detalla el sistema de API utilizado para obtener datos de los pools de Uniswap en WayPool. El sistema está diseñado para consultar datos en tiempo real de múltiples versiones de Uniswap (V3, V4) y múltiples redes blockchain (Ethereum, Polygon, Arbitrum, Unichain) a través de The Graph API.

## Autenticación

Los datos se obtienen utilizando The Graph API Gateway, que requiere autenticación mediante una API key:

- **Nombre de la variable de entorno**: `GRAPH_API_KEY`
- **Método de autenticación**: La API key debe incluirse tanto en la URL como en el header `Authorization`

## Endpoints y Proxy

Para evitar problemas de CORS, todas las peticiones se realizan a través de un proxy en el servidor:

```
/api/uniswap-proxy/gateway/{version}/{network}
```

donde:
- `{version}` puede ser `v3` o `v4`
- `{network}` puede ser `ethereum`, `polygon`, `arbitrum`, o `unichain`

## IDs de Subgraph

Cada combinación de versión y red tiene un subgraph ID específico en The Graph:

### Versión V3
- **Ethereum**: `5zvR82QoaXYFyDEKLZ9t6v9adgnptxYpKpSbxtgVENFV`
- **Polygon**: `3hCPRGf4z88VC5rsBKU5AA9FBBq5nF3jbKJG7VZCbhjm`
- **Arbitrum**: `AVmXxngrjXhyaWKfKKgQPsQKRvzXcPoPkCXsB7KfW4Ui`
- **Unichain**: `BCfy6Vw9No3weqVq9NhyGo4FkVCJep1ZN9RMJj5S32fX`

### Versión V4
- **Ethereum**: `GvoGwk8QBgP2rRM5tc6dV9ckWWwUXWsBKpCAMwMuJp67`
- **Polygon**: `BNB9gFSJGjacJ7gAQG8HkZxDfivvp9c1eSEsQRG1Qzw1`
- **Arbitrum**: (usa default) `5zvR82QoaXYFyDEKLZ9t6v9adgnptxYpKpSbxtgVENFV`
- **Unichain**: `FLPCQPysAdx4crQGHC9qZWQW5GzTSBEwTnTsMvuhvSW8`

## Estructura de la Consulta GraphQL

La consulta principal para obtener datos de pools sigue esta estructura:

```graphql
{
  bundles(first: 1) {
    ethPriceUSD
  }
  pools(first: 100, orderBy: volumeUSD, orderDirection: desc) {
    id
    feeTier
    liquidity
    token0 {
      id
      symbol
      name
    }
    token1 {
      id
      symbol
      name
    }
    volumeUSD
    txCount
    totalValueLockedUSD
    volumeUSD
    feesUSD
  }
}
```

## Cálculo de APR

El APR se calcula utilizando la siguiente fórmula:

```javascript
const apr = (parseFloat(pool.feesUSD) / parseFloat(pool.totalValueLockedUSD)) * 365 * 100;
```

- `feesUSD`: Comisiones generadas por el pool (acumuladas)
- `totalValueLockedUSD`: Valor total bloqueado en el pool
- Multiplicador 365: Anualiza las comisiones
- Multiplicador 100: Convierte a porcentaje

## Procesamiento y Filtrado

El sistema aplica los siguientes criterios y procesamiento:

1. **Filtro de volumen mínimo**: Pools con menos de 500,000 USD en volumen de 30 días son descartados
2. **Balance entre versiones**: Cuando se selecciona "Todas las versiones", muestra una distribución proporcional entre V3 y V4 (10 pools de cada uno)
3. **Ordenamiento**: Permite ordenar por APR (predeterminado), TVL o volumen en 1 día
4. **Normalización de datos**: Los nombres de tokens y símbolos se normalizan para mejor visualización
5. **Filtros adicionales**: Permite filtrar por protocolo y por tier de comisión

## Manejo de Errores y Fallbacks

- Si un subgraph específico no está disponible, se utiliza un ID predeterminado
- Si no se pueden obtener datos de una red/versión específica, el sistema continúa con las demás combinaciones disponibles
- Se implementa un sistema de caché para reducir el número de peticiones y mejorar el rendimiento

## URLs para Explorar Pools en Uniswap

Para cada pool, se genera un enlace directo a Uniswap con el siguiente formato:

```
https://app.uniswap.org/explore/pools/{network}/{pool-address}
```

donde:
- `{network}` es el identificador de la red (ethereum, polygon, arbitrum, unichain)
- `{pool-address}` es la dirección del contrato del pool

## Ejemplo de Implementación

1. **Obtener datos combinados de múltiples versiones y redes**:

```javascript
// Cliente
async function fetchAllPools() {
  const allVersionsNetworks = [
    { version: 'v3', network: 'ethereum' },
    { version: 'v3', network: 'polygon' },
    { version: 'v4', network: 'ethereum' },
    { version: 'v4', network: 'polygon' },
    // etc.
  ];
  
  const results = await Promise.all(
    allVersionsNetworks.map(({ version, network }) => 
      fetch(`/api/uniswap-proxy/gateway/${version}/${network}`)
        .then(res => res.json())
        .catch(err => ({ error: true, message: err.message }))
    )
  );
  
  return results.filter(r => !r.error).flatMap(r => r.pools || []);
}
```

2. **Servidor (Ruta de proxy)**:

```javascript
// Servidor
app.get('/api/uniswap-proxy/gateway/:version/:network', async (req, res) => {
  const { version, network } = req.params;
  const subgraphId = getSubgraphId(version, network);
  
  const url = `https://gateway.thegraph.com/api/${process.env.GRAPH_API_KEY}/subgraphs/id/${subgraphId}`;
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.GRAPH_API_KEY}`
      },
      body: JSON.stringify({
        query: `{
          bundles(first: 1) {
            ethPriceUSD
          }
          pools(first: 100, orderBy: volumeUSD, orderDirection: desc) {
            id
            feeTier
            liquidity
            // resto de campos
          }
        }`
      })
    });
    
    const data = await response.json();
    res.json(data.data);
  } catch (error) {
    console.error(`Error en consulta a ${version}-${network}:`, error);
    res.status(500).json({ error: 'Error consultando The Graph API' });
  }
});
```

## Notas Adicionales

- El sistema está diseñado para ser escalable, permitiendo añadir nuevas redes o versiones de Uniswap fácilmente
- Se implementa un sistema de caché para mejorar el rendimiento y reducir la carga en The Graph API
- Las consultas son priorizadas para obtener primero los datos más relevantes (Ethereum V3, Ethereum V4, etc.)
- Los datos obtenidos incluyen métricas importantes como APR, TVL, volumen, comisiones, y pares de tokens