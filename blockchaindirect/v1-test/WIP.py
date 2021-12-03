import requests
import json
import contract_libarary
from web3 import Web3
import time

class api_client(object):

    def __init__(self, bsc_scan_api_key):
        self.bsc_scan_api_key = bsc_scan_api_key

    def get_bnb_balance(self,address):
        url = "https://api.bscscan.com/api?module=account&action=balance&address={}&apikey={}".format(address, self.bsc_scan_api_key)
        response = requests.get(url)
        json_reponse = json.loads(response.content)
        balance = int(json_reponse["result"]) / 1000000000000000000
        print(balance)
#curl "https://api.bscscan.com/api?module=account&action=balance&address=0x837107fA17EfD21A10C5Fc43fADFbE79Bd29cC94&apikey=$bsc_scan_api_key"

class client(object):

    def __init__(self, my_address, contract, private_key):
        bsc = "https://bsc-dataseed.binance.org/"
        #bsc = "https://data-seed-prebsc-1-s1.binance.org:8545"
        self.web3 = Web3(Web3.HTTPProvider(bsc))
        self.my_address = self.web3.toChecksumAddress(my_address)
        self.private_key = private_key
        contract_details = contract_libarary.get_contract_details(contract)
        abi = json.loads(contract_details["abi"])
        contract_address = contract_details["address"]
        self.contract = self.web3.eth.contract(address=contract_address, abi=abi)

    def get_token_price(self, from_token, to_token):
        spend_token = self.web3.toChecksumAddress(from_token)
        token_to_buy = self.web3.toChecksumAddress(to_token)

        amount = self.web3.toWei(1,'ether')
        price = self.contract.functions.getAmountsOut(amount,[spend_token,token_to_buy]).call()[1]
        rounded_price = round(self.web3.fromWei(price,'ether'),10)
        return rounded_price
        
    def find_arbitrage(self, token_1, token_2, token_3):
        print("hey")

        
    def execute_buy_order(self, from_token, to_token, per_unit_amount_out):
        nonce = self.web3.eth.get_transaction_count(self.my_address)
        start = time.time()
        spend = self.web3.toChecksumAddress(from_token)
        token_to_buy = self.web3.toChecksumAddress(to_token)
        

        pancakeswap2_txn = self.contract.functions.swapTokensForExactTokens(
            self.web3.toWei(per_unit_amount_out,'ether'),   #amountOut
            self.web3.toWei(1,'ether'),                     #amountInMax
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
        print(per_unit_amount_out, self.web3.toWei(per_unit_amount_out,'ether'))
        print(1,self.web3.toWei(1,'ether'))
        print(spend,",",token_to_buy)
        print(self.my_address)
        print((int(time.time()) + 10000) )


        #signed_txn = self.web3.eth.account.sign_transaction(pancakeswap2_txn, private_key=self.private_key)
        #tx_token = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)



# main.py


import bsc_client
import cfg as cfg
import itertools

client = bsc_client.client(cfg.my_bep20_address, "pancake_router",cfg.private_key)


#print(client.get_token_price(cfg.tokens["BUSD"],cfg.tokens["CAKE"]))

lists = list(itertools.combinations(cfg.tokens.keys(), 2))
for li in lists:
    token_0 = "BUSD"
    token_0_hash = cfg.base_tokens[token_0]
    token_1 = li[0]
    token_1_hash = cfg.tokens[token_1]
    token_2 = li[1]
    token_2_hash = cfg.tokens[token_2]
    tokens = {
        "token_0" : {
            "symbol" : token_0

        },
        "token_1" : {
            "symbol" : token_1

        },
        "token_2" : {
            "symbol" : token_2
        }

    }

    token_1_price = client.get_token_price(token_1_hash,token_0_hash)
    token_2_price = client.get_token_price(token_2_hash,token_0_hash)
    token_1_token_2_price = client.get_token_price(token_1_hash,token_2_hash)


    print(token_1, token_0, token_1_price)
    print(token_2, token_0, token_2_price)
    print(token_1, token_2, token_1_token_2_price)
    #client.execute_buy_order(token_1_hash, token_2_hash, token_1_token_2_price)
    arbitrage_order_sequence = client.find_arbitrage(token_1_price,token_2_price)

    #client.execute_buy_order(from_token=token_0_hash, to_token=token_2_hash, per_unit_amount_out=token_2_price)
    