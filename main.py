
from web3 import Web3
import config
import utils

def main():
    web3 = utils.connect_web3(config.CDP_URL)
    if not web3:
        return

    try:
        # Initialize contracts
        gauge_contract, pool_contract, token0_contract, token1_contract, token0_address, token1_address = utils.initialize_contracts(web3)

        # Fetch staked balance
        staked_balance = gauge_contract.functions.balanceOf(web3.to_checksum_address(config.WALLET_ADDRESS)).call()
        print(f"Staked LP tokens in gauge: {staked_balance} (raw units)")

        # Fetch pool details
        total_supply = pool_contract.functions.totalSupply().call()
        reserves = pool_contract.functions.getReserves().call()

        # Get token info
        token0_decimals = utils.get_token_info(web3, token0_contract)
        token1_decimals = utils.get_token_info(web3, token1_contract)

        # Calculate and display shares
        _, user_token0, user_token1 = utils.calculate_user_share(staked_balance, total_supply, reserves[0], reserves[1])
        token0_human = round(utils.to_human_readable(user_token0, token0_decimals), 4)
        token1_human = round(utils.to_human_readable(user_token1, token1_decimals), 4)

        print(f"Your share of Token0 ({token0_address}): {token0_human}")
        print(f"Your share of Token1 ({token1_address}): {token1_human}")

        # Display token prices
        price_token0, price_token1 = utils.get_token_price(web3, pool_contract)
        if price_token0 and price_token1:
            print(f"Price of Token0 in terms of Token1: {round(price_token0, 4)}")
            print(f"Price of Token1 in terms of Token0: {round(price_token1, 4)}")

        # Handle rewards
        rewards_earned = gauge_contract.functions.earned(web3.to_checksum_address(config.WALLET_ADDRESS)).call()
        reward_token_address = gauge_contract.functions.rewardToken().call()
        reward_token_contract = web3.eth.contract(address=web3.to_checksum_address(reward_token_address), abi=config.ERC20_ABI)
        reward_decimals = utils.get_token_info(web3, reward_token_contract)
        rewards_human = round(utils.to_human_readable(rewards_earned, reward_decimals), 4)
        print(f"Rewards earned ({reward_token_address}): {rewards_human}")

        # Calculate USDC value
        reward_price_in_usdc = price_token0 if reward_token_address == token0_address else price_token1 if reward_token_address == token1_address else None
        if reward_price_in_usdc:
            rewards_in_usdc = round(rewards_human * reward_price_in_usdc, 4)
            print(f"Rewards value in USDC: ${rewards_in_usdc}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
