import contract_libarary

import asyncio
from transaction import Transaction, TransactionBuilder

import asyncio
#import nest_asyncio
#nest_asyncio.apply()

class Token(object):

    def __init__(self, client, token, init_type="standard",):
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
            self.verified = self.is_token_verified()
            self.safe_code = self.has_safe_code()
        elif init_type == "local":
            token_info = self.client.get_token_info(self.address)
            if token_info:
                self.decimals = token_info["decimals"]
                self.verified = token_info["verified"]
                self.safe_code = token_info["safe_code"]
            else:
                self.verified = self.is_token_verified()
                self.safe_code = self.has_safe_code()
                self.decimals = self.token_contract.functions.decimals().call()
                token_info = { "decimals" : self.decimals, "verified" : self.verified, "safe_code": self.safe_code}
                self.client.add_token_info(self.address, token_info)
        elif init_type == "live":
            token_info = self.client.get_token_info(self.address)
            if token_info:
                self.decimals = token_info["decimals"]
                self.verified = token_info["verified"]
                self.safe_code = token_info["safe_code"]
            else:
                self.decimals = None
                self.verified = False
                self.safe_code = False
        else:
            raise ValueError("'init_type' needs to be 'standard', 'live' or 'local'")

        self.token_symbol = None
        self.allowance = None
    
    def __str__(self):
        return self.address

    def get_token_balance(self):
        balance = self.token_contract.functions.balanceOf(self.client.my_address).call()
        return balance

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

    def has_safe_code(self):
        safe_code = True
        dodgy_code_statements = [
            "function transferFrom(address sender, address recipient, uint256 amount) public override returns (bool)",
            "marketingFee",
            #"function _approve(address owner, address spender, uint256 amount) internal",
            #"mint"
        ]
        response_code, response_json = self.client.get_abi(self.address)
        if response_code == 200:
            if "SourceCode" in response_json["result"][0]:
                #for line in response_json["result"][0]["SourceCode"].split("\n"):
                #    print(line)
                for code_statement in dodgy_code_statements:
                    if code_statement in response_json["result"][0]["SourceCode"]:
                        safe_code = False
        else:
            raise LookupError("Not 200 reponse")
        return safe_code

    def is_token_verified(self):
        verified = False
        response_code, response_json = self.client.get_abi(self.address)
        if response_code == 200:
            if "ABI" in response_json["result"][0]:
                if response_json["result"][0]["ABI"] != "Contract source code not verified":
                    verified = True
        else:
            raise LookupError("Not 200 reponse")
        return verified

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
            transaction_builder = TransactionBuilder(self.client, None)
            transaction_builder.create_transaction(txn)
            transaction = transaction_builder.sign_and_send_transaction()

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

