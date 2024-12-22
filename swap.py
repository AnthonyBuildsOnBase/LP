from web3 import Web3
from decimal import Decimal
import utils


def trade_tokens(web3, pool_contract, token_in, token_out, amount_in, recipient, sender_address, private_key):
    """
    Perform a trade between two tokens using the pool contract.
    Args:
        web3: A Web3 instance.
        pool_contract: The pool contract instance.
        token_in: Address of the token being sold.
        token_out: Address of the token being bought.
        amount_in: Amount of `token_in` to sell (raw units).
        recipient: Address to receive the `token_out`.
        sender_address: Address initiating the transaction.
        private_key: Private key of the sender to sign transactions.
    """
    try:
        # Approve the pool contract to spend the input token
        token_in_contract = web3.eth.contract(
            address=web3.to_checksum_address(token_in), abi=utils.ERC20_ABI
        )
        approve_tx = token_in_contract.functions.approve(
            pool_contract.address, amount_in
        ).build_transaction({
            'from': sender_address,
            'nonce': web3.eth.get_transaction_count(sender_address),
            'gas': 200000,  # Adjust based on network and contract complexity
            'gasPrice': web3.toWei('5', 'gwei')  # Adjust gas price as needed
        })

        # Sign and send the approval transaction
        signed_approve_tx = web3.eth.account.sign_transaction(approve_tx, private_key)
        approve_tx_hash = web3.eth.send_raw_transaction(signed_approve_tx.rawTransaction)
        print(f"Approval transaction sent: {web3.to_hex(approve_tx_hash)}")
        web3.eth.wait_for_transaction_receipt(approve_tx_hash)
        print("Approval confirmed.")

        # Fetch reserves for swap
        reserve_in, reserve_out, _ = pool_contract.functions.getReserves().call()
        reserve_in = Decimal(reserve_in)
        reserve_out = Decimal(reserve_out)

        # Calculate minimum output amount with 0.5% slippage
        amount_out = (reserve_out * amount_in) / (reserve_in + amount_in)
        amount_out_min = int(amount_out * Decimal('0.995'))  # 0.5% slippage

        # Perform the swap
        swap_tx = pool_contract.functions.swap(
            0 if token_in == pool_contract.functions.token0().call() else amount_in,
            0 if token_out == pool_contract.functions.token0().call() else amount_out_min,
            recipient,
            b''
        ).build_transaction({
            'from': sender_address,
            'nonce': web3.eth.get_transaction_count(sender_address),
            'gas': 300000,  # Adjust based on network and contract complexity
            'gasPrice': web3.toWei('5', 'gwei')  # Adjust gas price as needed
        })

        # Sign and send the swap transaction
        signed_swap_tx = web3.eth.account.sign_transaction(swap_tx, private_key)
        swap_tx_hash = web3.eth.send_raw_transaction(signed_swap_tx.rawTransaction)
        print(f"Swap transaction sent: {web3.to_hex(swap_tx_hash)}")
        print("Waiting for confirmation...")
        receipt = web3.eth.wait_for_transaction_receipt(swap_tx_hash)
        print(f"Transaction confirmed! Hash: {receipt.transactionHash.hex()}")

    except Exception as e:
        print(f"Error during token swap: {e}")


def main():
    # Connect to the blockchain network
    rpc_url = input("Enter the RPC URL: ")
    web3 = utils.connect_web3(rpc_url)
    if not web3:
        print("Failed to connect to the network.")
        return

    try:
        # Load pool contract
        pool_address = input("Enter the pool contract address: ")
        pool_contract = utils.load_contract(web3, pool_address, "pool.json")

        # User inputs for trade
        sender_address = input("Enter your wallet address: ")
        private_key = input("Enter your private key: ")  # Use secure input in production
        recipient = input("Enter the recipient address: ")
        token_in = input("Enter the token address you are selling: ")
        token_out = input("Enter the token address you want to buy: ")
        amount_in = int(input("Enter the amount to trade (raw units): "))

        # Provide a quote
        reserve_in, reserve_out, _ = pool_contract.functions.getReserves().call()
        reserve_in = Decimal(reserve_in)
        reserve_out = Decimal(reserve_out)
        amount_out = (reserve_out * amount_in) / (reserve_in + amount_in)
        amount_out_min = int(amount_out * Decimal('0.995'))

        print(f"Expected output: {int(amount_out)} units of {token_out}")
        print(f"Minimum output after slippage: {amount_out_min} units of {token_out}")

        # Confirm trade
        confirm = input("Do you want to proceed with the trade? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("Trade canceled.")
            return

        # Execute the trade
        trade_tokens(web3, pool_contract, token_in, token_out, amount_in, recipient, sender_address, private_key)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
