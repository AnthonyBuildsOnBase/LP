
from web3 import Web3
import config
import utils

def main():
    # Connect to blockchain
    web3 = utils.connect_web3(config.CDP_URL)
    if not web3:
        return

    try:
        # Load contracts
        gauge_contract = utils.load_contract(web3, config.GAUGE_CONTRACT_ADDRESS, "guage.json")
        pool_contract = utils.load_contract(web3, config.POOL_CONTRACT_ADDRESS, "pool.json")

        # Fetch staked balance
        staked_balance = gauge_contract.functions.balanceOf(
            web3.to_checksum_address(config.WALLET_ADDRESS)).call()
        print(f"Staked LP tokens in gauge: {staked_balance} (raw units)")

        # Fetch pool info
        total_supply = pool_contract.functions.totalSupply().call()
        reserves = pool_contract.functions.getReserves().call()
        token0_address = pool_contract.functions.token0().call()
        token1_address = pool_contract.functions.token1().call()

        # Create token contracts
        token0_contract = web3.eth.contract(
            address=web3.to_checksum_address(token0_address),
            abi=config.ERC20_ABI)
        token1_contract = web3.eth.contract(
            address=web3.to_checksum_address(token1_address),
            abi=config.ERC20_ABI)

        # Get token decimals
        token0_decimals = utils.get_token_info(web3, token0_contract)
        token1_decimals = utils.get_token_info(web3, token1_contract)

        # Calculate shares
        _, user_token0, user_token1 = utils.calculate_user_share(
            staked_balance, total_supply, reserves[0], reserves[1])

        # Convert to human readable
        token0_human = utils.to_human_readable(user_token0, token0_decimals)
        token1_human = utils.to_human_readable(user_token1, token1_decimals)

        print(f"Your share of Token0 ({token0_address}): {token0_human}")
        print(f"Your share of Token1 ({token1_address}): {token1_human}")

        # Fetch rewards
        rewards_earned = gauge_contract.functions.earned(
            web3.to_checksum_address(config.WALLET_ADDRESS)).call()
        reward_token_address = gauge_contract.functions.rewardToken().call()
        reward_token_contract = web3.eth.contract(
            address=web3.to_checksum_address(reward_token_address),
            abi=config.ERC20_ABI)
        reward_decimals = utils.get_token_info(web3, reward_token_contract)
        
        rewards_human = utils.to_human_readable(rewards_earned, reward_decimals)
        print(f"Rewards earned ({reward_token_address}): {rewards_human}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
