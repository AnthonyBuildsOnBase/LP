import json
from web3 import Web3
from dotenv import load_dotenv
import os

# Load environment variables (e.g., API key, wallet address)
load_dotenv()

# Your wallet address and Aerodrome contract address
WALLET_ADDRESS = "0xbdA0c74E10F166EdAbD5ed13A75efC2ae3Fa1896"
CONTRACT_ADDRESS = "0x6cDcb1C4A4D1C3C6d054b27AC5B77e89eAFb971d"  # Replace with the actual pool contract address

# Coinbase RPC endpoint
RPC_URL = "https://api.developer.coinbase.com/rpc/v1/base/uIPZ98fjLaKE3yKltlVBhMewDhtOBJyD"

# Connect to the blockchain
web3 = Web3(Web3.HTTPProvider(RPC_URL))

if web3.isConnected():
    print("Connected to Coinbase RPC!")
else:
    print("Failed to connect to Coinbase RPC.")
    exit()

# Load the ABI
with open("pool.json") as f:
    contract_abi = json.load(f)

# Access the contract
contract = web3.eth.contract(address=web3.toChecksumAddress(CONTRACT_ADDRESS), abi=contract_abi)

# Read the balance of the wallet from the contract
try:
    balance = contract.functions.balanceOf(web3.toChecksumAddress(WALLET_ADDRESS)).call()
    print(f"Balance of wallet {WALLET_ADDRESS}: {web3.fromWei(balance, 'ether')} tokens")
except Exception as e:
    print(f"Error reading balance: {e}")