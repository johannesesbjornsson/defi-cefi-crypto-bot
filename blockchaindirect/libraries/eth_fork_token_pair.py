import contract_libarary
import time
import token_config
import asyncio
from web3.logs import STRICT, IGNORE, DISCARD, WARN
from web3.exceptions import ContractLogicError #, TransactionNotFound
from eth_fork_token import Token
from eth_fork_transaction import Transaction, RouterTransaction

from eth_abi import decode_abi
from eth_utils import to_bytes


#import json
#import httpx

class TokenPair(object):
    def __init__(self, client, token_1, token_2):
        self.client = client
        self.token_1 = token_1
        self.token_2 = token_2
        
        liquidity_pool_address = self.client.factory_contract.functions.getPair(self.token_1.address, self.token_2.address).call()
        self.liquidity_pool_address = self.client.web3.toChecksumAddress(liquidity_pool_address)

        abi=contract_libarary.standard_contracts["liquidity_pool"]

        #time.sleep(5)
        self.set_pair_liquidity()

    def __str__(self):
        return f"{self.token_1.symbol}: {self.token_1.address},\n{self.token_2.symbol}: {self.token_2.address},\nLiquidity_address: {self.liquidity_pool_address}"
    
    def approve_tokens(self):
        if self.token_1.allowance_on_router == 0:
            self.token_1.approve_token()
        if self.token_2.allowance_on_router == 0:
            self.token_2.approve_token()
        return True

    def get_liquidity_impact_of_token_1_for_token_2(self,amount_in):
        liquidity_impact = amount_in/self.token_1_liquidity
        return liquidity_impact

    def get_liquidity_impact_of_token_2_for_token_1(self,amount_in):
        liquidity_impact = amount_in/self.token_2_liquidity
        return liquidity_impact

#    async def get_token_1_reserves(self, client, liquidity_pool_contract):
#        #params = liquidity_pool_contract.encodeABI(fn_name="token0",args=[])
#        #output = await self.client.web3_asybc.eth.call({"to": self.liquidity_pool_address, "data": params})
#        #decoded = decode_abi(["address"], output)[0]
#        #address = self.client.web3.toChecksumAddress(decoded)
#        #self.token_1_reserves_raw = address
#
#        params = liquidity_pool_contract.encodeABI(fn_name="token0",args=[])
#        data = {"jsonrpc": "2.0", "method": "eth_call", "params": [{"to": self.liquidity_pool_address, "data": params}, "latest"], "id": 1}
#        response = await client.post("https://polygon-rpc.com", headers={"Content-Type":"application/json"},json=data)
#        hex_str = response.json()["result"]
#        decoded = decode_abi(['address'], to_bytes(hexstr=hex_str))[0]
#        address = self.client.web3.toChecksumAddress(decoded)
#        self.token_1_reserves_raw = address
#
#    async def get_token_2_reserves(self, client, liquidity_pool_contract):
#        #params = liquidity_pool_contract.encodeABI(fn_name="token1",args=[])
#        #output = await self.client.web3_asybc.eth.call({"to": self.liquidity_pool_address, "data": params})
#        #decoded = decode_abi(["address"], output)[0]
#        #address = self.client.web3.toChecksumAddress(decoded)
#        #self.token_2_reserves_raw = address
#
#        params = liquidity_pool_contract.encodeABI(fn_name="token1",args=[])
#        data = {"jsonrpc": "2.0", "method": "eth_call", "params": [{"to": self.liquidity_pool_address, "data": params}, "latest"], "id": 1}
#        response = await client.post("https://polygon-rpc.com", headers={"Content-Type":"application/json"},json=data)
#        hex_str = response.json()["result"]
#        decoded = decode_abi(['address'], to_bytes(hexstr=hex_str))[0]
#        address = self.client.web3.toChecksumAddress(decoded)
#        self.token_2_reserves_raw = address
#
#    async def get_reserves_raw(self, client, liquidity_pool_contract):
#        #params = liquidity_pool_contract.encodeABI(fn_name="getReserves",args=[])
#        #output = await self.client.web3_asybc.eth.call({"to": self.liquidity_pool_address, "data": params})
#        #decoded = decode_abi(['uint112','uint112','uint32'], output)
#        #self.reserves_raw = decoded
#
#        params = liquidity_pool_contract.encodeABI(fn_name="getReserves",args=[])
#        data = {"jsonrpc": "2.0", "method": "eth_call", "params": [{"to": self.liquidity_pool_address, "data": params}, "latest"], "id": 1}
#        response = await client.post(url="https://polygon-rpc.com",headers={"Content-Type":"application/json"},json=data)
#        hex_str = response.json()["result"]
#        decoded = decode_abi(['uint112','uint112','uint32'], to_bytes(hexstr=hex_str))
#        self.reserves_raw = decoded
#
#
#    async def get_pair_liquidity_raw(self, liquidity_pool_contract):
#        #done, pending = await asyncio.wait([
#        #    self.get_token_1_reserves(liquidity_pool_contract),
#        #    self.get_token_2_reserves(liquidity_pool_contract),
#        #    self.get_reserves_raw(liquidity_pool_contract)
#        #])
#        async with httpx.AsyncClient() as client:
#            tasks = [
#                self.get_token_1_reserves(client,liquidity_pool_contract),
#                self.get_token_2_reserves(client,liquidity_pool_contract),
#                self.get_reserves_raw(client,liquidity_pool_contract)
#            ]
#            results = await asyncio.gather(*tasks)
#        return self.reserves_raw, self.token_1_reserves_raw, self.token_2_reserves_raw 

    def get_pair_liquidity(self,liquidity_pool_contract):
        reserves =  liquidity_pool_contract.functions.getReserves().call()
        reserves_token_1 = liquidity_pool_contract.functions.token0().call()
        reserves_token_2 = liquidity_pool_contract.functions.token1().call()
        return reserves, reserves_token_1, reserves_token_2

    def set_pair_liquidity(self):
        try:
            
            abi=contract_libarary.standard_contracts["liquidity_pool"]

            liquidity_pool_contract = self.client.web3.eth.contract(address=self.liquidity_pool_address, abi=abi)

            #reserves, reserves_token_1, reserves_token_2 = asyncio.run(self.get_pair_liquidity_raw(liquidity_pool_contract))
            reserves, reserves_token_1, reserves_token_2 = self.get_pair_liquidity(liquidity_pool_contract)
            
        except ValueError as e:
            reserves_token_1 = self.token_1.address
            reserves_token_2 = self.token_2.address
            reserves = [None, None]

        if reserves_token_1 == self.token_1.address and reserves_token_2 == self.token_2.address:
            token_1_liquidity = reserves[0]
            token_2_liquidity = reserves[1]
        elif reserves_token_2 == self.token_1.address and reserves_token_1 == self.token_2.address:
            token_1_liquidity = reserves[1]
            token_2_liquidity = reserves[0]

        self.token_1_liquidity = self.token_1.from_wei(token_1_liquidity)
        self.token_2_liquidity = self.token_2.from_wei(token_2_liquidity)

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
#        transaction_complete, transaction_successful = transaction.get_transaction_receipt(wait=True)
#        if not transaction_successful:
#            raise LookupError(f"{transaction.hash} Transaction not successful")
#
#        router_transaction = RouterTransaction(transaction)
#        amount_out = router_transaction.get_transaction_amount_out()
#        return amount_out

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

        #transaction_complete, transaction_successful = transaction.get_transaction_receipt(wait=True)
        #if not transaction_successful:
        #    raise LookupError(f"{transaction.hash} Transaction not successful")
        #router_transaction = RouterTransaction(transaction)
        #amount_out = router_transaction.get_transaction_amount_out()
        #return amount_out
