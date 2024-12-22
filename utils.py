import json
from web3 import Web3
from decimal import Decimal
import config  # Import the config module


def connect_web3(rpc_url):
    web3 = Web3(Web3.HTTPProvider(rpc_url))
    if web3.is_connected():
        print("Connected to RPC!")
        return web3
    print("Failed to connect to RPC.")
    return None


def load_contract(web3, address, abi_path):
    with open(abi_path) as f:
        abi = json.load(f)
    return web3.eth.contract(address=web3.to_checksum_address(address),
                             abi=abi)


def get_token_info(web3, token_contract):
    decimals = token_contract.functions.decimals().call()
    return decimals


def calculate_user_share(staked_balance, total_supply, reserve0, reserve1):
    user_share = Decimal(staked_balance) / Decimal(total_supply)
    user_token0 = Decimal(reserve0) * user_share
    user_token1 = Decimal(reserve1) * user_share
    return user_share, user_token0, user_token1


def to_human_readable(amount, decimals):
    return Decimal(amount) / Decimal(10**decimals)


def get_token_price(web3, pool_contract, token_contract):
    """
    Get price of a specific token from the pool.
    Args:
        web3: A Web3 instance
        pool_contract: The pool contract instance
        token_contract: The token contract whose price we want
    Returns:
        Decimal: Price of the token in terms of the other token in the pool
    """
    try:
        # Get token addresses from pool
        token0_address = pool_contract.functions.token0().call()
        token1_address = pool_contract.functions.token1().call()
        token_address = token_contract.address

        # Verify token is in pool
        if token_address not in [token0_address, token1_address]:
            raise ValueError("Token not in this pool")

        # Get reserves and decimals
        reserves = pool_contract.functions.getReserves().call()
        reserve0 = Decimal(reserves[0])
        reserve1 = Decimal(reserves[1])

        # Get decimals for both tokens
        token0_contract = web3.eth.contract(address=web3.to_checksum_address(token0_address), abi=config.ERC20_ABI)
        token1_contract = web3.eth.contract(address=web3.to_checksum_address(token1_address), abi=config.ERC20_ABI)
        
        token0_decimals = Decimal(10**token0_contract.functions.decimals().call())
        token1_decimals = Decimal(10**token1_contract.functions.decimals().call())

        # Adjust reserves to human-readable
        reserve0_human = reserve0 / token0_decimals
        reserve1_human = reserve1 / token1_decimals

        # Return price based on which token we're looking for
        if token_address == token0_address:
            return reserve1_human / reserve0_human
        else:
            return reserve0_human / reserve1_human

    except Exception as e:
        print(f"Error getting token price: {e}")
        return None
def initialize_contracts(web3):
    gauge_contract = load_contract(web3, config.GAUGE_CONTRACT_ADDRESS, "guage.json")
    pool_contract = load_contract(web3, config.POOL_CONTRACT_ADDRESS, "pool.json")
    
    token0_address = pool_contract.functions.token0().call()
    token1_address = pool_contract.functions.token1().call()
    
    token0_contract = web3.eth.contract(address=web3.to_checksum_address(token0_address), abi=config.ERC20_ABI)
    token1_contract = web3.eth.contract(address=web3.to_checksum_address(token1_address), abi=config.ERC20_ABI)
    
    return gauge_contract, pool_contract, token0_contract, token1_contract, token0_address, token1_address
