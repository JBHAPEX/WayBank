const { ethers } = require("ethers");
require('dotenv').config();

// Configuración inicial del proveedor y wallet
const provider = new ethers.providers.JsonRpcProvider(process.env.RPC_URL);
const wallet = new ethers.Wallet(process.env.PRIVATE_KEY, provider);

// Carga del ABI y dirección del contrato desplegado
const contractABI = require('./MultiPoolBalancerABI.json');
const contractAddress = process.env.CONTRACT_ADDRESS;

// Inicialización del contrato
const contract = new ethers.Contract(contractAddress, contractABI, wallet);

// Parámetros iniciales
const amountToHedge = ethers.utils.parseUnits("100", 6); // 100 USDC por ejemplo

// Función principal que ejecuta la estrategia
async function executeStrategy(poolId) {
    try {
        const tx = await contract.executeStrategy(poolId, amountToHedge);
        console.log(`Transacción enviada para pool ${poolId}:`, tx.hash);
        const receipt = await tx.wait();
        console.log(`Transacción confirmada para pool ${poolId}:`, receipt.transactionHash);
    } catch (error) {
        console.error(`Error al ejecutar estrategia para pool ${poolId}:`, error);
    }
}

// Ejecución periódica del bot (cada minuto)
async function monitorPools() {
    try {
        const poolsCount = await contract.getPoolsCount();
        console.log(`Número total de pools: ${poolsCount}`);

        for (let poolId = 0; poolId < poolsCount; poolId++) {
            const poolInfo = await contract.getPool(poolId);
            if (poolInfo.active) {
                console.log(`Ejecutando estrategia para pool activo: ${poolId}`);
                await executeStrategy(poolId);
            } else {
                console.log(`Pool ${poolId} inactivo, omitiendo.`);
            }
        }
    } catch (error) {
        console.error('Error en el monitoreo de pools:', error);
    }
}

// Ejecutar cada 60 segundos
setInterval(monitorPools, 60000);

// Ejecución inicial al arrancar
monitorPools();