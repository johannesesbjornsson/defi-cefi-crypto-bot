import contract_libarary
import time
import token_config
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
    def __init__(self, client, token_1, token_2, asynchronous_init=False):
        self.client = client
        self.token_1 = token_1
        self.token_2 = token_2
        self.abi=contract_libarary.standard_contracts["liquidity_pool"]
        
        

        if asynchronous_init:
            loop = asyncio.get_event_loop()
            results = loop.run_until_complete(self.asynchronous_object_init())
            self.liquidity_pool_address = results[0]
            self.liquidity_pool_contract = results[1]
            self.token_1_liquidity = results[2]
            self.token_2_liquidity = results[3]
        else:
            liquidity_pool_address = self.client.factory_contract.functions.getPair(self.token_1.address, self.token_2.address).call()
            self.liquidity_pool_address = self.client.web3.toChecksumAddress(liquidity_pool_address)
            try:
                self.liquidity_pool_contract = self.client.web3.eth.contract(address=self.liquidity_pool_address, abi=self.abi)
                self.token_1_liquidity, self.token_2_liquidity = self.get_pair_liquidity()
            except ValueError as e:
                self.liquidity_pool_contract = None
                self.token_1_liquidity = None
                self.token_2_liquidity = None     
        

    def __str__(self):
        return f"{self.token_1.symbol}: {self.token_1.address},\n{self.token_2.symbol}: {self.token_2.address},\nLiquidity_address: {self.liquidity_pool_address}"
    
    def approve_tokens(self):
        if self.token_1.allowance_on_router == 0:
            self.token_1.approve_token()
        if self.token_2.allowance_on_router == 0:
            self.token_2.approve_token()
        return True

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

    async def asynchronous_object_init(self):
        token_1_liquidity = None
        token_2_liquidity = None
        done, pending = await asyncio.wait([
            self.client.eth_call_raw_async(self.client.factory_contract, self.client.factory_contract_address, "getPair", ['address'], [self.token_1.address, self.token_2.address])
        ])
        liquidity_pool_address = self.client.web3.toChecksumAddress(list(done)[0].result()[0])
        liquidity_pool_contract = self.client.web3.eth.contract(address=liquidity_pool_address, abi=self.abi)

        done, pending = await asyncio.wait([
            self.client.eth_call_raw_async(liquidity_pool_contract, liquidity_pool_address, "token0", ['address'], []),
            self.client.eth_call_raw_async(liquidity_pool_contract, liquidity_pool_address, "getReserves", ['uint112','uint112','uint32'], []),
        ])
        results = [r.result() for r in done]
        token_1 = results[0][0] if len(results[0]) == 1 else results[1][0] 
        reserves = results[0][0:2] if len(results[0]) == 3 else results[1][0:2]
        clean_token_1 = self.client.web3.toChecksumAddress(token_1)

        if clean_token_1 == self.token_1.address:
            token_1_liquidity = self.token_1.from_wei(reserves[0])
            token_2_liquidity = self.token_2.from_wei(reserves[1])
        elif clean_token_1 == self.token_2.address:    
            token_1_liquidity = self.token_1.from_wei(reserves[1])
            token_2_liquidity = self.token_2.from_wei(reserves[0])
        
        return liquidity_pool_address, liquidity_pool_contract, token_1_liquidity, token_2_liquidity

    def quick_router_transction_analysis(self,router_txn):
        impact = 0
        transaction_value = 0

        if router_txn.amount_in is not None and len(router_txn.path) == 2:
            #impact = self.token_1.from_wei(router_txn.amount_in)/self.token_1_liquidity
            impact = self.get_liquidity_impact_of_token_1_for_token_2(self.token_1.from_wei(router_txn.amount_in))
            transaction_value = self.token_1.from_wei(router_txn.amount_in)
        elif router_txn.amount_out is not None:
            #impact = self.token_2.from_wei(router_txn.amount_out)/self.token_2_liquidity
            impact = self.get_liquidity_impact_of_token_2_for_token_1(self.token_2.from_wei(router_txn.amount_out))
            transaction_value = (self.token_1_liquidity/self.token_2_liquidity) * self.token_2.from_wei(router_txn.amount_out)

        return impact, transaction_value

    def get_pair_liquidity(self):
        reserves = self.liquidity_pool_contract.functions.getReserves().call()[0:2]
        reserves_token_1 = self.liquidity_pool_contract.functions.token0().call()
        reserves_token_2 = self.liquidity_pool_contract.functions.token1().call()

        if reserves_token_1 == self.token_1.address and reserves_token_2 == self.token_2.address:
            token_1_liquidity = reserves[0]
            token_2_liquidity = reserves[1]
        elif reserves_token_2 == self.token_1.address and reserves_token_1 == self.token_2.address:
            token_1_liquidity = reserves[1]
            token_2_liquidity = reserves[0]

        token_1_liquidity = self.token_1.from_wei(token_1_liquidity)
        token_2_liquidity = self.token_2.from_wei(token_2_liquidity)
        return token_1_liquidity, token_2_liquidity

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
            (int(time.time()) + 1000) 
            )
        return txn

    def swap_token_1_for_token_2(self, amount_in, amount_out, gas_price=None):
        from_token = self.token_1.address
        to_token = self.token_2.address
        from_token_amount = amount_in
        to_token_amount = int(amount_out * self.client.slippage)
        txn  = self.build_transaction(from_token, to_token, from_token_amount, to_token_amount)
        transaction = Transaction(self.client, None)
        transaction.create_transaction(txn,gas_price)
        transaction.sign_and_send_transaction()
        router_transaction = RouterTransaction(transaction)

        return router_transaction

    def swap_token_2_for_token_1(self, amount_in, amount_out, gas_price=None):
        from_token = self.token_2.address
        to_token = self.token_1.address
        from_token_amount = amount_in
        to_token_amount = int(amount_out * self.client.slippage)
        txn  = self.build_transaction(from_token, to_token, from_token_amount, to_token_amount)
        transaction = Transaction(self.client, None)
        transaction.create_transaction(txn,gas_price)
        transaction.sign_and_send_transaction()

        router_transaction = RouterTransaction(transaction)
        
        return router_transaction
