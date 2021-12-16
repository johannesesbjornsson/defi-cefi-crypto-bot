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
        
    def execute_buy_order(self, from_token, to_token, from_token_amount, to_token_amount):
        spend = self.web3.toChecksumAddress(self.known_tokens[from_token])
        token_to_buy = self.web3.toChecksumAddress(self.known_tokens[to_token])
        nonce = self.web3.eth.get_transaction_count(self.my_address)
        start = time.time()

        amount_out = self.web3.toWei(float(self.web3.fromWei(to_token_amount,'ether')) * 0.99,'ether')
        
        pancakeswap2_txn = self.contract.functions.swapExactTokensForTokens(
            from_token_amount, #amountIn 
            amount_out, #AmountOut
            [spend,token_to_buy],
            self.my_address,
            (int(time.time()) + 10000) 
            ).buildTransaction({
                'from': self.my_address,
                'value': 0,
                'gas': 250000, #TODO have this be not fixed
                'gasPrice': self.web3.toWei('5','gwei'),
                'nonce': nonce,
            })
        
        if self.debug_mode:
            print("amount in:", self.web3.fromWei(from_token_amount,'ether'), from_token_amount)
            print("amount out:", self.web3.fromWei(amount_out,'ether'), amount_out)
            print(spend,",",token_to_buy)
            print(self.my_address)
            print((int(time.time()) + 10000) )

        signed_txn = self.web3.eth.account.sign_transaction(pancakeswap2_txn, private_key=self.private_key)
        tx_token = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return self.web3.toHex(tx_token)
        
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

    def approve_token(self,token_hash):
        #token_hash = self.known_tokens[token]
        address = self.web3.toChecksumAddress(token_hash)
        abi = self.get_abi(address)
        token_contract = self.web3.eth.contract(address=address, abi=abi)
        nonce = self.web3.eth.get_transaction_count(self.my_address)
        is_approved = token_contract.functions.allowance(self.my_address,address).call()

        if is_approved == 0:
            tx = token_contract.functions.approve(address,value).buildTransaction({
                    'from': self.my_address,
                    'value': 0,
                    'gas': 250000,
                    'gasPrice': self.web3.toWei('5','gwei'),
                    'nonce': nonce,
                })
            signed_txn = self.web3.eth.account.sign_transaction(tx, private_key=self.private_key)
            tx_token = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return True


class Arbitrage(object):

    def __init__(self, client, token_0, token_1, token_2, from_range=[20,50], debug_mode=False):
        if type(client) != Client:
            raise ValueError("Argument must be object type Client")
        self.client = client
        self.debug_mode = debug_mode
        self.client.debug_mode = debug_mode
        self.token_0 = token_0
        self.token_1 = token_1
        self.token_2 = token_2
        self.from_range = from_range
        self.token_0_hash = self.client.known_tokens[token_0]
        self.token_1_hash = self.client.known_tokens[token_1]
        self.token_2_hash = self.client.known_tokens[token_2]


    def get_sequence_amount_out(self, amount_in, sequence):
        for pair in sequence:
            from_token = pair["from_token"]
            to_token = pair["to_token"]
            amount_out = self.client.get_token_amount_out(from_token,to_token,amount_in)
            if amount_out is None:
                return 0
            amount_in = amount_out
        return amount_out


    def find_arbitrage(self):
        self.available_arbitrage = None
        self.initial_swap_amount = None
        minimal_initial_offset = self.client.web3.toWei(self.from_range[0] * 1.02,'ether')
        found_arbitrage = False

        potential_arbitrage = {
            "option_1" : [
                {"from_token": self.token_0, "to_token": self.token_1 },
                {"from_token": self.token_1, "to_token": self.token_2 },
                {"from_token": self.token_2, "to_token": self.token_0 }
            ],
            "option_2" : [
                {"from_token": self.token_0, "to_token": self.token_2 },
                {"from_token": self.token_2, "to_token": self.token_1 },
                {"from_token": self.token_1, "to_token": self.token_0 }
            ]
        }

        for option in potential_arbitrage:
            initial_swap_amount = self.client.web3.toWei(self.from_range[0],'ether')
            amount_out = self.get_sequence_amount_out(initial_swap_amount,potential_arbitrage[option])
            max_profit = amount_out - initial_swap_amount

            if amount_out > minimal_initial_offset:
                self.available_arbitrage = potential_arbitrage[option]
                found_arbitrage = True
                optimal_swap_amount = initial_swap_amount
                
                # Finding the optimal amount to buy
                for starting_option in range(self.from_range[0]+1,self.from_range[1]):
                    initial_swap_amount = self.client.web3.toWei(starting_option,'ether')
                    amount_out = self.get_sequence_amount_out(initial_swap_amount,potential_arbitrage[option])
                    profit = amount_out - initial_swap_amount
                    
                    if profit > max_profit:
                        optimal_swap_amount = initial_swap_amount
                        max_profit = profit
                        
                    else:
                        break
                self.initial_swap_amount = optimal_swap_amount

                print(self.available_arbitrage)
                print("Profit", self.client.web3.fromWei(max_profit,'ether'))
                print("Intial Swap sum", self.client.web3.fromWei(initial_swap_amount,'ether'))
                print("--------------------------------------------")

        return found_arbitrage

        
        
    def execute_arbitrage(self):
        from_token_amount = self.initial_swap_amount
        for pair in self.available_arbitrage:
            if self.debug_mode:
                print("Execute order on pair", pair)
            from_token = pair["from_token"]
            to_token = pair["to_token"]
            
            self.client.approve_token(from_token)
            self.client.approve_token(to_token)

            to_token_amount = self.client.get_token_amount_out(from_token=from_token,to_token=to_token, from_token_amount=from_token_amount)
            transaction_hash = self.client.execute_buy_order(from_token, to_token, from_token_amount, to_token_amount)
            data = self.client.get_transaction_final_swap(transaction_hash)
            if data["amount0Out"] != 0:
                from_token_amount = data["amount0Out"]
            elif data["amount1Out"] != 0:
                from_token_amount = data["amount1Out"]
        