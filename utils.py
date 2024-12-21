
import json
from web3 import Web3
from decimal import Decimal

def connect_web3(rpc_url):
    web3 = Web3(Web3.HTTPProvider(rpc_url))
    if web3.is_connected():
        print("Connected to Coinbase RPC!")
        return web3
    print("Failed to connect to Coinbase RPC.")
    return None

def load_contract(web3, address, abi_path):
    with open(abi_path) as f:
        abi = json.load(f)
    return web3.eth.contract(address=web3.to_checksum_address(address), abi=abi)

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
