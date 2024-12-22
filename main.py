
from web3 import Web3
import config
import utils
import LP

def main():
    web3 = utils.connect_web3(config.CDP_URL)
    if not web3:
        return

    try:
        # Get LP position details
        lp_details = LP.get_lp_position(web3, config.WALLET_ADDRESS)
        
        # Display token shares
        print(f"\nLP Token Shares:")
        print(f"Token0 ({lp_details['shares']['token0']['address']}): {lp_details['shares']['token0']['amount']}")
        print(f"Token1 ({lp_details['shares']['token1']['address']}): {lp_details['shares']['token1']['amount']}")
        
        # Display token prices
        print(f"\nToken Prices:")
        print(f"Token0 in Token1: {lp_details['prices']['token0_in_token1']}")
        print(f"Token1 in Token0: {lp_details['prices']['token1_in_token0']}")
        
        # Display rewards
        print(f"\nRewards:")
        print(f"Token Address: {lp_details['rewards']['token_address']}")
        print(f"Amount: {lp_details['rewards']['amount']}")
        if lp_details['rewards']['usdc_value']:
            print(f"Value in USDC: ${lp_details['rewards']['usdc_value']}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
