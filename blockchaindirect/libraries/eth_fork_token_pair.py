import contract_libarary
import time
import token_config
from web3.logs import STRICT, IGNORE, DISCARD, WARN
from web3.exceptions import ContractLogicError
from eth_fork_client import Client
from eth_fork_token import Token


class TokenPair(object):
    def __init__(self, client, token_1, token_2):
        if type(client) != Client or type(token_1) != Token or type(token_1) != Token:
            raise ValueError("First arguments must be object types Client, Token and Token")

        self.client = client
        self.token_1 = token_1
        self.token_2 = token_2
        
        liquidity_pool_address = self.client.factory_contract.functions.getPair(self.token_1.address, self.token_2.address).call()
        self.liquidity_pool_address = self.client.web3.toChecksumAddress(liquidity_pool_address)
        self.token_1_liquidity = None
        self.token_2_liquidity = None

    def __str__(self):
        return f"{self.token_1.name}: {self.token_1.address},\n{self.token_2.name}: {self.token_2.address},\nLiquidity_address: {self.liquidity_pool_address}"
    
    def approve_tokens(self):
        if self.token_1.allowance_on_router == 0:
            self.token_1.approve_token()
        if self.token_2.allowance_on_router == 0:
            self.token_2.approve_token()
        return True

    def set_pair_liquidity(self):
        try:
            abi = self.client.get_abi(self.liquidity_pool_address)
            liquidity_pool_contract = self.client.web3.eth.contract(address=self.liquidity_pool_address, abi=abi)
            reserves =  liquidity_pool_contract.functions.getReserves().call()
            reserves_token_1 = liquidity_pool_contract.functions.token0().call()
            reserves_token_2 = liquidity_pool_contract.functions.token1().call()
        except ValueError as e:
            reserves_token_1 = self.token_1.address
            reserves_token_2 = self.token_2.address
            reserves = [0, 0]

        if reserves_token_1 == self.token_1.address and reserves_token_2 == self.token_2.address:
            token_1_liquidity = reserves[0]
            token_2_liquidity = reserves[1]
        elif reserves_token_2 == self.token_1.address and reserves_token_1 == self.token_2.address:
            token_1_liquidity = reserves[1]
            token_2_liquidity = reserves[0]

        self.token_1_liquidity = self.token_1.from_wei(token_1_liquidity)
        self.token_2_liquidity = self.token_2.from_wei(token_2_liquidity)

    def get_pair_liquidity(self):
        return self.token_1_liquidity, self.token_2_liquidity

    def get_amount_token_2_out_by_liquidity(self, amount_in):
        if self.token_1_liquidity > amount_in * 100:
            per_unit_amount = self.token_2_liquidity/self.token_1_liquidity * amount_in
        else:
            per_unit_amount = 0
        return per_unit_amount

    def get_amount_token_1_out_by_liquidity(self, amount_in):
        if self.token_2_liquidity > amount_in * 100:
            per_unit_amount = self.token_1_liquidity/self.token_2_liquidity * amount_in
        else:
            per_unit_amount = 0
        return per_unit_amount

    def get_amount_token_2_out(self, amount_in):
        try:
            amount_out = self.client.router_contract.functions.getAmountsOut(amount_in,[self.token_1.address,self.token_2.address]).call()[1]
        except ContractLogicError as e:
            amount_out = 0 
        
        return amount_out

    def get_amount_token_1_out(self, amount_in):
        try:
            amount_out = self.client.router_contract.functions.getAmountsOut(amount_in,[self.token_2.address,self.token_1.address]).call()[1]
        except ContractLogicError as e:
            amount_out = 0 
        
        return amount_out

    def build_transaction(self, from_token, to_token, from_token_amount, to_token_amount):
        start = time.time()
        txn = self.client.router_contract.functions.swapExactTokensForTokens(
            from_token_amount,
            to_token_amount,
            [from_token,to_token],
            self.client.my_address,
            (int(time.time()) + 10000) 
            )
        return txn

    def swap_token_1_for_token_2(self, amount_in, amount_out):
        from_token = self.token_1.address
        to_token = self.token_2.address
        from_token_amount = amount_in
        to_token_amount = int(amount_out * self.client.slippage)
        txn  = self.build_transaction(from_token, to_token, from_token_amount, to_token_amount)
        transaction_receipt = self.client.sign_and_send_transaction(txn)
        amount_out = self.get_transaction_amount_out(transaction_receipt)

        return amount_out

    def swap_token_2_for_token_1(self, amount_in, amount_out):
        from_token = self.token_2.address
        to_token = self.token_1.address
        from_token_amount = amount_in
        to_token_amount = int(amount_out * self.client.slippage)
        txn  = self.build_transaction(from_token, to_token, from_token_amount, to_token_amount)
        transaction_receipt = self.client.sign_and_send_transaction(txn)
        amount_out = self.get_transaction_amount_out(transaction_receipt)

        return amount_out

    def get_transaction_amount_out(self,transaction_receipt):
        if isinstance(transaction_receipt, str):
            transaction_receipt = self.client.web3.eth.wait_for_transaction_receipt(transaction_receipt)

        if self.client.blockchain == "polygon":
            log_location_index = -2
        elif self.client.blockchain == "bsc":
            log_location_index = -1

        tx_dict = dict(transaction_receipt)
        data = tx_dict["logs"][log_location_index]["data"]
        address = tx_dict["logs"][log_location_index]["address"]
        
        address = self.client.web3.toChecksumAddress(address)
        abi = self.client.get_abi(address)
        contract = self.client.web3.eth.contract(address=address, abi=abi)
        events = contract.events.Swap().processReceipt(transaction_receipt,errors=IGNORE)
        decoded_data = dict(dict(list(events)[log_location_index])["args"])

        if decoded_data["amount0Out"] != 0:
            amount_out = decoded_data["amount0Out"]
        elif decoded_data["amount1Out"] != 0:
            amount_out = decoded_data["amount1Out"]
        return amount_out