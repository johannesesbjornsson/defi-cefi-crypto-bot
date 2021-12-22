import requests
import json
import contract_libarary
from web3 import Web3
import time
import token_config
from web3.logs import STRICT, IGNORE, DISCARD, WARN
from web3.exceptions import ContractLogicError


class Client(object):

    def __init__(self, blockchain, my_address, private_key, api_key):
        if blockchain == "polygon":
            self.api_key = api_key
            provider_url = "https://speedy-nodes-nyc.moralis.io/0279106ed82b874b3e1b195d/polygon/mainnet"
            #provider_url = "https://polygon-rpc.com"
            #provider_url = "https://matic.slingshot.finance"
            self.web3 = Web3(Web3.HTTPProvider(provider_url))
            router_contract_name = "quickswap_router"
            factory_contract_name = "quickswap_factory"  
            self.get_polygon_tokens()
            self.gas_price = self.web3.toWei('30','gwei')
            self.default_gas_limit = 300000 #TODO have this be not fixed
            self.slippage = 0.995
        elif blockchain == "bsc":
            self.api_key = api_key
            provider_url = "https://bsc-dataseed.binance.org/"
            self.web3 = Web3(Web3.HTTPProvider(provider_url))
            router_contract_name = "pancake_router"
            factory_contract_name = "pancake_factory"  
            self.get_bep20_tokens()
            self.slippage = 0.99 
            self.default_gas_limit = 250000
            self.gas_price = self.web3.toWei('5','gwei')
        else:
            raise ValueError(blockchain + "is not a supported blockchain")

        
        self.blockchain = blockchain
        self.my_address = self.web3.toChecksumAddress(my_address)
        self.private_key = private_key
        contract_details = contract_libarary.get_contract_details(router_contract_name)
        abi = json.loads(contract_details["abi"])
        contract_address = self.web3.toChecksumAddress(contract_details["address"])
        self.router_contract_address = contract_address 
        self.router_contract = self.web3.eth.contract(address=contract_address, abi=abi)
        contract_details = contract_libarary.get_contract_details(factory_contract_name)
        abi = json.loads(contract_details["abi"])
        contract_address = self.web3.toChecksumAddress(contract_details["address"])
        self.factory_contract = self.web3.eth.contract(address=contract_address, abi=abi)


    def get_bep20_tokens(self,exclude_tokens=["BUSD", "USDT","USDC","SAFEMOON"]):
        url = "https://api.pancakeswap.info/api/v2/pairs"
        response = requests.get(url)
        json_reponse = json.loads(response.content)["data"]
        known_tokens = {}
        for pair in json_reponse:
            token_1 = pair.split("_")[0]
            token_2 = pair.split("_")[1]
            token_1_symbol = json_reponse[pair]["base_symbol"]
            token_2_symbol = json_reponse[pair]["quote_symbol"]
            if token_1_symbol in exclude_tokens or token_2_symbol in exclude_tokens:
                #skip stable coins
                continue
            elif token_1_symbol not in known_tokens:
                known_tokens[token_1_symbol] = token_1
            elif token_2_symbol not in known_tokens:
                known_tokens[token_2_symbol] = token_2

        self.tokens_to_check = known_tokens

        all_tokens = known_tokens.copy()
        all_tokens.update(token_config.bep20_all_tokens)
        self.known_tokens = all_tokens

    def get_polygon_tokens(self):
        self.tokens_to_check = token_config.polygon_tokens
        self.known_tokens = token_config.polygon_all_tokens


    def get_abi(self,address):
        if self.blockchain == "bsc":
            url = "https://api.bscscan.com/api?module=contract&action=getabi&address={}&apikey={}".format(address, self.api_key)
            response = requests.get(url)
            json_reponse = json.loads(response.content)
        elif self.blockchain == "polygon":
            url = "https://api.polygonscan.com/api?module=contract&action=getabi&address={}&apikey={}".format(address, self.api_key)
            response = requests.get(url)
            json_reponse = json.loads(response.content)
      
        return json_reponse["result"]

    def sign_and_send_transaction(self, transaction):
        nonce = self.web3.eth.get_transaction_count(self.my_address)
        built_txn = transaction.buildTransaction({
                'from': self.my_address,
                'value': 0,
                'gas': self.default_gas_limit, 
                'gasPrice': self.gas_price,
                'nonce': nonce,
            })

        signed_txn = self.web3.eth.account.sign_transaction(built_txn, private_key=self.private_key)
        txn_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        transaction_receipt = self.web3.eth.wait_for_transaction_receipt(txn_hash)
        
        return self.web3.toHex(txn_hash)


class Token(object):

    def __init__(self, client, token):
        if type(client) != Client:
            raise ValueError("Argument must be object type Client")
        self.known_tokens = client.known_tokens
        self.client = client

        try:
            self.address = self.client.web3.toChecksumAddress(token)
            self.name = "Uknown"
        except ValueError as e:
            self.address = self.client.web3.toChecksumAddress(self.known_tokens[token])
            self.name = token

        self.abi = self.client.get_abi(self.address)
        self.token_contract = self.client.web3.eth.contract(address=self.address, abi=self.abi)

        self.set_proxy_details()
        self.allowance_on_router =  self.token_contract.functions.allowance(self.client.my_address,self.client.router_contract_address).call()
        self.decimals = self.token_contract.functions.decimals().call()
    
    def __str__(self):
        return self.address

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
        if self.allowance_on_router == 0:
            value = self.client.web3.toWei(2**84-1,'ether')
            txn = self.token_contract.functions.approve(self.client.router_contract_address,value)
            self.client.sign_and_send_transaction(txn)

        return True

    def to_wei(self, n):
        wei = n * ( 10 ** self.decimals)
        return int(wei)

    def from_wei(self, n):
        non_wei = n / ( 10 ** self.decimals)
        return float(non_wei)


class TokenPair(object):
    def __init__(self, client, token_1, token_2):
        if type(client) != Client or type(token_1) != Token or type(token_1) != Token:
            raise ValueError("First arguments must be object types Client, Token and Token")

        self.client = client
        self.token_1 = token_1
        self.token_2 = token_2
        self.set_pair_liquidity()

    def __str__(self):
        return f"{self.token_1.name}: {self.token_1.address}, {self.token_2.name}: {self.token_2.address}"
        
    def set_pair_liquidity(self):
        try:
            liquidity_pool_address = self.client.factory_contract.functions.getPair(self.token_1.address, self.token_2.address).call()
            liquidity_pool_address = self.client.web3.toChecksumAddress(liquidity_pool_address)
            abi = self.client.get_abi(liquidity_pool_address)
            liquidity_pool_contract = self.client.web3.eth.contract(address=liquidity_pool_address, abi=abi)
            reserves =  liquidity_pool_contract.functions.getReserves().call()
            reserves_token_1 = liquidity_pool_contract.functions.token0().call()
            reserves_token_2 = liquidity_pool_contract.functions.token1().call()
        except ValueError as e:
            reserves_token_1 = self.token_1.address
            reserves_token_2 = self.token_2.address
            reserves = [0, 0]
            liquidity_pool_address = None

        if reserves_token_1 == self.token_1.address and reserves_token_2 == self.token_2.address:
            token_1_liquidity = reserves[0]
            token_2_liquidity = reserves[1]
        elif reserves_token_2 == self.token_1.address and reserves_token_1 == self.token_2.address:
            token_1_liquidity = reserves[1]
            token_2_liquidity = reserves[0]

        self.token_1_liquidity = self.token_1.from_wei(token_1_liquidity)
        self.token_2_liquidity = self.token_2.from_wei(token_2_liquidity)
        self.liquidity_pool_address = liquidity_pool_address

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
        amount_in_wei = self.token_1.to_wei(amount_in)
        try:
            amount_out_wei = self.client.router_contract.functions.getAmountsOut(amount_in_wei,[self.token_1.address,self.token_2.address]).call()[1]
        except ContractLogicError as e:
            amount_out_wei = 0 
        amount_out = self.token_2.from_wei(amount_out_wei)
        return amount_out

    def get_amount_token_1_out(self, amount_in):
        amount_in_wei = self.token_2.to_wei(amount_in)
        try:
            amount_out_wei = self.client.router_contract.functions.getAmountsOut(amount_in_wei,[self.token_2.address,self.token_1.address]).call()[1]
        except ContractLogicError as e:
            amount_out_wei = 0 
        amount_out = self.token_1.from_wei(amount_out_wei)
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
        from_token_amount = self.token_1.to_wei(amount_in)
        to_token_amount = self.token_2.to_wei(amount_out * self.client.slippage)
        txn  = self.build_transaction(from_token, to_token, from_token_amount, to_token_amount)
        txn_hash = self.client.sign_and_send_transaction(txn)
        return txn_hash

    def swap_token_2_for_token_1(self, amount_in, amount_out):
        from_token = self.token_2.address
        to_token = self.token_1.address
        from_token_amount = self.token_2.to_wei(amount_in)
        to_token_amount = self.token_1.to_wei(amount_out * self.client.slippage)
        txn  = self.build_transaction(from_token, to_token, from_token_amount, to_token_amount)
        txn_hash = self.client.sign_and_send_transaction(txn)
        return txn_hash