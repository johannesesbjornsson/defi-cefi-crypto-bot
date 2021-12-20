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
            #provider_url = "https://speedy-nodes-nyc.moralis.io/0279106ed82b874b3e1b195d/polygon/mainnet"
            #provider_url = "https://polygon-rpc.com"
            provider_url = "https://matic.slingshot.finance"
            self.web3 = Web3(Web3.HTTPProvider(provider_url))
            router_contract_name = "quickswap_router"
            factory_contract_name = "quickswap_factory"  
            self.get_polygon_tokens()
            self.gas_price = self.web3.toWei('60','gwei')
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
        self.contract_address = contract_address 
        self.contract = self.web3.eth.contract(address=contract_address, abi=abi)
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

    def get_token_amount_out(self, from_token, to_token, from_token_amount):
        spend_token = self.web3.toChecksumAddress(self.known_tokens[from_token])
        token_to_buy = self.web3.toChecksumAddress(self.known_tokens[to_token])

        try:
            token_price = self.contract.functions.getAmountsOut(from_token_amount,[spend_token,token_to_buy]).call()[1]
            if token_price == 0:
                token_price = None
        
        except ContractLogicError as e:
            token_price = None
        
        return token_price

    def build_transaction(self, from_token, to_token, from_token_amount, to_token_amount):
        spend = self.web3.toChecksumAddress(self.known_tokens[from_token])
        token_to_buy = self.web3.toChecksumAddress(self.known_tokens[to_token])
        start = time.time()
        amount_out = self.web3.toWei(float(self.web3.fromWei(to_token_amount,'ether')) * self.slippage,'ether')

        pancakeswap2_txn = self.contract.functions.swapExactTokensForTokens(
            from_token_amount, #amountIn 
            amount_out, #AmountOut
            [spend,token_to_buy],
            self.my_address,
            (int(time.time()) + 10000) 
            )
        
        order = {
            "Amount in" : from_token_amount,
            "Amount out" : amount_out,
            "Spend" : [spend, token_to_buy],
            "Address": self.my_address,
            "Timeout": (int(time.time()) + 10000)
        }

        return pancakeswap2_txn, order

    def execute_buy_order(self, from_token, to_token, from_token_amount, to_token_amount):
        txn, order = self.build_transaction(from_token, to_token, from_token_amount, to_token_amount)
        nonce = self.web3.eth.get_transaction_count(self.my_address)
        pancakeswap2_txn = txn.buildTransaction({
                'from': self.my_address,
                'value': 0,
                'gas': self.default_gas_limit, 
                'gasPrice': self.web3.toWei('5','gwei'),
                'nonce': nonce,
            })

        # TODO: uncomment
        signed_txn = self.web3.eth.account.sign_transaction(pancakeswap2_txn, private_key=self.private_key)
        tx_token = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return self.web3.toHex(tx_token), order
        
        return "0xcdde2e6e068aebc0d9fa662c68445f45cac69f4fbb2c7ee47d017b3e76eed88c", order

    def get_transaction_final_data(self,transaction_hash):
        transaction_receipt = self.web3.eth.wait_for_transaction_receipt(transaction_hash)

        tx_dict = dict(transaction_receipt)
        data = tx_dict["logs"][-1]["data"]
        address = tx_dict["logs"][-1]["address"]
        
        address = self.web3.toChecksumAddress(address)
        abi = self.get_abi(address)
        contract = self.web3.eth.contract(address=address, abi=abi)
        events = contract.events.Swap().processReceipt(transaction_receipt,errors=IGNORE)
        decoded_data = dict(dict(list(events)[-1])["args"])
        
        return decoded_data

    def approve_token(self,token):
        token_hash = self.known_tokens[token]
        token_address = self.web3.toChecksumAddress(token_hash)
        abi = self.get_abi(token_address)
        token_contract = self.web3.eth.contract(address=token_address, abi=abi)

        if "allowance" not in dir(token_contract.functions):
            proxy_contract_address = token_contract.functions.implementation().call()
            proxy_abi  = self.get_abi(proxy_contract_address)
            proxy_contract = self.web3.eth.contract(address=token_address, abi=proxy_abi)
            token_contract = proxy_contract

        is_approved = token_contract.functions.allowance(self.my_address,self.contract_address).call()

        if is_approved == 0:
            nonce = self.web3.eth.get_transaction_count(self.my_address)
            #value = self.web3.toWei(2**64-1,'ether')
            value = self.web3.toWei(2**84-1,'ether')
            tx = token_contract.functions.approve(self.contract_address,value).buildTransaction({
                    'from': self.my_address,
                    'value': 0,
                    'gas': self.default_gas_limit,
                    'gasPrice': self.gas_price,
                    'nonce': nonce,
                })

            # TODO: uncomment
            signed_txn = self.web3.eth.account.sign_transaction(tx, private_key=self.private_key)
            tx_token = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            transaction_receipt = self.web3.eth.wait_for_transaction_receipt(tx_token)

        return True
    
    def estimate_gas_price(self):
        from_amount = 0.1
        from_token_amount = self.web3.toWei(from_amount,'ether')
        to_token_amount = self.get_token_amount_out("BUSD", "CAKE", from_token_amount)
        nonce = self.web3.eth.get_transaction_count(self.my_address)

        txn, order = self.build_transaction("BUSD", "CAKE", from_token_amount, to_token_amount)

        pancakeswap2_txn = txn.estimateGas({
                'from': self.my_address,
                'value': 0,
                'gas': 250000, #TODO have this be not fixed
                'gasPrice': self.gas_price,
                'nonce': nonce,
            })
        print("Estimated gass:", pancakeswap2_txn)


    def get_pair_liquidity(self,token_1,token_2):
        token_1_liquidity = None
        token_2_liquidity = None
        token_1_hash = self.web3.toChecksumAddress(self.known_tokens[token_1])
        token_2_hash = self.web3.toChecksumAddress(self.known_tokens[token_2])
        

        try:
            liquidity_pool_address = self.factory_contract.functions.getPair(token_1_hash,token_2_hash).call()
            address = self.web3.toChecksumAddress(liquidity_pool_address)
            abi = self.get_abi(address)
            liquidity_pool_contract = self.web3.eth.contract(address=address, abi=abi)

            reserves =  liquidity_pool_contract.functions.getReserves().call()
            reserves_token_1 = liquidity_pool_contract.functions.token0().call()
            reserves_token_2 = liquidity_pool_contract.functions.token1().call()
        except ValueError as e:
            reserves_token_1 = token_1_hash
            reserves_token_2 = token_2_hash
            reserves = [0, 0]
            address = None

        if reserves_token_1 == token_1_hash and reserves_token_2 == token_2_hash:
            token_1_liquidity = reserves[0]
            token_2_liquidity = reserves[1]
        elif reserves_token_2 == token_1_hash and reserves_token_1 == token_2_hash:
            token_1_liquidity = reserves[1]
            token_2_liquidity = reserves[0]

        return float(token_1_liquidity), float(token_2_liquidity), address


    def get_amount_out_by_liqudity_pool(self, from_token, to_token, from_token_amount):
        from_token_liquidity, to_token_liquidity, liquidity_pool_address = self.get_pair_liquidity(from_token,to_token)
        if from_token in token_config.polygon_tokens_extra_decimals:
            from_token_liquidity = from_token_liquidity * token_config.polygon_tokens_extra_decimals[from_token]
        if to_token in token_config.polygon_tokens_extra_decimals:
            to_token_liquidity = to_token_liquidity * token_config.polygon_tokens_extra_decimals[to_token]         
        if from_token_liquidity > from_token_amount *100:
            #print(f" {from_token} -> {to_token} || LIQ: {self.web3.fromWei(from_token_liquidity,'ether')} {self.web3.fromWei(to_token_liquidity,'ether')} {liquidity_pool_address}")
            per_unit_amount = to_token_liquidity/from_token_liquidity * float(self.web3.fromWei(from_token_amount,'ether'))
        else:
            #print("Insufficent liquidity")
            #print(f" {from_token} -> {to_token} || LIQ: {self.web3.fromWei(from_token_liquidity,'ether')} {self.web3.fromWei(to_token_liquidity,'ether')} {liquidity_pool_address}")
            per_unit_amount = 0

        return self.web3.toWei(per_unit_amount,'ether')
        


