Connect to MetaMask
You can connect your dapp to users' MetaMask wallets by detecting MetaMask in their browsers and connecting to their accounts. This page provides instructions for connecting to MetaMask using the wallet detection mechanism introduced by EIP-6963. This approach allows you to detect multiple installed wallets and connect to them without conflicts.

info
Learn more about EIP-6963 in Wallet interoperability.

tip
To connect to MetaMask without using EIP-6963, see the Create a simple dapp tutorial.

You can connect to MetaMask using third-party libraries or directly using Vite.

Connect to MetaMask using third-party libraries
You can connect to MetaMask using the following third-party libraries that support EIP-6963:

Wagmi 2+
Web3Modal 3+
MIPD Store
RainbowKit
Web3-Onboard
ConnectKit
Connect to MetaMask directly using Vite
To connect to MetaMask directly, we recommend implementing support for EIP-6963 using the Vite build tool with vanilla TypeScript or React TypeScript.

Vanilla TypeScript
Follow these steps for creating a vanilla TypeScript project to connect to MetaMask:

1. Create a project
Create a Vite project using the template for vanilla TypeScript:

npm create vite@latest vanilla-ts-6963 -- --template vanilla-ts
2. Set up the project
In your Vite project, update src/vite-env.d.ts with the EIP-6963 interfaces:

vite-env.d.ts
/// <reference types="vite/client" />

interface EIP6963ProviderInfo {
  rdns: string
  uuid: string
  name: string
  icon: string
}

interface EIP6963ProviderDetail {
  info: EIP6963ProviderInfo
  provider: EIP1193Provider
}

type EIP6963AnnounceProviderEvent = {
  detail: {
    info: EIP6963ProviderInfo
    provider: Readonly<EIP1193Provider>
  }
}

interface EIP1193Provider {
  isStatus?: boolean
  host?: string
  path?: string
  sendAsync?: (
    request: { method: string; params?: Array<unknown> },
    callback: (error: Error | null, response: unknown) => void
  ) => void
  send?: (
    request: { method: string; params?: Array<unknown> },
    callback: (error: Error | null, response: unknown) => void
  ) => void
  request: (request: {
    method: string
    params?: Array<unknown>
  }) => Promise<unknown>
}
note
In addition to the EIP-6963 interfaces, you need a EIP1193Provider interface (defined by EIP-1193), which is the foundational structure for Ethereum wallet providers, and represents the essential properties and methods for interacting with MetaMask and other Ethereum wallets in JavaScript.

3. Update main.ts
Update src/main.ts with the following code:

main.ts
import "./style.css"
import { listProviders } from "./providers.ts"

document.querySelector<HTMLDivElement>("#app")!.innerHTML = `
  <div>
    <div id="providerButtons"></div>
  </div>
`

listProviders(document.querySelector<HTMLDivElement>("#providerButtons")!)
The querySelector finds and returns the first HTML element that matches the CSS selector app, and sets its innerHTML. You need to include a basic HTML structure with an inner div to inject a list of buttons, each representing a detected wallet provider.

You'll create the listProviders function in the next step, and pass an argument which represents the div element.

4. Connect to wallets
Create a file src/providers.ts with the following code:

providers.ts
declare global {
  interface WindowEventMap {
    "eip6963:announceProvider": CustomEvent
  }
}

// Connect to the selected provider using eth_requestAccounts.
const connectWithProvider = async (
  wallet: EIP6963AnnounceProviderEvent["detail"]
) => {
  try {
    await wallet.provider.request({ method: "eth_requestAccounts" })
  } catch (error) {
    console.error("Failed to connect to provider:", error)
  }
}

// Display detected providers as connect buttons.
export function listProviders(element: HTMLDivElement) {
  window.addEventListener(
    "eip6963:announceProvider",
    (event: EIP6963AnnounceProviderEvent) => {
      const button = document.createElement("button")

      button.innerHTML = `
        <img src="${event.detail.info.icon}" alt="${event.detail.info.name}" />
        <div>${event.detail.info.name}</div>
      `

      // Call connectWithProvider when a user selects the button.
      button.onclick = () => connectWithProvider(event.detail)
      element.appendChild(button)
    }
  )

  // Notify event listeners and other parts of the dapp that a provider is requested.
  window.dispatchEvent(new Event("eip6963:requestProvider"))
}
The connectWithProvider function connects the user to the selected provider using eth_requestAccounts. The wallet object is passed as an argument to the function, indicating the argument type.

The listProviders function uses a simplified approach. Instead of mapping and joining an entire block of HTML, it directly passes the event.detail object to the connectWithProvider function when a provider is announced.

5. View the project
Run the following command to view and test the Vite project in your browser:

npm run dev
Example
See the vanilla TypeScript example for more information. You can clone the repository and run the example locally using npm i && npm run dev.

React TypeScript
Follow these steps for creating a React TypeScript project to connect to MetaMask:

1. Create a project
Create a Vite project using the template for React TypeScript:

npm create vite@latest react-ts-6963 -- --template react-ts
2. Set up the project
In your Vite project, update src/vite-env.d.ts with the EIP-6963 interfaces:

vite-env.d.ts
/// <reference types="vite/client" />

interface EIP6963ProviderInfo {
  rdns: string
  uuid: string
  name: string
  icon: string
}

interface EIP6963ProviderDetail {
  info: EIP6963ProviderInfo
  provider: EIP1193Provider
}

type EIP6963AnnounceProviderEvent = {
  detail: {
    info: EIP6963ProviderInfo
    provider: Readonly<EIP1193Provider>
  }
}

interface EIP1193Provider {
  isStatus?: boolean
  host?: string
  path?: string
  sendAsync?: (
    request: { method: string; params?: Array<unknown> },
    callback: (error: Error | null, response: unknown) => void
  ) => void
  send?: (
    request: { method: string; params?: Array<unknown> },
    callback: (error: Error | null, response: unknown) => void
  ) => void
  request: (request: {
    method: string
    params?: Array<unknown>
  }) => Promise<unknown>
}
note
In addition to the EIP-6963 interfaces, you need a EIP1193Provider interface (defined by EIP-1193), which is the foundational structure for Ethereum wallet providers, and represents the essential properties and methods for interacting with MetaMask and other Ethereum wallets in JavaScript.

3. Update App.tsx
Update src/App.tsx with the following code:

App.tsx
import "./App.css"
import { DiscoverWalletProviders } from "./components/DiscoverWalletProviders"

function App() {
  return (
    <DiscoverWalletProviders/>
  )
}

export default App
This code renders the DiscoverWalletProviders component that you'll create in the next step, which contains the logic for detecting and connecting to wallet providers.

4. Detect and connect to wallets
In the src/components directory, create a component DiscoverWalletProviders.tsx with the following code:

DiscoverWalletProviders.tsx
import { useState } from "react"
import { useSyncProviders } from "../hooks/useSyncProviders"
import { formatAddress } from "~/utils"

export const DiscoverWalletProviders = () => {
  const [selectedWallet, setSelectedWallet] = useState<EIP6963ProviderDetail>()
  const [userAccount, setUserAccount] = useState<string>("")
  const providers = useSyncProviders()

  // Connect to the selected provider using eth_requestAccounts.
  const handleConnect = async (providerWithInfo: EIP6963ProviderDetail) => {
    try {
      const accounts = await providerWithInfo.provider.request({
        method: "eth_requestAccounts"
      })

      setSelectedWallet(providerWithInfo)
      setUserAccount(accounts?.[0])
    } catch (error) {
      console.error(error)
    }
  }

  // Display detected providers as connect buttons.
  return (
    <>
      <h2>Wallets Detected:</h2>
      <div>
        {
          providers.length > 0 ? providers?.map((provider: EIP6963ProviderDetail) => (
            <button key={provider.info.uuid} onClick={() => handleConnect(provider)} >
              <img src={provider.info.icon} alt={provider.info.name} />
              <div>{provider.info.name}</div>
            </button>
          )) :
            <div>
              No Announced Wallet Providers
            </div>
        }
      </div>
      <hr />
      <h2>{userAccount ? "" : "No "}Wallet Selected</h2>
      {userAccount &&
        <div>
          <div>
            <img src={selectedWallet.info.icon} alt={selectedWallet.info.name} />
            <div>{selectedWallet.info.name}</div>
            <div>({formatAddress(userAccount)})</div>
          </div>
        </div>
      }
    </>
  )
}
In this code:

selectedWallet is a state variable that holds the user's most recently selected wallet.
userAccount is a state variable that holds the user's connected wallet's address.
useSyncProviders is a custom hook that returns the providers array (wallets installed in the browser).
The handleConnect function takes a providerWithInfo, which is an EIP6963ProviderDetail object. That object is used to request the user's accounts from the provider using eth_requestAccounts.

If the request succeeds, the selectedWallet and userAccount local state variables are set.

Then, the component maps over the providers array and renders a button for each detected provider.

Finally, if the userAccount state variable is not empty, the selected wallet icon, name, and address are displayed.

5. Add React hooks
Create a src/hooks directory and add a store.ts file with the following code:

hooks/store.ts
declare global {
  interface WindowEventMap {
    "eip6963:announceProvider": CustomEvent
  }
}

// An array to store the detected wallet providers.
let providers: EIP6963ProviderDetail[] = []

export const store = {
  value: () => providers,
  subscribe: (callback: () => void) => {
    function onAnnouncement(event: EIP6963AnnounceProviderEvent) {
      if (providers.map((p) => p.info.uuid).includes(event.detail.info.uuid))
        return
      providers = [...providers, event.detail]
      callback()
    }

    // Listen for eip6963:announceProvider and call onAnnouncement when the event is triggered.
    window.addEventListener("eip6963:announceProvider", onAnnouncement)

    // Dispatch the event, which triggers the event listener in the MetaMask wallet.
    window.dispatchEvent(new Event("eip6963:requestProvider"))

    // Return a function that removes the event listener.
    return () =>
      window.removeEventListener("eip6963:announceProvider", onAnnouncement)
  },
}
Also, add a file useSyncProviders.ts with the following code to the hooks directory:

hooks/useSyncProviders.ts
import { useSyncExternalStore } from "react"
import { store } from "./store"

export const useSyncProviders = () =>
  useSyncExternalStore(store.subscribe, store.value, store.value)
This hook allows you to subscribe to MetaMask events, read updated values, and update components. It uses the store.value and store.subscribe methods defined in the store.ts hook.

6. Create utility functions
Create a src/utils directory and add a file index.ts with the following code:

index.ts
export const formatBalance = (rawBalance: string) => {
  const balance = (parseInt(rawBalance) / 1000000000000000000).toFixed(2)
  return balance
}

export const formatChainAsNum = (chainIdHex: string) => {
  const chainIdNum = parseInt(chainIdHex)
  return chainIdNum
}

export const formatAddress = (addr: string) => {
  const upperAfterLastTwo = addr.slice(0, 2) + addr.slice(2)
  return `${upperAfterLastTwo.substring(0, 5)}...${upperAfterLastTwo.substring(39)}`
}
This is a good place to store utility functions that you might need to reuse throughout your dapp. This example only uses the formatAddress function, but the others might be useful for other applications.

Example
See the React TypeScript example for more information. You can clone the repository and run the example locally using npm i && npm run dev.

Next steps
After connecting to MetaMask directly, you can:

Detect, add, and switch networks.
Send transactions.
Sign data.
Display tokens, contract methods, and icons in MetaMask.Access a user's accounts
User accounts are used in a variety of contexts in Ethereum, including as identifiers and for signing transactions. To request a signature from a user or have a user approve a transaction, your dapp can access the user's accounts using the eth_requestAccounts RPC method.

note
eth_requestAccounts internally calls wallet_requestPermissions to request permission to call the restricted eth_accounts method.

When accessing a user's accounts:

Only initiate a connection request in response to direct user action, such as selecting a connect button.
Always disable the connect button while the connection request is pending.
Never initiate a connection request on page load.
note
You can also access users' accounts on some non-EVM networks.

Create a connect button
Important
This section describes how to create a single connect button. When connecting to multiple wallets, use the Connect to MetaMask guide to create multiple connect buttons.

We recommend providing a button to allow users to connect MetaMask to your dapp. Selecting this button should call eth_requestAccounts to access the user's accounts.

For example, the following JavaScript code accesses the user's accounts when they select a connect button:

index.js
// You should only attempt to request the user's account in response to user interaction, such as
// selecting a button. Otherwise, you pop-up spam the user like it's 1999. If you fail to retrieve
// the user's account, you should encourage the user to initiate the attempt.
const ethereumButton = document.querySelector(".enableEthereumButton")
const showAccount = document.querySelector(".showAccount")

ethereumButton.addEventListener("click", () => {
  getAccount()
})

// While awaiting the call to eth_requestAccounts, you should disable any buttons the user can
// select to initiate the request. MetaMask rejects any additional requests while the first is still
// pending.
async function getAccount() {
  const accounts = await provider // Or window.ethereum if you don't support EIP-6963.
    .request({ method: "eth_requestAccounts" })
    .catch((err) => {
      if (err.code === 4001) {
        // EIP-1193 userRejectedRequest error.
        // If this happens, the user rejected the connection request.
        console.log("Please connect to MetaMask.")
      } else {
        console.error(err)
      }
    })
  const account = accounts[0]
  showAccount.innerHTML = account
}
The following HTML code displays the button and the current account:

index.html
<!-- Display a connect button and the current account -->
<button class="enableEthereumButton">Enable Ethereum</button>
<h2>Account: <span class="showAccount"></span></h2>
Handle accounts
Use the eth_accounts RPC method to handle user accounts. Listen to the accountsChanged provider event to be notified when the user changes accounts.

The following code handles user accounts and detects when the user changes accounts:

index.js
let currentAccount = null
provider // Or window.ethereum if you don't support EIP-6963.
  .request({ method: "eth_accounts" })
  .then(handleAccountsChanged)
  .catch((err) => {
    // Some unexpected error.
    // For backwards compatibility reasons, if no accounts are available, eth_accounts returns an
    // empty array.
    console.error(err)
  })

// Note that this event is emitted on page load. If the array of accounts is non-empty, you're
// already connected.
provider // Or window.ethereum if you don't support EIP-6963.
  .on("accountsChanged", handleAccountsChanged)

// eth_accounts always returns an array.
function handleAccountsChanged(accounts) {
  if (accounts.length === 0) {
    // MetaMask is locked or the user has not connected any accounts.
    console.log("Please connect to MetaMask.")
  } else if (accounts[0] !== currentAccount) {
    // Reload your interface with accounts[0].
    currentAccount = accounts[0]
    // Update the account displayed (see the HTML for the connect button)
    showAccount.innerHTML = currentAccount
  }
}
note
eth_accounts now returns the full list of accounts for which the user has permitted access to. Previously, eth_accounts returned at most one account in the accounts array. The first account in the array will always be considered the user's "selected" account.

Disconnect a user's accounts
Since eth_requestAccounts internally calls wallet_requestPermissions for permission to call eth_accounts, you can use wallet_revokePermissions to revoke this permission, revoking your dapp's access to the user's accounts.

This is useful as a method for users to log out (or disconnect) from your dapp. You can then use wallet_getPermissions to determine whether the user is connected or disconnected to your dapp.

See how to revoke permissions for an example.Detect a user's network
It's important to keep track of the user's network chain ID because all RPC requests are submitted to the currently connected network.

Use the eth_chainId RPC method to detect the chain ID of the user's current network. Listen to the chainChanged provider event to detect when the user changes networks.

For example, the following code detects a user's network and when the user changes networks:

index.js
const chainId = await provider // Or window.ethereum if you don't support EIP-6963.
  .request({ method: "eth_chainId" })

provider // Or window.ethereum if you don't support EIP-6963.
  .on("chainChanged", handleChainChanged)

function handleChainChanged(chainId) {
  // We recommend reloading the page, unless you must do otherwise.
  window.location.reload()
}Add a network
In some cases, such as when interacting with smart contracts, your dapp must connect a user to a new network in MetaMask. Instead of the user adding a new network manually, which requires them to configure RPC URLs and chain IDs, your dapp can use the wallet_addEthereumChain and wallet_switchEthereumChain RPC methods to prompt the user to add a specific, pre-configured network to their MetaMask wallet.

These methods are specified by EIP-3085 and EIP-3326, and we recommend using them together.

wallet_addEthereumChain creates a confirmation asking the user to add the specified network to MetaMask.
wallet_switchEthereumChain creates a confirmation asking the user to switch to the specified network.
The confirmations look like the following:

Add network confirmation
Switch network confirmation
Development and non-EVM networks
To add a local development network such as Hardhat to MetaMask, see Run a development network.
To add a non-EVM network such as Starknet to MetaMask, see Use non-EVM networks.
Example
The following is an example of using wallet_addEthereumChain and wallet_switchEthereumChain to prompt a user to add and switch to a new network:

try {
  await provider // Or window.ethereum if you don't support EIP-6963.
    .request({
      method: "wallet_switchEthereumChain",
      params: [{ chainId: "0xf00" }],
    })
} catch (switchError) {
  // This error code indicates that the chain has not been added to MetaMask.
  if (switchError.code === 4902) {
    try {
      await provider // Or window.ethereum if you don't support EIP-6963.
        .request({
          method: "wallet_addEthereumChain",
          params: [
            {
              chainId: "0xf00",
              chainName: "...",
              rpcUrls: ["https://..."] /* ... */,
            },
          ],
        })
    } catch (addError) {
      // Handle "add" error.
    }
  }
  // Handle other "switch" errors.
}Sign data
You can use the following RPC methods to request cryptographic signatures from users:

eth_signTypedData_v4 - Use this method to request the most human-readable signatures that are efficient to process onchain. We recommend this for most use cases.
personal_sign - Use this method for the easiest way to request human-readable signatures that don't need to be efficiently processed onchain.
caution
eth_sign is deprecated.

note
MetaMask supports signing transactions using Trezor and Ledger hardware wallets. These wallets only support signing data using personal_sign. If you can't log in to a dapp when using a Ledger or Trezor, the dapp might be requesting you to sign data using an unsupported method, in which case we recommend using your standard MetaMask account.

Use eth_signTypedData_v4
eth_signTypedData_v4 provides the most human-readable signatures that are efficient to process onchain. It follows the EIP-712 specification to allow users to sign typed structured data that can be verified onchain. It renders the structured data in a useful way (for example, displaying known account names in place of addresses).

eth_signTypedData_v4


An eth_signTypedData_v4 payload uses a standard format of encoding structs, but has a different format for the top-level struct that is signed, which includes some metadata about the verifying contract to provide replay protection of these signatures between different contract instances.

We recommend using eth-sig-util to generate and validate signatures. You can use eip712-codegen to generate most of the Solidity required to verify these signatures onchain. It currently doesn't generate the top-level struct verification code, so you must write that part manually. See this example implementation.

caution
Since the top-level struct type's name and the domain.name are presented to the user prominently in the confirmation, consider your contract name, the top-level struct name, and the struct keys to be a user-facing security interface. Ensure your contract is as readable as possible to the user.

Example
The following is an example of using eth_signTypedData_v4 with MetaMask:

index.js
signTypedDataV4Button.addEventListener("click", async function (event) {
  event.preventDefault()

  // eth_signTypedData_v4 parameters. All of these parameters affect the resulting signature.
  const msgParams = JSON.stringify({
    domain: {
      // This defines the network, in this case, Mainnet.
      chainId: 1,
      // Give a user-friendly name to the specific contract you're signing for.
      name: "Ether Mail",
      // Add a verifying contract to make sure you're establishing contracts with the proper entity.
      verifyingContract: "0xCcCCccccCCCCcCCCCCCcCcCccCcCCCcCcccccccC",
      // This identifies the latest version.
      version: "1",
    },

    // This defines the message you're proposing the user to sign, is dapp-specific, and contains
    // anything you want. There are no required fields. Be as explicit as possible when building out
    // the message schema.
    message: {
      contents: "Hello, Bob!",
      attachedMoneyInEth: 4.2,
      from: {
        name: "Cow",
        wallets: [
          "0xCD2a3d9F938E13CD947Ec05AbC7FE734Df8DD826",
          "0xDeaDbeefdEAdbeefdEadbEEFdeadbeEFdEaDbeeF",
        ],
      },
      to: [
        {
          name: "Bob",
          wallets: [
            "0xbBbBBBBbbBBBbbbBbbBbbbbBBbBbbbbBbBbbBBbB",
            "0xB0BdaBea57B0BDABeA57b0bdABEA57b0BDabEa57",
            "0xB0B0b0b0b0b0B000000000000000000000000000",
          ],
        },
      ],
    },
    // This refers to the keys of the following types object.
    primaryType: "Mail",
    types: {
      // This refers to the domain the contract is hosted on.
      EIP712Domain: [
        { name: "name", type: "string" },
        { name: "version", type: "string" },
        { name: "chainId", type: "uint256" },
        { name: "verifyingContract", type: "address" },
      ],
      // Not an EIP712Domain definition.
      Group: [
        { name: "name", type: "string" },
        { name: "members", type: "Person[]" },
      ],
      // Refer to primaryType.
      Mail: [
        { name: "from", type: "Person" },
        { name: "to", type: "Person[]" },
        { name: "contents", type: "string" },
      ],
      // Not an EIP712Domain definition.
      Person: [
        { name: "name", type: "string" },
        { name: "wallets", type: "address[]" },
      ],
    },
  })

  var from = await web3.eth.getAccounts()

  var params = [from[0], msgParams]
  var method = "eth_signTypedData_v4"

  provider // Or window.ethereum if you don't support EIP-6963.
    .sendAsync(
      {
        method,
        params,
        from: from[0],
      },
      function (err, result) {
        if (err) return console.dir(err)
        if (result.error) {
          alert(result.error.message)
        }
        if (result.error) return console.error("ERROR", result)
        console.log("TYPED SIGNED:" + JSON.stringify(result.result))

        const recovered = sigUtil.recoverTypedSignature_v4({
          data: JSON.parse(msgParams),
          sig: result.result,
        })

        if (
          ethUtil.toChecksumAddress(recovered) ===
          ethUtil.toChecksumAddress(from)
        ) {
          alert("Successfully recovered signer as " + from)
        } else {
          alert(
            "Failed to verify signer when comparing " + result + " to " + from
          )
        }
      }
    )
})
The following HTML displays a sign button:

index.html
<h3>Sign typed data v4</h3>
<button type="button" id="signTypedDataV4Button">eth_signTypedData_v4</button>
See the live example and test dapp source code for more information.

Use personal_sign
personal_sign is the easiest way to request human-readable signatures that don't need to be efficiently processed onchain. It's often used for signature challenges that are authenticated on a web server, such as Sign-In with Ethereum.

Personal sign


important
Don't use this method to display binary data, because the user wouldn't be able to understand what they're agreeing to.
If using this method for a signature challenge, think about what would prevent a phisher from reusing the same challenge and impersonating your site. Add text referring to your domain, or the current time, so the user can easily verify if this challenge is legitimate.
Example
The following is an example of using personal_sign with MetaMask:

index.js
personalSignButton.addEventListener("click", async function (event) {
  event.preventDefault()
  const exampleMessage = "Example `personal_sign` message."
  try {
    const from = accounts[0]
    // For historical reasons, you must submit the message to sign in hex-encoded UTF-8.
    // This uses a Node.js-style buffer shim in the browser.
    const msg = `0x${Buffer.from(exampleMessage, "utf8").toString("hex")}`
    const sign = await ethereum.request({
      method: "personal_sign",
      params: [msg, from],
    })
    personalSignResult.innerHTML = sign
    personalSignVerify.disabled = false
  } catch (err) {
    console.error(err)
    personalSign.innerHTML = `Error: ${err.message}`
  }
})
The following HTML displays a sign button:

index.html
<h3>Personal sign</h3>
<button type="button" id="personalSignButton">personal_sign</button>
personal_sign prepends the message with \x19Ethereum Signed Message:\n<length of message> before hashing and signing it.

Sign in with Ethereum
You can set up Sign-In with Ethereum (SIWE) to enable users to easily sign in to your dapp by authenticating with their MetaMask wallet.

MetaMask supports the SIWE standard message format as specified in ERC-4361. When your dapp prompts a user to sign a message that follows the SIWE format, MetaMask parses the message and gives the user a friendly interface prompting them to sign in to your dapp:

Sign-in with Ethereum request

Domain binding
MetaMask supports domain binding with SIWE to help prevent phishing attacks. When a site asks a user to sign a SIWE message, but the domain in the message doesn't match the site the user is on, MetaMask displays a warning in the sign-in interface. The user must explicitly select to proceed, accepting the risk of a phishing attack.

important
MetaMask displays a prominent warning for mismatched domains, but does not block users from bypassing the warning and accepting the sign-in request. This is to not break existing dapps that may have use cases for mismatched domains.

Sign-in bad domain
Sign-in bad domain pop-up
Example
The following is an example of setting up SIWE with MetaMask using personal_sign:

index.js
const siweSign = async (siweMessage) => {
  try {
    const from = accounts[0]
    const msg = `0x${Buffer.from(siweMessage, "utf8").toString("hex")}`
    const sign = await provider // Or window.ethereum if you don't support EIP-6963.
      .request({
        method: "personal_sign",
        params: [msg, from],
      })
    siweResult.innerHTML = sign
  } catch (err) {
    console.error(err)
    siweResult.innerHTML = `Error: ${err.message}`
  }
}

siwe.onclick = async () => {
  const domain = window.location.host
  const from = accounts[0]
  const siweMessage = `${domain} wants you to sign in with your Ethereum account:\n${from}\n\nI accept the MetaMask Terms of Service: https://community.metamask.io/tos\n\nURI: https://${domain}\nVersion: 1\nChain ID: 1\nNonce: 32891757\nIssued At: 2021-09-30T16:25:24.000Z`
  siweSign(siweMessage)
}
The following HTML displays the SIWE button:

index.html
<h4>Sign-In with Ethereum</h4>
<button type="button" id="siwe">Sign-In with Ethereum</button>
<p class="alert">Result:<span id="siweResult"></span></p>
See the live example and test dapp source code for more information.

Send transactions
You can send a transaction in MetaMask using the eth_sendTransaction RPC method.

For example, the following JavaScript gets the user's accounts and sends a transaction when they select each button:

index.js
const ethereumButton = document.querySelector(".enableEthereumButton");
const sendEthButton = document.querySelector(".sendEthButton");

let accounts = [];

sendEthButton.addEventListener("click", () => {
  provider // Or window.ethereum if you don't support EIP-6963.
    .request({
      method: "eth_sendTransaction",
      params: [
        {
          from: accounts[0], // The user's active address.
          to: "0x0000000000000000000000000000000000000000", // Address of the recipient. Not used in contract creation transactions.
          value: "0x0", // Value transferred, in wei. Only required to send ether to the recipient from the initiating external account.
          gasLimit: "0x5028", // Customizable by the user during MetaMask confirmation.
          maxPriorityFeePerGas: "0x3b9aca00", // Customizable by the user during MetaMask confirmation.
          maxFeePerGas: "0x2540be400", // Customizable by the user during MetaMask confirmation.
        },
      ],
    })
    .then((txHash) => console.log(txHash))
    .catch((error) => console.error(error));
});

ethereumButton.addEventListener("click", () => {
  getAccount();
});

async function getAccount() {
  accounts = await provider // Or window.ethereum if you don't support EIP-6963.
    .request({ method: "eth_requestAccounts" });
}
The following HTML displays the buttons:

index.html
<button class="enableEthereumButton btn">Enable Ethereum</button>
<button class="sendEthButton btn">Send ETH</button>
Transaction parameters
The transaction parameters depend on the transaction type. The following are examples of transaction objects for each type:

Legacy transaction
Access list transaction
EIP-1559 transaction
{
  nonce: "0x0", // Number of transactions made by the sender before this one.
  gasPrice: "0x09184e72a000", // Gas price, in wei, provided by the sender.
  gasLimit: "0x2710", // Maximum gas provided by the sender.
  to: "0x0000000000000000000000000000000000000000", // Address of the recipient. Not used in contract creation transactions.
  value: "0x0", // Value transferred, in wei.
  data: "0x7f7465737432000000000000000000000000000000000000000000000000000000600057", // Used for defining contract creation and interaction.
  v: "0x1", // ECDSA recovery ID.
  r: "0xa07fd6c16e169f0e54b394235b3a8201101bb9d0eba9c8ae52dbdf556a363388", // ECDSA signature r.
  s: "0x36f5da9310b87fefbe9260c3c05ec6cbefc426f1ff3b3a41ea21b5533a787dfc", // ECDSA signature s.
}
Nonce
note
MetaMask ignores this field.

In Ethereum, every transaction has a nonce, so each transaction can only be processed by the blockchain once. To be a valid transaction, either:

The nonce must be 0.
A transaction with a nonce of the previous number, from the same account, must have been processed.
This means that transactions are always processed in order for a given account.

Nonces are easy to mess up, especially when a user is interacting with multiple applications with pending transactions using the same account, potentially across multiple devices. Because of this, MetaMask doesn't allow dapp developers to customize nonces. Instead, MetaMask assists the user in managing their transaction queue themselves.

Gas price
gasPrice is an optional parameter. It is used in legacy transactions and specifies the gas price the sender is willing to pay for the transaction. MetaMask automatically configures gas settings, but users can also customize these settings.

Gas limit
gasLimit is an optional parameter. It specifies the maximum amount of gas units the sender is willing to pay for the transaction. MetaMask automatically sets this parameter, but users can also customize their gas settings.

Max priority fee per gas
maxPriorityFeePerGas is an optional parameter. It is used in EIP-1559 transactions and specifies the maximum fee the sender is willing to pay per gas above the base fee, in order to get their transaction prioritized. MetaMask automatically sets this parameter, but users can also customize their gas settings.

Max fee per gas
maxFeePerGas is an optional parameter. It is used in EIP-1559 transactions and specifies the maximum total fee (base fee + priority fee) the sender is willing to pay per gas. MetaMask automatically sets this parameter, but users can also customize their gas settings.

To
The to parameter is a hex-encoded Ethereum address. It's required for transactions with a recipient (all transactions except for contract creation).

Contract creation occurs when there is no to value but there is a data value.

Value
The value parameter is a hex-encoded value of the network's native currency to send. On Mainnet, this is ether, which is denominated in wei.

These numbers are often far higher precision than native JavaScript numbers, and can cause unpredictable behavior if not anticipated. We recommend using BN.js when manipulating values intended for Ethereum.

Data
The data parameter is required for smart contract creation.

This field is also used for specifying contract methods and their parameters. See the Solidity ABI spec for more information on how the data is encoded.

Chain ID
note
MetaMask ignores this field.

The chain ID is derived from the user's current selected network. Use eth_chainId to get the user's chain ID. If you need the network version, use net_version.

In the future, MetaMask might allow connecting to multiple networks at the same time, at which point this parameter will become important, so it might be useful to be in the habit of including it now.

Edit this pageManage permissions
To call a restricted RPC method, your dapp must request permission from the user using the wallet_requestPermissions RPC method. You can get the user's current permissions using wallet_getPermissions, and revoke permissions previously granted to your dapp using wallet_revokePermissions. These methods are specified by EIP-2255 and MIP-2.

wallet_requestPermissions creates a confirmation asking the user to connect to an account and allow the dapp to call the requested method. The confirmation screen describes the functions and data the requested method can access. For example, something like the following confirmation displays when you request permission to call the restricted method eth_accounts:

Request permissions confirmation 1
Request permissions confirmation 2
note
To access accounts, we recommend using eth_requestAccounts, which automatically asks for permission to use eth_accounts by calling wallet_requestPermissions internally. See how to access a user's accounts for more information. Granting permission for eth_accounts also grants access to eth_sendTransaction, personal_sign, and eth_signTypedData_v4.

Request permissions example
The following example uses wallet_requestPermissions to request permission from the user to call eth_accounts:

document.getElementById("requestPermissionsButton", requestPermissions)

function requestPermissions() {
  provider // Or window.ethereum if you don't support EIP-6963.
    .request({
      method: "wallet_requestPermissions",
      params: [{ eth_accounts: {} }],
    })
    .then((permissions) => {
      const accountsPermission = permissions.find(
        (permission) => permission.parentCapability === "eth_accounts"
      )
      if (accountsPermission) {
        console.log("eth_accounts permission successfully requested!")
      }
    })
    .catch((error) => {
      if (error.code === 4001) {
        // EIP-1193 userRejectedRequest error
        console.log("Permissions needed to continue.")
      } else {
        console.error(error)
      }
    })
}
Revoke permissions example
The following example uses wallet_revokePermissions to revoke the dapp's permission to call eth_accounts:

await provider // Or window.ethereum if you don't support EIP-6963.
  .request({
    method: "wallet_revokePermissions",
    params: [
      {
        eth_accounts: {},
      },
    ],
  })Use the MetaMask onboarding library
Sending users away from your dapp to install MetaMask presents challenges. You must inform the user to return to your dapp and refresh their browser after the installation. Your dapp detects the user's newly installed MetaMask extension only after that refresh.

You can use MetaMask's onboarding library to improve and simplify the onboarding experience. The library exposes an API to initiate the onboarding process.

During the onboarding process, the library registers your dapp as the origin of the onboarding request. MetaMask checks for this origin after the user completes the onboarding flow. If it finds an origin, the final confirmation button of the MetaMask onboarding flow indicates that the user will be redirected back to your dapp.

tip
MetaMask SDK incorporates the functionality of the MetaMask onboarding library. You don't need to set up the onboarding library if you use the SDK.

Steps
Install @metamask/onboarding.

Import the library or include it in your page:

// As an ES6 module
import MetaMaskOnboarding from "@metamask/onboarding"
// Or as an ES5 module
const MetaMaskOnboarding = require("@metamask/onboarding")
Alternatively, you can include the prebuilt ES5 bundle that ships with the library:

<script src="./metamask-onboarding.bundle.js"></script>
Create a new instance of the onboarding library:

const onboarding = new MetaMaskOnboarding()
Start the onboarding process in response to a user event (for example, a button click):

onboarding.startOnboarding()
Example
The following are example ways to use the onboarding library in various frameworks:

React
TypeScript
Vanilla JavaScript and HTML
import MetaMaskOnboarding from "@metamask/onboarding"
import React from "react"

const ONBOARD_TEXT = "Click here to install MetaMask!"
const CONNECT_TEXT = "Connect"
const CONNECTED_TEXT = "Connected"

export function OnboardingButton() {
  const [buttonText, setButtonText] = React.useState(ONBOARD_TEXT)
  const [isDisabled, setDisabled] = React.useState(false)
  const [accounts, setAccounts] = React.useState([])
  const onboarding = React.useRef()

  React.useEffect(() => {
    if (!onboarding.current) {
      onboarding.current = new MetaMaskOnboarding()
    }
  }, [])

  React.useEffect(() => {
    if (MetaMaskOnboarding.isMetaMaskInstalled()) {
      if (accounts.length > 0) {
        setButtonText(CONNECTED_TEXT)
        setDisabled(true)
        onboarding.current.stopOnboarding()
      } else {
        setButtonText(CONNECT_TEXT)
        setDisabled(false)
      }
    }
  }, [accounts])

  React.useEffect(() => {
    function handleNewAccounts(newAccounts) {
      setAccounts(newAccounts)
    }
    if (MetaMaskOnboarding.isMetaMaskInstalled()) {
      provider // Or window.ethereum if you don't support EIP-6963.
        .request({ method: "eth_requestAccounts" })
        .then(handleNewAccounts)
      provider // Or window.ethereum if you don't support EIP-6963.
        .on("accountsChanged", handleNewAccounts)
      return () => {
        provider // Or window.ethereum if you don't support EIP-6963.
          .removeListener("accountsChanged", handleNewAccounts)
      }
    }
  }, [])

  const onClick = () => {
    if (MetaMaskOnboarding.isMetaMaskInstalled()) {
      provider // Or window.ethereum if you don't support EIP-6963.
        .request({ method: "eth_requestAccounts" })
        .then((newAccounts) => setAccounts(newAccounts))
    } else {
      onboarding.current.startOnboarding()
    }
  }
  return (
    <button disabled={isDisabled} onClick={onClick}>
      {buttonText}
    </button>
  )
}
Run a development network
You can run a personal Ethereum development network using Hardhat, which allows you to develop a dapp in a secure test environment.

note
When using a local development blockchain such as Hardhat Network or anvil, your node must calculate gas to make transactions on MetaMask.

Connect to Hardhat
Follow these steps to connect MetaMask to Hardhat Network.

Set up a Hardhat project.

Create a new MetaMask seed phrase specifically for development.

important
Your seed phrase controls all your accounts, so we recommend keeping at least one seed phrase for development, separate from any used to store real value. You can manage multiple seed phrases by using multiple browser profiles, each with its own MetaMask installation.

In your hardhat.config.js file, specify a networks configuration with a hardhat network. In this networks.hardhat configuration:

Specify your MetaMask seed phrase in the accounts.mnemonic field.

tip
Alternatively, to prevent committing your seed phrase, we recommend adding your seed phrase to a .env file and using the process.env global variable in hardhat.config.js.

Specify the chain ID 1337 in the chainId field.

For example:

hardhat.config.js
module.exports = {
  networks: {
    hardhat: {
      accounts: {
        mnemonic: process.env.SEED_PHRASE,
      },
      chainId: 1337,
    },
  },
}
Hardhat automatically gives each of your first 20 accounts 10000 test ether (you can modify these numbers in the accounts configuration), which makes it easy to start development.

Run npx hardhat node to run Hardhat Network and expose a JSON-RPC interface.

You can now connect MetaMask to your Hardhat Network RPC URL, http://127.0.0.1:8545/. In the MetaMask extension:

In the upper left corner, select the network you're currently connected to.

Select Add network.

Select Add a network manually.

Enter your Hardhat Network RPC URL, http://127.0.0.1:8545/ (or http://localhost:8545).

Enter your Hardhat Network chain ID, 1337 (or 0x539 in hexadecimal format).

tip
Alternatively, you can add Hardhat Network to MetaMask using wallet_addEthereumChain in the interactive API playground.

Reset your local nonce calculation
If you restart your development network, you can accidentally confuse MetaMask because it calculates the next nonce based on both the network state and the known sent transactions.

To clear MetaMask's transaction queue and reset its nonce calculation, go to Settings > Advanced and select Reset account.

Next steps
Once you have your development environment set up and development network running, you can connect your dapp to MetaMask by setting up MetaMask SDK, detecting MetaMask, detecting a user's network, and accessing a user's accounts.

For an end-to-end example, you can also follow the Create a simple React dapp tutorial.Secure your dapp
We recommend implementing security controls, such as HTTPS and Content Security Policy (CSP), to improve the security of your dapp and protect your users.

caution
The following security advice isn't exhaustive.

Use HTTPS
HTTPS can protect your dapp against attackers who might try to eavesdrop or tamper with the communication channel between your dapp and your users. HTTPS encrypts data transmitted between the web server and the user's browser, making it difficult for attackers to intercept or modify the data.

To secure your dapp using HTTPS, obtain an SSL/TLS certificate from a trusted certificate authority (CA). For example, Let's Encrypt offers free SSL/TLS certificates.

Install the certificate on your web server. If you're using a static website hosting service, it might have a default way to enable HTTPS on your dapp.

Use Content Security Policy
Content Security Policy (CSP) is a security feature that can protect your dapp against various types of attacks, such as cross-site scripting (XSS) and clickjacking.

CSP defines a set of policies that the browser must follow when displaying the dapp. See the full list of CSP directives that you can enable for your dapp in the MDN CSP reference documentation.

Use CSP with a server setup
If your dapp uses a server setup, enable CSP by setting the Content-Security-Policy header in all responses from your server. For example, in Express.js, add the following middleware at the top of your server:

app.use((req, res, next) => {
  res.setHeader(
    "Content-Security-Policy",
    "default-src 'self'; frame-ancestors 'none'"
  )
  next()
})
In a header, this looks like the following:

Content-Security-Policy: default-src 'self'; frame-ancestors 'none'
See more examples of CSP in popular web frameworks and languages.

Use CSP with a static site
If your dapp uses a third-party hosting provider, and you can't set a custom Content-Security-Policy header in the server responses, you can enable CSP by using the <meta> HTML tag.

Add this tag to the head section of an HTML file to instruct the browser on which CSP directives should be followed. For example:

<head>
  <meta
    http-equiv="Content-Security-Policy"
    content="default-src 'self'; frame-ancestors 'none'"
  />
</head>
Configure your CSP
CSP configuration is specific to each dapp. We recommend starting with the following secure and restrictive CSP:

default-src 'self'; frame-ancestors 'none'
default-src 'self' - By default, your dapp's code can't load or connect to content from outside your domain.
frame-ancestors 'none' - Your dapp can't be embedded within the webpage of another domain (to prevent clickjacking attacks).
From here, you can make adjustments as needed by your dapp to support the content you want to load. For example, if your dapp loads images hosted on OpenSea, you can enable this by adding img-src 'opensea.io' to your CSP:

default-src: 'self'; frame-ancestors 'none'; img-src: 'opensea.io'
For more information and common use cases for CSP, see the MDN CSP documentation.