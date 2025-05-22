Quickstart
The CDP SDK allows you to create wallets and send funds onchain within minutes. In this quickstart, you will learn how to create a wallet, fund it with testnet ETH, transfer funds between wallets, and trade assets.


Tip
See Securing a Wallet to learn how to protect your wallets.

What You'll Learn
How to install the CDP SDK
How to create a Developer-Managed Wallet and view its default address
How to fund your wallet with testnet ETH
How to transfer funds between wallets
How to trade assets in a wallet
Requirements

Info
Make sure that your developer environment satisfies all of the requirements before proceeding through the quickstart.

Node.js 18+

The Coinbase server-side SDK requires Node.js version 18 or higher and npm version 9.7.2 or higher. To view your currently installed versions of Node.js, run the following from the command-line:

node -v
npm -v

We recommend installing and managing Node.js and npm versions with nvm. See Installing and Updating in the nvm README for instructions on how to install nvm.

Once nvm has been installed, you can install and use the latest versions of Node.js and npm by running the following commands:

nvm install node # "node" is an alias for the latest version
nvm use node

Installation
Clone CDP SDK quickstart template
The CDP SDK provides a quickstart template to get started with the SDK. Clone the repository and navigate to the quickstart template directory:

git clone git@github.com:coinbase/coinbase-sdk-nodejs.git; cd coinbase-sdk-nodejs/quickstart-template

Install the dependencies:

npm install

The file index.js contains the code to perform your first transfer with the CDP SDK. Let's break down the content of this file.

Creating a Wallet
The following instructions illustrate how to create a Developer-Managed (1-of-1) Wallet from scratch, using the CDP SDK.

Create a CDP Secret API key
Initialize the CDP SDK by passing your downloaded API key file
Create a new Developer-Managed (1-of-1) wallet

Tip
This quickstart creates wallets on Base Sepolia testnet. You can create wallets across various EVM networks, including Base, Ethereum L1, and Polygon.

Initialize the SDK by passing your API key information:

index.js
import { Coinbase, Wallet } from "@coinbase/coinbase-sdk";

const apiKeyName = "Copy your secret API key name here."
const apiKeyPrivateKey = "Copy your secret API key's private key here."

Coinbase.configure(apiKeyName, apiKeyPrivateKey)

Another way to initialize the SDK is by sourcing the API key from the JSON file that contains your secret API key, downloaded from the CDP portal:

index.js
let coinbase = Coinbase.configureFromJson({ filePath: '~/Downloads/cdp_api_key.json' });

Now create a wallet:

index.js
// Create a new Wallet
let wallet = await Wallet.create();
console.log(`Wallet successfully created: `, wallet.toString());

// Wallets are not saved locally by default. Refer to the Wallets concept for more information.

Wallets are initialized with a single default Address, accessible via getDefaultAddress:

index.js
let address = await wallet.getDefaultAddress();
console.log(`Default address for the wallet: `, address.toString());


Caution
In a production environment, we recommend turning on IP Whitelisting and using the 2-of-2 Coinbase-Managed Wallet for additional security.

The wallet created should be persisted to avoid losing access to it. Refer to Persisting a wallet section for more information.

Importing a Wallet
The following instructions illustrate how to bring your own wallet into the CDP ecosystem, as a Developer-Managed (1-of-1) Wallet, using the CDP SDK.

Create a CDP Secret API key
Initialize the CDP SDK by passing your downloaded API key file
Create a new Developer-Managed (1-of-1) wallet using your BIP-39 mnemonic seed phrase

Tip
This quickstart creates wallets on Base Sepolia testnet. You can create wallets across various EVM networks, including Base, Ethereum L1, and Polygon.

Initialize the SDK by passing your API key information:

index.js
import { Coinbase, Wallet } from "@coinbase/coinbase-sdk";

const apiKeyName = "Copy your secret API key name here."
const apiKeyPrivateKey = "Copy your secret API key's private key here."

Coinbase.configure(apiKeyName, apiKeyPrivateKey)

Another way to initialize the SDK is by sourcing the API key from the JSON file that contains your secret API key, downloaded from the CDP portal:

index.js
let coinbase = Coinbase.configureFromJson({ filePath: '~/Downloads/cdp_api_key.json' });

Now import your wallet:

index.js
// Import your Wallet into CDP using your BIP-39 mnemonic seed phrase.
// NOTE 1: For security reasons, we recommend storing your seed phrase in an environment variable.
// NOTE 2: Your wallet's seed and seed phrase will not leave your device.
let wallet = await Wallet.import({ mnemonicPhrase: process.env.MNEMONIC_PHRASE });
console.log(`Wallet successfully created: `, wallet.toString());

// Wallets are not saved locally by default. Refer to the Wallets concept for more information.

Wallets are initialized with a single default Address, accessible via getDefaultAddress:

index.js
let address = await wallet.getDefaultAddress();
console.log(`Default address for the wallet: `, address.toString());


Caution
In a production environment, we recommend turning on IP Whitelisting and using the 2-of-2 Coinbase-Managed Wallet for additional security.

Once initialized, your imported wallet should be stored as a Wallet data object, for easy re-instantiation. Refer to Persisting a wallet section for more information.

Funding a Wallet
Wallets do not have funds on them to start. For Base Sepolia and Ethereum Sepolia testnets, we provide a faucet method to fund your wallet with testnet ETH.

index.js
const faucetTransaction = await wallet.faucet();

// Wait for transaction to land on-chain.
await faucetTransaction.wait();

console.log(`Faucet transaction completed successfully: `, faucetTransaction.toString());

Transferring Funds
Now that your faucet transaction has successfully completed, you can send the funds in your wallet to another wallet. The code below creates another wallet, and sends testnet ETH from the first wallet to the second:


Warning
Creating multiple transactions simultaneously can lead to failures.

All transfers, excluding gasless transfers, do not support concurrent transactions. We recommend running sequential calls and waiting for the previous transaction to confirm before continuing.

See Processing multiple transfers for same address as an example. If you need more assistance, reach out to us on Discord in #wallet-api.

index.js
let anotherWallet = await Wallet.create();
console.log(`Second Wallet successfully created: `, anotherWallet.toString());

const transfer = await wallet.createTransfer({
  amount: 0.00001,
  assetId: Coinbase.assets.Eth,
  destination: anotherWallet,
});

// Wait for the transfer to settle.
await transfer.wait()

// Check if the transfer successfully completed on-chain.
if (transfer.getStatus() === 'complete') {
  console.log(`Transfer successfully completed: `, transfer.toString());
} else {
  console.error('Transfer failed on-chain: ', transfer.toString());
}

See Transfers for more information.

You can create your wallet, fund it with testnet tokens and perform your first transfer by running the following command:

npm start

Trading Assets
On base-mainnet you can trade between different assets from your wallet. Since trading is only supported on mainnet wallets, wallet should be funded with real assets before trading. The code below creates a wallet and trades some ETH to USDC and then all of the USDC to WETH:

Refer to trade.js for a complete example of trading assets.

trade_assets.js
import { Coinbase, Wallet } from "@coinbase/coinbase-sdk";

let coinbase = Coinbase.configureFromJson({ filePath: '~/Downloads/cdp_api_key.json' });

// Create a Wallet on base-mainnet to trade assets with.
let wallet = await Wallet.create({ networkId: Coinbase.networks.BaseMainnet });

// Fund the Wallet's default Address with ETH from an external source.
// Trade 0.00001 ETH to USDC.
let trade = await wallet.createTrade({
  amount: 0.00001,
  fromAssetId: Coinbase.assets.Eth,
  toAssetId: Coinbase.assets.Usdc
});

await trade.wait();

if (trade.getStatus() === 'complete') {
  console.log(`Trade successfully completed: `, trade.toString());
} else {
  console.log(`Trade failed on-chain: `, trade.toString());
}

// Trade the wallet's full balance of USDC to WETH.
let trade2 = await wallet.createTrade({
  amount: wallet.getBalance(Coinbase.assets.Usdc),
  fromAssetId: Coinbase.assets.Usdc,
  toAssetId: Coinbase.assets.Weth,
});

await trade2.wait();

if (trade2.getStatus() === "complete") {
  console.log(`Trade successfully completed: `, trade2.toString());
} else {
  console.log(`Trade failed on-chain: `, trade2.toString());
}

See Trades for more information.


Warning
The Developer-Managed Wallets created in the above quickstart are not persisted. We recommend Coinbase-Managed Wallets in production environments.Wallets
A wallet is a collection of addresses on a network. Wallets come with a single default address. Wallets can hold a balance of one or more assets.

A wallet's assets are controlled via the addresses' private keys, which in turn are derived from a seed. Think of a seed / private key as the password to a wallet. For more, see What is a private key?.

Wallets created within the CDP SDK can be either Coinbase-Managed or Developer-Managed, based on how the wallet's private keys are managed. Users can also import existing wallets via the import method and using a seed phrase.

Wallets can create new addresses, list their addresses, list their balances and transfer assets to other addresses or wallets.

Wallets are created on a specific network. Certain features are only available on certain networks. For example, faucets are only available on Base Sepolia and Ethereum Sepolia. Trades are only available on Base Mainnet.

Creating a Wallet
SDK Documentation

Refer to the Wallet class SDK docs for a full list of supported methods.

let wallet = await Wallet.create();

A wallet starts with a single defaultAddress. You can also create more addresses in the wallet, and list them:

// Get the default_address in the wallet.
let address = await wallet.getDefaultAddress();
console.log(`Address: ${address}`);

// Create another address in the wallet.
let address2 = await wallet.createAddress();
console.log(`Address: ${address2}`);

// List the two addresses in the wallet.
let addresses = wallet.getAddresses();

By default, wallets are created for Base Sepolia. The CDP SDK also supports creating wallets for the following networks. To do that, pass the network ID as an argument:

SDK Documentation

let wallet = Wallet.create({ networkId: Coinbase.networks.BaseMainnet });

Securing a Wallet
There are two types of wallets that can be created using the CDP SDK, depending on how the private keys are managed: Coinbase-Managed (2-of-2) Wallets and Developer-Managed (1-of-1) Wallets. Developer-Managed wallets are best for rapid testing and prototyping, while Coinbase-Managed wallets are recommended for any production environments.


Turn on IP Whitelisting in the CDP Portal
IP whitelisting provides another layer of protection for your wallets and prevents an attacker from using your CDP API key outside of your infrastructure. See API Key Security Best Practices on how to enable IP whitelisting on your secret API keys.


Secure your CDP Secret API Key
MPC does not safeguard your CDP API keys or account credentials. If your CDP login or API keys are compromised, funds held in API Wallets could potentially be at risk even when using 2-of-2 MPC.
Coinbase recommends that you store your secret API keys in a dedicated solution such as AWS secret manager, Azure key vault, or some other secure storage option. Your CDP account can be used to mint new secret API keys and should be stored securely using a password manager. Always follow the principle of least privilege when deciding who within your organization can access your CDP account funds.
Coinbase-Managed Wallets
Wallet API offers a state-of-the-art Multi-Party Computation (MPC) option that splits private keys into two shares between Coinbase and the developer, ensuring improved security. Even if a developer's share of the private key is compromised, assets will not be at risk as long as the CDP API keys and account credentials remain secure.

These Coinbase-Managed (2-of-2) wallets use the Server-Signer, a deployable component that simplifies key management and provides a secure way to sign transactions. For production applications requiring maximal security, we recommend using Coinbase-Managed Wallets.

Developer-Managed Wallets
For Developer-Managed (1-of-1) Wallets, it is your responsibility as the developer to securely store the data required to re-instantiate your wallets. For example, you may choose to store this data in an encrypted database. As with any 1-of-1 wallet solution, losing access to the wallet could result in a loss of funds.

The CDP SDK provides two key pieces of information to persist Developer-Managed (1-of-1) Wallets:

Seed: a 32-byte hexadecimal string. This seed is used to derive all of the private keys in the wallet and provides access to spend the assets in the wallet.
Wallet ID: a string used to identify the wallet.
This information is encapsulated in a wallet's export data, obtained by calling the export method:

// Export the data required to re-instantiate the wallet. The data contains the seed and the ID of the wallet.
let data = wallet.export();

// You should implement the "store" method to securely persist the data object,
// which is required to re-instantiate the wallet at a later time. For ease of use,
// the data object is converted to a Hash first.
await store(data);

It is your responsibility as the developer to securely store the seeds and wallet IDs required to re-instantiate your wallets. For example, you may choose to store this data in an encrypted database.

Persisting Locally
For convenience, we provide a method that stores the wallet seed to a local file that you specify.


Warning
This is an insecure method of storing wallet seeds and should only be used for development purposes.

To save your wallet seed, run the following:

// Pick a file to which to save your wallet seed.
 let filePath = 'my_seed.json';

// Set encrypt to true to encrypt the wallet seed with your CDP secret API key.
w.saveSeed(filePath, true);

console.log(`Seed for wallet ${w.getId()} successfully saved to ${filePath}.`);

To encrypt the local wallet data, set encrypt to true. Note that your CDP secret API key also serves as the encryption key for the seed persisted locally. This is for development purposes only. In production, developers should use their own encryption mechanisms and not rely on CDP API keys, as they can be rotated. To re-instantiate wallets with encrypted data, ensure that your SDK is configured with the same API key when invoking save_seed! and load_seed.

Re-instantiating a Wallet
The seed and the ID of the wallet are required to re-instantiate a wallet when a new session is started. This data is encapsulated in the export data of a wallet, which should be securely persisted by the developer.

The following code demonstrates how to import the data required to re-instantiate a wallet.

// You should implement the "fetch" method to retrieve the securely persisted data object,
// keyed by the wallet ID.
let fetchedData = await fetch(wallet.getId());


// importedWallet will be equivalent to wallet.
let importedWallet = await Wallet.import(fetchedData);

Hydrating a Wallet
Another method of re-instantiating a wallet is to "hydrate" it. Hydration consists of two parts:

Fetching the wallet from the server
Setting the correct seed on the wallet
A wallet that is fetched from the server is at first unhydrated, because only you, the developer, have access to the wallet's seed, and the wallet is unaware of its own seed. Unhydrated wallets can perform read operations, such as viewing balances and addresses, but not write operations, such as creating new addresses or transferring funds.

The code below demonstrates the process of fetching an unhydrated wallet, and hydrating it with a seed:

// Get the unhydrated wallet from the server.
const fetchedWallet = await Wallet.fetch(wallet.getId());

// The fact that fetchedWallet is unhydrated is encapsulated by the canSign method.
// For example, calling fetchedWallet.createAddress() would throw an error.
console.log(`fetchedWallet is hydrated: ${fetchedWallet.canSign()}`);

// To hydrate the wallet, set the correct seed on it.
fetchedWallet.setSeed(fetchedData.seed);

// The wallet is now hydrated, and can create addresses and sign transactions.
console.log(`fetchedWallet is hydrated: ${fetchedWallet.canSign()}`);

Hydrating Locally
If you used the saveSeed function to persist a wallet's seed to a local file, then you can first fetch the unhydrated wallet from the server, and then use the loadSeed method to re-instantiate the wallet.

// Get the unhydrated wallet from the server.
const fetchedWallet = await Wallet.fetch(w.getId());

// You can now load the seed into the wallet from the local file.
// fetchedWallet will be equivalent to importedWallet.
await fetchedWallet.loadSeed(filePath);

If you set encrypt to true when calling saveSeed, ensure that your SDK is configured with the same API key when calling loadSeed.

Importing a Wallet
The CDP SDK allows you to import your own wallet via a mnemonic seed phrase, so that you can bring your existing wallets into the CDP ecosystem.

Easily import wallets from other tools: Use your BIP-39 mnemonic seed phrase to import your existing wallet (ie, from MetaMask, Coinbase Wallet app, etc.) into the CDP ecosystem, allowing you to create complex, programmatic, or agentic interactions.
1-of-1 (Developer-Managed) security: Your wallet's seed and seed phrase will not leave your device.
To import a wallet, use the following commands. Please note that defining your seed phrase within an environment variable is recommended for security.


Warning
Remember to back up your seed phrase. Coinbase is not responsible for any loss of your seed phrase.

// Import your wallet using your BIP-39 mnemonic seed phrase.
// NOTE: for security reasons, we recommend storing your seed phrase in an environment variable.
let importedWallet = await Wallet.import({ mnemonicPhrase: process.env.MNEMONIC_PHRASE }, Coinbase.networks.BaseSepolia );

Once your wallet has been imported, you won't need to import it again:

Export your wallet data (includes your seed and wallet ID) to your desired storage medium.
Re-instantiate your wallet at any time using your exported wallet data, without needing to use your mnemonic seed phrase.
Faucets
On Testnets, asset issuers and others provide faucets for developers to easily fund their wallets for testing purposes.

The CDP SDK provide a faucet method to fund your wallet with ETH, USDC, EURC, cbBTC on Base Sepolia and Ethereum Sepolia testnets.

You are allowed 100 faucet claims per 24-hour window for ETH, and 10 faucet claims per 24-hour window for ERC20 tokens.

Faucet requests can be made at the wallet and address levels in the CDP SDK.

ETH faucet
// Create a faucet request that returns a Faucet transaction, which can be used to retrieve the transaction hash.
let faucetTransaction = await wallet.faucet();

// Wait for the faucet transaction to land on-chain.
await faucetTransaction.wait();

console.log(`Faucet transaction: ${faucetTransaction}`);

ERC20 faucet
// Create a faucet request that returns a Faucet transaction, which can be used to retrieve the transaction hash.
let faucetTransaction = await wallet.faucet(Coinbase.assets.Usdc);

// Wait for the faucet transaction to land on-chain.
await faucetTransaction.wait();

console.log(`Faucet transaction: ${faucetTransaction}`);

Other supported ERC20 assets on Base Sepolia and Ethereum Sepolia:

EURC ("eurc")
cbBTC ("cbbtc")
Other faucets on Base Sepolia:

ETH faucet
USDC faucet / EURC faucet - specify Base Sepolia as the network
Retrieving Balances
To view the amount of assets held in a wallet, call the following:

let balance = await wallet.listBalances();

Or, to obtain the balance of a specific asset, call the following:

let balance = await wallet.getBalance(Coinbase.assets.Eth);

Note that list method only returns balances for the top 20 assets supported by symbol. For other assets, use get as follows.

let balance = await wallet.getBalance("0x036CbD53842c5426634e7929541eC2318f3dCF7e")

Creating webhook
You can create a webhook for the current wallet.

The webhook allow you to receive real-time notifications of wallet activity directly to your application via a specified callback notification URL. By creating a webhook, you can monitor events related to all the addresses for a wallet. See Webhook page for more details on supported event types, event payload and supported networks.

let webhook = await wallet.createWebhook('https://call_back_uri_for_webhook')

Exporting wallets to an external provider
API Wallets provide exportable private keys compatible with all major wallet providers, such as Coinbase Wallet and MetaMask. To export the private key for an address that can be imported into an external provider, use the following code snippet:

let privateKey = address.export();Smart Wallets
A Smart Wallet is an ERC-4337 compatible account abstraction wallet. The Smart Wallet API uses the same smart contract as the Frontend SDK. This new feature is currently in beta.

The Wallet API supports creation of SmartWallets as a backend wallet, offering features like paymaster for sponsoring gas and batch transactions.


Note
If you are interested in using SmartWallet for your users in your frontend application, navigate to the Frontend SDK instead.

A Smart Wallet is a single address that works across EVM networks. For now, only Base Mainnet and Base Sepolia are supported. As we introduce new networks, existing SmartWallets will have the same address and be automatically supported.

A SmartWallet has a single owner, which is the account backed by a private key that signs transactions for the wallet. Think of a private key as the password to a wallet. For more, see What is a private key?.

Creating a Smart Wallet
We recommend using Viem to create the private key and owner account of the SmartWallet.

Refer to the SmartWallet SDK docs for a full list of supported methods.

import { generatePrivateKey, privateKeyToAccount } from "viem/accounts";
import { createSmartWallet } from "@coinbase/coinbase-sdk";
import { Coinbase } from "@coinbase/coinbase-sdk";

// This key must be stored securely and persisted across sessions! See Securing a Smart Wallet below for more information.
const privateKey = generatePrivateKey();
const owner = privateKeyToAccount(privateKey);
const smartWallet = await createSmartWallet({
    signer: owner
});
// Get the smart wallet address
const smartWalletAddress = smartWallet.address;

Sending a User operation
A UserOperation is used to execute transactions through a Smart Wallet, using account abstraction to enable features like batch transactions and sponsored gas fees without needing a traditional EOA wallet.

sendUserOperation is how you send operations for the SmartWallet. It supports batch transactions and paymaster for sponsoring.

For more on Paymaster, see the Paymaster docs.

You can either provide an ABI and the function to call, or the encoded function data. The next example demonstrates a batch transaction that sends ETH to a destination address and calls a function on a contract.

const smartWallet = await createSmartWallet({
    signer: owner
});
const ABI = [
  {
    inputs: [
      { internalType: "uint256", name: "a", type: "uint256" },
      { internalType: "bool", name: "b", type: "bool" },
      { internalType: "address", name: "c", type: "address" },
    ],
    name: "someFunction",
    outputs: [],
    stateMutability: "nonpayable",
    type: "function",
  },
] as const; // This "as const" is very important!

const userOperation = await smartWallet.sendUserOperation({
  calls: [
    {
      to: "0x1234567890123456789012345678901234567890",
      value: parseEther("0.0000005"),
      data: "0x",
    },
    {
      to: "0xb720E683CB90838F23F66a37Adb26c24e04D1b60",
      abi: ABI,
      functionName: "someFunction",
      args: [123n, true, "0x3234567890123456789012345678901234567890"],
    },
  ],
  chainId: 84532,
});

const userOperationResult = await waitForUserOperation(userOperation);
// You can now use the result to see the status and get the transactionHash if it was successful.

For ABIs, make sure to include as const as this is needed by Typescript for proper compilation.

Paymaster
For Base Sepolia, the CDP API automatically sponsors gas for the SmartWallet, so you don't need any gas to send user operations! For Base Mainnet, you can pass in a Paymaster URL to the sendUserOperation function to sponsor the gas for the operation.

Check out the Paymaster docs for more information and getting started with your own Paymaster.

const userOperation = await smartWallet.sendUserOperation({
    calls: [
        {
            to: "0x1234567890123456789012345678901234567890",
            value: parseEther("0.0000005"), 
            data: "0x",
        },
    ],
    chainId: 8453,
    paymasterURL: "https://api.developer.coinbase.com/rpc/v1/base/someapikey",
});

Securing a Smart Wallet
The private key for the owner account must be securely stored. It is your responsibility as the developer to securely store this key. For example, you may choose to store this data in an encrypted database.


Secure your Private Key
Losing the private key for the owner of the SmartWallet could result in a loss of funds. Please take all necessary precautions to secure this key.

Persisting Locally
Here's an example of how to store a private key locally.

To save your private key, run the following:

import fs from "fs";

// create a smart wallet with viem wallet owner
const privateKey = generatePrivateKey();
const owner = privateKeyToAccount(privateKey);
const smartWallet = await createSmartWallet({ signer: owner });

// persist the privateKey and persist the smartWallet address
fs.writeFileSync("privateKey.txt", privateKey);
fs.writeFileSync("smartWalletAddress.txt", smartWallet.address);

In production, developers should encrypt the private key!


Warning
This is an insecure method of storing private keys and should only be used for development purposes.

Re-instantiating a Smart Wallet
The private key and the smart wallet address are required to re-instantiate a wallet when a new session is started.

The following code demonstrates how to import the data required to re-instantiate a wallet.

import fs from "fs";
import { privateKeyToAccount } from "viem/accounts";
import { toSmartWallet } from "@coinbase/coinbase-sdk";

const privateKey = fs.readFileSync("privateKey.txt", "utf8");
const owner = privateKeyToAccount(privateKey as `0x${string}`);
const smartWalletAddress = fs.readFileSync("smartWalletAddress.txt", "utf8") as `0x${string}`;
const smartWallet = toSmartWallet({ smartWalletAddress, signer: owner });

You can now use the smartWallet for all your operations.Addresses
An address is a user-controlled account on a blockchain network. An address can hold a balance of one or more assets, and can be used to send or receive crypto.

An address is backed by a private key, which provides access to spend the assets in the address. Addresses can list their balances and support various verbs depending on the type of address.

Address Types
Depending on how the associated private key is managed, addresses can be classified into two types, wallet and external.

Wallet Addresses
Wallet addresses belong to developer custodied wallets. See Creating a Wallet section. The private keys for these addresses are managed by the CDP SDK. Wallet addresses support all verbs that CDP SDK supports.

External Addresses
External addresses do not belong to CDP Wallets. The CDP SDK can be used to interact with these addresses; but because the SDK does not manage private keys for them, all signing operations are done off-platform. External addresses only support retrieving balances, staking verbs, and funding with testnet tokens with the faucet.

SDK Documentation You can refer to the Address class SDK docs for a full list of supported methods.

Creating Wallet Addresses
Wallet addresses belong to a wallet:

let address = await wallet.createAddress();

A wallet comes with a single address by default, accessible via default_address.

Creating External Addresses
To create an External Address object, provide the address string and the network:

let externalAddress = new ExternalAddress("base-sepolia", "YOUR_WALLET_ADDRESS");

Viewing Address IDs
To view the hexadecimal string that actually represents your address, use the address_id property:

let addressId = address.getId();

Listing Address historical balances for an asset
To view the historical balances of assets of an address, call the following:

let resp = await address.listHistoricalBalances(Coinbase.assets.Usdc);
let historicalBalances = resp.data;

Listing Address transactions
To view all transactions for a specific address in the blockchain, you can use the following code snippet:

let resp = await address.listTransactions();
let transactions = resp.data;Transfers
A transfer is the act of sending an asset from one wallet or address to another.

To transfer an asset, ensure that the source contains some ETH (by using a faucet if on testnet, for example). This is required because the network uses ETH to pay for transaction fees.

Crypto transactions take varying amounts of time—anywhere from hundreds of milliseconds, to tens of minutes, depending on the blockchain network and wallet set-up. For example, transactions on Bitcoin can take upwards of 30 minutes, while transactions on Base take a second or two.

Once your source has ETH in it, call the transfer function as follows:


Warning
Creating multiple transactions simultaneously can lead to failures.

All transfers, excluding gasless transfers, do not support concurrent transactions. We recommend running sequential calls and waiting for the previous transaction to confirm before continuing.

See Processing multiple transfers for same address as an example. If you need more assistance, reach out to us on Discord in #wallet-api.

SDK Documentation

You can refer to the Transfer class SDK docs for a full list of supported methods.

// Transfer 0.00001 Ether to the destination address.
let transfer = await wallet.createTransfer({
  amount: 0.00001,
  assetId: Coinbase.assets.Usdc,
  destination: anotherWallet
});

// Wait for the transfer to settle.
await transfer.wait()

Transfers of arbitrary ERC20 assets
You can transfer ERC20 assets that are not assets supported by symbol by using the contract address as the asset ID.

let contractAddress = "0x036CbD53842c5426634e7929541eC2318f3dCF7e";
let balance = await wallet.getBalance(contractAddress)

// Transfer the full balance of the ERC20 asset to the destination wallet.
let transfer = await wallet.createTransfer({
  amount: balance,
  assetId: contractAddress,
  destination: anotherWallet
});

// Wait for the transfer to settle.
await transfer.wait()

Gasless Transfers
Coinbase will pay for the gas for transfers of USDC, EURC and cbBTC on Base Mainnet and Base Sepolia!

To initiate a USDC transfer on Base Mainnet with gas fees covered, set the gasless flag to true.

import { Wallet, TimeoutError } from '@coinbase/coinbase-sdk';

// Create a wallet on Base Mainnet
let wallet = await Wallet.create({ networkId: Coinbase.networks.BaseMainnet });

// Out-of-Band: Fund the wallet's default address with USDC

// Create a gasless USDC transfer on Base Mainnet
try {
  const transfer = await wallet.createTransfer({
    amount: 0.00001,
    assetId: Coinbase.assets.Usdc,
    destination: anotherWallet,
    gasless: true
  });
} catch (error) {
  console.error(`Error while transferring: `, error);
}

// Wait for transfer to land on-chain.
try {
  await transfer.wait();
} catch (err) {
  if (err instanceof TimeoutError) {
    console.log("Waiting for transfer timed out");
  } else {
    console.error("Error while waiting for transfer to complete: ", error);
  }
}

// Check if transfer successfully completed on-chain
if (transfer.getStatus() === 'complete') {
  console.log('Transfer completed on-chain: ', transfer.toString());
} else {
  console.error('Transfer failed on-chain: ', transfer.toString());
}

Batching
By default, gasless transfers are batched together, which optimizes for high transaction throughput. While batched transfers typically take longer than non-batched ones to process, this approach allows your application to handle many concurrent transactions efficiently.

You can significantly reduce processing time by disabling batching with skipBatching: true. However, this comes with an important tradeoff:

Disabling batching significantly reduces your application's ability to handle concurrent transactions.
We recommend keeping batching enabled to ensure reliable performance as your transaction volume grows.

import { Wallet, TimeoutError } from '@coinbase/coinbase-sdk';

// Create a wallet on Base Mainnet
let wallet = await Wallet.create({ networkId: Coinbase.networks.BaseMainnet });

// Out-of-Band: Fund the wallet's default address with USDC

// Create a gasless USDC transfer on Base Mainnet
try {
  const transfer = await wallet.createTransfer({
    amount: 0.00001,
    assetId: Coinbase.assets.Usdc,
    destination: anotherWallet,
    gasless: true,
    skipBatching: true,
  });
} catch (error) {
  console.error(`Error while transferring: `, error);
}

// Wait for transfer to land on-chain.
try {
  await transfer.wait();
} catch (err) {
  if (err instanceof TimeoutError) {
    console.log("Waiting for transfer timed out");
  } else {
    console.error("Error while waiting for transfer to complete: ", error);
  }
}

// Check if transfer successfully completed on-chain
if (transfer.getStatus() === 'complete') {
  console.log('Transfer completed on-chain: ', transfer.toString());
} else {
  console.error('Transfer failed on-chain: ', transfer.toString());
}

Processing multiple transfers for same address
When creating multiple transfers for the same source address, it is important to create them sequentially instead of all at once. Wait for the previous transfer to have a final state (COMPLETE / FAILED) before creating a new one. Creating multiple transactions simultaneously can lead to failures due to how nonces are managed by the CDP APIs.

An example of how to process transactions sequentially:

for (let i = 0; i < 5; i++)  {
  try {
    const transfer = await wallet.createTransfer({
      amount: 0.00001,
      assetId: Coinbase.assets.Eth,
      destination: wallet,
    });

    await transfer.wait()
  } catch (error) {
    console.error(`Error while transferring: `, error);
  }
}

Transfer to ENS or Basenames
ENS names and Basenames are core building blocks that enable anyone to establish their onchain identity by registering human-readable names for their wallet addresses. CDP SDK supports ENS or Basename as the destination address in your transfers.

// Transfer 0.00001 Ether to the address that belongs to the Base Name/ENS.
let transfer := await wallet.createTransfer({
 amount: 0.00001,
 assetId: Coinbase.assets.Usdc,
 destination: "my-ens-name.base.eth",
 gasless: true
});

# Wait for the transfer to settle.
await transfer.wait()Assets
An asset is a representation of value on a blockchain network. Common types of assets include (fungible) tokens and NFTs (non-fungible tokens). CDP APIs support certain popular assets by their symbols and the vast majority by their contract addresses.

Assets supported by symbol
The CDP APIs support the following assets on the Base Sepolia & Mainnet networks to be identified by their symbols.

Asset
Type
Base-Mainnet
Base-Sepolia
Description
Ether, also known as ETH
native


This is the native token of many networks that run on the Ethereum Virtual Machine (EVM), including Base. ETH is used to pay for transactions on the network, and the network provides native APIs to send, receive, and otherwise interact with ETH.
USDC
ERC‑20


backed 1:1 by a U.S. Dollar.
WETH
ERC-20


backed 1:1 by ETH.
DAI
ERC-20


Dai Stablecoin on Base-Mainnet.
RETH
ERC-20


Rocket Pool ETH on Base-Mainnet.
BRETT
ERC-20


Brett on Base-Mainnet.
W
ERC-20


Wormhole Token on Base-Mainnet.
CBETH
ERC-20


Coinbase Wrapped Ether on Base-Mainnet.
AXL
ERC-20


Axelar on Base-Mainnet.
IOTX
ERC-20


IoTeX on Base-Mainnet.
PRIME
ERC-20


Prime on Base-Mainnet.
AERO
ERC-20


Aerodrome on Base-Mainnet.
RSR
ERC-20


Reserve Rights on Base-Mainnet.
MOG
ERC-20


Mog Coin on Base-Mainnet.
TBTC
ERC-20


Base tBTC v2 on Base-Mainnet.
NPC
ERC-20


Non-Playable Coin on Base-Mainnet.
YFI
ERC-20


Yearn Finance on Base-Mainnet.

In addition to Base, CDP APIs also support ETH & USDC on Ethereum Mainnet, MATIC & USDC on Polygon Mainnet and ARB & USDC on Arbitrum Mainnet.

Assets supported by contract address
Besides the assets listed in the above table, CDP APIs support all other ERC20 tokens using their respective contract addresses.

Transfer an ERC20 from a wallet with contract address
The following example demonstrates how to create a transfer for USDC on Base-Sepolia using its contract address. Use Circle faucet to fund your wallet.

let wallet = await Wallet.create({ networkId: Coinbase.networks.BaseSepolia });

const transfer = await wallet.createTransfer({
  amount: 0.0001,
  assetId: "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
  destination: anotherWallet,
});

// Wait for the transfer to complete.
await transfer.wait();

Trade an ERC20 in a wallet with contract address
The following example demonstrates how to create a trade for USDC on Base-Mainnet using its contract address. Remember to fund your wallet with USDC to complete the trade.

let wallet = await Wallet.create({ networkId: Coinbase.networks.BaseMainnet });

// Out-of-band: Fund the wallet.

// Create trade from ETH to `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`.
let trade = await wallet.createTrade({
  amount: 0.00001,
  fromAssetId: Coinbase.assets.Eth,
  toAssetId: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
});

// Wait for the trade to complete.
await trade.wait();

Fetch balances for assets
Fetch balance for assets identified by symbol
let balance = await wallet.getBalance(Coinbase.assets.Eth)

Fetch balance for assets identified by contract address
let balance = await wallet.getBalance("0x036CbD53842c5426634e7929541eC2318f3dCF7e")

Denominations of ETH
ETH provides 18 places of decimal precision. The smallest amount of sendable ETH is 10-18, also known as a Wei.

Commonly used denominations of ETH:

Denomination
Amount in Wei
Description
Wei
1 Wei
Smallest denomination of ETH
Gwei
109 Wei
Denomination of ETH commonly used for gas (i.e., transaction fee) calculations
Ether / ETH
1018 Wei
Largest denomination of ETH, commonly used for trading

The SDK supports transfers in denominations of Wei, Gwei, and ETH.

SDK Documentation

You can refer to the Asset class SDK docs for a full list of supported methods.

In Node.js, asset IDs are accessed through the assets property of the Coinbase class.

ETH's asset ID is Coinbase.assets.Eth
USDC's asset ID is Coinbase.assets.Usdc
WETH's asset ID is Coinbase.assets.WethIncentivized AI Learning
A simple onchain AI app for reinforcement learning from human feedback.

AI
Wallet API
AI agents cannot get bank accounts, but they can get crypto wallets. Wallet API is a powerful and secure way to give agents crypto wallets and introduce the ability to transfer value to artificial intelligence. Automate complex financial transactions that would be time-consuming for humans to manage at scale, and seamlessly connect AI to the crypto ecosystem.

Incentivized AI Learning


Replit for easy deployments
Replit is an AI-powered software development & deployment platform for building, sharing, and shipping software fast. Coinbase has partnered with Replit to create a template that enables developers to build and deploy AI Wallet applications in just minutes.

Get started with our AI Wallet Replit template. If you plan to deploy this template publicly, read Securing a Wallet to learn how to protect your wallets.

Key Benefits
Financial Autonomy for AI: Enable AI agents to make financial decisions and transactions on your behalf.
Enhanced Security: With Wallet API's 2-of-2 configuration, utilize MPC technology to ensure AI operations remain controlled and secure.
Scalability: Effortlessly handle millions of transactions.
Example Use Cases
Natural Language Financial Transactions: Allow users to manage their finances through simple text commands, with AI interpreting and executing complex financial operations.
AI Financial Concierge: Personal AI assistants that not only recommend services but also handle payments, booking, and planning.
AI-Driven Content Monetization: Create automated systems that create, publish, and monetize content, and manage earnings as an autonomous entity.
Self-Owned Autonomous Vehicle: A self-driving vehicle that picks up drivers, receives payments, and pays for maintenance? The future may be closer than it seems.

Info
We use the Base Sepolia network to demonstrate sending crypto from an AI agent to a user.

We will use the AI feedback app here to demonstrate the solution.

Overview
After you install the CDP SDK, the steps below walk through the AI agent sample app to do the following:

Import required modules.
Create the AI agent's wallet.
Fund the AI agent's wallet with faucet.
Create wallets for end-users to receive payments.
Send crypto from the AI agent's wallet to the user wallet.
Receive funds from other agents or users.
Display the AI agent's wallet balance after sending crypto to the user.
Prerequisites
Install the CDP SDK.
installation
npm install @coinbase/coinbase-sdk

Send crypto from the AI agent's wallet to a user
Step 1. Import required modules
app/api/route.ts
import { Coinbase, Wallet } from "@coinbase/coinbase-sdk"; // Use CDP SDK

Step 2. Create the AI agent's wallet
The app takes the following inputs as environment variables:

NAME: Enter the name of your downloaded CDP API key.
PRIVATE_KEY: Enter the private key of your downloaded CDP API key.
WALLET_DATA: Enter the seed data of your wallet, if you have an existing wallet. Leave it empty if you want a new wallet to be created for the agent. Refer to the persisting wallet section to see how to fetch wallet data.
Expand to see valid WALLET_DATA
Code Reference

The code below shows how to import wallet or create a new one if WALLET_DATA env var is not set.

app/api/route.ts
const { NAME, PRIVATE_KEY, WALLET_DATA } = process.env;

// Check if the environment variables are set
if (!NAME || !PRIVATE_KEY) {
  return Response.json(
    { message: "Environment variables are not set" },
    { status: 500 }
  );
}

const body = await request.json();

// Check if the address is provided
if (!body?.address) {
  return Response.json({ message: "Address is required" }, { status: 400 });
}

// Create a new Coinbase instance
const coinbase = new Coinbase({
  apiKeyName: NAME as string,
  privateKey: PRIVATE_KEY.replaceAll("\\n", "\n") as string,
});

let userWallet;

// Check if the wallet data is provided
if (WALLET_DATA && WALLET_DATA?.length > 0) {
  try {
    // Parse the wallet data
    const seedFile = JSON.parse(WALLET_DATA || "{}");

    // Get the wallet ids from the seed file. The seed file is a JSON object with wallet ids as keys.
    const walletIds = Object.keys(seedFile);

    // Get a random wallet id
    const walletId = getRandomItems(walletIds, 1)[0];

    // Get the seed of the wallet
    const seed = seedFile[walletId]?.seed;

    // Import the wallet
    userWallet = await Wallet.import({ seed, walletId });
    await userWallet.listAddresses();
  } catch (e) {
    return Response.json(
      { message: "Failed to import wallet" },
      { status: 500 }
    );
  }
} else {
  // Otherwise, create a new wallet
  userWallet = await Wallet.create();
}

Step 3. Fund the AI agent's Wallet with faucet
To fund the wallet with ETH on Base Sepolia, utilize the faucet method.

app/api/route.ts
// Fund the wallet with faucet if required
try {
  // Request funds from the faucet if it's available
  let faucetTx = await userWallet?.faucet()

  await faucetTx.wait();
} catch (e) {
  // Log if the faucet is not available.
  console.log("Faucet is not available");
}

Step 4. Create wallets for end-users to receive payments
Use Coinbase Smart Wallets to enable users without an existing wallet to get payments from the AI agent.

Smart Wallets provide a seamless account creation process in seconds, eliminating the need for an app or extension. This is made possible by utilizing passkeys for signing, which are securely generated and stored on users' devices.

The code to integrate Coinbase Smart Wallet in your application can be found here.

Step 5. Send crypto from the AI agent's wallet to the user wallet
Use createTransfer to send crypto from the AI agent's wallet to the user wallet after the user has completed their task.

app/api/route.ts
// Create a transfer to the destination address
const transfer = await userWallet?.createTransfer({
  amount: 0.00000001,
  assetId: "eth",
  destination: body.address,
});

// Wait for transfer to settle.
await transfer.wait();

  // Return the transaction hash and link
return Response.json(
  {
    transactionHash: transfer?.getTransactionHash()?.substring(0, 10),
    transactionLink: transfer?.getTransactionLink(),
    successful: transfer.getStatus() === 'complete'
  },
  { status: 200 }
);

Step 6. Receive funds from other agents or users
To receive funds from other agents or users, fetch the default address of the AI agent's wallet with the following method:

// Get the default address of the wallet
const defaultAddress = await userWallet?.getDefaultAddress();
console.log("AI agent's Wallet's Address: ", defaultAddress);

Step 7. Display the AI agent's wallet balance after sending crypto to the user
Use balances to get the balance of the AI agent's wallet after sending crypto to the user.

// Get the balance of the wallet
const balances = await userWallet?.balances();
console.log("Balances: ", balances);

To see the full code, refer to the AI agent sample app.