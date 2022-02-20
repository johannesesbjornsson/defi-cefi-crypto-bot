import contract_libarary
import time

import asyncio
from web3.logs import STRICT, IGNORE, DISCARD, WARN
from web3.exceptions import ContractLogicError
from eth_fork_token import Token
from eth_fork_transaction import Transaction, RouterTransaction

from eth_abi import decode_abi
from eth_utils import to_bytes

import nest_asyncio
nest_asyncio.apply()
#__import__('IPython').embed()

#import json
#import httpx

class TokenPair(object):
    def __init__(self, client, token_1, token_2, init_type="standard"):
        self.client = client
        self.token_1 = token_1
        self.token_2 = token_2
        self.abi=contract_libarary.standard_contracts["liquidity_pool"]
        
        
        if init_type == "standard":
            self.standard_init()
            self.has_token_fees = self.token_pair_has_fees()
        elif init_type == "local":
            pair_info = self.client.get_pair_info([self.token_1.address, self.token_2.address])
            if pair_info:
                self.raw_reserves_token_1 = pair_info["token0"]
                self.has_token_fees = pair_info["has_token_fees"]
                self.liquidity_pool_address = pair_info["liquidity_pool_address"]
                self.liquidity_pool_contract = self.client.web3.eth.contract(address=self.liquidity_pool_address, abi=self.abi)
                self.token_1_liquidity, self.token_2_liquidity = self.get_pair_liquidity()
            else:
                self.standard_init()
                self.has_token_fees = self.token_pair_has_fees()
                pair = [self.token_1.address, self.token_2.address]
                pair_info = { "token0" : self.raw_reserves_token_1, "liquidity_pool_address" : self.liquidity_pool_address, "has_token_fees": self.has_token_fees }
                self.client.add_pair_info(pair, pair_info)
        elif init_type == "live":
            pair_info = self.client.get_pair_info([self.token_1.address, self.token_2.address])
            if pair_info:
                self.raw_reserves_token_1 = pair_info["token0"]
                self.has_token_fees = pair_info["has_token_fees"]
                self.liquidity_pool_address = pair_info["liquidity_pool_address"]
                self.liquidity_pool_contract = self.client.web3.eth.contract(address=self.liquidity_pool_address, abi=self.abi)
                self.token_1_liquidity, self.token_2_liquidity = self.get_pair_liquidity()
            else:
                self.raw_reserves_token_1 = None
                self.has_token_fees = True
                self.liquidity_pool_address = None
                self.liquidity_pool_contract = None
                self.token_1_liquidity = 0
                self.token_2_liquidity = 0
        else:
            raise ValueError("'init_type' needs to be 'standard', 'live' or 'local'")
        
        
            
    def __str__(self):
        return f"{self.token_1.symbol}: {self.token_1.address},\n{self.token_2.symbol}: {self.token_2.address},\nLiquidity_address: {self.liquidity_pool_address}"

    def standard_init(self):
        liquidity_pool_address = self.client.factory_contract.functions.getPair(self.token_1.address, self.token_2.address).call()
        self.liquidity_pool_address = self.client.web3.toChecksumAddress(liquidity_pool_address)
        try:
            self.liquidity_pool_contract = self.client.web3.eth.contract(address=self.liquidity_pool_address, abi=self.abi)
            self.raw_reserves_token_1 = self.liquidity_pool_contract.functions.token0().call()
            self.token_1_liquidity, self.token_2_liquidity = self.get_pair_liquidity()
        except ValueError as e:
            self.liquidity_pool_contract = None
            self.token_1_liquidity = None
            self.token_2_liquidity = None


    async def fetch_single_transaction(self, transaction_hash):
        router_txn = None
        try:
            transaction_info = await self.client.web3_asybc.eth.get_transaction(transaction_hash)
        except Exception as e:
            return None
        txn = Transaction(self.client, transaction_info)
        if txn.to == self.client.router_contract_address:
            router_txn = RouterTransaction(txn)
        return router_txn

    async def get_router_contract_interaction(self, txns):
        functions_called = []
        if len(txns) == 0:
            return None
        
        done, pending = await asyncio.wait(
            [self.fetch_single_transaction(arg,) for arg in txns]
        )
        for result in done:
            router_txn = result.result()
            if router_txn:
                functions_called.append(router_txn.function_called)
        return functions_called
        

    def token_pair_has_fees(self):
        has_token_fees = False
        response_code, response_json = self.client.get_address_logs(self.liquidity_pool_address, "swap")
        hashes = {}
        bad_hashes = []
        bad_methods = [
            "swapExactTokensForETHSupportingFeeOnTransferTokens",
            "swapExactTokensForTokensSupportingFeeOnTransferTokens",
            "swapExactETHForTokensSupportingFeeOnTransferTokens",
        ]
        if response_code == 200:
            for log in response_json["result"]:
                txn_hash = log["transactionHash"]
                if txn_hash in hashes:
                    hashes[txn_hash] += 1
                    if hashes[txn_hash] > 2:
                        has_token_fees = True 
                        bad_hashes.append(txn_hash)

                else:
                    hashes[txn_hash] = 1
                #decoded = decode_abi(['uint256','uint256','uint256','uint256'], to_bytes(hexstr=data))
        else:
            raise LookupError("Not 200 reponse")
        bad_hashes = list(set(bad_hashes))
        functions = asyncio.run(self.get_router_contract_interaction(bad_hashes))
        if functions:
            for method in bad_methods:
                if method in functions:
                    has_token_fees = True

        return has_token_fees

    def get_amount_in_from_liquidity_impact_of_token_1_for_token_2(self,liquidity_impact):
        try:
             amount_in = liquidity_impact * self.token_1_liquidity
        except ZeroDivisionError as e:
            liquidity_impact = 0
        return amount_in

    def get_amount_in_from_liquidity_impact_of_token_2_for_token_1(self,liquidity_impact):
        try:
             amount_in = liquidity_impact * self.token_2_liquidity
        except ZeroDivisionError as e:
            liquidity_impact = 0
        return amount_in

    def get_liquidity_impact_of_token_1_for_token_2(self,amount_in):
        try:
            liquidity_impact = amount_in/self.token_1_liquidity
        except ZeroDivisionError as e:
            liquidity_impact = 0
        return liquidity_impact

    def get_liquidity_impact_of_token_2_for_token_1(self,amount_in):
        try:
            liquidity_impact = amount_in/self.token_2_liquidity
        except ZeroDivisionError as e:
            liquidity_impact = 0        
        return liquidity_impact

    def quick_router_transction_analysis(self,router_txn):
        impact = 0
        transaction_value = 0
        slippage = 0
        attacking_txn_max_amount_in = 0
        
        # Checks if input token is token 1 and input is defined
        if router_txn.amount_in is not None and router_txn.path[0] == self.token_1.address and router_txn.path[1] == self.token_2.address:
            impact = self.get_liquidity_impact_of_token_1_for_token_2(self.token_1.from_wei(router_txn.amount_in))
            transaction_value = self.token_1.from_wei(router_txn.amount_in)
        # checks if output token is token 2 and second to last token is token 1
        elif router_txn.amount_out is not None and router_txn.path[-1] == self.token_2.address and router_txn.path[-2] == self.token_1.address:
            impact = self.get_liquidity_impact_of_token_2_for_token_1(self.token_2.from_wei(router_txn.amount_out))
            transaction_value = (self.token_1_liquidity/self.token_2_liquidity) * self.token_2.from_wei(router_txn.amount_out)
        
        if impact > 0 and transaction_value > 1 and router_txn.amount_in and router_txn.amount_out and len(router_txn.path) == 2:
            amount_out_with_slippage = self.get_amount_token_2_out(router_txn.amount_in,offline_calculation=True)
            txn_slippage = (amount_out_with_slippage/router_txn.amount_out) - 1
            if txn_slippage > 0:
                attacking_txn_max_amount_in = self.get_amount_in_from_liquidity_impact_of_token_1_for_token_2(txn_slippage)
                slippage = txn_slippage
        elif (router_txn.amount_in and not router_txn.amount_out) or (not router_txn.amount_in and router_txn.amount_out):
            attacking_txn_max_amount_in = transaction_value
            slippage = 1
        elif impact > 0.01 and transaction_value > self.client.minimum_scanned_transaction:
            slippage = 0.02
            print("poop")
            attacking_txn_max_amount_in = transaction_value/10



        return impact, transaction_value, slippage, attacking_txn_max_amount_in

    def get_pair_liquidity(self):
        reserves = self.liquidity_pool_contract.functions.getReserves().call()[0:2]

        if self.raw_reserves_token_1 == self.token_1.address:
            token_1_liquidity = reserves[0]
            token_2_liquidity = reserves[1]
        elif self.raw_reserves_token_1 == self.token_2.address:
            token_1_liquidity = reserves[1]
            token_2_liquidity = reserves[0]

        token_1_liquidity = self.token_1.from_wei(token_1_liquidity)
        token_2_liquidity = self.token_2.from_wei(token_2_liquidity)
        return token_1_liquidity, token_2_liquidity

    def get_amount_token_2_out(self, amount_in, offline_calculation=False):
        if offline_calculation:
            constant_product = self.token_2_liquidity * self.token_1_liquidity        
            new_token_2 = constant_product/( self.token_1_liquidity + self.token_1.from_wei(amount_in))
            amount_out_non_wei = (self.token_2_liquidity - new_token_2) * (1- self.client.router_swap_fee)   
            amount_out = self.token_2.to_wei(amount_out_non_wei)
        else:
            try:
                amount_out = self.client.router_contract.functions.getAmountsOut(amount_in,[self.token_1.address,self.token_2.address]).call()[1]
            except ContractLogicError as e:
                amount_out = 0
        
        return amount_out

    def get_amount_token_1_out(self, amount_in, offline_calculation=False):
        if offline_calculation:
            constant_product = self.token_2_liquidity * self.token_1_liquidity        
            new_token_1 = constant_product/( self.token_2_liquidity + self.token_2.from_wei(amount_in))
            amount_out_non_wei = (self.token_1_liquidity - new_token_1) * (1- self.client.router_swap_fee)   
            amount_out = self.token_1.to_wei(amount_out_non_wei)
        else:
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
            (int(time.time()) + 1000) 
            )
        return txn

    def swap_token_1_for_token_2(self, amount_in, amount_out, gas_price=None, nonce=None):
        from_token = self.token_1.address
        to_token = self.token_2.address
        from_token_amount = amount_in
        to_token_amount = int(amount_out * self.client.slippage)
        txn  = self.build_transaction(from_token, to_token, from_token_amount, to_token_amount)
        transaction = Transaction(self.client, None)
        transaction.create_transaction(txn,gas_price,nonce)
        transaction.sign_and_send_transaction()
        router_transaction = RouterTransaction(transaction)

        return router_transaction

    def swap_token_2_for_token_1(self, amount_in, amount_out, gas_price=None, nonce=None):
        from_token = self.token_2.address
        to_token = self.token_1.address
        from_token_amount = amount_in
        to_token_amount = int(amount_out * self.client.slippage)
        txn  = self.build_transaction(from_token, to_token, from_token_amount, to_token_amount)
        transaction = Transaction(self.client, None)
        transaction.create_transaction(txn,gas_price,nonce)
        transaction.sign_and_send_transaction()

        router_transaction = RouterTransaction(transaction)
        
        return router_transaction
