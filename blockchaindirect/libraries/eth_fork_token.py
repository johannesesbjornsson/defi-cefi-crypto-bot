import contract_libarary

import asyncio
from eth_fork_transaction import Transaction

import asyncio
#import nest_asyncio
#nest_asyncio.apply()

class Token(object):

    def __init__(self, client, token, init_type="standard"):
        self.known_tokens = client.known_tokens
        self.client = client

        try:
            self.address = self.client.web3.toChecksumAddress(token)
            self.name = "Uknown"
        except ValueError as e:
            self.address = self.client.web3.toChecksumAddress(self.known_tokens[token])
            self.name = token

        
        self.token_contract = self.client.web3.eth.contract(
            address=self.address, 
            abi=contract_libarary.standard_contracts["token"])
        
        if init_type == "standard":
            self.decimals = self.token_contract.functions.decimals().call()
        elif init_type == "local":
            token_info = self.client.get_token_info(self.address)
            if token_info:
                self.decimals = token_info["decimals"]
            else:
                self.decimals = self.token_contract.functions.decimals().call()
                token_info = { "decimals" : self.decimals }
                self.client.add_token_info(self.address, token_info)
        else:
            raise ValueError("'init_type' needs to be 'standard' or 'local'")

        self.token_symbol = None
        self.allowance = None
    
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
            self.allowance = self.token_contract.functions.allowance(self.client.my_address,self.client.router_contract_address).call()
        return self.allowance

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
        transaction = None
        if self.allowance_on_router == 0:
            value = self.client.web3.toWei(2**64-1,'ether')
            txn = self.token_contract.functions.approve(self.client.router_contract_address,value)
            transaction = Transaction(self.client, None)
            transaction.create_transaction(txn)
            transaction.sign_and_send_transaction()
            #try:
            #    transaction.sign_and_send_transaction()
            #except ValueError as e:
            #    if str(e) == "{'code': -32000, 'message': 'nonce too low'}":
            #        print("Having to resend transaction")
            #        transaction.nonce += 1
            #        transaction.sign_and_send_transaction()
            #    else:
            #        raise ValueError(str(e))

            transaction_complete, transaction_successful = transaction.get_transaction_receipt(wait=True)
            if not transaction_successful:
                raise LookupError(f"Approve token was not successful, see {transaction.hash}")

            self.allowance =  self.token_contract.functions.allowance(self.client.my_address,self.client.router_contract_address).call()

        return transaction

    def to_wei(self, n):
        wei = n * ( 10 ** self.decimals)
        return int(wei)

    def from_wei(self, n):
        non_wei = n / ( 10 ** self.decimals)
        return float(non_wei)

