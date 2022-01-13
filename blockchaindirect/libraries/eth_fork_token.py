import contract_libarary
import token_config
import asyncio
#from web3.logs import STRICT, IGNORE, DISCARD, WARN
#from web3.exceptions import ContractLogicError, TransactionNotFound, TimeExhausted
#import re
#import time
from eth_fork_transaction import Transaction


class Token(object):

    def __init__(self, client, token, use_standard_contracts=True):
        self.known_tokens = client.known_tokens
        self.client = client

        try:
            self.address = self.client.web3.toChecksumAddress(token)
            self.name = "Uknown"
        except ValueError as e:
            self.address = self.client.web3.toChecksumAddress(self.known_tokens[token])
            self.name = token

        if use_standard_contracts:
            self.token_contract = self.client.web3.eth.contract(
                address=self.address, 
                abi=contract_libarary.standard_contracts["token"])
        else:
            self.abi = self.client.get_abi(self.address)
            self.token_contract = self.client.web3.eth.contract(address=self.address, abi=self.abi)
            self.set_proxy_details()
        
        
        #self.allowance_on_router =  self.token_contract.functions.allowance(self.client.my_address,self.client.router_contract_address).call()
        self.decimals = self.token_contract.functions.decimals().call()
        self.token_symbol = None
        self.allowance = None

        #self.symbol = self.token_contract.functions.symbol().call()
        #asyncio.run(self.fetch_remote_token_info())
    
    def __str__(self):
        return self.address

    @property 
    def symbol(self):
        if not self.token_symbol:
            self.token_symbol = self.token_contract.functions.symbol().call()
        return self.token_symbol

    @property 
    def allowance_on_router(self):
        if not self.allowance:
            self.token_symbol = self.token_contract.functions.allowance(self.client.my_address,self.client.router_contract_address).call()
        return self.allowance

#    async def fetch_remote_token_info(self):
#        done, pending = await asyncio.wait(
#            [self.fetch_symbol(), self.fetch_allowance(), self.fetch_decimals()]
#        )
#
#    async def fetch_symbol(self):
#        self.symbol = self.token_contract.functions.symbol().call()
#
#    async def fetch_allowance(self):
#        self.allowance_on_router =  self.token_contract.functions.allowance(self.client.my_address,self.client.router_contract_address).call()
#
#    async def fetch_decimals(self):
#        self.decimals = self.token_contract.functions.decimals().call()

    def set_proxy_details(self):
        is_proxy = False
        token_contract = self.token_contract

        if "proxyType" in dir(token_contract.functions):
            proxy_contract_address = token_contract.functions.implementation().call()
            proxy_abi  = self.client.get_abi(proxy_contract_address)
            proxy_contract = self.client.web3.eth.contract(address=self.address, abi=proxy_abi)
            
            token_contract = proxy_contract
            is_proxy = True

        self.is_proxy =  is_proxy
        self.token_contract = token_contract

    def approve_token(self):
        if self.allowance == 0:
            value = self.client.web3.toWei(2**64-1,'ether')
            txn = self.token_contract.functions.approve(self.client.router_contract_address,value)
            #transaction_receipt = self.client.sign_and_send_transaction(txn)
            transaction = Transaction(self.client, None)
            transaction.create_transaction(txn)
            transaction.sign_and_send_transaction()
            transaction_complete, transaction_successful = transaction.get_transaction_receipt(wait=True)
            if not transaction_successful:
                raise LookupError("Approve token was not successful")

            self.allowance =  self.token_contract.functions.allowance(self.client.my_address,self.client.router_contract_address).call()

        return True

    def to_wei(self, n):
        wei = n * ( 10 ** self.decimals)
        return int(wei)

    def from_wei(self, n):
        non_wei = n / ( 10 ** self.decimals)
        return float(non_wei)

