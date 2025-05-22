Respuesta Directa
Puntos clave: Parece probable que puedas configurar una aplicación web3 para conectar billeteras y realizar transacciones entre dos billeteras usando React, Web3Modal y web3.js. La evidencia sugiere que necesitas un ID de proyecto de WalletConnect, configurar cadenas como Ethereum, y usar un formulario para enviar transacciones. Ten en cuenta que la seguridad, como no exponer claves privadas, es crucial, y siempre prueba en redes de prueba antes de usar la red principal.
Configuración Básica
Para conectar una billetera y realizar transacciones, primero instala los paquetes necesarios con npm install web3modal-web3js web3js. Obtén un ID de proyecto de WalletConnect y configura tu aplicación React con Web3Modal para que los usuarios se conecten usando billeteras como MetaMask.

Conexión de Billetera
Usa el componente <w3m-button/> para permitir que los usuarios se conecten. Una vez conectados, obtén la cuenta del usuario y muestra un formulario para ingresar la dirección del destinatario y la cantidad en ETH.

Realizar Transacciones
Con la cuenta conectada, puedes enviar transacciones usando web3.eth.sendTransaction, especificando la cuenta del remitente, el destinatario, la cantidad (en wei, convertida con web3.utils.toWei), y ajustes de gas (por ejemplo, 21,000 gas y 50 Gwei de precio de gas). Esto permite transferir ETH entre dos billeteras.

Detalle Inesperado
Un detalle interesante es que no necesitas manejar claves privadas directamente si usas Web3Modal, ya que la firma se maneja a través de la billetera del usuario, mejorando la seguridad.

Nota Detallada
Esta sección proporciona una visión profunda y técnica de cómo configurar una aplicación web3 para conectar billeteras y realizar transacciones entre dos billeteras, siguiendo estándares comunes y utilizando herramientas como React, Web3Modal y web3.js. Incluye todos los detalles necesarios para una implementación completa, basada en la investigación y ejemplos disponibles.

Contexto y Requerimientos
La solicitud implica crear una aplicación descentralizada (dApp) que permita a los usuarios conectar sus billeteras web3, como MetaMask, y realizar transacciones entre dos billeteras: una vinculada (la del usuario) y un destinatario, posiblemente pasando parámetros como dirección y cantidad. Esto requiere tanto una interfaz de usuario (frontend) como la lógica para interactuar con la blockchain, típicamente Ethereum, dado el uso de web3.js.

La investigación sugiere que Web3Modal es una herramienta versátil para la conexión de billeteras, soportando más de 500 proveedores de billeteras y facilitando la integración con frameworks como React. Para las transacciones, web3.js ofrece métodos como eth.sendTransaction para enviar ETH entre cuentas, y se pueden configurar parámetros como gas y precio de gas para garantizar la ejecución.

Configuración Técnica
Para comenzar, es necesario instalar los paquetes requeridos. Los comandos son:

npm install web3modal-web3js web3js para las bibliotecas principales.
npm install --save-dev vite @vitejs/plugin-react si usas Vite para el desarrollo React.
Luego, obtén un ID de proyecto de WalletConnect, necesario para Web3Modal. Este ID permite la conexión con proveedores de billeteras a través de WalletConnect.

Configuración de Web3Modal
La configuración incluye definir cadenas soportadas y metadatos. Por ejemplo, para Ethereum mainnet:

Chain ID: 1
Nombre: Ethereum
Moneda: ETH
URL del explorador: Etherscan
URL RPC: https://cloudflare-eth.com
Un objeto de metadatos típico sería:

Nombre: "Mi Sitio Web"
Descripción: "Descripción de mi sitio web"
URL: https://miwebsite.com
Íconos: ['https://avatars.miwebsite.com/']
La configuración se puede codificar en un archivo, por ejemplo src/config.js:

javascript

Contraer

Ajuste

Copiar
import { defaultConfig } from 'web3modal-web3/react';
import Web3 from 'web3';

const projectId = 'TU_ID_DE_PROYECTO'; // Reemplaza con tu ID
const mainnet = {
  chainId: 1,
  name: 'Ethereum',
  currency: 'ETH',
  explorerUrl: 'https://etherscan.io',
  rpcUrl: 'https://cloudflare-eth.com',
};
const metadata = {
  name: 'Mi Sitio Web',
  description: 'Descripción de mi sitio web',
  url: 'https://miwebsite.com',
  icons: ['https://avatars.miwebsite.com/'],
};

const web3Config = defaultConfig({
  metadata,
  enableEIP6963: true,
  enableInjected: true,
  enableCoinbase: true,
  defaultChainId: 1,
});

export { projectId, mainnet, web3Config };
Implementación en React
En el componente principal, como App.js, crea una instancia de Web3Modal y maneja la conexión:

javascript

Contraer

Ajuste

Copiar
import { createWeb3Modal } from 'web3modal-web3/react';
import { projectId, mainnet, web3Config } from './config';
import Web3 from 'web3';
import { useState, useEffect } from 'react';

createWeb3Modal({
  web3Config,
  chains: [mainnet],
  projectId,
  enableAnalytics: true,
});

function App() {
  const [web3, setWeb3] = useState(null);
  const [account, setAccount] = useState(null);
  const [recipient, setRecipient] = useState('');
  const [amount, setAmount] = useState('');

  useEffect(() => {
    const connectWallet = async () => {
      if (window.ethereum) {
        const web3Instance = new Web3(window.ethereum);
        setWeb3(web3Instance);
        const accounts = await web3Instance.eth.getAccounts();
        if (accounts.length > 0) {
          setAccount(accounts[0]);
        }
      }
    };
    connectWallet();
  }, []);

  const sendTransaction = async (e) => {
    e.preventDefault();
    if (!web3 || !account) return alert('Por favor, conecta tu billetera primero.');
    try {
      await web3.eth.sendTransaction({
        from: account,
        to: recipient,
        value: web3.utils.toWei(amount, 'ether'),
        gas: 21000,
        gasPrice: web3.utils.toWei('50', 'gwei'),
      });
      alert('Transacción enviada con éxito!');
    } catch (error) {
      alert('Error al enviar la transacción: ' + error.message);
    }
  };

  return (
    <div>
      <w3m-button />
      {account && (
        <div>
          <p>Cuenta Conectada: {account}</p>
          <form onSubmit={sendTransaction}>
            <input
              type="text"
              placeholder="Dirección del Destinatario"
              value={recipient}
              onChange={(e) => setRecipient(e.target.value)}
              required
            />
            <input
              type="number"
              step="0.000000000000000001"
              placeholder="Cantidad en ETH"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              required
            />
            <button type="submit">Enviar Transacción</button>
          </form>
        </div>
      )}
    </div>
  );
}

export default App;
Detalles de la Transacción
La transacción se envía usando web3.eth.sendTransaction, con los siguientes parámetros:

from: La cuenta del remitente, obtenida después de la conexión.
to: La dirección del destinatario, ingresada por el usuario.
value: La cantidad en wei, convertida de ETH usando web3.utils.toWei.
gas: 21,000, el límite de gas estándar para transferencias de ETH.
gasPrice: 50 Gwei, ajustable según las condiciones de la red.
Es importante destacar que este enfoque no requiere manejar claves privadas, ya que la firma se realiza a través de la billetera conectada, mejorando la seguridad. Sin embargo, siempre se debe probar en una red de prueba, como Goerli, antes de usar la red principal para evitar pérdidas de fondos.

Consideraciones de Seguridad
Nunca almacenes claves privadas en código del lado del cliente; este ejemplo usa el proveedor de la billetera para firmar, lo que es más seguro.
Implementa controles de acceso robustos y mantén actualizada la biblioteca web3.js para mitigar vulnerabilidades.
Considera usar un nodo remoto, como Infura, para la conexión RPC, con un URL como https://mainnet.infura.io/v3/TU_ID_INFURA.
Tabla de Recursos y Configuraciones
Paso	Descripción	Ejemplo/Nota
Instalación	Instala paquetes necesarios	npm install web3modal-web3js web3js
ID de Proyecto	Obtén de WalletConnect	Reemplaza 'TU_ID_DE_PROYECTO' con tu ID real
Configuración de Cadena	Define cadena principal (Ethereum)	Chain ID 1, RPC URL https://cloudflare-eth.com
Metadatos	Información del sitio web	Nombre, URL, íconos, etc.
Conexión de Billetera	Usa <w3m-button/> para conectar	Soporta 500+ proveedores de billeteras
Envío de Transacción	Usa web3.eth.sendTransaction	Ajusta gas y gasPrice según la red
Conclusión
Esta configuración proporciona una solución completa para conectar billeteras y realizar transacciones entre dos billeteras, siguiendo estándares de la industria y priorizando la seguridad. Es adaptable a otros frameworks y cadenas, como Solana o Bitcoin, dependiendo de las necesidades del proyecto.

Voy a crear un código completo para una aplicación Web3 que permita conectar con una wallet y realizar transacciones entre dos monederos. Este código utilizará ethers.js y Web3Modal para la conexión con la wallet y la gestión de transacciones en la blockchain de Ethereum.Aplicación Web3 para transferencias entre walletsCódigo 
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web3 Wallet Transfer</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/He creado un código HTML completo con JavaScript que implementa una aplicación Web3 para conectar wallets y realizar transferencias entre direcciones. Esta aplicación incluye:

Conexión de wallet - Permite conectar tu wallet (como MetaMask) a la aplicación.
Transferencias de ETH - Permite enviar ETH a cualquier dirección.
Transferencias de tokens ERC-20 - Permite enviar tokens ERC-20 a cualquier dirección.

Características principales:

Conexión mediante Web3Modal (compatible con MetaMask y otras wallets)
Reconocimiento automático de la red (Ethereum, Polygon, BSC, etc.)
Visualización del balance de ETH
Interfaz para enviar ETH con opciones de gas personalizadas
Interfaz para enviar tokens ERC-20
Detección automática de información de tokens (nombre, símbolo, decimales)
Seguimiento del estado de las transacciones
Enlaces a exploradores de bloques para verificar transacciones

Requisitos:
La aplicación utiliza las siguientes librerías:

ethers.js - Para interactuar con la blockchain
Web3Modal - Para la conexión de wallets
Tailwind CSS - Para los estilos

Cómo usar:

Guarda el código en un archivo HTML
Abre el archivo en un navegador que tenga MetaMask u otra wallet Web3 instalada
Haz clic en "Conectar Wallet" y autoriza la conexión
Ya puedes realizar transferencias de ETH o tokens ERC-20

Si necesitas personalizar algo específico o tienes dudas sobre cómo funciona alguna parte del código, házme saber.

<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web3 Wallet Transfer</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/ethers/5.7.2/ethers.umd.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/web3modal/1.9.9/index.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/walletconnect/1.8.0/esm/index.min.js"></script>
</head>
<body class="bg-gray-100 min-h-screen">
    <div class="container mx-auto px-4 py-8">
        <header class="mb-8 text-center">
            <h1 class="text-3xl font-bold text-blue-600">Web3 Wallet Transfer</h1>
            <p class="text-gray-600 mt-2">Conecta tu wallet y transfiere fondos de manera segura</p>
        </header>

        <div class="bg-white rounded-lg shadow-md p-6 mb-6">
            <div class="flex flex-col md:flex-row md:justify-between items-center mb-6">
                <div>
                    <h2 class="text-xl font-semibold text-gray-800">Estado de conexión</h2>
                    <p id="connection-status" class="text-red-500 mt-1">No conectado</p>
                    <p id="wallet-address" class="text-gray-600 mt-1 text-sm hidden"></p>
                    <p id="network" class="text-gray-600 mt-1 text-sm hidden"></p>
                    <p id="balance" class="text-gray-600 mt-1 text-sm hidden"></p>
                </div>
                <button id="connect-button" class="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition mt-4 md:mt-0">
                    Conectar Wallet
                </button>
            </div>
        </div>

        <div id="transfer-container" class="bg-white rounded-lg shadow-md p-6 mb-6 hidden">
            <h2 class="text-xl font-semibold text-gray-800 mb-4">Realizar transferencia</h2>

            <div class="space-y-4">
                <div>
                    <label for="recipient" class="block text-gray-700 mb-2">Dirección de destino</label>
                    <input type="text" id="recipient" class="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-600 focus:border-transparent" placeholder="0x...">
                </div>

                <div>
                    <label for="amount" class="block text-gray-700 mb-2">Cantidad (ETH)</label>
                    <input type="number" id="amount" class="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-600 focus:border-transparent" placeholder="0.001" step="0.001" min="0">
                </div>

                <div>
                    <label for="gas-price" class="block text-gray-700 mb-2">Precio de Gas (opcional, en Gwei)</label>
                    <input type="number" id="gas-price" class="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-600 focus:border-transparent" placeholder="Gas price en Gwei">
                </div>

                <button id="send-button" class="w-full bg-green-600 text-white py-2 rounded-md hover:bg-green-700 transition mt-2">
                    Enviar Transacción
                </button>
            </div>
        </div>

        <div id="token-transfer-container" class="bg-white rounded-lg shadow-md p-6 mb-6 hidden">
            <h2 class="text-xl font-semibold text-gray-800 mb-4">Transferir tokens ERC-20</h2>

            <div class="space-y-4">
                <div>
                    <label for="token-address" class="block text-gray-700 mb-2">Dirección del Token</label>
                    <input type="text" id="token-address" class="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-600 focus:border-transparent" placeholder="0x...">
                </div>

                <div>
                    <label for="token-recipient" class="block text-gray-700 mb-2">Dirección de destino</label>
                    <input type="text" id="token-recipient" class="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-600 focus:border-transparent" placeholder="0x...">
                </div>

                <div>
                    <label for="token-amount" class="block text-gray-700 mb-2">Cantidad de tokens</label>
                    <input type="number" id="token-amount" class="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-600 focus:border-transparent" placeholder="1" step="0.000001" min="0">
                </div>

                <button id="token-send-button" class="w-full bg-purple-600 text-white py-2 rounded-md hover:bg-purple-700 transition mt-2">
                    Enviar Tokens
                </button>

                <div id="token-info" class="bg-gray-100 p-3 rounded-md hidden">
                    <p id="token-name" class="text-gray-800 text-sm"></p>
                    <p id="token-symbol" class="text-gray-800 text-sm"></p>
                    <p id="token-decimals" class="text-gray-800 text-sm"></p>
                    <p id="token-balance" class="text-gray-800 text-sm"></p>
                </div>
            </div>
        </div>

        <div id="transaction-status" class="bg-white rounded-lg shadow-md p-6 mb-6 hidden">
            <h2 class="text-xl font-semibold text-gray-800 mb-4">Estado de la transacción</h2>
            <div id="tx-status" class="p-3 rounded-md"></div>
            <div id="tx-hash" class="mt-2"></div>
        </div>
    </div>

    <script>
        // Variables globales
        let provider;
        let signer;
        let web3Modal;
        let userAddress;
        let networkName;
        let chainId;

        // Elementos DOM
        const connectButton = document.getElementById('connect-button');
        const connectionStatus = document.getElementById('connection-status');
        const walletAddress = document.getElementById('wallet-address');
        const networkElement = document.getElementById('network');
        const balanceElement = document.getElementById('balance');
        const transferContainer = document.getElementById('transfer-container');
        const tokenTransferContainer = document.getElementById('token-transfer-container');
        const transactionStatus = document.getElementById('transaction-status');
        const txStatus = document.getElementById('tx-status');
        const txHash = document.getElementById('tx-hash');
        const sendButton = document.getElementById('send-button');
        const tokenSendButton = document.getElementById('token-send-button');
        const tokenInfoDiv = document.getElementById('token-info');

        // Inicializar al cargar la página
        window.addEventListener('load', async () => {
            initWeb3Modal();
            setupEventListeners();
        });

        // Inicializar Web3Modal
        function initWeb3Modal() {
            const providerOptions = {
                // Puedes añadir más proveedores aquí como WalletConnect
                // walletconnect: {
                //     package: WalletConnectProvider,
                //     options: {
                //         infuraId: "TU_INFURA_ID" // Reemplazar con tu clave de Infura
                //     }
                // }
            };

            web3Modal = new Web3Modal.default({
                cacheProvider: true,
                providerOptions,
                disableInjectedProvider: false,
            });
        }

        // Configurar event listeners
        function setupEventListeners() {
            connectButton.addEventListener('click', connectWallet);
            sendButton.addEventListener('click', sendTransaction);
            tokenSendButton.addEventListener('click', sendTokenTransaction);

            // Evento para obtener info de los tokens al ingresar una dirección
            document.getElementById('token-address').addEventListener('change', getTokenInfo);
        }

        // Conectar a la wallet
        async function connectWallet() {
            try {
                const instance = await web3Modal.connect();

                // Crear provider de ethers.js
                provider = new ethers.providers.Web3Provider(instance);
                signer = provider.getSigner();

                // Obtener dirección del usuario
                userAddress = await signer.getAddress();

                // Obtener información de la red
                const network = await provider.getNetwork();
                chainId = network.chainId;

                // Mapeo de IDs de red a nombres
                const networkMap = {
                    1: 'Ethereum Mainnet',
                    3: 'Ropsten Testnet',
                    4: 'Rinkeby Testnet',
                    5: 'Goerli Testnet',
                    42: 'Kovan Testnet',
                    56: 'Binance Smart Chain',
                    137: 'Polygon Mainnet',
                    80001: 'Mumbai Testnet',
                    42161: 'Arbitrum One',
                    10: 'Optimism',
                    250: 'Fantom Opera'
                };

                networkName = networkMap[chainId] || `Chain ID: ${chainId}`;

                // Obtener balance de ETH
                const balance = await provider.getBalance(userAddress);
                const formattedBalance = ethers.utils.formatEther(balance);

                // Actualizar UI
                connectionStatus.textContent = 'Conectado';
                connectionStatus.classList.remove('text-red-500');
                connectionStatus.classList.add('text-green-500');

                walletAddress.textContent = `Dirección: ${shortenAddress(userAddress)}`;
                walletAddress.classList.remove('hidden');

                networkElement.textContent = `Red: ${networkName}`;
                networkElement.classList.remove('hidden');

                balanceElement.textContent = `Balance: ${parseFloat(formattedBalance).toFixed(4)} ETH`;
                balanceElement.classList.remove('hidden');

                // Mostrar contenedores de transferencia
                transferContainer.classList.remove('hidden');
                tokenTransferContainer.classList.remove('hidden');

                // Cambiar el botón de conectar a desconectar
                connectButton.textContent = 'Desconectar';
                connectButton.removeEventListener('click', connectWallet);
                connectButton.addEventListener('click', disconnectWallet);

                // Configurar eventos para cambios en la cuenta y la red
                instance.on('accountsChanged', handleAccountsChanged);
                instance.on('chainChanged', handleChainChanged);
                instance.on('disconnect', handleDisconnect);

            } catch (error) {
                console.error('Error al conectar la wallet:', error);
                showTransactionStatus('error', 'No se pudo conectar a la wallet. Por favor, inténtalo de nuevo.');
            }
        }

        // Desconectar la wallet
        async function disconnectWallet() {
            if (web3Modal) {
                await web3Modal.clearCachedProvider();
            }

            // Resetear variables
            provider = null;
            signer = null;
            userAddress = null;

            // Actualizar UI
            connectionStatus.textContent = 'No conectado';
            connectionStatus.classList.remove('text-green-500');
            connectionStatus.classList.add('text-red-500');

            walletAddress.classList.add('hidden');
            networkElement.classList.add('hidden');
            balanceElement.classList.add('hidden');

            // Ocultar contenedores de transferencia
            transferContainer.classList.add('hidden');
            tokenTransferContainer.classList.add('hidden');
            transactionStatus.classList.add('hidden');

            // Cambiar el botón de desconectar a conectar
            connectButton.textContent = 'Conectar Wallet';
            connectButton.removeEventListener('click', disconnectWallet);
            connectButton.addEventListener('click', connectWallet);
        }

        // Manejar cambio de cuentas
        function handleAccountsChanged(accounts) {
            window.location.reload();
        }

        // Manejar cambio de red
        function handleChainChanged() {
            window.location.reload();
        }

        // Manejar desconexión
        function handleDisconnect() {
            disconnectWallet();
        }

        // Enviar transacción de ETH
        async function sendTransaction() {
            if (!provider || !signer) {
                showTransactionStatus('error', 'No hay una wallet conectada. Por favor, conecta tu wallet primero.');
                return;
            }

            // Obtener valores de los inputs
            const recipient = document.getElementById('recipient').value;
            const amount = document.getElementById('amount').value;
            const gasPrice = document.getElementById('gas-price').value;

            // Validar inputs
            if (!ethers.utils.isAddress(recipient)) {
                showTransactionStatus('error', 'La dirección de destino no es válida.');
                return;
            }

            if (!amount || parseFloat(amount) <= 0) {
                showTransactionStatus('error', 'Por favor, ingresa una cantidad válida mayor que cero.');
                return;
            }

            try {
                // Preparar la transacción
                const tx = {
                    to: recipient,
                    value: ethers.utils.parseEther(amount)
                };

                // Añadir gas price si está especificado
                if (gasPrice && parseFloat(gasPrice) > 0) {
                    tx.gasPrice = ethers.utils.parseUnits(gasPrice, 'gwei');
                }

                // Mostrar estado de la transacción
                showTransactionStatus('pending', 'Enviando transacción...');

                // Enviar la transacción
                const transaction = await signer.sendTransaction(tx);

                // Actualizar UI con el hash de la transacción
                showTransactionStatus('pending', 'Transacción enviada. Esperando confirmación...');
                showTransactionHash(transaction.hash);

                // Esperar a que la transacción sea minada
                const receipt = await transaction.wait();

                if (receipt.status === 1) {
                    showTransactionStatus('success', 'Transacción completada con éxito!');

                    // Actualizar el balance
                    const balance = await provider.getBalance(userAddress);
                    const formattedBalance = ethers.utils.formatEther(balance);
                    balanceElement.textContent = `Balance: ${parseFloat(formattedBalance).toFixed(4)} ETH`;
                } else {
                    showTransactionStatus('error', 'La transacción falló. Por favor, verifica los detalles e inténtalo de nuevo.');
                }

            } catch (error) {
                console.error('Error al enviar la transacción:', error);

                // Manejar errores comunes
                if (error.code === 'INSUFFICIENT_FUNDS') {
                    showTransactionStatus('error', 'Fondos insuficientes para completar la transacción.');
                } else if (error.code === 'USER_DENIED_TRANSACTION_SIGNATURE') {
                    showTransactionStatus('error', 'Transacción rechazada por el usuario.');
                } else {
                    showTransactionStatus('error', `Error: ${error.message || 'Desconocido'}`);
                }
            }
        }

        // Obtener información del token ERC-20
        async function getTokenInfo() {
            if (!provider || !signer) {
                showTransactionStatus('error', 'No hay una wallet conectada. Por favor, conecta tu wallet primero.');
                return;
            }

            const tokenAddress = document.getElementById('token-address').value;

            if (!ethers.utils.isAddress(tokenAddress)) {
                return;
            }

            try {
                // ABI mínimo para interactuar con tokens ERC-20
                const erc20ABI = [
                    "function name() view returns (string)",
                    "function symbol() view returns (string)",
                    "function decimals() view returns (uint8)",
                    "function balanceOf(address) view returns (uint256)",
                    "function transfer(address to, uint amount) returns (bool)"
                ];

                // Crear contrato
                const tokenContract = new ethers.Contract(tokenAddress, erc20ABI, provider);

                // Obtener información del token
                const name = await tokenContract.name();
                const symbol = await tokenContract.symbol();
                const decimals = await tokenContract.decimals();
                const balance = await tokenContract.balanceOf(userAddress);
                const formattedBalance = ethers.utils.formatUnits(balance, decimals);

                // Mostrar información del token
                document.getElementById('token-name').textContent = `Nombre: ${name}`;
                document.getElementById('token-symbol').textContent = `Símbolo: ${symbol}`;
                document.getElementById('token-decimals').textContent = `Decimales: ${decimals}`;
                document.getElementById('token-balance').textContent = `Balance: ${parseFloat(formattedBalance).toFixed(4)} ${symbol}`;

                tokenInfoDiv.classList.remove('hidden');

            } catch (error) {
                console.error('Error al obtener información del token:', error);
                showTransactionStatus('error', 'No se pudo obtener información del token. Verifica que la dirección corresponda a un token ERC-20 válido.');
                tokenInfoDiv.classList.add('hidden');
            }
        }

        // Enviar transacción de tokens ERC-20
        async function sendTokenTransaction() {
            if (!provider || !signer) {
                showTransactionStatus('error', 'No hay una wallet conectada. Por favor, conecta tu wallet primero.');
                return;
            }

            // Obtener valores de los inputs
            const tokenAddress = document.getElementById('token-address').value;
            const recipient = document.getElementById('token-recipient').value;
            const amount = document.getElementById('token-amount').value;

            // Validar inputs
            if (!ethers.utils.isAddress(tokenAddress)) {
                showTransactionStatus('error', 'La dirección del token no es válida.');
                return;
            }

            if (!ethers.utils.isAddress(recipient)) {
                showTransactionStatus('error', 'La dirección de destino no es válida.');
                return;
            }

            if (!amount || parseFloat(amount) <= 0) {
                showTransactionStatus('error', 'Por favor, ingresa una cantidad válida mayor que cero.');
                return;
            }

            try {
                // ABI mínimo para interactuar con tokens ERC-20
                const erc20ABI = [
                    "function name() view returns (string)",
                    "function symbol() view returns (string)",
                    "function decimals() view returns (uint8)",
                    "function balanceOf(address) view returns (uint256)",
                    "function transfer(address to, uint amount) returns (bool)"
                ];

                // Crear contrato
                const tokenContract = new ethers.Contract(tokenAddress, erc20ABI, signer);

                // Obtener decimales del token
                const decimals = await tokenContract.decimals();

                // Convertir la cantidad a la unidad correcta
                const tokenAmount = ethers.utils.parseUnits(amount, decimals);

                // Verificar balance
                const balance = await tokenContract.balanceOf(userAddress);
                if (balance.lt(tokenAmount)) {
                    showTransactionStatus('error', 'Balance de tokens insuficiente para completar la transacción.');
                    return;
                }

                // Mostrar estado de la transacción
                showTransactionStatus('pending', 'Enviando transacción de tokens...');

                // Enviar la transacción
                const transaction = await tokenContract.transfer(recipient, tokenAmount);

                // Actualizar UI con el hash de la transacción
                showTransactionStatus('pending', 'Transacción de tokens enviada. Esperando confirmación...');
                showTransactionHash(transaction.hash);

                // Esperar a que la transacción sea minada
                const receipt = await transaction.wait();

                if (receipt.status === 1) {
                    showTransactionStatus('success', 'Transacción de tokens completada con éxito!');

                    // Actualizar el balance de tokens
                    const newBalance = await tokenContract.balanceOf(userAddress);
                    const symbol = await tokenContract.symbol();
                    const formattedBalance = ethers.utils.formatUnits(newBalance, decimals);
                    document.getElementById('token-balance').textContent = `Balance: ${parseFloat(formattedBalance).toFixed(4)} ${symbol}`;
                } else {
                    showTransactionStatus('error', 'La transacción de tokens falló. Por favor, verifica los detalles e inténtalo de nuevo.');
                }

            } catch (error) {
                console.error('Error al enviar la transacción de tokens:', error);

                // Manejar errores comunes
                if (error.code === 'INSUFFICIENT_FUNDS') {
                    showTransactionStatus('error', 'Fondos insuficientes para cubrir el gas de la transacción.');
                } else if (error.code === 'USER_DENIED_TRANSACTION_SIGNATURE') {
                    showTransactionStatus('error', 'Transacción rechazada por el usuario.');
                } else {
                    showTransactionStatus('error', `Error: ${error.message || 'Desconocido'}`);
                }
            }
        }

        // Mostrar estado de la transacción
        function showTransactionStatus(type, message) {
            transactionStatus.classList.remove('hidden');
            txStatus.textContent = message;

            // Limpiar clases anteriores
            txStatus.classList.remove('bg-yellow-100', 'text-yellow-800', 'bg-green-100', 'text-green-800', 'bg-red-100', 'text-red-800');

            // Aplicar estilo según el tipo
            if (type === 'pending') {
                txStatus.classList.add('bg-yellow-100', 'text-yellow-800');
            } else if (type === 'success') {
                txStatus.classList.add('bg-green-100', 'text-green-800');
            } else if (type === 'error') {
                txStatus.classList.add('bg-red-100', 'text-red-800');
            }
        }

        // Mostrar hash de la transacción
        function showTransactionHash(hash) {
            const explorerUrl = getExplorerUrl(chainId, hash);
            txHash.innerHTML = `
                <p class="text-sm text-gray-600">Hash de la transacción:</p>
                <a href="${explorerUrl}" target="_blank" class="text-blue-600 hover:underline break-all">${hash}</a>
                <p class="text-xs text-gray-500 mt-1">Haz clic en el hash para ver la transacción en el explorador de bloques</p>
            `;
        }

        // Obtener URL del explorador según la red
        function getExplorerUrl(chainId, hash) {
            const explorers = {
                1: 'https://etherscan.io/tx/',
                3: 'https://ropsten.etherscan.io/tx/',
                4: 'https://rinkeby.etherscan.io/tx/',
                5: 'https://goerli.etherscan.io/tx/',
                42: 'https://kovan.etherscan.io/tx/',
                56: 'https://bscscan.com/tx/',
                137: 'https://polygonscan.com/tx/',
                80001: 'https://mumbai.polygonscan.com/tx/',
                42161: 'https://arbiscan.io/tx/',
                10: 'https://optimistic.etherscan.io/tx/',
                250: 'https://ftmscan.com/tx/'
            };

            const baseUrl = explorers[chainId] || 'https://etherscan.io/tx/';
            return `${baseUrl}${hash}`;
        }

        // Acortar dirección para mostrar en la UI
        function shortenAddress(address) {
            return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
        }
    </script>
</body>
</html>

Configuración completa de una DApp Web3 (frontend) con Ethers.js – MetaMask, WalletConnect, Coinbase y transacciones USDC
Introducción
En esta guía configuraremos una aplicación Web3 en el frontend (HTML/JS) que cumpla con los siguientes requisitos:
Conexión a múltiples wallets (MetaMask, WalletConnect, Coinbase Wallet) usando Ethers.js (y la librería Web3Modal para simplificar la selección de wallet).
Envío de transacciones del token USDC (USD Coin, un token ERC-20) entre dos direcciones: la dirección del usuario conectado (mediante la wallet) y una dirección de destino especificada en el código.
Soporte para redes Ethereum Mainnet y Polygon (Matic) – la aplicación detectará la red activa y permitirá cambiarla si es necesario.
Código completo en HTML/JavaScript para conexión, firma y envío de transacciones USDC, incluyendo configuración de proveedores (Infura, Alchemy u otros RPC públicos) necesarios para interactuar con la blockchain.
Buenas prácticas de desarrollo Web3 en frontend, con referencias a la documentación técnica oficial.
A continuación, abordaremos la integración de las wallets, la gestión de la red (Ethereum/Polygon) y el envío de USDC paso a paso, culminando con un ejemplo completo de código.
Conexión de múltiples wallets (MetaMask, WalletConnect, Coinbase)
Para conectar nuestra aplicación web a distintas wallets, podemos utilizar Ethers.js junto con Web3Modal. Ethers.js nos proporciona las herramientas para interactuar con Ethereum (proveedores, signers, contratos, etc.), mientras que Web3Modal nos ofrece una interfaz unificada para que el usuario elija su wallet preferida (MetaMask, WalletConnect, Coinbase Wallet, etc.)​
MEDIUM.COM
. MetaMask (proveedor inyectado): MetaMask inyecta un objeto window.ethereum en el navegador. Ethers.js puede envolver este proveedor Web3 estándar usando ethers.providers.Web3Provider. Por ejemplo, el código siguiente inicializa un proveedor de Ethers a partir de MetaMask y solicita al usuario conectar sus cuentas (lo que abrirá la ventana de MetaMask)​
DOCS.ETHERS.ORG
:
js
Copiar
Editar
// Conectar con MetaMask mediante Ethers.js
const provider = new ethers.providers.Web3Provider(window.ethereum);
// MetaMask requiere pedir permiso para conectar las cuentas del usuario
await provider.send("eth_requestAccounts", []);  
const signer = provider.getSigner();  // Obtenemos el signer (cuenta conectada)
Como muestra la documentación de Ethers, Web3Provider encapsula el proveedor inyectado por MetaMask (window.ethereum)​
DOCS.ETHERS.ORG
 y getSigner() nos da un objeto signer para la cuenta Ethereum del usuario, con la capacidad de firmar transacciones. WalletConnect: WalletConnect permite conectar con wallets móviles (y otras) mediante un código QR. Para usar WalletConnect en una app web, se utiliza un proveedor específico (@walletconnect/web3-provider). Al integrar Web3Modal, podemos configurarlo proporcionando un Infura ID o URLs RPC públicas para las redes que soportaremos. Según la documentación, el proveedor de WalletConnect requiere que le indiquemos cómo conectarse a la red deseada, ya sea mediante un Infura project ID (válido para Ethereum mainnet y testnets soportados) o un mapeo de URLs RPC por chainId​
NPMJS.COM
​
NPMJS.COM
:
js
Copiar
Editar
// Ejemplo de configuración de WalletConnect Provider (Infura o RPC personalizado)
const providerOptions = {
  walletconnect: {
    package: WalletConnectProvider, // paquete del proveedor WalletConnect
    options: {
      infuraId: "YOUR_INFURA_ID", // Infura ID para Ethereum (Mainnet, Ropsten, etc.)&#8203;:contentReference[oaicite:5]{index=5}
      // Alternativamente, se puede especificar RPCs personalizados:
      rpc: {
        1: "https://mainnet.infura.io/v3/YOUR_INFURA_ID",      // Ethereum Mainnet
        137: "https://polygon-rpc.com"                        // Polygon Mainnet&#8203;:contentReference[oaicite:6]{index=6}
      }
    }
  },
  // ... otros providers (ej: coinbasewallet) se configuran abajo
};
En el ejemplo anterior, usamos infuraId para las redes Ethereum soportadas por Infura​
NPMJS.COM
. Para Polygon (chainId 137), Infura también ofrece soporte si configuras el proyecto apropiadamente, o podemos indicar un RPC público de Polygon (como https://polygon-rpc.com) en la opción rpc mapeada al chainId 137​
NPMJS.COM
. Nota: En lugar de Infura, podríamos usar Alchemy u otro proveedor de nodos: por ejemplo, Alchemy proporciona URLs RPC para Ethereum (eth-mainnet.alchemyapi.io/v2/YOUR_API_KEY) y Polygon (polygon-mainnet.g.alchemy.com/v2/YOUR_API_KEY). Cualquiera de estos servicios requiere obtener una API key o project ID registrándose en sus sitios. Coinbase Wallet: Coinbase Wallet (no confundir con la cuenta de Coinbase Exchange) es otra wallet popular. Para conectarla en Web3Modal, existe el SDK @coinbase/wallet-sdk. Podemos configurarlo en providerOptions bajo la clave coinbasewallet (o mediante un conector custom usando WalletLink). Por ejemplo​
BLOG.OPENREPLAY.COM
:
js
Copiar
Editar
providerOptions.coinbasewallet = {
  package: CoinbaseWalletSDK,  // SDK de Coinbase Wallet
  options: {
    appName: "Mi DApp",        // Nombre de la aplicación
    infuraId: "YOUR_INFURA_ID",// Podemos reutilizar Infura ID para conectarse a Ethereum
    chainId: 1,                // 1 = Ethereum Mainnet (por defecto Coinbase conecta a Ethereum)&#8203;:contentReference[oaicite:10]{index=10}
    // rpc: { 137: "https://polygon-rpc.com" } // (Opcional) podría especificarse RPC de Polygon si se desea default a Polygon
  }
};
En este caso indicamos el infuraId y la red por defecto (Ethereum Mainnet, chainId 1)​
BLOG.OPENREPLAY.COM
. Coinbase Wallet SDK usará esos datos para establecer la conexión. Nota: si quisiéramos forzar la conexión inicial a Polygon (chainId 137) desde Coinbase Wallet, podríamos pasar chainId: 137 y un rpc de Polygon; sin embargo, en la práctica la app de Coinbase Wallet suele requerir confirmar el cambio de red manualmente si no está ya en esa red, por lo que es habitual conectarse primero a Ethereum y luego pedir al usuario cambiar a Polygon en la propia wallet. Inicializando Web3Modal: Una vez definidos los providerOptions con WalletConnect, Coinbase, etc., podemos crear la instancia de Web3Modal. Por ejemplo:
js
Copiar
Editar
const web3Modal = new Web3Modal({
  cacheProvider: false,  // No recordamos el último proveedor (para siempre mostrar opciones)
  providerOptions       // Pasamos las opciones de proveedores configuradas
});

// Mostrar modal de selección de wallet al usuario:
const web3ModalProvider = await web3Modal.connect();
const provider = new ethers.providers.Web3Provider(web3ModalProvider);
const signer = provider.getSigner();
Cuando llamamos web3Modal.connect(), se desplegará una ventana/modal permitiendo elegir entre MetaMask (u otra wallet inyectada), WalletConnect, Coinbase Wallet, etc. Una vez el usuario selecciona y autoriza, obtenemos un web3ModalProvider que es un proveedor EIP-1193 estándar (similar a window.ethereum pero puede ser de WalletConnect o Coinbase). Lo envolvemos en Ethers.js usando ethers.providers.Web3Provider para poder usar la misma interfaz de Ethers independientemente del wallet elegido. Luego obtenemos el signer para la cuenta conectada. Manejando eventos de la wallet: Es buena práctica suscribirse a eventos como cambio de cuentas o de red en el proveedor, para que nuestra interfaz responda a ellos (por ejemplo, si el usuario cambia de cuenta en MetaMask, actualizar la cuenta mostrada en la DApp). Podemos utilizar el proveedor EIP-1193 para esto, por ejemplo​
ETHEREUM.STACKEXCHANGE.COM
:
js
Copiar
Editar
provider.provider.on("accountsChanged", (accounts) => {
  console.log("Cuenta cambiada:", accounts);
  // Aquí podríamos actualizar la interfaz o reiniciar flujo de conexión
});
provider.provider.on("chainChanged", (chainId) => {
  console.log("Red cambiada a:", chainId);
  // Podemos verificar chainId y actuar en consecuencia (p.ej. recargar datos)
});
Web3Modal ya maneja internamente algunos de estos eventos y puede cerrar sesión si se desconecta la wallet, etc., pero es útil saber que están disponibles.
Detección y cambio de red (Ethereum ↔ Polygon)
Nuestra aplicación debe soportar tanto Ethereum Mainnet como Polygon Mainnet. Cada una tiene un chainId distinto (Ethereum = 1 o 0x1 en hex; Polygon = 137 o 0x89 en hex). Después de conectar la wallet, conviene detectar la red actual y verificar si es la esperada para las transacciones USDC que vamos a realizar. Podemos obtener la red mediante Ethers.js fácilmente:
js
Copiar
Editar
const network = await provider.getNetwork();
console.log("Conectado a la red:", network.name, "chainId:", network.chainId);
Si la red activa no es la deseada, podemos solicitar al usuario que cambie. MetaMask provee métodos especiales para esto: wallet_switchEthereumChain (para cambiar a una red ya configurada en MetaMask) y wallet_addEthereumChain (para añadir una nueva red a MetaMask si no existe en la configuración). Podemos invocarlos a través de provider.provider.request({...}). Por ejemplo, para asegurarnos de cambiar a Polygon si el usuario está en Ethereum, haríamos:
js
Copiar
Editar
const polygonChainIdHex = "0x89";  // 137 en hexadecimal
try {
  await provider.provider.request({
    method: 'wallet_switchEthereumChain',
    params: [{ chainId: polygonChainIdHex }]
  });
} catch (error) {
  // Si la red no está añadida en MetaMask, el método anterior puede fallar con error code 4902.
  if (error.code === 4902) {
    // Pedimos agregar la configuración de Polygon a MetaMask:
    await provider.provider.request({
      method: 'wallet_addEthereumChain',
      params: [{
        chainId: polygonChainIdHex,
        chainName: "Polygon Mainnet",
        nativeCurrency: { name: "MATIC", symbol: "MATIC", decimals: 18 },
        rpcUrls: ["https://polygon-rpc.com"],
        blockExplorerUrls: ["https://polygonscan.com/"]
      }]
    });
    // Luego de añadir, intentamos de nuevo el switch:
    await provider.provider.request({
      method: 'wallet_switchEthereumChain',
      params: [{ chainId: polygonChainIdHex }]
    });
  } else {
    console.error("Error cambiando de red:", error);
  }
}
El código anterior intentará cambiar la red en MetaMask usando el método RPC correspondiente​
STACKOVERFLOW.COM
. Si MetaMask no tiene la red de Polygon configurada, atrapa el error 4902 y luego llama a wallet_addEthereumChain con los parámetros de Polygon Mainnet (chainId, nombre, moneda nativa MATIC, URL RPC pública y explorador)​
ETHEREUM.STACKEXCHANGE.COM
. Tras agregarla, vuelve a intentar el cambio. De esta forma, garantizamos que el usuario esté en la red correcta. Para cambiar a Ethereum Mainnet de forma similar, usaríamos chainId: '0x1' en la llamada a wallet_switchEthereumChain​
STACKOVERFLOW.COM
. Nótese que por razones de seguridad MetaMask suele permitir switch a mainnet sin necesidad de addEthereumChain (pues Ethereum ya está preconfigurada en la wallet). WalletConnect y Coinbase: En el caso de wallets conectadas via WalletConnect, la red suele venir determinada por la configuración RPC que proporcionamos (por ejemplo, si dimos un RPC de Polygon, el provider ya estará en Polygon). Sin embargo, es posible que tengamos que re-instanciar WalletConnect con la cadena correcta si el usuario quiere cambiar, ya que no hay un método estandarizado de "switch" remoto (el usuario tendría que reconectar eligiendo la red). Con Coinbase Wallet, si la conexión inicial fue a Ethereum, el usuario deberá cambiar de red desde la app Coinbase Wallet para usar Polygon – nuestra DApp puede detectar el chainId y mostrar una instrucción al usuario en tal caso. En resumen, tras la conexión conviene verificar network.chainId. Si no es el esperado para nuestras operaciones, aplicar la lógica anterior:
Si es MetaMask, invocar wallet_switchEthereumChain (o wallet_addEthereumChain si hace falta) para guiar al usuario.
Si es otra wallet que no soporte cambio programático, notificar al usuario que cambie manualmente la red en su wallet.
Envío de transacciones USDC (ERC-20)
Con la wallet conectada (tenemos un signer de Ethers) y la red correcta seleccionada, podemos proceder a enviar USDC. USD Coin (USDC) es un token ERC-20, lo que significa que no se envía con una transacción normal de ether, sino invocando la función transfer del contrato del token. Para ello necesitamos:
La dirección del contrato USDC en la red correspondiente.
El ABI (Application Binary Interface) del token, o al menos la parte que incluye la función transfer(address,uint256).
En Ethereum Mainnet, la dirección de USDC (contrato ERC-20 de Circle) es 0xA0b86991C6218b36c1d19d4a2e9Eb0CE3606EB48​
ETHERSCAN.IO
. En Polygon Mainnet, USDC (versión bridgada o nativa) está en la dirección 0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174​
POLYGON.TECHNOLOGY
. Usaremos la adecuada según network.chainId detectado. El ABI de ERC-20 estándar contiene la función transfer. Podemos usar un ABI mínimo como:
js
Copiar
Editar
const ERC20_ABI = [
  "function balanceOf(address) view returns (uint256)",
  "function transfer(address to, uint256 amount) returns (bool)"
];
Con la dirección y ABI, creamos un objeto Contract de Ethers conectado con nuestro signer, por ejemplo:
js
Copiar
Editar
const usdcAddress = (network.chainId === 137) 
      ? "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"  // USDC en Polygon
      : "0xA0b86991C6218b36c1d19D4a2e9Eb0CE3606EB48"; // USDC en Ethereum

const usdcContract = new ethers.Contract(usdcAddress, ERC20_ABI, signer);
Ahora podemos llamar a usdcContract.transfer(destino, monto) utilizando el signer conectado. Esto creará y firmará la transacción para transferir USDC desde la cuenta del usuario (signer) hacia la dirección de destino. Importante: USDC tiene 6 decimales de precisión. Esto quiere decir que, por ejemplo, para enviar 1 USDC, el monto que espera el contrato es 1000000 (ya que 1.000000 = 1 USDC). Ethers.js proporciona utilidades para manejar esto. Podemos usar ethers.utils.parseUnits(cantidad, decimales) para convertir un número en formato humano a el entero en la unidad mínima. Por ejemplo, ethers.utils.parseUnits("5.0", 6) nos da 5000000 (que representa 5.0 USDC). Ejecutamos la transferencia así:
js
Copiar
Editar
const destination = "0x...direccionDestino...";  // dirección de destino especificada en el código
const amountUSDC = "10.5";  // Ejemplo: 10.5 USDC a enviar
const amountWei = ethers.utils.parseUnits(amountUSDC, 6);  // convierte 10.5 a 10500000 (6 decimales)

const tx = await usdcContract.transfer(destination, amountWei);
console.log("Transacción enviada, hash:", tx.hash);
await tx.wait();  // opcional: esperar a que se confirme en el bloque
console.log("¡Transacción de USDC confirmada!");
Cuando llamamos transfer, Ethers.js automáticamente formará la transacción con la llamada al contrato (el data apropiado) y la enviará usando nuestro signer. Bajo el capó, es equivalente a construir una transacción con to: usdcAddress, data: ... pero la abstracción de Contract lo hace sencillo. Según la documentación, transferir tokens con un signer se resume en dos líneas: conectar el contrato con el signer y luego invocar transfer​
SUPPORT.INFURA.IO
​
SUPPORT.INFURA.IO
:
“...necesitas conectar el contrato a un signer para poder pagar el gas de la transacción, y luego usar la función transfer del contrato para enviar el token ERC-20. Básicamente, todo el proceso se reduce a dos líneas de código:
const contractSigner = contract.connect(signer)
const tx = await contractSigner.transfer(toAddress, amount);”​
SUPPORT.INFURA.IO
​
SUPPORT.INFURA.IO
En nuestro ejemplo, usdcContract ya está conectado al signer desde su creación, por lo que podemos llamar directamente usdcContract.transfer(...). Esto retornará un TransactionResponse de Ethers, que podemos esperar con .wait() para asegurarnos de que se minó. La función transfer del contrato USDC retornará un booleano true/false indicando éxito, pero normalmente no es necesario capturarlo manualmente ya que si la transacción se incluye en un bloque sin revertir, asumimos que el token fue transferido correctamente. Nota sobre gas: Ethers.js automáticamente calculará el gas necesario para la transacción y usará parámetros EIP-1559 por defecto (maxPriorityFee, maxFee) adecuados​
SUPPORT.INFURA.IO
. El usuario tendrá que aprobar la transacción en su wallet (MetaMask/WalletConnect/Coinbase) y pagar la comisión en la moneda nativa de la red (ETH en Ethereum, MATIC en Polygon). Asegúrate de que el usuario tenga suficiente saldo en la moneda nativa para cubrir las fees.
Código completo de ejemplo (HTML/JS)
A continuación se presenta un ejemplo completo que integra todo lo anterior. Este código HTML/JavaScript incluye la conexión con las wallets mediante Web3Modal + Ethers, la detección/cambio de red y la realización de una transferencia USDC. Los comentarios en el código explican cada parte:
html
Copiar
Editar
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <title>DApp Web3 – USDC Transfer</title>
  <!-- Incluimos Ethers.js y Web3Modal (CDN para facilidad de demostración) -->
  <script src="https://cdn.ethers.io/lib/ethers-5.2.umd.min.js" type="application/javascript"></script>
  <script src="https://unpkg.com/web3modal/dist/index.js"></script>
  <script src="https://unpkg.com/@walletconnect/web3-provider/dist/umd/index.min.js"></script>
  <script src="https://unpkg.com/@coinbase/wallet-sdk/dist/CoinbaseWalletSDK.min.js"></script>
</head>
<body>
  <h1>Aplicación Web3 – Transferencia de USDC</h1>
  <!-- Botón para conectar la wallet -->
  <button id="connectBtn">Conectar Wallet</button>

  <!-- Selección de la red deseada -->
  <select id="networkSelect">
    <option value="1">Ethereum Mainnet</option>
    <option value="137">Polygon (Matic) Mainnet</option>
  </select>

  <!-- Campo para dirección de destino y monto -->
  <div>
    <input id="destAddress" type="text" placeholder="Dirección de destino" size="42" />
    <input id="usdcAmount" type="text" placeholder="Monto USDC" size="10" />
    <button id="sendBtn">Enviar USDC</button>
  </div>

  <p id="status"></p>

<script>
(async () => {
  // Configuración de opciones de proveedores para Web3Modal
  const providerOptions = {
    walletconnect: {
      package: window.WalletConnectProvider.default, // paquete WalletConnect
      options: {
        infuraId: "YOUR_INFURA_ID", // ID de Infura para Ethereum&#8203;:contentReference[oaicite:23]{index=23}
        rpc: {
          137: "https://polygon-rpc.com" // RPC público para Polygon&#8203;:contentReference[oaicite:24]{index=24}
        }
      }
    },
    coinbasewallet: {
      package: window.CoinbaseWalletSDK, // SDK de Coinbase Wallet
      options: {
        appName: "MiDApp",
        infuraId: "YOUR_INFURA_ID", // reutilizamos Infura (Coinbase también usará este RPC)
        chainId: 1                 // por defecto, conectar a Ethereum Mainnet&#8203;:contentReference[oaicite:25]{index=25}
        // rpc: {137: "https://polygon-rpc.com"} // podría añadirse si se prefiere default Polygon
      }
    }
    // Nota: MetaMask (u otros inyectados) se detecta automáticamente por Web3Modal
  };

  const web3Modal = new window.Web3Modal.default({
    cacheProvider: false,
    providerOptions
  });

  let ethersProvider;  // Ethers provider global
  let signer;          // Signer global

  const statusEl = document.getElementById("status");
  const connectBtn = document.getElementById("connectBtn");
  const sendBtn = document.getElementById("sendBtn");
  const networkSelect = document.getElementById("networkSelect");
  const destAddressInput = document.getElementById("destAddress");
  const usdcAmountInput = document.getElementById("usdcAmount");

  // Dirección de destino predefinida (opcionalmente el desarrollador puede fijarla aquí)
  const PREDEFINED_DEST = "0x1234...ABCDEF";  // <- reemplazar por la dirección deseada
  destAddressInput.value = PREDEFINED_DEST;

  connectBtn.onclick = async function() {
    try {
      const instance = await web3Modal.connect();       // abre modal para seleccionar wallet
      ethersProvider = new ethers.providers.Web3Provider(instance);
      signer = ethersProvider.getSigner();
      const network = await ethersProvider.getNetwork();
      console.log("Cuenta conectada:", await signer.getAddress());
      console.log("Red conectada:", network.name, "(chainId:", network.chainId + ")");
      statusEl.textContent = "Wallet conectada: " + (network.name || "ChainId "+ network.chainId);

      // Suscribir a eventos de cambio de cuenta o red, si se desea:
      instance.on("accountsChanged", (accounts) => {
        console.log("Cuenta cambiada:", accounts);
        // Podríamos actualizar UI o reiniciar estado de app
      });
      instance.on("chainChanged", (chainId) => {
        console.log("Red cambiada a chainId:", chainId);
        statusEl.textContent = "Red cambiada. ChainId activo: " + chainId;
      });

    } catch (error) {
      console.error("Error al conectar wallet:", error);
      statusEl.textContent = "Error al conectar: " + error;
    }
  };

  sendBtn.onclick = async function() {
    if (!signer) {
      statusEl.textContent = "Por favor, conecta una wallet primero.";
      return;
    }
    const dest = destAddressInput.value.trim();
    const amountStr = usdcAmountInput.value.trim();
    if (!ethers.utils.isAddress(dest)) {
      statusEl.textContent = "Dirección de destino inválida.";
      return;
    }
    if (!amountStr || isNaN(Number(amountStr))) {
      statusEl.textContent = "Por favor ingresa un monto USDC válido.";
      return;
    }
    // Decidir la red objetivo según selección del usuario
    const targetChainId = Number(networkSelect.value);
    const currentNetwork = await ethersProvider.getNetwork();
    if (currentNetwork.chainId !== targetChainId) {
      // Solicitar cambio de red
      try {
        await ethersProvider.provider.request({
          method: 'wallet_switchEthereumChain',
          params: [{ chainId: ethers.utils.hexValue(targetChainId) }]
        });
      } catch (switchError) {
        // Si la red no está agregada en MetaMask, intentar agregarla
        if (switchError.code === 4902) {
          try {
            if (targetChainId === 137) {
              await ethersProvider.provider.request({
                method: 'wallet_addEthereumChain',
                params: [{
                  chainId: '0x89',
                  chainName: 'Polygon Mainnet',
                  nativeCurrency: { name: 'MATIC', symbol: 'MATIC', decimals: 18 },
                  rpcUrls: ['https://polygon-rpc.com'],
                  blockExplorerUrls: ['https://polygonscan.com/']
                }]
              });
            } else if (targetChainId === 1) {
              // Ethereum Mainnet (suele existir ya; MetaMask no permite addEthereumChain para 0x1)
              console.log('Ethereum Mainnet ya configurada en MetaMask.');
            }
            // Reintentar cambio de red
            await ethersProvider.provider.request({
              method: 'wallet_switchEthereumChain',
              params: [{ chainId: ethers.utils.hexValue(targetChainId) }]
            });
          } catch (addError) {
            console.error("No se pudo agregar la red solicitada:", addError);
            statusEl.textContent = "Por favor agrega la red en tu wallet.";
            return;
          }
        } else {
          console.error("Error al cambiar de red:", switchError);
          statusEl.textContent = "Error al cambiar de red: " + switchError.message;
          return;
        }
      }
      // Actualizar provider/signer a la nueva red:
      ethersProvider = new ethers.providers.Web3Provider(ethersProvider.provider);
      signer = ethersProvider.getSigner();
    }

    // Determinar dirección de contrato USDC según la red
    const chainIdNow = (await ethersProvider.getNetwork()).chainId;
    let usdcAddress;
    if (chainIdNow === 1) {
      usdcAddress = "0xA0b86991C6218b36c1d19D4a2e9Eb0CE3606EB48"; // USDC Ethereum&#8203;:contentReference[oaicite:26]{index=26}
    } else if (chainIdNow === 137) {
      usdcAddress = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"; // USDC Polygon&#8203;:contentReference[oaicite:27]{index=27}
    } else {
      statusEl.textContent = "Red no soportada para USDC.";
      return;
    }
    const ERC20_ABI = [
      "function balanceOf(address) view returns (uint256)",
      "function transfer(address to, uint256 amount) returns (bool)"
    ];
    const usdcContract = new ethers.Contract(usdcAddress, ERC20_ABI, signer);
    try {
      const amountWei = ethers.utils.parseUnits(amountStr, 6);
      statusEl.textContent = "Enviando " + amountStr + " USDC...";
      const tx = await usdcContract.transfer(dest, amountWei);
      console.log("Transacción enviada. Hash:", tx.hash);
      statusEl.textContent = "Transacción enviada. Esperando confirmación...";
      await tx.wait();
      console.log("Transacción minada en bloque:", (await ethersProvider.getTransactionReceipt(tx.hash)).blockNumber);
      statusEl.textContent = "¡Transacción completada! Hash: " + tx.hash;
    } catch (err) {
      console.error("Error en envío de USDC:", err);
      statusEl.textContent = "Error al enviar USDC: " + (err.message || err);
    }
  };
})();
</script>
</body>
</html>
Explicación del código:
Se incluyen las librerías vía CDN: Ethers.js, Web3Modal, WalletConnect Provider y Coinbase Wallet SDK. (En un entorno de producción, es mejor instalar estos paquetes con npm y empaquetarlos, o alojar las librerías uno mismo por seguridad. De hecho, Ethers recomienda alojar su librería en tu propio servidor en vez de depender de un CDN externo​
DOCS.ETHERS.ORG
.)
Se configuran providerOptions para Web3Modal con WalletConnect (usando Infura ID y RPC de Polygon) y Coinbase Wallet (con Infura ID). MetaMask no hace falta listarlo porque Web3Modal detecta el proveedor inyectado automáticamente​
GITHUB.COM
​
GITHUB.COM
.
Al hacer clic en "Conectar Wallet", se inicia web3Modal.connect() que abre la selección de wallet. Una vez conectado, actualizamos ethersProvider y signer, mostramos la red conectada y suscribimos a eventos de cambio de cuenta/red.
Hay un menú desplegable para que el usuario elija a cuál red quiere enviar (Ethereum o Polygon). Esto nos ayuda a decidir si necesitamos cambiar la red activa antes de enviar el token.
Al hacer clic en "Enviar USDC", el código valida que haya una wallet conectada, una dirección destino válida y un monto numérico. Luego comprueba si la red actual (currentNetwork.chainId) coincide con la seleccionada en el dropdown (targetChainId). Si no coincide, intenta cambiar de red usando wallet_switchEthereumChain. Si la red no está en MetaMask (error 4902), la añade (wallet_addEthereumChain) con los parámetros correspondientes (mostrado para Polygon)​
ETHEREUM.STACKEXCHANGE.COM
.
Tras asegurarnos de estar en la red correcta, seleccionamos la dirección del contrato USDC según el chainId (1 o 137). Creamos el contrato USDC con el ABI mínimo y el signer.
Calculamos el monto en las unidades menores con parseUnits(monto, 6) dado que USDC tiene 6 decimales.
Llamamos usdcContract.transfer(dest, amountWei) y esperamos el resultado. Esto abrirá la wallet del usuario para confirmar la transacción de token. Si el usuario confirma, la transacción se envía a la red.
Informamos al usuario mediante el elemento status en pantalla sobre el progreso (enviando, esperando confirmación, completada, o errores). También hacemos logs en consola para depuración.
Detalles adicionales y buenas prácticas:
El ejemplo contempla solo transacciones directas de USDC. Si se quisiera enviar todo el saldo USDC disponible, habría primero que leer usdcContract.balanceOf(cuenta) y luego transferir ese valor (teniendo en cuenta que no se gasta ETH en valor, solo en gas).
Seguridad: Nunca incluyas claves privadas en este código frontend. Aquí el signer proviene de la wallet del usuario, que maneja su clave privada de forma segura. Si necesitaras un proveedor de solo lectura (por ejemplo, para consultar datos sin una wallet), podrías usar ethers.providers.InfuraProvider o JsonRpcProvider con tu Infura/Alchemy URL, pero para enviar transacciones siempre se usa la wallet del usuario o un backend seguro.
Infura/Alchemy Limits: Usar un Infura ID o endpoint desde frontend es aceptable ya que esas keys no son secretas, pero ten en cuenta que pueden tener límites de uso. Para una aplicación pública robusta, considera manejar tus propias credenciales en un servidor (por ejemplo, un backend proxy) o usar restricciones de dominio en Infura.
Cambio de red manual: En algunas wallets (por ej. WalletConnect con ciertas wallets móviles, o Coinbase), la DApp no puede cambiar la red automáticamente. Siempre provee feedback al usuario (statusEl.textContent) pidiéndole que verifique la red en su wallet si la automática no funciona.
Comprobación de éxito: Después de tx.wait(), podríamos verificar el recibo para confirmar que status es 1 (success). En ERC-20, si la transacción no se revierte, es que fue exitosa (el contrato retorna true). También se puede escuchar el evento Transfer del contrato USDC, pero es avanzado para este scope.
Documentación de referencia: Para más información sobre estas integraciones, puedes revisar:
Documentación oficial de MetaMask para métodos de cambio de red y conexión de cuentas​
STACKOVERFLOW.COM
.
Documentación de Ethers.js sobre Providers, Signers y Contracts (por ejemplo, el tutorial de uso de MetaMask​
DOCS.ETHERS.ORG
 y el ejemplo de transferencia de tokens ERC-20​
SUPPORT.INFURA.IO
​
SUPPORT.INFURA.IO
).
Guía de Infura sobre envío de tokens con Ethers.js​
SUPPORT.INFURA.IO
​
SUPPORT.INFURA.IO
.
Repositorio y tutoriales de Web3Modal, que explican cómo soportar múltiples wallets de forma sencilla​
MEDIUM.COM
.
Con todo lo anterior, la aplicación frontend estaría lista. Al abrir el HTML en un navegador con MetaMask, por ejemplo, el usuario podrá conectar su wallet, elegir la red (Ethereum/Polygon) y enviar USDC a la dirección destino especificada. Los conceptos cubiertos aquí sientan una base sólida para aplicaciones Web3 más complejas. ¡Listo! Hemos implementado una configuración completa de una DApp Web3 en frontend con soporte multi-wallet, cambio de red y transferencia de un token ERC-20 (USDC), aplicando las mejores prácticas actuales. Buena suerte con tu desarrollo Web3 🚀.