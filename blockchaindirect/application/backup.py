import requests
import json
import contract_libarary
from web3 import Web3
import time
import cfg
from web3.logs import STRICT, IGNORE, DISCARD, WARN
from web3.exceptions import ContractLogicError


class Client(object):

    def __init__(self, my_address, private_key, bsc_scan_api_key):
        bsc = "https://bsc-dataseed.binance.org/"
        self.bsc_scan_api_key = bsc_scan_api_key
        self.debug_mode = False
        self.web3 = Web3(Web3.HTTPProvider(bsc))
        self.my_address = self.web3.toChecksumAddress(my_address)
        self.private_key = private_key
        contract_details = contract_libarary.get_contract_details("pancake_router")
        abi = json.loads(contract_details["abi"])
        contract_address = contract_details["address"]
        self.contract = self.web3.eth.contract(address=contract_address, abi=abi)
        contract_details = contract_libarary.get_contract_details("pancake_factory")
        abi = json.loads(contract_details["abi"])
        contract_address = contract_details["address"]
        self.factory_contract = self.web3.eth.contract(address=contract_address, abi=abi)
        self.get_tokens()

    def get_tokens(self,exclude_tokens=["BUSD", "USDT","USDC","SAFEMOON"]):
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
        all_tokens.update(cfg.all_tokens)
        self.known_tokens = all_tokens


    def get_abi(self,address):
        url = "https://api.bscscan.com/api?module=contract&action=getabi&address={}&apikey={}".format(address, self.bsc_scan_api_key)
        response = requests.get(url)
        json_reponse = json.loads(response.content)
        return json_reponse["result"]
        
    def get_token_price(self, from_token, to_token):
        spend_token = self.web3.toChecksumAddress(self.known_tokens[from_token])
        token_to_buy = self.web3.toChecksumAddress(self.known_tokens[to_token])
        amount = self.web3.toWei(0.00001,'ether')

        try:
            price = self.contract.functions.getAmountsOut(amount,[spend_token,token_to_buy]).call()
            re_adjusted_price = price[1] * 100000
            token_price = self.web3.fromWei(re_adjusted_price,'ether')
            
            if token_price == 0:
                token_price = None
        
        except ContractLogicError as e:
            token_price = None
        
        return token_price
        
    def execute_buy_order(self, from_token, to_token, per_unit_amount_out, from_token_amount):
        spend = self.web3.toChecksumAddress(self.known_tokens[from_token])
        token_to_buy = self.web3.toChecksumAddress(self.known_tokens[to_token])
        nonce = self.web3.eth.get_transaction_count(self.my_address)
        start = time.time()

        #amount_out = (float(from_token_amount)/ float(per_unit_amount_out) * 0.96)
        amount_out = (float(from_token_amount) * float(per_unit_amount_out) * 0.96)
        

        #swapExactTokensForTokens <- investigate when to use
        #swapTokensForExactTokens <- investigate when to use
        pancakeswap2_txn = self.contract.functions.swapExactTokensForTokens(
            self.web3.toWei(from_token_amount,'ether'),
            self.web3.toWei(amount_out,'ether'),
            [spend,token_to_buy],
            self.my_address,
            (int(time.time()) + 10000) 
            ).buildTransaction({
                'from': self.my_address,
                'value': 0,
                'gas': 250000,
                'gasPrice': self.web3.toWei('5','gwei'),
                'nonce': nonce,
            })
        
        if self.debug_mode:
            print("amount out:", amount_out, self.web3.toWei(amount_out,'ether'))
            print("amount in:", from_token_amount,self.web3.toWei(from_token_amount,'ether'))
            print(spend,",",token_to_buy)
            print(self.my_address)
            print((int(time.time()) + 10000) )

        signed_txn = self.web3.eth.account.sign_transaction(pancakeswap2_txn, private_key=self.private_key)
        #tx_token = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        #return self.web3.toHex(tx_token)
        
        return "0xcdde2e6e068aebc0d9fa662c68445f45cac69f4fbb2c7ee47d017b3e76eed88c"

    def get_transaction_final_swap(self,transaction_hash):
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

    def get_pair_liquidity(self,token_1,token_2):
        token_1_liquidity = None
        token_2_liquidity = None
        token_1_hash = self.web3.toChecksumAddress(self.known_tokens[token_1])
        token_2_hash = self.web3.toChecksumAddress(self.known_tokens[token_2])


        liquidity_pool_address = self.factory_contract.functions.getPair(token_1_hash,token_2_hash).call()

        address = self.web3.toChecksumAddress(liquidity_pool_address)
        abi = self.get_abi(address)
        liquidity_pool_contract = self.web3.eth.contract(address=address, abi=abi)

        reserves =  liquidity_pool_contract.functions.getReserves().call()
        reserves_token_1 = liquidity_pool_contract.functions.token0().call()
        reserves_token_2 = liquidity_pool_contract.functions.token1().call()

        if reserves_token_1 == token_1_hash and reserves_token_2 == token_2_hash:
            token_1_liquidity = self.web3.fromWei(reserves[0],'ether')
            token_2_liquidity = self.web3.fromWei(reserves[1],'ether')
        elif reserves_token_2 == token_1_hash and reserves_token_1 == token_2_hash:
            token_1_liquidity = self.web3.fromWei(reserves[1],'ether')
            token_2_liquidity = self.web3.fromWei(reserves[0],'ether')

        if self.debug_mode:
            print("-------")
            print("liquidy address:", liquidity_pool_address)
            print("token_1:", token_1, token_1_liquidity)
            print("token_2:", token_2, token_2_liquidity)
            print("------")

        return token_1_liquidity, token_2_liquidity, liquidity_pool_address


    def approve_contract(self):
        address = self.web3.toChecksumAddress("0x84ba3922ab9cb47ac4d7dfa48ef2215a8dec18e6")
        abi = self.get_abi(address)
        nonce = self.web3.eth.get_transaction_count(self.my_address)
        liquidity_pool_contract = self.web3.eth.contract(address=address, abi=abi)
        value = self.web3.toWei(2**64-1,'ether')
        
        tx = liquidity_pool_contract.functions.approve(address,value).buildTransaction({
                'from': self.my_address,
                'value': 0,
                'gas': 250000,
                'gasPrice': self.web3.toWei('5','gwei'),
                'nonce': nonce,
            })

        #signed_txn = self.web3.eth.account.sign_transaction(tx, private_key=self.private_key)
        #tx_token = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return self.web3.toHex(tx_token)


class Arbitrage(object):

    def __init__(self, client, token_0, token_1, token_2, from_range=[2,20], debug_mode=False):
        if type(client) != Client:
            raise ValueError("Argument must be object type Client")
        self.client = client
        self.debug_mode = debug_mode
        self.client.debug_mode = debug_mode
        self.token_0 = token_0
        self.token_1 = token_1
        self.token_2 = token_2
        self.token_0_hash = self.client.known_tokens[token_0]
        self.token_1_hash = self.client.known_tokens[token_1]
        self.token_2_hash = self.client.known_tokens[token_2]
        self.token_1_price = client.get_token_price(from_token=self.token_1,to_token=self.token_0)
        self.token_2_price = client.get_token_price(from_token=self.token_2,to_token=self.token_0)
        self.token_2_token_1_price = client.get_token_price(from_token=self.token_2,to_token=self.token_1)
        self.token_1_token_2_price = client.get_token_price(from_token=self.token_1,to_token=self.token_2)

    def print_prices(self):
        print("------- TOKEN PRICES -------")
        print("token_1_price", self.token_1, self.token_0, self.token_1_price)
        print("token_2_price", self.token_2, self.token_0, self.token_2_price)
        print("token_1_token_2_price", self.token_1, self.token_2, self.token_1_token_2_price)
        print("----------------------------")

    def find_arbitrage(self):
        self.available_arbitrage = None
        found_arbitrage = False
        offset = 0.03
        if self.token_1_token_2_price is None or self.token_2_price is None or self.token_1_price is None:
            if self.debug_mode:
                print("Unable to find prices for a token", self.token_1_price, self.token_2_price, self.token_1_token_2_price)
            return found_arbitrage


        indirect_token_1_price = self.token_1_token_2_price * self.token_2_price
        indirect_token_2_price = self.token_2_token_1_price * self.token_1_price


        if self.token_1_price/indirect_token_1_price > (1 + offset):
            # Cheaper to buy token_2 and buy token_1 then sell to token_0
            if self.debug_mode:
                print(indirect_token_1_price, "Indirectly cheaper by:",round(self.token_1_price/indirect_token_1_price,5))
            self.available_arbitrage = [
                {"from_token": self.token_0, "to_token": self.token_2 },
                {"from_token": self.token_2, "to_token": self.token_1 },
                {"from_token": self.token_1, "to_token": self.token_0 }
            ]
            found_arbitrage = True

        elif self.token_2_price/indirect_token_2_price > (1 + offset):
            # Cheaper to buy token_1 and buy token_2 then sell to token_0
            if self.debug_mode:
                print(indirect_token_2_price, "Indirectly cheaper by:",round(self.token_2_price/indirect_token_2_price,5))
            self.available_arbitrage = [
                {"from_token": self.token_0, "to_token": self.token_1 },
                {"from_token": self.token_1, "to_token": self.token_2 },
                {"from_token": self.token_2, "to_token": self.token_0 }
            ]
            found_arbitrage = True
        

        if found_arbitrage == True:
            if self.debug_mode:
                print(self.available_arbitrage[0]["from_token"], "->",
                    self.available_arbitrage[0]["to_token"], "->", 
                    self.available_arbitrage[1]["to_token"], "->", 
                    self.available_arbitrage[2]["to_token"]  )
            found_arbitrage = self.arbitrage_liquidity()

        return found_arbitrage

        

    def arbitrage_liquidity(self):
        enough_liquidity = True
        from_amount = 1.0
        required_liquidity = 150
        self.from_token_amount = from_amount 
        for pair in self.available_arbitrage:
            from_token_liquidity, to_token_liquidity, liquidity_pool_address = self.client.get_pair_liquidity(pair["from_token"],pair["to_token"])
            
            if pair["to_token"] == self.token_0:
                dollar_wroth = 1
            else:
                dollar_wroth = self.client.get_token_price(from_token=pair["to_token"],to_token=self.token_0)
            dollar_liquidity =  float(to_token_liquidity * dollar_wroth)
            
            if dollar_liquidity < required_liquidity:
                enough_liquidity = False
                if self.debug_mode:
                    print("Insufficient on ", liquidity_pool_address, "for pair",  pair["from_token"], pair["to_token"], )
        return enough_liquidity
        
    def execute_arbitrage(self):
        
        from_token_amount = self.from_token_amount
        for pair in self.available_arbitrage:
            if self.debug_mode:
                print("Execute order on pair", pair)
            from_token = pair["from_token"]
            to_token = pair["to_token"]
            
            per_unit_amount_out = self.client.get_token_price(from_token=from_token,to_token=to_token)
            transaction_hash = self.client.execute_buy_order(from_token, to_token, per_unit_amount_out, from_token_amount)
            data = self.client.get_transaction_final_swap(transaction_hash)
            from_token_amount = self.client.web3.fromWei(data["amount0Out"],'ether')
        
        
        