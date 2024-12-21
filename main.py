import json
from web3 import Web3
from dotenv import load_dotenv
import os

# Load environment variables from Replit Secrets
WALLET_ADDRESS = os.getenv('WALLET_ADDRESS')
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')
RPC_URL = os.getenv('RPC_URL')

if not all([WALLET_ADDRESS, CONTRACT_ADDRESS, RPC_URL]):
    print("Error: Missing required environment variables. Please check your Secrets.")
    exit()

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