
import os
from decimal import Decimal, getcontext

# Set precision for Decimal calculations
getcontext().prec = 30

# Wallet and Contract Addresses
WALLET_ADDRESS = "0xbdA0c74E10F166EdAbD5ed13A75efC2ae3Fa1896"
GAUGE_CONTRACT_ADDRESS = "0x4F09bAb2f0E15e2A078A227FE1537665F55b8360"
POOL_CONTRACT_ADDRESS = "0x6cDcb1C4A4D1C3C6d054b27AC5B77e89eAFb971d"

# RPC URL
CDP_URL = os.environ.get('COINBASE_CDP_URL')

# Basic ERC20 ABI
ERC20_ABI = [{
    "constant": True,
    "inputs": [],
    "name": "decimals",
    "outputs": [{
        "name": "",
        "type": "uint8"
    }],
    "type": "function"
}]
