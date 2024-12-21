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

    # Calculate user's share of the pool
    user_share = staked_balance_dec / total_lp_supply_dec
    user_token0 = reserve0 * user_share
    user_token1 = reserve1 * user_share

    # Convert to human-readable format
    user_token0_human_readable = user_token0 / Decimal(
        10**18)  # Assuming 18 decimals
    user_token1_human_readable = user_token1 / Decimal(
        10**18)  # Assuming 18 decimals

    print(
        f"Your share of Token0 ({token0_address}): {user_token0_human_readable}"
    )
    print(
        f"Your share of Token1 ({token1_address}): {user_token1_human_readable}"
    )

except Exception as e:
    print(f"Error: {e}")
