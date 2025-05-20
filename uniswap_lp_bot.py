import os
import time
import json
from web3 import Web3
from web3.middleware import geth_poa_middleware
from math import sqrt, log
from decimal import Decimal, getcontext

# Set precision for financial calculations
getcontext().prec = 50

# --- 1. Configuration and Blockchain Connection ---
class Config:
    def __init__(self):
        # Node URL for connecting to the blockchain (e.g., Infura, Alchemy, or a local node)
        # Use environment variables for sensitive info like API keys.
        self.NODE_URL = os.getenv("NODE_URL", "https://mainnet.infura.io/v3/YOUR_INFURA_ID") # Or your L2 RPC node
        # Your wallet's private key. EXTREMELY DANGEROUS TO STORE IN CODE.
        # For production, use a more secure method (e.g., KMS, hardware wallet, encrypted keystore).
        self.PRIVATE_KEY = os.getenv("PRIVATE_KEY", "YOUR_PRIVATE_KEY")
        # Your wallet address corresponding to the private key.
        self.WALLET_ADDRESS = os.getenv("WALLET_ADDRESS", "YOUR_WALLET_ADDRESS")

        # Uniswap V3 Contract Addresses (Example for Ethereum Mainnet)
        # Verify these addresses for the specific network you are operating on.
        self.UNISWAP_FACTORY_ADDRESS = "0x1F98431c8Ef1800Ec79B6425a1F7Ff43C5f5fFfF" # V3 Factory
        self.UNISWAP_NFT_POSITION_MANAGER_ADDRESS = "0xC36442b4a4522E871399CD717aBDD847Ab11FE88" # NFT Position Manager

        # ABIs (Application Binary Interfaces) for interacting with smart contracts.
        # These JSON files define the contract's functions and events.
        # Ensure these ABI files are located in a 'abi' subdirectory.
        self.UNISWAP_FACTORY_ABI = json.load(open("abi/UniswapV3Factory.json"))
        self.UNISWAP_POOL_ABI = json.load(open("abi/UniswapV3Pool.json"))
        self.UNISWAP_NFT_POSITION_MANAGER_ABI = json.load(open("abi/UniswapV3PositionManager.json"))
        self.ERC20_ABI = json.load(open("abi/ERC20.json")) # Generic ABI for ERC20 tokens

        # Configuration for the specific Uniswap V3 pool to manage.
        # Example: WETH/USDC pool on Ethereum.
        # TOKEN0_ADDRESS should generally be the token with the lower address lexicographically,
        # but Uniswap V3 handles this internally. For clarity, assign your primary volatile asset to TOKEN0.
        self.TOKEN0_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2" # WETH (assuming it's token0, the volatile one)
        self.TOKEN1_ADDRESS = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48" # USDC (assuming it's token1, the stablecoin)
        self.POOL_FEE = 3000 # 0.3% fee tier for the pool (e.g., 500 for 0.05%, 3000 for 0.3%, 10000 for 1%)

        # Configuration for the delta neutral hedging strategy.
        # These would be API keys for a centralized exchange (CEX) or a decentralized derivatives platform.
        self.DERIVATIVES_EXCHANGE_API_KEY = os.getenv("DERIVATIVES_EXCHANGE_API_KEY", "YOUR_CEX_API_KEY")
        self.DERIVATIVES_EXCHANGE_API_SECRET = os.getenv("DERIVATIVES_EXCHANGE_API_SECRET", "YOUR_CEX_API_SECRET")
        self.SHORT_TOKEN_SYMBOL = "ETH-PERP" # The trading pair symbol for the perpetual swap or futures contract

        # Chainlink Price Feed Addresses (Example for Ethereum Mainnet)
        # IMPORTANT: These addresses are specific to each blockchain network.
        # You MUST find the correct addresses for your chosen network (e.g., Polygon, Arbitrum, Base).
        # You can find them on Chainlink's official documentation: https://docs.chain.link/data-feeds/price-feeds/addresses
        self.CHAINLINK_ETH_USD_FEED = "0x5f4eC3Df9cbd43714FE2740D5E3616155c5b841" # ETH/USD on Ethereum Mainnet
        self.CHAINLINK_USDC_USD_FEED = "0x8fFfFfd4AfB6115b954Bd326cbe7B4BA57E2F0Cc" # USDC/USD on Ethereum Mainnet (often very close to 1)
        # ABI for Chainlink AggregatorV3Interface.
        # You can find this ABI on Chainlink's GitHub or Etherscan (search for a price feed contract).
        self.CHAINLINK_ABI = json.load(open("abi/ChainlinkAggregatorV3.json"))


class BlockchainClient:
    def __init__(self, config: Config):
        self.w3 = Web3(Web3.HTTPProvider(config.NODE_URL))
        # Inject middleware for Proof-of-Authority (PoA) networks (like Polygon, BNB Chain)
        # This is necessary for proper transaction signing and nonce management on these networks.
        if "polygon" in config.NODE_URL.lower() or "bsc" in config.NODE_URL.lower() or "arbitrum" in config.NODE_URL.lower() or "base" in config.NODE_URL.lower():
             self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        # Verify blockchain connection.
        if not self.w3.is_connected():
            raise Exception("Could not connect to the blockchain.")

        self.config = config
        # Load account from private key. Use with extreme caution.
        self.account = self.w3.eth.account.from_key(config.PRIVATE_KEY)
        print(f"Connected to blockchain. Address: {self.account.address}")

    def get_contract(self, address, abi):
        """Returns a Web3 contract instance for a given address and ABI."""
        return self.w3.eth.contract(address=Web3.to_checksum_address(address), abi=abi)

    def send_transaction(self, tx):
        """Builds, signs, and sends a transaction to the blockchain."""
        nonce = self.w3.eth.get_transaction_count(self.account.address)
        # It's recommended to estimate gas before sending to avoid failures or overpaying
        # gas_limit = tx.estimate_gas({'from': self.account.address}) # Uncomment if you want to estimate gas
        tx_build = tx.build_transaction({
            'chainId': self.w3.eth.chain_id,
            'from': self.account.address,
            'nonce': nonce,
            # For Ethereum Mainnet (EIP-1559), you might want to use w3.eth.get_block('latest').baseFeePerGas
            # For simplicity, using legacy gasPrice here. Adjust based on network.
            'gasPrice': self.w3.eth.gas_price
            # 'gas': gas_limit # Uncomment if using estimated gas
        })
        signed_tx = self.w3.eth.account.sign_transaction(tx_build, private_key=self.config.PRIVATE_KEY)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"Transaction sent: {tx_hash.hex()}")
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 1:
            print(f"Transaction successful: {tx_hash.hex()}")
        else:
            print(f"Transaction failed: {tx_hash.hex()}")
            # It's crucial to add more robust error handling here, potentially reverting or retrying.
            raise Exception(f"Transaction failed: {tx_hash.hex()}")
        return receipt

# --- 2. Price and Oracle Module ---
class PriceOracle:
    def __init__(self, blockchain_client: BlockchainClient):
        self.client = blockchain_client
        # Initialize Chainlink price feed contracts
        self.eth_usd_feed = self.client.get_contract(self.client.config.CHAINLINK_ETH_USD_FEED, self.client.config.CHAINLINK_ABI)
        self.usdc_usd_feed = self.client.get_contract(self.client.config.CHAINLINK_USDC_USD_FEED, self.client.config.CHAINLINK_ABI)
        # Store token decimals for accurate price conversions.
        # For a more generic solution, you would fetch these on demand or from a token list.
        self.token_decimals = {
            self.client.config.TOKEN0_ADDRESS: self.client.get_contract(self.client.config.TOKEN0_ADDRESS, self.client.config.ERC20_ABI).functions.decimals().call(),
            self.client.config.TOKEN1_ADDRESS: self.client.get_contract(self.client.config.TOKEN1_ADDRESS, self.client.config.ERC20_ABI).functions.decimals().call(),
        }


    def get_token_price_usd(self, token_address: str) -> Decimal:
        """
        Gets the price of a token in USD using Chainlink Price Feeds.
        """
        print(f"Getting USD price for {token_address} using Chainlink...")
        try:
            if token_address == self.client.config.TOKEN0_ADDRESS: # WETH
                # Chainlink's latestRoundData returns (roundId, answer, startedAt, updatedAt, answeredInRound)
                latest_data = self.eth_usd_feed.functions.latestRoundData().call()
                price_raw = latest_data[1] # The 'answer' field
                # Chainlink price feeds usually have 8 decimals, but check the specific feed's documentation
                return Decimal(price_raw) / Decimal(10**8) # Assuming 8 decimals for Chainlink feeds
            elif token_address == self.client.config.TOKEN1_ADDRESS: # USDC
                latest_data = self.usdc_usd_feed.functions.latestRoundData().call()
                price_raw = latest_data[1]
                return Decimal(price_raw) / Decimal(10**8) # Assuming 8 decimals for Chainlink feeds
            else:
                print(f"No Chainlink feed configured for {token_address}. Returning 0.")
                return Decimal("0")
        except Exception as e:
            print(f"Error getting price from Chainlink for {token_address}: {e}")
            return Decimal("0") # Return 0 or raise an error as appropriate


    def get_pool_prices(self, pool_address: str) -> tuple[Decimal, Decimal]:
        """
        Gets the current prices of token0 and token1 in the pool from Uniswap V3's slot0.
        Returns (price0_per_1, price1_per_0) where price0_per_1 is how much of token1 you get for 1 token0.
        """
        pool_contract = self.client.get_contract(pool_address, self.client.config.UNISWAP_POOL_ABI)
        slot0 = pool_contract.functions.slot0().call()
        sqrt_price_x96 = Decimal(slot0[0])

        # Get decimals for accurate price conversion
        decimals0 = self.token_decimals[self.client.config.TOKEN0_ADDRESS]
        decimals1 = self.token_decimals[self.client.config.TOKEN1_ADDRESS]

        # Calculate price0_per_1 (how much token1 for 1 token0) from sqrtPriceX96
        # price_token0_per_token1 = (sqrt_price_x96 / 2**96)**2
        # price_token1_per_token0 = 1 / price_token0_per_token1
        price0_per_1_raw = (sqrt_price_x96 / Decimal(2**96))**2

        # Adjust for token decimals to get human-readable price
        adjusted_price0_per_1 = price0_per_1_raw * Decimal(10**decimals1) / Decimal(10**decimals0)
        adjusted_price1_per_0 = 1 / adjusted_price0_per_1

        print(f"Price in pool: {adjusted_price1_per_0} {self.client.config.TOKEN0_ADDRESS_SYMBOL}/{self.client.config.TOKEN1_ADDRESS_SYMBOL} (Token0 per Token1)")
        return adjusted_price0_per_1, adjusted_price1_per_0 # price0_per_1 (token1 per token0), price1_per_0 (token0 per token1)

# --- 3. Uniswap V3 Liquidity Management Module ---
class UniswapLPManager:
    def __init__(self, client: BlockchainClient, oracle: PriceOracle):
        self.client = client
        self.oracle = oracle
        self.factory = client.get_contract(client.config.UNISWAP_FACTORY_ADDRESS, client.config.UNISWAP_FACTORY_ABI)
        self.nft_manager = client.get_contract(client.config.UNISWAP_NFT_POSITION_MANAGER_ADDRESS, client.config.UNISWAP_NFT_POSITION_MANAGER_ABI)

    def get_pool_address(self, token0_address, token1_address, fee):
        """Retrieves the address of a Uniswap V3 pool for a given token pair and fee tier."""
        pool_address = self.factory.functions.getPool(
            Web3.to_checksum_address(token0_address),
            Web3.to_checksum_address(token1_address),
            fee
        ).call()
        if pool_address == "0x0000000000000000000000000000000000000000":
            raise Exception("Pool not found for the given parameters.")
        print(f"Pool address: {pool_address}")
        return pool_address

    def calculate_tick_from_price(self, price: Decimal, token0_decimals: int, token1_decimals: int) -> int:
        """
        Calculates the Uniswap V3 tick corresponding to a given price.
        Price is defined as amount_token1 / amount_token0.
        """
        # Adjust price by token decimals to match the contract's internal representation
        adjusted_price = price * Decimal(10**token0_decimals) / Decimal(10**token1_decimals) # Price is token1 per token0, so adjust accordingly
        # The formula for tick is log_1.0001(sqrt(adjusted_price))
        # price = (sqrtPriceX96 / 2**96)^2 * (10**decimals0 / 10**decimals1)
        # sqrtPriceX96 = sqrt(price / (10**decimals0 / 10**decimals1)) * 2**96
        # tick = log(sqrtPriceX96 / (2**96), sqrt(1.0001))
        # log_sqrt(1.0001)(P) = log(P) / log(sqrt(1.0001))
        
        # Invert the adjustment for price to match contract representation for tick calculation
        price_for_tick_calc = price / (Decimal(10**token1_decimals) / Decimal(10**token0_decimals))
        
        # It's actually: P = (1.0001)^tick, so tick = log(1.0001, P)
        # The price provided to `calculate_tick_from_price` is price of token0 in terms of token1.
        # i.e., how many TOKEN1 you get for 1 TOKEN0.
        # Uniswap V3's internal price is token1 / token0.
        # So we need to ensure `adjusted_price` matches `token1 / token0` with 18 decimals each.
        
        # Normalize price to a common 1e18 basis (similar to how Uniswap's sqrtPriceX96 works relative to 1e18)
        # P_actual = price_in_human_readable * 10**(decimals0 - decimals1)
        # The 'price' argument here is token0 per token1.
        # Uniswap uses `sqrtPriceX96 = sqrt(P) * 2^96` where P is token1/token0.
        # So if we have price = token0_value / token1_value (e.g., ETH/USDC), we need to invert for internal price.
        # price_internal = 1 / price_token0_per_token1 (how much token0 for 1 token1)
        # If your `price` is (ETH/USDC), then that's `token0_per_token1`.
        # Uniswap internal price `P` is `token1 / token0`.
        # So, $P = 1/price$.
        
        # Re-evaluating based on Uniswap V3 whitepaper for tick and price:
        # P_tick = (1.0001)^tick
        # The current price (P_human) is token1 per token0, adjusted by decimals.
        # P_human = (sqrtPriceX96 / 2^96)^2 * (10^decimals1 / 10^decimals0)
        # If `price` input is token0_per_token1 (e.g., WETH/USDC):
        # We need to compute tick for P_internal = 1/price
        # P_internal_adjusted = (1/price) * (10**decimals0 / 10**decimals1) # internal price is token0/token1, adjusted for common scale
        # tick = log(P_internal_adjusted, 1.0001)

        # Let's assume 'price' is indeed `price_of_token0_in_token1` (e.g., $3000 USDC/WETH)
        # The contract's internal price P is how much TOKEN1 you get for 1 unit of TOKEN0, normalized to 1e18.
        # P = price * (10**decimals1 / 10**decimals0)
        
        normalized_price = price * Decimal(10**(decimals0 - decimals1))
        # The formula for tick is log_sqrt(1.0001)(P) where P is the raw price.
        # P = sqrtPriceX96^2 / 2^192
        # price_token0_per_token1 = (sqrtPriceX96 / 2**96)**2 * (10**decimals1 / 10**decimals0)
        # Rearranging to get (sqrtPriceX96 / 2**96)
        # sqrtPriceRatio = sqrt(price / (10**decimals1 / 10**decimals0))
        # tick = log(sqrtPriceRatio, sqrt(1.0001))
        # Use Decimal.log10() and Decimal.from_float() for precision
        
        # Corrected tick calculation based on Uniswap V3 docs:
        # price in P = token1 / token0
        # Given `price` as `token0_per_token1` (e.g., WETH/USDC price).
        # We need `price_token1_per_token0 = 1 / price`.
        # Normalized price for internal tick calculation (P_normalized):
        # P_normalized = (1 / price) * (10**decimals0 / 10**decimals1)
        # tick = log_1.0001(P_normalized)

        price_token1_per_token0 = Decimal("1") / price
        P_normalized = price_token1_per_token0 * Decimal(10**decimals0) / Decimal(10**decimals1)
        
        # log_b(x) = log_e(x) / log_e(b)
        tick = int(P_normalized.ln() / Decimal("1.0001").ln())
        return tick


    def calculate_price_from_tick(self, tick: int, token0_decimals: int, token1_decimals: int) -> Decimal:
        """
        Calculates the price (amount_token0 / amount_token1) from a Uniswap V3 tick.
        This function returns price as `token0_per_token1`.
        """
        # P = 1.0001^tick. This P is `token1 / token0` (internal price)
        internal_price = Decimal("1.0001")**tick
        
        # Convert internal price back to human-readable `token0_per_token1`
        # human_readable_price = (1 / internal_price) * (10**decimals1 / 10**decimals0)
        # The convention is usually price of token0 in terms of token1.
        # So price = token1 / token0 (from tick) * (10**decimals0 / 10**decimals1)
        # Adjusted price is price of token0 in terms of token1 (ETH/USDC).
        # P_human = (sqrtPriceX96 / 2**96)^2 * (10**decimals1 / 10**decimals0)
        # From Uniswap's current tick, it's (1.0001)^tick.
        # This is `price_token1_per_token0_raw`.
        
        price_token1_per_token0_raw = Decimal("1.0001")**tick
        price_token0_per_token1 = (Decimal("1") / price_token1_per_token0_raw) * Decimal(10**token1_decimals) / Decimal(10**token0_decimals)
        return price_token0_per_token1


    def parse_mint_receipt_for_token_id(self, receipt) -> int:
        """
        Parses a transaction receipt to find the tokenId of a newly minted LP position.
        The NFT Position Manager emits an 'IncreaseLiquidity' event when minting.
        """
        # The 'IncreaseLiquidity' event signature is needed for parsing.
        # IncreaseLiquidity(uint256 indexed tokenId, uint128 liquidity, uint256 amount0, uint256 amount1)
        # The `tokenId` is the first indexed argument.
        
        # Using the contract's event filter is the most reliable way.
        try:
            processed_logs = self.nft_manager.events.IncreaseLiquidity().process_receipt(receipt)
            if processed_logs:
                # Assuming the first log is the one we're interested in for a fresh mint
                token_id = processed_logs[0]['args']['tokenId']
                print(f"Parsed tokenId {token_id} from transaction receipt.")
                return token_id
            else:
                raise Exception(f"No IncreaseLiquidity event found in transaction {receipt.transactionHash.hex()}")
        except Exception as e:
            print(f"Error parsing mint receipt for tokenId: {e}")
            raise


    def provide_liquidity(self, token0_amount: Decimal, token1_amount: Decimal, lower_price: Decimal, upper_price: Decimal) -> int:
        """Provides new liquidity to a Uniswap V3 pool within a specified price range."""
        pool_address = self.get_pool_address(self.client.config.TOKEN0_ADDRESS, self.client.config.TOKEN1_ADDRESS, self.client.config.POOL_FEE)

        token0_contract = self.client.get_contract(self.client.config.TOKEN0_ADDRESS, self.client.config.ERC20_ABI)
        token1_contract = self.client.get_contract(self.client.config.TOKEN1_ADDRESS, self.client.config.ERC20_ABI)
        decimals0 = token0_contract.functions.decimals().call()
        decimals1 = token1_contract.functions.decimals().call()

        lower_tick = self.calculate_tick_from_price(lower_price, decimals0, decimals1)
        upper_tick = self.calculate_tick_from_price(upper_price, decimals0, decimals1)

        # Adjust ticks to the fee tier's granularity (tick spacing)
        # Ticks must be multiples of tick_spacing for the chosen fee tier.
        tick_spacing = self.client.config.POOL_FEE // 50 # e.g. 3000 / 50 = 60
        lower_tick = (lower_tick // tick_spacing) * tick_spacing
        upper_tick = (upper_tick // tick_spacing) * tick_spacing
        # Ensure upper tick is greater than lower tick to form a valid range
        if upper_tick <= lower_tick:
            upper_tick = lower_tick + tick_spacing


        # Convert human-readable amounts to wei/raw amounts using token decimals
        amount0_wei = int(token0_amount * Decimal(10**decimals0))
        amount1_wei = int(token1_amount * Decimal(10**decimals1))

        # Check current allowance for token0 and approve if insufficient
        current_allowance0 = token0_contract.functions.allowance(
            self.client.config.WALLET_ADDRESS, self.client.config.UNISWAP_NFT_POSITION_MANAGER_ADDRESS
        ).call()
        if current_allowance0 < amount0_wei:
            print(f"Approving {token0_amount} {self.client.config.TOKEN0_ADDRESS_SYMBOL} for NFT Position Manager...")
            approval_tx0 = token0_contract.functions.approve(
                self.client.config.UNISWAP_NFT_POSITION_MANAGER_ADDRESS, amount0_wei
            )
            self.client.send_transaction(approval_tx0)
            print(f"Approval for {self.client.config.TOKEN0_ADDRESS_SYMBOL} successful.")
        else:
            print(f"Allowance for {self.client.config.TOKEN0_ADDRESS_SYMBOL} is sufficient.")

        # Check current allowance for token1 and approve if insufficient
        current_allowance1 = token1_contract.functions.allowance(
            self.client.config.WALLET_ADDRESS, self.client.config.UNISWAP_NFT_POSITION_MANAGER_ADDRESS
        ).call()
        if current_allowance1 < amount1_wei:
            print(f"Approving {token1_amount} {self.client.config.TOKEN1_ADDRESS_SYMBOL} for NFT Position Manager...")
            approval_tx1 = token1_contract.functions.approve(
                self.client.config.UNISWAP_NFT_POSITION_MANAGER_ADDRESS, amount1_wei
            )
            self.client.send_transaction(approval_tx1)
            print(f"Approval for {self.client.config.TOKEN1_ADDRESS_SYMBOL} successful.")
        else:
            print(f"Allowance for {self.client.config.TOKEN1_ADDRESS_SYMBOL} is sufficient.")


        # Parameters for the `mint` function of the NFT Position Manager contract.
        # amount0Min/amount1Min: Slippage tolerance. Ensure you don't receive less than expected.
        # recipient: The address that will receive the NFT representing the LP position.
        # deadline: The timestamp after which the transaction will revert if not processed.
        params = {
            'token0': Web3.to_checksum_address(self.client.config.TOKEN0_ADDRESS),
            'token1': Web3.to_checksum_address(self.client.config.TOKEN1_ADDRESS),
            'fee': self.client.config.POOL_FEE,
            'tickLower': lower_tick,
            'tickUpper': upper_tick,
            'amount0Desired': amount0_wei,
            'amount1Desired': amount1_wei,
            'amount0Min': int(amount0_wei * Decimal("0.99")), # 1% slippage tolerance
            'amount1Min': int(amount1_wei * Decimal("0.99")), # 1% slippage tolerance
            'recipient': self.client.config.WALLET_ADDRESS,
            'deadline': int(time.time()) + 60 * 20 # 20 minutes from now
        }

        # Build and send the mint transaction.
        mint_tx = self.nft_manager.functions.mint(params)
        mint_receipt = self.client.send_transaction(mint_tx)
        print(f"Mint transaction sent. Receipt: {mint_receipt.transactionHash.hex()}")
        
        # Parse the transaction receipt to get the tokenId.
        token_id = self.parse_mint_receipt_for_token_id(mint_receipt)
        return token_id # Return the actual tokenId


    def get_position_info(self, token_id: int):
        """Gets detailed information about a Uniswap V3 NFT position."""
        position_data = self.nft_manager.functions.positions(token_id).call()
        # position_data tuple: (nonce, operator, token0, token1, fee, tickLower, tickUpper,
        # liquidity, feeGrowthOutside0X128, feeGrowthOutside1X128, tokensOwed0, tokensOwed1)
        print(f"Position {token_id} info: {position_data}")
        return position_data

    def collect_fees(self, token_id: int):
        """Collects accrued fees from an LP position."""
        position_data = self.get_position_info(token_id)
        tokens_owed0 = position_data[9] # tokensOwed0 (fee amounts)
        tokens_owed1 = position_data[10] # tokensOwed1 (fee amounts)

        if tokens_owed0 == 0 and tokens_owed1 == 0:
            print(f"No fees to collect for position {token_id}.")
            return

        # Parameters for the `collect` function.
        # amount0Max/amount1Max: Max amounts to collect. Usually set to the owed amounts.
        params = {
            'tokenId': token_id,
            'recipient': self.client.config.WALLET_ADDRESS,
            'amount0Max': tokens_owed0,
            'amount1Max': tokens_owed1
        }

        # Build and send the collect transaction.
        collect_tx = self.nft_manager.functions.collect(params)
        collect_receipt = self.client.send_transaction(collect_tx)
        print(f"Fees collected for position {token_id}. Receipt: {collect_receipt.transactionHash.hex()}")


    def decrease_liquidity(self, token_id: int, liquidity_to_remove: int) -> tuple[Decimal, Decimal]:
        """Decreases liquidity from an LP position."""
        # Parameters for the `decreaseLiquidity` function.
        # amount0Min/amount1Min: Slippage tolerance for tokens received after removing liquidity.
        params = {
            'tokenId': token_id,
            'liquidity': liquidity_to_remove, # Amount of liquidity (not tokens) to remove
            'amount0Min': 0, # Set to 0 for simplicity, but in production, use a non-zero value based on slippage
            'amount1Min': 0,
            'deadline': int(time.time()) + 60 * 20
        }
        decrease_tx = self.nft_manager.functions.decreaseLiquidity(params)
        decrease_receipt = self.client.send_transaction(decrease_tx)
        print(f"Liquidity decreased for {token_id} by {liquidity_to_remove}. Receipt: {decrease_receipt.transactionHash.hex()}")
        
        # --- START OF TODO 4 IMPLEMENTATION (Parse recovered amounts) ---
        # Parse the transaction receipt to get the amounts of tokens received.
        # The 'DecreaseLiquidity' event is emitted:
        # DecreaseLiquidity(uint256 indexed tokenId, uint128 liquidity, uint256 amount0, uint256 amount1)
        try:
            processed_logs = self.nft_manager.events.DecreaseLiquidity().process_receipt(decrease_receipt)
            if processed_logs:
                amount0_recovered_raw = processed_logs[0]['args']['amount0']
                amount1_recovered_raw = processed_logs[0]['args']['amount1']

                decimals0 = self.oracle.token_decimals[self.client.config.TOKEN0_ADDRESS]
                decimals1 = self.oracle.token_decimals[self.client.config.TOKEN1_ADDRESS]

                amount0_recovered = Decimal(amount0_recovered_raw) / Decimal(10**decimals0)
                amount1_recovered = Decimal(amount1_recovered_raw) / Decimal(10**decimals1)
                
                print(f"Recovered {amount0_recovered} {self.client.config.TOKEN0_ADDRESS_SYMBOL} and {amount1_recovered} {self.client.config.TOKEN1_ADDRESS_SYMBOL}.")
                return amount0_recovered, amount1_recovered
            else:
                raise Exception(f"No DecreaseLiquidity event found in transaction {decrease_receipt.transactionHash.hex()}")
        except Exception as e:
            print(f"Error parsing decrease liquidity receipt for amounts: {e}")
            raise
        # --- END OF TODO 4 IMPLEMENTATION (Parse recovered amounts) ---


    def increase_liquidity(self, token_id: int, token0_amount: Decimal, token1_amount: Decimal):
        """Increases liquidity for an existing LP position."""
        token0_contract = self.client.get_contract(self.client.config.TOKEN0_ADDRESS, self.client.config.ERC20_ABI)
        token1_contract = self.client.get_contract(self.client.config.TOKEN1_ADDRESS, self.client.config.ERC20_ABI)
        decimals0 = token0_contract.functions.decimals().call()
        decimals1 = token1_contract.functions.decimals().call()

        amount0_wei = int(token0_amount * Decimal(10**decimals0))
        amount1_wei = int(token1_amount * Decimal(10**decimals1))

        # Check and approve tokens again for increasing liquidity, as amounts might exceed previous approvals
        # This logic is similar to `provide_liquidity`'s approval block.
        current_allowance0 = token0_contract.functions.allowance(
            self.client.config.WALLET_ADDRESS, self.client.config.UNISWAP_NFT_POSITION_MANAGER_ADDRESS
        ).call()
        if current_allowance0 < amount0_wei:
            print(f"Approving {token0_amount} {self.client.config.TOKEN0_ADDRESS_SYMBOL} for NFT Position Manager (increase)...")
            approval_tx0 = token0_contract.functions.approve(
                self.client.config.UNISWAP_NFT_POSITION_MANAGER_ADDRESS, amount0_wei
            )
            self.client.send_transaction(approval_tx0)
        else:
            print(f"Allowance for {self.client.config.TOKEN0_ADDRESS_SYMBOL} is sufficient for increase.")

        current_allowance1 = token1_contract.functions.allowance(
            self.client.config.WALLET_ADDRESS, self.client.config.UNISWAP_NFT_POSITION_MANAGER_ADDRESS
        ).call()
        if current_allowance1 < amount1_wei:
            print(f"Approving {token1_amount} {self.client.config.TOKEN1_ADDRESS_SYMBOL} for NFT Position Manager (increase)...")
            approval_tx1 = token1_contract.functions.approve(
                self.client.config.UNISWAP_NFT_POSITION_MANAGER_ADDRESS, amount1_wei
            )
            self.client.send_transaction(approval_tx1)
        else:
            print(f"Allowance for {self.client.config.TOKEN1_ADDRESS_SYMBOL} is sufficient for increase.")

        # Parameters for the `increaseLiquidity` function.
        params = {
            'tokenId': token_id,
            'amount0Desired': amount0_wei,
            'amount1Desired': amount1_wei,
            'amount0Min': int(amount0_wei * Decimal("0.99")),
            'amount1Min': int(amount1_wei * Decimal("0.99")),
            'deadline': int(time.time()) + 60 * 20
        }
        increase_tx = self.nft_manager.functions.increaseLiquidity(params)
        increase_receipt = self.client.send_transaction(increase_tx)
        print(f"Liquidity increased for {token_id} with {token0_amount} {self.client.config.TOKEN0_ADDRESS_SYMBOL} and {token1_amount} {self.client.config.TOKEN1_ADDRESS_SYMBOL}. Receipt: {increase_receipt.transactionHash.hex()}")


# --- 4. Derivatives Management Module (for Delta Neutral) ---
# --- START OF TODO 5 IMPLEMENTATION (DerivativesManager with conceptual client) ---
class DerivativesClient:
    """Conceptual client for interacting with a derivatives exchange."""
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        print("DerivativesClient initialized. (In a real scenario, this connects to a CEX/DEX SDK)")
        # In a real scenario, you'd initialize a client for Binance, dYdX, etc.
        # Example for a hypothetical Binance client:
        # self.binance_client = Client(api_key, api_secret)

    def get_market_price(self, symbol: str) -> Decimal:
        """Gets the current market price of the perpetual/futures contract."""
        print(f"Fetching market price for {symbol}...")
        # This would be a real API call. Dummy value for demonstration.
        # Example for Binance:
        # ticker = self.binance_client.get_symbol_ticker(symbol=symbol)
        # return Decimal(ticker['price'])
        return Decimal("3000") # Dummy ETH-PERP price

    def get_current_position(self, symbol: str) -> Decimal:
        """Gets the current open position size for a given symbol."""
        print(f"Fetching current position for {symbol}...")
        # This would be a real API call to check your open futures/perpetual positions.
        # Example for Binance:
        # account_info = self.binance_client.futures_account()
        # for position in account_info['positions']:
        #     if position['symbol'] == symbol:
        #         return Decimal(position['positionAmt']) # Returns amount, positive for long, negative for short
        return Decimal("0") # Dummy: assume no open position initially

    def place_order(self, symbol: str, side: str, amount: Decimal, order_type: str = "MARKET"):
        """Places a market order on the derivatives exchange."""
        print(f"Placing {side} {amount} {symbol} {order_type} order. (This would be a real API call)")
        # This would be a real API call to execute a trade.
        # Example for Binance:
        # order = self.binance_client.futures_create_order(
        #     symbol=symbol,
        #     side=side, # 'BUY' or 'SELL'
        #     type=order_type,
        #     quantity=str(amount.normalize()) # Convert Decimal to string
        # )
        # print(f"Order placed: {order}")
        print(f"Simulated order: {side} {amount} {symbol}")


class DerivativesManager:
    def __init__(self, config: Config):
        self.config = config
        self.client = DerivativesClient(config.DERIVATIVES_EXCHANGE_API_KEY, config.DERIVATIVES_EXCHANGE_API_SECRET)

    def get_position_size(self, symbol: str) -> Decimal:
        """Gets the current position size in the derivatives market for a given symbol."""
        return self.client.get_current_position(symbol)

    def open_short_position(self, symbol: str, amount: Decimal):
        """Opens a short position on the asset."""
        # For a short position, you usually 'SELL' the asset.
        # Ensure amount is positive when calling place_order.
        if amount > 0:
            self.client.place_order(symbol, "SELL", amount, "MARKET")
        else:
            print(f"Attempted to open short position with non-positive amount: {amount}")

    def close_position(self, symbol: str, amount: Decimal):
        """Closes an existing position or part of it."""
        # If your current position is short (negative amount), to close it, you 'BUY'.
        # If your current position is long (positive amount), to close it, you 'SELL'.
        # This function assumes 'amount' is the absolute quantity to close.
        current_pos = self.get_position_size(symbol)
        
        if current_pos < 0: # Currently short, need to buy to close
            amount_to_buy = min(amount, abs(current_pos)) # Don't buy more than needed to close short
            if amount_to_buy > 0:
                self.client.place_order(symbol, "BUY", amount_to_buy, "MARKET")
        elif current_pos > 0: # Currently long, need to sell to close
            amount_to_sell = min(amount, abs(current_pos)) # Don't sell more than needed to close long
            if amount_to_sell > 0:
                self.client.place_order(symbol, "SELL", amount_to_sell, "MARKET")
        else:
            print(f"No open position for {symbol} to close.")


    def calculate_delta_hedge_amount(self, current_lp_delta: Decimal, price_of_token_to_hedge: Decimal) -> Decimal:
        """
        Calculates the amount of token to short to neutralize the delta.
        lp_delta: The delta exposure of your LP position in terms of the volatile token.
                  This is complex to calculate for Uniswap V3 and depends on liquidity,
                  range, and current price.
        price_of_token_to_hedge: The current price of the volatile token in USD.
        """
        # This function is now just a pass-through for the calculated LP delta.
        # The complexity of calculating LP delta is moved to `get_current_lp_exposure`.
        return current_lp_delta # This represents the amount in units of the volatile token (e.g., ETH)
# --- END OF TODO 5 IMPLEMENTATION (DerivativesManager with conceptual client) ---

# --- 5. Main Bot Logic ---
class LiquidityManagerBot:
    def __init__(self):
        self.config = Config()
        self.blockchain_client = BlockchainClient(self.config)
        self.price_oracle = PriceOracle(self.blockchain_client)
        self.lp_manager = UniswapLPManager(self.blockchain_client, self.price_oracle)
        self.derivatives_manager = DerivativesManager(self.config)
        self.position_token_id = None # Will store the tokenId of the LP position.

    def initial_setup(self, initial_token0_amount: Decimal, initial_token1_amount: Decimal,
                      lower_price: Decimal, upper_price: Decimal):
        """Performs the initial setup of the LP position."""
        print("Performing initial LP setup...")
        # This will call provide_liquidity, which now handles approvals and minting.
        self.position_token_id = self.lp_manager.provide_liquidity(initial_token0_amount, initial_token1_amount, lower_price, upper_price)
        
        if self.position_token_id:
            print(f"LP position created with Token ID: {self.position_token_id}")
            # TODO: Store the tokenId persistently (e.g., in a database or file)
            self._save_position_id(self.position_token_id)
        else:
            print("Failed to create LP position or retrieve Token ID.")

    def _save_position_id(self, token_id: int):
        """Saves the position ID to a file for persistence."""
        try:
            with open("position_id.txt", "w") as f:
                f.write(str(token_id))
            print(f"Position ID {token_id} saved to position_id.txt")
        except Exception as e:
            print(f"Error saving position ID: {e}")

    def _load_position_id(self) -> int | None:
        """Loads the position ID from a file."""
        try:
            if os.path.exists("position_id.txt"):
                with open("position_id.txt", "r") as f:
                    token_id_str = f.read().strip()
                    if token_id_str:
                        token_id = int(token_id_str)
                        print(f"Loaded existing position ID: {token_id}")
                        return token_id
            return None
        except Exception as e:
            print(f"Error loading position ID: {e}")
            return None

    def get_current_lp_exposure(self, token_id: int) -> Decimal:
        """
        Calculates the net exposure of your LP position to the volatile token (TOKEN0).
        This is a more accurate, but still simplified, calculation based on Uniswap V3 math.
        It assumes TOKEN0 is the volatile asset you want to hedge (e.g., ETH) and TOKEN1 is stable (USDC).
        """
        position_info = self.lp_manager.get_position_info(token_id)
        liquidity = Decimal(position_info[7]) # Liquidity of the position
        tick_lower = position_info[5]
        tick_upper = position_info[6]

        pool_address = self.lp_manager.get_pool_address(self.config.TOKEN0_ADDRESS, self.config.TOKEN1_ADDRESS, self.config.POOL_FEE)
        pool_contract = self.blockchain_client.get_contract(pool_address, self.config.UNISWAP_POOL_ABI)
        slot0 = pool_contract.functions.slot0().call()
        current_sqrt_price_x96 = Decimal(slot0[0])

        decimals0 = self.price_oracle.token_decimals[self.config.TOKEN0_ADDRESS]
        decimals1 = self.price_oracle.token_decimals[self.config.TOKEN1_ADDRESS]

        sqrt_price_lower_x96 = Decimal.from_float(sqrt(Decimal("1.0001")**tick_lower)) * Decimal(2**96)
        sqrt_price_upper_x96 = Decimal.from_float(sqrt(Decimal("1.0001")**tick_upper)) * Decimal(2**96)

        # --- START OF TODO 6 IMPLEMENTATION (More accurate LP delta calculation) ---
        # Calculate x and y amounts for a given liquidity and price range
        # These are the "virtual" amounts of tokens held by the position at the current price.
        # This is based on Uniswap V3 whitepaper formulas for x and y reserves in a range.

        amount0_current = Decimal("0")
        amount1_current = Decimal("0")

        # Normalize sqrt_price_x96 by 2**96 to get sqrt(P)
        current_sqrt_price = current_sqrt_price_x96 / Decimal(2**96)
        sqrt_price_lower = sqrt_price_lower_x96 / Decimal(2**96)
        sqrt_price_upper = sqrt_price_upper_x96 / Decimal(2**96)

        # Case 1: Current price is below the lower tick
        if current_sqrt_price <= sqrt_price_lower:
            amount0_current = liquidity * ((sqrt_price_upper - sqrt_price_lower) / (sqrt_price_lower * sqrt_price_upper))
            amount1_current = Decimal("0") # Only token0 is left in the position

        # Case 2: Current price is above the upper tick
        elif current_sqrt_price >= sqrt_price_upper:
            amount0_current = Decimal("0") # Only token1 is left in the position
            amount1_current = liquidity * (sqrt_price_upper - sqrt_price_lower)

        # Case 3: Current price is within the range [lower_tick, upper_tick]
        else:
            amount0_current = liquidity * ((sqrt_price_upper - current_sqrt_price) / (current_sqrt_price * sqrt_price_upper))
            amount1_current = liquidity * (current_sqrt_price - sqrt_price_lower)
        
        # Adjust for token decimals for human-readable amounts
        amount0_human = amount0_current / Decimal(10**decimals0)
        amount1_human = amount1_current / Decimal(10**decimals1)

        print(f"Current theoretical LP holdings: {amount0_human} {self.config.TOKEN0_ADDRESS_SYMBOL}, {amount1_human} {self.config.TOKEN1_ADDRESS_SYMBOL}")

        # The delta exposure is primarily to TOKEN0 (WETH) in a WETH/USDC pool.
        # It's the amount of TOKEN0 held (long exposure).
        # We need to account for the value of TOKEN1 if we think of it as "short" TOKEN0.
        # For a standard delta hedge, we want to short the volatile asset.
        # So, the effective long exposure to TOKEN0 is `amount0_human`.
        # However, as price moves, the ratio of tokens changes.
        # When price goes up, you have more TOKEN1 (USDC), less TOKEN0 (ETH).
        # When price goes down, you have more TOKEN0 (ETH), less TOKEN1 (USDC).
        # Your effective delta is how many units of TOKEN0 your position is "long".

        # A more precise delta calculation would be the derivative of the value function
        # with respect to the price of TOKEN0.
        # For simplicity in this context, we will consider the `amount0_human` as the primary
        # long exposure to TOKEN0 that needs to be hedged. This is a common approximation.
        # If your strategy needs to hedge the `amount1_human` against a short ETH position,
        # it gets more complex (e.g., if you consider your USDC as a short ETH position when price goes up).

        # For a delta-neutral position, if your LP has a long TOKEN0 exposure, you short TOKEN0.
        # So, the amount of TOKEN0 to hedge is `amount0_human`.
        
        # Let's refine the delta: The position has TOKEN0 and TOKEN1.
        # Value = Amount0 * Price_Token0 + Amount1 * Price_Token1
        # If Price_Token0 changes, how much does Value change?
        # dValue/dPrice_Token0 = Amount0 + Amount1 * (dPrice_Token1/dPrice_Token0)
        # If Token1 is stable (Price_Token1 = 1), dPrice_Token1/dPrice_Token0 = 0.
        # So, Delta ~ Amount0.

        # This simple delta considers only the current actual token amounts.
        # The issue is that the actual amounts in your position change as price moves.
        # A true "delta" for a range order is non-linear.
        # A common proxy for delta is the amount of TOKEN0 you would have if price moved to the lower bound,
        # minus the amount if it moved to the upper bound, relative to liquidity.
        
        # A more common interpretation of delta for LP:
        # If current price `P` is between `P_L` and `P_U`:
        # x_amount = L * (1/sqrt(P) - 1/sqrt(P_U))
        # y_amount = L * (sqrt(P) - sqrt(P_L))
        # Where L is liquidity, sqrt(P) is current sqrtPriceX96 normalized, etc.
        # Delta_x = dx/dP = -0.5 * L * P^(-1.5) + 0 (if P_U is constant wrt P)
        # Delta_y = dy/dP = 0.5 * L * P^(-0.5)
        # Total delta in terms of token0 would be Delta_x + Delta_y / P_current

        # For practical purposes and given the context, let's use the current `amount0_human` as the delta.
        # This implicitly assumes you're hedging against the ETH exposure in your LP position.
        # If `amount0_human` is high, you're long ETH, and need to short ETH.
        # If `amount0_human` is low (meaning more USDC), you're less long ETH.

        estimated_delta_exposure_token0 = amount0_human
        
        print(f"Estimated Delta Exposure to {self.config.TOKEN0_ADDRESS_SYMBOL} from LP: {estimated_delta_exposure_token0} {self.config.TOKEN0_ADDRESS_SYMBOL}")
        return estimated_delta_exposure_token0
        # --- END OF TODO 6 IMPLEMENTATION (More accurate LP delta calculation) ---


    def rebalance_lp(self, token_id: int):
        """
        Rebalances the LP position if the price moves out of range or if optimization is needed.
        """
        position_info = self.lp_manager.get_position_info(token_id)
        # Get current prices from the pool itself for rebalance decision
        current_price0_per_1, current_price1_per_0 = self.price_oracle.get_pool_prices(
            self.lp_manager.get_pool_address(self.config.TOKEN0_ADDRESS, self.config.TOKEN1_ADDRESS, self.config.POOL_FEE)
        )

        lower_tick = position_info[5]
        upper_tick = position_info[6]

        decimals0 = self.price_oracle.token_decimals[self.config.TOKEN0_ADDRESS]
        decimals1 = self.price_oracle.token_decimals[self.config.TOKEN1_ADDRESS]

        current_lower_price = self.lp_manager.calculate_price_from_tick(lower_tick, decimals0, decimals1)
        current_upper_price = self.lp_manager.calculate_price_from_tick(upper_tick, decimals0, decimals1)

        print(f"Current Pool Price (Token0/Token1): {current_price1_per_0}, LP Range: {current_lower_price} (lower price for Token0) - {current_upper_price} (upper price for Token0)")

        # Rebalancing logic:
        # 1. If the price is outside the defined range (or near boundary):
        #    - Decrease current liquidity (withdraw tokens).
        #    - Collect any accrued fees.
        #    - Calculate a new range centered on the current price.
        #    - Re-provide liquidity in the new range with the recovered tokens.
        # Note: This strategy incurs gas fees for each rebalance.
        # Define a threshold for "out of range" to avoid rebalancing too frequently on small price movements.
        # E.g., if price is 1% below lower bound or 1% above upper bound.
        if current_price1_per_0 < current_lower_price * Decimal("0.99") or current_price1_per_0 > current_upper_price * Decimal("1.01"):
            print("Price is out of range (or near boundary). Rebalancing LP...")
            # Decrease all liquidity from the current position.
            liquidity_to_remove = position_info[7] # Get total liquidity from position info
            
            # Use the updated decrease_liquidity to get recovered amounts
            recovered_token0_amount, recovered_token1_amount = self.lp_manager.decrease_liquidity(token_id, liquidity_to_remove)
            self.lp_manager.collect_fees(token_id) # Collect fees before re-depositing

            print(f"Recovered amounts: {recovered_token0_amount} {self.config.TOKEN0_ADDRESS_SYMBOL}, {recovered_token1_amount} {self.config.TOKEN1_ADDRESS_SYMBOL}")

            # Calculate a new range: e.g., +/- 10% of the current price
            # Always ensure the new range is valid (lower < upper) and aligned with tick spacing.
            new_lower_price = current_price1_per_0 * Decimal("0.90")
            new_upper_price = current_price1_per_0 * Decimal("1.10")

            # Re-provide liquidity with the recovered tokens and the new range.
            # IMPORTANT: After `decreaseLiquidity`, the `token_id` of the old position might be burned
            # or the liquidity moved. A new `mint` operation will create a new `tokenId`.
            # So, we should call `initial_setup` to get a new `tokenId` or update `self.position_token_id`.
            
            # Since `provide_liquidity` already returns a new tokenId, let's use that.
            self.position_token_id = self.lp_manager.provide_liquidity(recovered_token0_amount, recovered_token1_amount,
                                               new_lower_price, new_upper_price)
            self._save_position_id(self.position_token_id) # Save new ID
            print("LP rebalance completed and new position ID saved.")
        else:
            print("Price is within range. No LP rebalance needed.")

    def manage_delta_neutral(self, token_id: int):
        """Manages the hedging position to maintain delta neutrality."""
        print("Managing delta neutral strategy...")

        # 1. Get the current estimated delta exposure of the LP position to the volatile token (TOKEN0).
        lp_exposure_token0 = self.get_current_lp_exposure(token_id)

        # 2. Get the current price of the volatile token (TOKEN0) in USD, needed for derivatives trading.
        token0_usd_price = self.price_oracle.get_token_price_usd(self.config.TOKEN0_ADDRESS)
        if token0_usd_price == 0:
            print("Could not get Token0 USD price. Skipping delta hedge.")
            return

        # 3. Get the current size of your short position on the derivatives exchange.
        # Note: get_position_size will return positive for long, negative for short.
        current_short_position_size = self.derivatives_manager.get_position_size(self.config.SHORT_TOKEN_SYMBOL)

        # Calculate the target short amount to neutralize the LP's delta exposure.
        # If lp_exposure_token0 is positive (meaning your LP is effectively "long" token0),
        # you need a short position of that same amount to neutralize it.
        # Target short amount is simply lp_exposure_token0 (since we're hedging the long).
        target_short_amount = lp_exposure_token0 

        # Determine the amount of adjustment needed for the short position.
        # If target_short_amount is 5 ETH and current_short_position_size is 3 ETH,
        # you need to increase short by 2 ETH (5 - 3 = 2).
        # If target_short_amount is 5 ETH and current_short_position_size is -2 ETH (meaning 2 ETH long),
        # you need to increase short by 7 ETH (5 - (-2) = 7).
        # If target_short_amount is 2 ETH and current_short_position_size is 5 ETH,
        # you need to decrease short by 3 ETH (2 - 5 = -3).
        amount_to_adjust = target_short_amount - current_short_position_size

        # Execute derivative trades to adjust the short position.
        # Use a small threshold (e.g., 0.001) to avoid tiny, gas-inefficient trades.
        HEDGE_THRESHOLD = Decimal("0.001") # Example: 0.001 ETH

        if amount_to_adjust > HEDGE_THRESHOLD: # Need to increase short position (or reduce existing long)
            print(f"Need to increase net short position by {amount_to_adjust} {self.config.SHORT_TOKEN_SYMBOL}")
            self.derivatives_manager.open_short_position(self.config.SHORT_TOKEN_SYMBOL, amount_to_adjust)
        elif amount_to_adjust < -HEDGE_THRESHOLD: # Need to reduce short position (or increase existing long)
            # Note: -amount_to_adjust is positive, representing the amount to reduce.
            print(f"Need to reduce net short position by {-amount_to_adjust} {self.config.SHORT_TOKEN_SYMBOL}")
            # The close_position function in DerivativesManager handles if it's currently short or long
            self.derivatives_manager.close_position(self.config.SHORT_TOKEN_SYMBOL, -amount_to_adjust)
        else:
            print("Delta neutral hedge position stable. No significant adjustment needed.")

    def run(self):
        """Main execution loop for the bot."""
        print("Starting liquidity management and delta neutral bot...")

        # Load tokenId of existing positions if you already have them
        self.position_token_id = self._load_position_id()

        # Set token symbols for clearer logging messages
        self.config.TOKEN0_ADDRESS_SYMBOL = "WETH"
        self.config.TOKEN1_ADDRESS_SYMBOL = "USDC"

        # Continuous loop for bot operations
        while True:
            try:
                if self.position_token_id:
                    print(f"\n--- Managing LP Position {self.position_token_id} ---")
                    # Perform LP rebalancing first
                    self.rebalance_lp(self.position_token_id)
                    # Then manage the delta neutral hedge
                    self.manage_delta_neutral(self.position_token_id)

                    # You can also collect fees periodically
                    # self.lp_manager.collect_fees(self.position_token_id)
                else:
                    print("\nNo active LP position loaded. Attempting initial setup (if enabled)...")
                    # This will attempt to mint a new position if one isn't loaded.
                    # ONLY UNCOMMENT AND USE IF YOU INTEND TO MINT A NEW LP POSITION!
                    # You need to ensure your wallet has sufficient tokens and has approved the NFT Manager.
                    # Example: 0.01 WETH and 25 USDC, target range for WETH: $2400-$2600.
                    # If you run this, it will attempt to mint a new position and save its ID.
                    # self.initial_setup(Decimal("0.01"), Decimal("25"), Decimal("2400"), Decimal("2600")) 
                    
                    # If you're just testing the loop without minting, leave this commented.
                    # If you uncommented `initial_setup`, you must restart the bot after the first successful mint
                    # to ensure the `position_token_id` is loaded from `position_id.txt`.
                    
                    pass # Keep looping but don't try to manage non-existent position.

            except Exception as e:
                print(f"Error during bot execution: {e}")
                # TODO: Implement a robust alert system (e.g., Telegram, Discord, email)
                # to notify you of errors or critical events.
                
                # In case of a critical error, you might want to stop the bot or implement a backoff.
                # For now, just print and continue after a delay.

            print("Waiting 5 minutes before next execution cycle...")
            time.sleep(5 * 60) # Pause for 5 minutes (adjust as needed for your strategy and gas costs)


# --- Bot Execution (Example Usage) ---
if __name__ == "__main__":
    # BEFORE RUNNING:
    # 1. Create an 'abi' folder in the same directory as this script.
    # 2. Download and save the ABIs for Uniswap V3 Factory, Pool, NonfungiblePositionManager, ERC20, and Chainlink AggregatorV3Interface into the 'abi' folder.
    #    - Chainlink AggregatorV3Interface ABI can be found on Chainlink's official documentation or Etherscan for any Chainlink price feed.
    # 3. Set your environment variables (NODE_URL, PRIVATE_KEY, WALLET_ADDRESS, DERIVATIVES_EXCHANGE_API_KEY, DERIVATIVES_EXCHANGE_API_SECRET).
    #    - Example for Linux/macOS:
    #      export NODE_URL="https://polygon-mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"
    #      export PRIVATE_KEY="0xYOUR_PRIVATE_KEY"
    #      export WALLET_ADDRESS="0xYOUR_WALLET_ADDRESS"
    #      export DERIVATIVES_EXCHANGE_API_KEY="YOUR_CEX_API_KEY"
    #      export DERIVATIVES_EXCHANGE_API_SECRET="YOUR_CEX_API_SECRET"
    #    - Or hardcode them in Config, but BE AWARE OF THE SECURITY RISKS.

    bot = LiquidityManagerBot()
    
    # --- IMPORTANT ---
    # If you want to create a NEW LP position from scratch:
    # 1. Ensure your wallet has enough WETH and USDC (or your chosen tokens).
    # 2. Ensure the Uniswap V3 NFT Position Manager has **approval** to spend your WETH and USDC.
    #    The `provide_liquidity` function includes approval checks, but it's good to be aware.
    # 3. UNCOMMENT the `bot.initial_setup` line below and set desired amounts and price range.
    #    After a successful mint, the `tokenId` will be saved to `position_id.txt`.
    #    You should then **comment out `initial_setup` again** and restart the bot so it loads the existing ID.
    #
    # Example: 0.01 WETH, 25 USDC, target range for WETH: $2400-$2600.
    # bot.initial_setup(Decimal("0.01"), Decimal("25"), Decimal("2400"), Decimal("2600"))

    # If you have an EXISTING Uniswap V3 LP position (an NFT):
    # 1. Find its Token ID (e.g., on Etherscan, by looking up your wallet address under ERC721 tokens).
    # 2. UNCOMMENT the `bot.position_token_id` line below and REPLACE `123456789` with your actual NFT ID.
    #    This will tell the bot to manage that specific position.
    # bot.position_token_id = 123456789 # <--- REPLACE WITH YOUR ACTUAL LP NFT ID

    bot.run()
