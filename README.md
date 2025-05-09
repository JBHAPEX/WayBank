# WayPool
APEX --> WayPool --> Uniswap V4

PROJECT APEX
<div align="center">
  <h2>Intelligent Liquidity Optimization</h2>
  <p><i>A definitive solution to impermanent loss in DeFi</i></p>
</div>
<div align="center">
</div>
📝 Table of Contents

About the Project
Problem Statement
Proposed Solution
Technical Architecture
Smart Contracts
Automation Bot
Installation and Usage
Configuration
Roadmap
Security
Contributions
License
Contact

🔍 About the Project
Project Apex is an innovative solution that offers complete protection against impermanent loss for liquidity providers on Uniswap V3. Through a combination of advanced automation, dynamic hedging strategies, and intelligent price range adjustments, Apex enables users to maximize their returns without suffering losses due to market volatility.
Implemented on the Polygon network to ensure fast and low-cost transactions, Apex represents a revolutionary advancement in liquidity management in the DeFi ecosystem.
❓ Problem Statement
Impermanent loss is one of the most significant challenges for liquidity providers in AMMs (Automated Market Makers) like Uniswap. This phenomenon occurs when fluctuations in asset prices generate a loss in value compared to simply holding the assets in a wallet.
In Uniswap V3, despite the introduction of concentrated liquidity, impermanent loss persists when asset prices move outside the defined range, which can result in:

Significant losses for liquidity providers
Reduced participation in pools, diminishing market liquidity
Entry barriers for new users and institutional investors
Limitations in the mass adoption of DeFi

💡 Proposed Solution
Project Apex addresses impermanent loss through three key components:
1. Automated Dynamic Hedging

Continuous price monitoring through decentralized oracles (Chainlink)
Detection of deviations outside the established range
Automatic opening of compensatory positions on derivatives platforms (Synthetix, GMX)
Risk neutralization through hedging strategies

2. Dynamic Price Range Adjustment

Automatic redistribution of liquidity in Uniswap V3 towards optimal ranges
Continuous adaptation to market conditions
Maximization of fee generation by keeping liquidity in active zones

3. Implementation on Polygon

Fast and low-cost transactions
High execution speed to respond in real-time to market fluctuations
Scalability to manage large volumes without degrading performance

🏗 Technical Architecture
The architecture of Project Apex consists of:
Main Components

Smart Contracts: Smart contracts that manage liquidity, monitor prices, and execute hedging strategies.
Decentralized Oracles: Integration with Chainlink to obtain accurate and real-time price data.
Automation Bot: Autonomous system that executes strategies periodically.
External Integrations: Connections with Uniswap V3, derivatives platforms, and oracle services.

Operation Flow

The system continuously monitors asset prices.
If the price deviates from the defined range, a hedge is automatically executed.
Simultaneously, the liquidity range is adjusted to maintain efficiency.
The entire process occurs without manual intervention, protecting the user's capital.

💻 Smart Contracts
The core of the project is the MultiPoolBalancer contract, which manages multiple Uniswap V3 pools simultaneously:
solidity// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@uniswap/v3-periphery/contracts/interfaces/INonfungiblePositionManager.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

interface IDerivatives {
    function hedge(bool isLong, uint256 amount, uint256 price) external returns (uint256 positionId);
}

contract MultiPoolBalancer is Ownable, Pausable {

    struct PoolInfo {
        IERC20 token0;
        IERC20 token1;
        uint24 fee;
        int24 tickLower;
        int24 tickUpper;
        uint256 lowerRange;  // scaled to 1e8
        uint256 upperRange;  // scaled to 1e8
        address derivativesContract;
        AggregatorV3Interface priceOracle;
    }

    INonfungiblePositionManager public positionManager;
    PoolInfo[] public pools;

    event PoolAdded(uint256 indexed poolId);
    event RangeAdjusted(uint256 indexed poolId, uint256 newLower, uint256 newUpper);
    event HedgeExecuted(uint256 indexed poolId, string action, uint256 positionId);

    constructor(address _positionManager) {
        positionManager = INonfungiblePositionManager(_positionManager);
    }

    function addPool(
        address token0, address token1, uint24 fee, int24 tickLower, int24 tickUpper,
        uint256 lowerRange, uint256 upperRange, address derivativesContract, address priceOracle
    ) external onlyOwner {
        pools.push(PoolInfo({
            token0: IERC20(token0),
            token1: IERC20(token1),
            fee: fee,
            tickLower: tickLower,
            tickUpper: tickUpper,
            lowerRange: lowerRange,
            upperRange: upperRange,
            derivativesContract: derivativesContract,
            priceOracle: AggregatorV3Interface(priceOracle)
        }));
        emit PoolAdded(pools.length - 1);
    }

    function executeStrategy(uint256 poolId, uint256 amountToHedge) external onlyOwner whenNotPaused {
        PoolInfo storage pool = pools[poolId];
        (, int256 price,,,) = pool.priceOracle.latestRoundData();
        require(price > 0, "Invalid price");
        uint256 currentPrice = uint256(price);

        if (currentPrice > pool.upperRange) {
            uint256 positionId = IDerivatives(pool.derivativesContract).hedge(false, amountToHedge, currentPrice);
            emit HedgeExecuted(poolId, "Short Hedge Executed", positionId);
            adjustLiquidityRange(poolId, pool.upperRange, pool.upperRange + (pool.upperRange - pool.lowerRange));
        } else if (currentPrice < pool.lowerRange) {
            uint256 positionId = IDerivatives(pool.derivativesContract).hedge(true, amountToHedge, currentPrice);
            emit HedgeExecuted(poolId, "Long Hedge Executed", positionId);
            adjustLiquidityRange(poolId, pool.lowerRange - (pool.upperRange - pool.lowerRange), pool.lowerRange);
        } else {
            emit HedgeExecuted(poolId, "Price within range, no action", 0);
        }
    }

    function adjustLiquidityRange(uint256 poolId, uint256 newLower, uint256 newUpper) internal {
        PoolInfo storage pool = pools[poolId];
        require(newLower < newUpper, "Invalid range");
        pool.lowerRange = newLower;
        pool.upperRange = newUpper;
        emit RangeAdjusted(poolId, newLower, newUpper);
    }

    // Additional functions for liquidity provision
    // ...
}
Main Functionalities

Multi-Pool Management: Ability to manage different token pairs and strategies.
Dynamic Hedging: Automatic execution of hedging positions on derivatives platforms.
Range Adjustment: Modification of the liquidity range based on market conditions.
Security: Implementation of pause mechanisms and access control.

🤖 Automation Bot
The automation bot is a crucial component that executes hedging strategies periodically:
javascriptrequire('dotenv').config();
const { ethers } = require("ethers");
const fs = require('fs');
const path = require('path');
const axios = require('axios');

// Configuration
const POLLING_INTERVAL = process.env.POLLING_INTERVAL || 60000; // 1 minute by default
const CONTRACT_ADDRESS = process.env.CONTRACT_ADDRESS;
const PRIVATE_KEY = process.env.PRIVATE_KEY;
const RPC_URL = process.env.RPC_URL;
const POOLS_CONFIG = JSON.parse(process.env.POOLS_CONFIG || '[]');

// Initialize blockchain connection
const provider = new ethers.providers.JsonRpcProvider(RPC_URL);
const wallet = new ethers.Wallet(PRIVATE_KEY, provider);

// Load ABI
const contractABI = require('./artifacts/MultiPoolBalancer.json').abi;
const contract = new ethers.Contract(CONTRACT_ADDRESS, contractABI, wallet);

// Logging system
const logDir = path.join(__dirname, 'logs');
if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir);
}

function log(message) {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] ${message}\n`;
    console.log(logMessage.trim());
    
    const logFile = path.join(logDir, `bot-${new Date().toISOString().split('T')[0]}.log`);
    fs.appendFileSync(logFile, logMessage);
}

// Main monitoring function
async function monitorAndExecuteStrategies() {
    try {
        log("Starting monitoring cycle...");
        
        // Verify connection
        const blockNumber = await provider.getBlockNumber();
        log(`Connected to the network. Current block: ${blockNumber}`);
        
        // Check wallet balance for gas
        const balance = await wallet.getBalance();
        log(`Wallet balance: ${ethers.utils.formatEther(balance)} MATIC`);
        
        if (balance.lt(ethers.utils.parseEther("0.1"))) {
            log("⚠️ WARNING: Low gas balance. Please recharge wallet.");
        }
        
        // Iterate over configured pools
        for (const poolConfig of POOLS_CONFIG) {
            const { poolId, amountToHedge } = poolConfig;
            
            log(`Processing pool ID: ${poolId}`);
            
            try {
                // Get pool information
                const pool = await contract.pools(poolId);
                log(`Pool information: Token0=${pool.token0}, Token1=${pool.token1}`);
                
                // Get current price
                const priceData = await contract.getPoolPrice(poolId);
                log(`Current price: ${ethers.utils.formatUnits(priceData, 8)}`);
                
                // Check if we need to execute strategy
                const needsHedge = await contract.needsHedging(poolId);
                
                if (needsHedge) {
                    log(`⚠️ Pool ${poolId} requires hedging. Executing strategy...`);
                    
                    // Execute strategy
                    const hedgeAmount = ethers.utils.parseUnits(amountToHedge.toString(), 6); // Assuming USDC
                    const tx = await contract.executeStrategy(poolId, hedgeAmount);
                    
                    log(`Transaction sent: ${tx.hash}`);
                    
                    // Wait for confirmation
                    const receipt = await tx.wait();
                    
                    if (receipt.status === 1) {
                        log(`✅ Strategy executed successfully. Gas used: ${receipt.gasUsed.toString()}`);
                        
                        // Analyze events
                        const hedgeEvents = receipt.events.filter(e => e.event === "HedgeExecuted");
                        for (const event of hedgeEvents) {
                            log(`HedgeExecuted event: ${JSON.stringify(event.args)}`);
                        }
                    } else {
                        log(`❌ Error in transaction execution.`);
                    }
                } else {
                    log(`✅ Pool ${poolId} in safe range. No action required.`);
                }
            } catch (poolError) {
                log(`❌ Error processing pool ${poolId}: ${poolError.message}`);
                
                // Continue with the next pool
                continue;
            }
        }
        
        log("Monitoring cycle completed.");
    } catch (error) {
        log(`❌ CRITICAL ERROR: ${error.message}`);
        
        // If network error, try to reconnect
        if (error.code === 'NETWORK_ERROR') {
            log("Attempting to reconnect in 30 seconds...");
            setTimeout(monitorAndExecuteStrategies, 30000);
            return;
        }
    }
    
    // Schedule next execution
    setTimeout(monitorAndExecuteStrategies, POLLING_INTERVAL);
}

// Start monitoring system
log("🚀 Starting Project Apex automation bot");
log(`Configuration: Interval=${POLLING_INTERVAL}ms, Contract=${CONTRACT_ADDRESS}`);

// Verify environment
if (!

## 📥 Instalación y Uso

### Requisitos Previos

- Node.js (v14 o superior)
- npm o yarn
- Una wallet con fondos en MATIC (para gas en la red Polygon)
- Acceso a un nodo RPC de Polygon

### Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/JBH/proyecto-apex.git
   cd proyecto-apex

Instalar dependencias:
bashnpm install

Compilar contratos:
bashnpx hardhat compile

Configurar variables de entorno:
bashcp .env.example .env
# Editar .env con tus propios valores


Despliegue

Desplegar el contrato en Polygon:
bashnpx hardhat run scripts/deploy.js --network polygon

Iniciar el bot de automatización:
bashnpm run start:bot


⚙️ Configuración
Variables de Entorno
# Red
RPC_URL=https://polygon-rpc.com

# Wallet
PRIVATE_KEY=tu_clave_privada_aqui

# Contrato
CONTRACT_ADDRESS=0x...

# Bot
POLLING_INTERVAL=60000

# Pools (formato JSON)
POOLS_CONFIG=[{"poolId":0,"amountToHedge":100},{"poolId":1,"amountToHedge":200}]
Configuración de Pools
Para añadir un nuevo pool al sistema:

Llamar a la función addPool del contrato con los parámetros adecuados.
Actualizar la configuración del bot para incluir el nuevo pool.

🗓 Roadmap

Fase 1 (Completada): Investigación y diseño del protocolo
Fase 2 (Completada): Desarrollo de smart contracts y pruebas internas
Fase 3 (Actual): Lanzamiento en testnet y auditorías externas
Fase 4 (2025): Lanzamiento en mainnet y captación de usuarios
Fase 5 (2026+): Optimización, expansión y nuevas funcionalidades

🔒 Seguridad
El protocolo implementa diversas medidas de seguridad:

Auditorías Externas: Verificación por firmas reconocidas como CertiK y OpenZeppelin.
Circuit Breaker: Mecanismo de pausa para situaciones de emergencia.
Límites de Ejecución: Parámetros seguros para evitar operaciones en condiciones extremas.
Verificación de Oráculos: Uso de fuentes confiables para datos de precios.

👥 Contribuciones
Las contribuciones son bienvenidas. Para colaborar:

Fork del repositorio
Crear una rama con tu característica o corrección
Enviar un pull request

Por favor, asegúrate de seguir las directrices de contribución y el código de conducta.

📄 Licencia
Este proyecto está licenciado bajo MIT License.

📞 Contacto
Email: info@elysiumdubai.net


⚠️ Disclaimer
El código proporcionado en este repositorio tiene únicamente fines educativos y de demostración. No representa una versión funcional ni completa, y no debe utilizarse en producción o entornos reales sin una auditoría profesional. El uso de este código sin revisión exhaustiva puede derivar en pérdidas de capital, vulnerabilidades de seguridad y riesgos financieros.

<div align="center">
  <p>© 2025 Proyecto Apex - Todos los derechos reservados</p>
  <p>Desarrollado por el equipo Elysium Media</p>
</div>



PROYECTO APEX

<div align="center">
  <h2>Optimización Inteligente de Liquidez</h2>
  <p><i>Una solución definitiva al impermanent loss en DeFi</i></p>
</div>
<div align="center">
</div>
📝 Tabla de Contenidos

Acerca del Proyecto
Problema a Resolver
Solución Propuesta
Arquitectura Técnica
Smart Contracts
Bot de Automatización
Instalación y Uso
Configuración
Roadmap
Seguridad
Contribuciones
Licencia
Contacto

🔍 Acerca del Proyecto
Proyecto Apex es una solución innovadora que ofrece protección completa contra el impermanent loss para proveedores de liquidez en Uniswap V3. Mediante una combinación de automatización avanzada, estrategias de cobertura dinámica y ajustes inteligentes de rango de precios, Apex permite a los usuarios maximizar sus rendimientos sin sufrir pérdidas debidas a la volatilidad del mercado.
Implementado en la red Polygon para garantizar transacciones rápidas y de bajo coste, Apex representa un avance revolucionario en la gestión de liquidez en el ecosistema DeFi.
❓ Problema a Resolver
El impermanent loss es uno de los desafíos más significativos para los proveedores de liquidez en AMMs (Automated Market Makers) como Uniswap. Este fenómeno ocurre cuando las fluctuaciones en los precios de los activos generan una pérdida de valor en comparación con mantener los activos en una billetera.
En Uniswap V3, a pesar de la introducción de la liquidez concentrada, el impermanent loss persiste cuando el precio de los activos se mueve fuera del rango definido, lo que puede resultar en:

Pérdidas significativas para los proveedores de liquidez
Menor participación en los pools, reduciendo la liquidez del mercado
Barrera de entrada para nuevos usuarios e inversores institucionales
Limitación en la adopción masiva de DeFi

💡 Solución Propuesta
Proyecto Apex aborda el impermanent loss mediante tres componentes clave:
1. Cobertura Dinámica Automatizada

Monitoreo continuo de precios a través de oráculos descentralizados (Chainlink)
Detección de desviaciones fuera del rango establecido
Apertura automática de posiciones compensatorias en plataformas de derivados (Synthetix, GMX)
Neutralización del riesgo mediante estrategias de cobertura

2. Ajuste Dinámico del Rango de Precios

Redistribución automática de la liquidez en Uniswap V3 hacia rangos óptimos
Adaptación continua a las condiciones del mercado
Maximización de la generación de comisiones al mantener la liquidez en zonas activas

3. Implementación en Polygon

Transacciones rápidas y de bajo coste
Alta velocidad de ejecución para responder en tiempo real a las fluctuaciones del mercado
Escalabilidad para gestionar grandes volúmenes sin degradar el rendimiento

🏗 Arquitectura Técnica
La arquitectura de Proyecto Apex se compone de:
Componentes Principales

Smart Contracts: Contratos inteligentes que gestionan la liquidez, monitorizan precios y ejecutan estrategias de cobertura.
Oráculos Descentralizados: Integración con Chainlink para obtener datos de precios precisos y en tiempo real.
Bot de Automatización: Sistema autónomo que ejecuta estrategias periódicamente.
Integraciones Externas: Conexiones con Uniswap V3, plataformas de derivados y servicios de oráculos.

Flujo de Operación

El sistema monitorea continuamente los precios de los activos.
Si el precio se desvía del rango definido, se ejecuta automáticamente una cobertura.
Simultáneamente, el rango de liquidez se ajusta para mantener la eficiencia.
Todo el proceso ocurre sin intervención manual, protegiendo el capital del usuario.

💻 Smart Contracts
El núcleo del proyecto es el contrato MultiPoolBalancer, que gestiona múltiples pools de Uniswap V3 simultáneamente:
solidity// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@uniswap/v3-periphery/contracts/interfaces/INonfungiblePositionManager.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

interface IDerivatives {
    function hedge(bool isLong, uint256 amount, uint256 price) external returns (uint256 positionId);
}

contract MultiPoolBalancer is Ownable, Pausable {

    struct PoolInfo {
        IERC20 token0;
        IERC20 token1;
        uint24 fee;
        int24 tickLower;
        int24 tickUpper;
        uint256 lowerRange;  // scaled to 1e8
        uint256 upperRange;  // scaled to 1e8
        address derivativesContract;
        AggregatorV3Interface priceOracle;
    }

    INonfungiblePositionManager public positionManager;
    PoolInfo[] public pools;

    event PoolAdded(uint256 indexed poolId);
    event RangeAdjusted(uint256 indexed poolId, uint256 newLower, uint256 newUpper);
    event HedgeExecuted(uint256 indexed poolId, string action, uint256 positionId);

    constructor(address _positionManager) {
        positionManager = INonfungiblePositionManager(_positionManager);
    }

    function addPool(
        address token0, address token1, uint24 fee, int24 tickLower, int24 tickUpper,
        uint256 lowerRange, uint256 upperRange, address derivativesContract, address priceOracle
    ) external onlyOwner {
        pools.push(PoolInfo({
            token0: IERC20(token0),
            token1: IERC20(token1),
            fee: fee,
            tickLower: tickLower,
            tickUpper: tickUpper,
            lowerRange: lowerRange,
            upperRange: upperRange,
            derivativesContract: derivativesContract,
            priceOracle: AggregatorV3Interface(priceOracle)
        }));
        emit PoolAdded(pools.length - 1);
    }

    function executeStrategy(uint256 poolId, uint256 amountToHedge) external onlyOwner whenNotPaused {
        PoolInfo storage pool = pools[poolId];
        (, int256 price,,,) = pool.priceOracle.latestRoundData();
        require(price > 0, "Invalid price");
        uint256 currentPrice = uint256(price);

        if (currentPrice > pool.upperRange) {
            uint256 positionId = IDerivatives(pool.derivativesContract).hedge(false, amountToHedge, currentPrice);
            emit HedgeExecuted(poolId, "Short Hedge Executed", positionId);
            adjustLiquidityRange(poolId, pool.upperRange, pool.upperRange + (pool.upperRange - pool.lowerRange));
        } else if (currentPrice < pool.lowerRange) {
            uint256 positionId = IDerivatives(pool.derivativesContract).hedge(true, amountToHedge, currentPrice);
            emit HedgeExecuted(poolId, "Long Hedge Executed", positionId);
            adjustLiquidityRange(poolId, pool.lowerRange - (pool.upperRange - pool.lowerRange), pool.lowerRange);
        } else {
            emit HedgeExecuted(poolId, "Price within range, no action", 0);
        }
    }

    function adjustLiquidityRange(uint256 poolId, uint256 newLower, uint256 newUpper) internal {
        PoolInfo storage pool = pools[poolId];
        require(newLower < newUpper, "Invalid range");
        pool.lowerRange = newLower;
        pool.upperRange = newUpper;
        emit RangeAdjusted(poolId, newLower, newUpper);
    }

    // Funciones adicionales para provisión de liquidez
    // ...
}
Funcionalidades Principales

Gestión Multi-Pool: Capacidad para gestionar diferentes pares de tokens y estrategias.
Cobertura Dinámica: Ejecución automática de posiciones de cobertura en plataformas de derivados.
Ajuste de Rango: Modificación del rango de liquidez basado en condiciones del mercado.
Seguridad: Implementación de mecanismos de pausa y control de acceso.

🤖 Bot de Automatización
El bot de automatización es un componente crucial que ejecuta estrategias de cobertura periódicamente:
javascriptrequire('dotenv').config();
const { ethers } = require("ethers");
const fs = require('fs');
const path = require('path');
const axios = require('axios');

// Configuración
const POLLING_INTERVAL = process.env.POLLING_INTERVAL || 60000; // 1 minuto por defecto
const CONTRACT_ADDRESS = process.env.CONTRACT_ADDRESS;
const PRIVATE_KEY = process.env.PRIVATE_KEY;
const RPC_URL = process.env.RPC_URL;
const POOLS_CONFIG = JSON.parse(process.env.POOLS_CONFIG || '[]');

// Inicializar conexión con blockchain
const provider = new ethers.providers.JsonRpcProvider(RPC_URL);
const wallet = new ethers.Wallet(PRIVATE_KEY, provider);

// Cargar ABI
const contractABI = require('./artifacts/MultiPoolBalancer.json').abi;
const contract = new ethers.Contract(CONTRACT_ADDRESS, contractABI, wallet);

// Sistema de logs
const logDir = path.join(__dirname, 'logs');
if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir);
}

function log(message) {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] ${message}\n`;
    console.log(logMessage.trim());
    
    const logFile = path.join(logDir, `bot-${new Date().toISOString().split('T')[0]}.log`);
    fs.appendFileSync(logFile, logMessage);
}

// Función principal de monitoreo
async function monitorAndExecuteStrategies() {
    try {
        log("Iniciando ciclo de monitoreo...");
        
        // Verificar conexión
        const blockNumber = await provider.getBlockNumber();
        log(`Conectado a la red. Bloque actual: ${blockNumber}`);
        
        // Verificar balance para gas
        const balance = await wallet.getBalance();
        log(`Balance de la wallet: ${ethers.utils.formatEther(balance)} MATIC`);
        
        if (balance.lt(ethers.utils.parseEther("0.1"))) {
            log("⚠️ ADVERTENCIA: Balance bajo para gas. Recargar wallet.");
        }
        
        // Iterar sobre los pools configurados
        for (const poolConfig of POOLS_CONFIG) {
            const { poolId, amountToHedge } = poolConfig;
            
            log(`Procesando pool ID: ${poolId}`);
            
            try {
                // Obtener información del pool
                const pool = await contract.pools(poolId);
                log(`Pool información: Token0=${pool.token0}, Token1=${pool.token1}`);
                
                // Obtener precio actual
                const priceData = await contract.getPoolPrice(poolId);
                log(`Precio actual: ${ethers.utils.formatUnits(priceData, 8)}`);
                
                // Verificar si necesitamos ejecutar estrategia
                const needsHedge = await contract.needsHedging(poolId);
                
                if (needsHedge) {
                    log(`⚠️ Pool ${poolId} requiere cobertura. Ejecutando estrategia...`);
                    
                    // Ejecutar estrategia
                    const hedgeAmount = ethers.utils.parseUnits(amountToHedge.toString(), 6); // Asumiendo USDC
                    const tx = await contract.executeStrategy(poolId, hedgeAmount);
                    
                    log(`Transacción enviada: ${tx.hash}`);
                    
                    // Esperar confirmación
                    const receipt = await tx.wait();
                    
                    if (receipt.status === 1) {
                        log(`✅ Estrategia ejecutada correctamente. Gas usado: ${receipt.gasUsed.toString()}`);
                        
                        // Analizar eventos
                        const hedgeEvents = receipt.events.filter(e => e.event === "HedgeExecuted");
                        for (const event of hedgeEvents) {
                            log(`Evento HedgeExecuted: ${JSON.stringify(event.args)}`);
                        }
                    } else {
                        log(`❌ Error en la ejecución de la transacción.`);
                    }
                } else {
                    log(`✅ Pool ${poolId} en rango seguro. No requiere acción.`);
                }
            } catch (poolError) {
                log(`❌ Error procesando pool ${poolId}: ${poolError.message}`);
                
                // Continuar con el siguiente pool
                continue;
            }
        }
        
        log("Ciclo de monitoreo completado.");
    } catch (error) {
        log(`❌ ERROR CRÍTICO: ${error.message}`);
        
        // Si es un error de red, intentar reconectar
        if (error.code === 'NETWORK_ERROR') {
            log("Intentando reconectar en 30 segundos...");
            setTimeout(monitorAndExecuteStrategies, 30000);
            return;
        }
    }
    
    // Programar próxima ejecución
    setTimeout(monitorAndExecuteStrategies, POLLING_INTERVAL);
}

// Iniciar sistema de monitoreo
log("🚀 Iniciando bot de automatización Proyecto Apex");
log(`Configuración: Interval=${POLLING_INTERVAL}ms, Contract=${CONTRACT_ADDRESS}`);

// Verificar entorno
if (!CONTRACT_ADDRESS || !PRIVATE_KEY || !RPC_URL) {
    log("❌ ERROR: Configuración incompleta. Verifique las variables de entorno.");
    process.exit(1);
}

// Iniciar monitoreo
monitorAndExecuteStrategies();

// Manejar señales de terminación
process.on('SIGINT', () => {
    log("Deteniendo bot de automatización...");
    process.exit(0);
});

process.on('unhandledRejection', (reason, promise) => {
    log(`❌ Promesa no controlada rechazada: ${reason}`);
});
Características del Bot

Monitoreo Periódico: Verifica el estado de los pools cada intervalo definido.
Manejo de Errores: Sistema robusto de gestión de errores y reconexión.
Logs Detallados: Registro completo de actividades y transacciones.
Configuración Flexible: Gestión de múltiples pools con parámetros individualizados.
Seguridad: Protección de claves privadas mediante variables de entorno.

📥 Instalación y Uso
Requisitos Previos

Node.js (v14 o superior)
npm o yarn
Una wallet con fondos en MATIC (para gas en la red Polygon)
Acceso a un nodo RPC de Polygon

Instalación

Clonar el repositorio:
bashgit clone https://github.com/JBH/proyecto-apex.git
cd proyecto-apex

Instalar dependencias:
bashnpm install

Compilar contratos:
bashnpx hardhat compile

Configurar variables de entorno:
bashcp .env.example .env
# Editar .env con tus propios valores


Despliegue

Desplegar el contrato en Polygon:
bashnpx hardhat run scripts/deploy.js --network polygon

Iniciar el bot de automatización:
bashnpm run start:bot


⚙️ Configuración
Variables de Entorno
# Red
RPC_URL=https://polygon-rpc.com

# Wallet
PRIVATE_KEY=tu_clave_privada_aqui

# Contrato
CONTRACT_ADDRESS=0x...

# Bot
POLLING_INTERVAL=60000

# Pools (formato JSON)
POOLS_CONFIG=[{"poolId":0,"amountToHedge":100},{"poolId":1,"amountToHedge":200}]
Configuración de Pools
Para añadir un nuevo pool al sistema:

Llamar a la función addPool del contrato con los parámetros adecuados.
Actualizar la configuración del bot para incluir el nuevo pool.

🗓 Roadmap

Fase 1 (Completada): Investigación y diseño del protocolo
Fase 2 (Completada): Desarrollo de smart contracts y pruebas internas
Fase 3 (Actual): Lanzamiento en testnet y auditorías externas
Fase 4 (2025): Lanzamiento en mainnet y captación de usuarios
Fase 5 (2026+): Optimización, expansión y nuevas funcionalidades

🔒 Seguridad
El protocolo implementa diversas medidas de seguridad:

Auditorías Externas: Verificación por firmas reconocidas como CertiK y OpenZeppelin.
Circuit Breaker: Mecanismo de pausa para situaciones de emergencia.
Límites de Ejecución: Parámetros seguros para evitar operaciones en condiciones extremas.
Verificación de Oráculos: Uso de fuentes confiables para datos de precios.

👥 Contribuciones
Las contribuciones son bienvenidas. Para colaborar:

Fork del repositorio
Crear una rama con tu característica o corrección
Enviar un pull request

Por favor, asegúrate de seguir las directrices de contribución y el código de conducta.

📄 Licencia
Este proyecto está licenciado bajo MIT License.

📞 Contacto
Email: info@elysiumdubai.net


⚠️ Disclaimer
El código proporcionado en este repositorio tiene únicamente fines educativos y de demostración. No representa una versión funcional ni completa, y no debe utilizarse en producción o entornos reales sin una auditoría profesional. El uso de este código sin revisión exhaustiva puede derivar en pérdidas de capital, vulnerabilidades de seguridad y riesgos financieros.

<div align="center">
  <p>© 2025 Proyecto Apex - Todos los derechos reservados</p>
  <p>Desarrollado por el equipo Elysium Media</p>
</div>
