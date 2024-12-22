
from web3 import Web3
from decimal import Decimal
import utils
import config

class LPPosition:
    def __init__(self, web3, wallet_address):
        self.web3 = web3
        self.wallet_address = wallet_address
        self.gauge_contract = None
        self.pool_contract = None
        self.token0_contract = None
        self.token1_contract = None
        self.token0_address = None
        self.token1_address = None
        self.initialize_contracts()

    def initialize_contracts(self):
        (
            self.gauge_contract,
            self.pool_contract,
            self.token0_contract,
            self.token1_contract,
            self.token0_address,
            self.token1_address
        ) = utils.initialize_contracts(self.web3)

    def get_staked_balance(self):
        staked_balance = self.gauge_contract.functions.balanceOf(
            self.web3.to_checksum_address(self.wallet_address)
        ).call()
        return staked_balance

    def get_pool_details(self):
        total_supply = self.pool_contract.functions.totalSupply().call()
        reserves = self.pool_contract.functions.getReserves().call()
        return total_supply, reserves

    def get_token_shares(self):
        staked_balance = self.get_staked_balance()
        total_supply, reserves = self.get_pool_details()
        
        token0_decimals = utils.get_token_info(self.web3, self.token0_contract)
        token1_decimals = utils.get_token_info(self.web3, self.token1_contract)
        
        _, user_token0, user_token1 = utils.calculate_user_share(
            staked_balance, total_supply, reserves[0], reserves[1]
        )
        
        token0_human = round(utils.to_human_readable(user_token0, token0_decimals), 4)
        token1_human = round(utils.to_human_readable(user_token1, token1_decimals), 4)
        
        return {
            'token0': {
                'address': self.token0_address,
                'amount': token0_human
            },
            'token1': {
                'address': self.token1_address,
                'amount': token1_human
            }
        }

    def get_token_prices(self):
        price_token0 = utils.get_token_price(self.web3, self.pool_contract, self.token0_contract)
        price_token1 = utils.get_token_price(self.web3, self.pool_contract, self.token1_contract)
        return price_token0, price_token1

    def get_rewards(self):
        rewards_earned = self.gauge_contract.functions.earned(
            self.web3.to_checksum_address(self.wallet_address)
        ).call()
        
        reward_token_address = self.gauge_contract.functions.rewardToken().call()
        reward_token_contract = self.web3.eth.contract(
            address=self.web3.to_checksum_address(reward_token_address),
            abi=config.ERC20_ABI
        )
        
        reward_decimals = utils.get_token_info(self.web3, reward_token_contract)
        rewards_human = round(utils.to_human_readable(rewards_earned, reward_decimals), 4)
        
        # Calculate USDC value
        price_token0, price_token1 = self.get_token_prices()
        reward_price_in_usdc = None
        
        if reward_token_address == self.token0_address:
            reward_price_in_usdc = price_token0
        elif reward_token_address == self.token1_address:
            reward_price_in_usdc = price_token1
            
        rewards_in_usdc = None
        if reward_price_in_usdc:
            rewards_in_usdc = round(rewards_human * reward_price_in_usdc, 4)
            
        return {
            'token_address': reward_token_address,
            'amount': rewards_human,
            'usdc_value': rewards_in_usdc
        }

def get_lp_position(web3, wallet_address):
    position = LPPosition(web3, wallet_address)
    shares = position.get_token_shares()
    prices = position.get_token_prices()
    rewards = position.get_rewards()
    
    return {
        'shares': shares,
        'prices': {
            'token0_in_token1': round(prices[0], 4) if prices[0] else None,
            'token1_in_token0': round(prices[1], 4) if prices[1] else None
        },
        'rewards': rewards
    }
