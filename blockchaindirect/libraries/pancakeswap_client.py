import requests
import json
import contract_libarary
from web3 import Web3
import time
import token_config
from web3.logs import STRICT, IGNORE, DISCARD, WARN
from web3.exceptions import ContractLogicError


class Client(object):

    def __init__(self, my_address, private_key, bsc_scan_api_key):
        bsc = "https://bsc-dataseed.binance.org/"
        self.bsc_scan_api_key = bsc_scan_api_key
        self.web3 = Web3(Web3.HTTPProvider(bsc))
        self.my_address = self.web3.toChecksumAddress(my_address)
        self.private_key = private_key
        contract_details = contract_libarary.get_contract_details("pancake_router")
        abi = json.loads(contract_details["abi"])
        contract_address = contract_details["address"]
        self.contract_address = self.web3.toChecksumAddress(contract_address) 
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
        all_tokens.update(token_config.all_tokens)
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

    def build_transaction(self, from_token, to_token, from_token_amount, to_token_amount):
        spend = self.web3.toChecksumAddress(self.known_tokens[from_token])
        token_to_buy = self.web3.toChecksumAddress(self.known_tokens[to_token])
        start = time.time()
        amount_out = self.web3.toWei(float(self.web3.fromWei(to_token_amount,'ether')) * 0.99,'ether')

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
                'gas': 250000, #TODO have this be not fixed
                'gasPrice': self.web3.toWei('5','gwei'),
                'nonce': nonce,
            })

        
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

        #is_approved = token_contract.functions.allowance(self.my_address,token_address).call()
        is_approved = token_contract.functions.allowance(self.my_address,self.contract_address).call()
        
        if is_approved == 0:
            print("not approved")
            nonce = self.web3.eth.get_transaction_count(self.my_address)
            #value = self.web3.toWei(2**64-1,'ether')
            value = self.web3.toWei(2**84-1,'ether')
            tx = token_contract.functions.approve(self.contract_address,value).buildTransaction({
                    'from': self.my_address,
                    'value': 0,
                    'gas': 250000,
                    'gasPrice': self.web3.toWei('5','gwei'),
                    'nonce': nonce,
                })

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
                'gasPrice': self.web3.toWei('5','gwei'),
                'nonce': nonce,
            })
        print("Estimated gass:", pancakeswap2_txn)


