import json
from web3 import Web3
import os
from decimal import Decimal, getcontext

# Set precision for Decimal calculations
getcontext().prec = 30

# Wallet and Contract Addresses
WALLET_ADDRESS = "0xbdA0c74E10F166EdAbD5ed13A75efC2ae3Fa1896"
GAUGE_CONTRACT_ADDRESS = "0x4F09bAb2f0E15e2A078A227FE1537665F55b8360"
POOL_CONTRACT_ADDRESS = "0x6cDcb1C4A4D1C3C6d054b27AC5B77e89eAFb971d"

# Get Coinbase CDP credentials from environment variables
CDP_URL = os.environ.get('COINBASE_CDP_URL')
# Connect to the blockchain
web3 = Web3(Web3.HTTPProvider(CDP_URL))

if web3.is_connected():
    print("Connected to Coinbase RPC!")
else:
    print("Failed to connect to Coinbase RPC.")
    exit()

# Load the ABIs
with open("guage.json") as f:
    gauge_abi = json.load(f)
with open("pool.json") as f:
    pool_abi = json.load(f)
erc20_abi = [{
    "constant": True,
    "inputs": [],
    "name": "decimals",
    "outputs": [{
        "name": "",
        "type": "uint8"
    }],
    "type": "function"
}]

# Access the gauge and pool contracts
gauge_contract = web3.eth.contract(
    address=web3.to_checksum_address(GAUGE_CONTRACT_ADDRESS), abi=gauge_abi)
pool_contract = web3.eth.contract(
    address=web3.to_checksum_address(POOL_CONTRACT_ADDRESS), abi=pool_abi)

try:
    # Fetch staked balance from gauge
    staked_balance = gauge_contract.functions.balanceOf(
        web3.to_checksum_address(WALLET_ADDRESS)).call()
    staked_balance_dec = Decimal(staked_balance)
    print(f"Staked LP tokens in gauge: {staked_balance_dec} (raw units)")

    # Fetch total supply of LP tokens from pool
    total_lp_supply = pool_contract.functions.totalSupply().call()
    total_lp_supply_dec = Decimal(total_lp_supply)

    # Fetch reserves from pool
    reserves = pool_contract.functions.getReserves().call()
    reserve0, reserve1 = Decimal(reserves[0]), Decimal(reserves[1])

    # Fetch token0 and token1 addresses from pool
    token0_address = pool_contract.functions.token0().call()
    token1_address = pool_contract.functions.token1().call()

    # Access token contracts
    token0_contract = web3.eth.contract(
        address=web3.to_checksum_address(token0_address), abi=erc20_abi)
    token1_contract = web3.eth.contract(
        address=web3.to_checksum_address(token1_address), abi=erc20_abi)

    # Fetch token decimals
    token0_decimals = token0_contract.functions.decimals().call()
    token1_decimals = token1_contract.functions.decimals().call()

    # Calculate user's share of the pool
    user_share = staked_balance_dec / total_lp_supply_dec
    user_token0 = reserve0 * user_share
    user_token1 = reserve1 * user_share

    # Convert to human-readable format using token decimals
    user_token0_human_readable = user_token0 / Decimal(10**token0_decimals)
    user_token1_human_readable = user_token1 / Decimal(10**token1_decimals)

    print(
        f"Your share of Token0 ({token0_address}): {user_token0_human_readable}"
    )
    print(
        f"Your share of Token1 ({token1_address}): {user_token1_human_readable}"
    )

    # Fetch rewards earned from the gauge
    rewards_earned = gauge_contract.functions.earned(
        web3.to_checksum_address(WALLET_ADDRESS)).call()
    rewards_earned_dec = Decimal(rewards_earned)

    # Fetch reward token address and decimals
    reward_token_address = gauge_contract.functions.rewardToken().call()
    reward_token_contract = web3.eth.contract(
        address=web3.to_checksum_address(reward_token_address), abi=erc20_abi)
    reward_token_decimals = reward_token_contract.functions.decimals().call()

    # Convert rewards to human-readable format
    rewards_human_readable = rewards_earned_dec / Decimal(
        10**reward_token_decimals)
    print(f"Rewards earned ({reward_token_address}): {rewards_human_readable}")

except Exception as e:
    print(f"Error: {e}")
