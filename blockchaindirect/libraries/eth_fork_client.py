import requests
import json
import contract_libarary
from web3 import Web3
import time
import token_config
from web3.logs import STRICT, IGNORE, DISCARD, WARN
from web3.exceptions import ContractLogicError, TransactionNotFound


class Client(object):

    def __init__(self, blockchain, my_address, private_key, api_key):
        if blockchain == "polygon":
            self.api_key = api_key
            provider_url = "https://speedy-nodes-nyc.moralis.io/0279106ed82b874b3e1b195d/polygon/mainnet"
            #provider_url = "https://polygon-rpc.com"
            #provider_url = "https://matic.slingshot.finance"
            provider_ws = "wss://speedy-nodes-nyc.moralis.io/0279106ed82b874b3e1b195d/polygon/mainnet/ws"
            self.web3_ws = Web3(Web3.WebsocketProvider(provider_ws))
            self.web3 = Web3(Web3.HTTPProvider(provider_url))
            router_contract_name = "quickswap_router"
            factory_contract_name = "quickswap_factory"  
            self.get_polygon_tokens()
            self.max_gas_price = self.web3.toWei('750','gwei')
            self.default_gas_limit = 300000 #TODO have this be not fixed
            self.slippage = 0.995
            self.token_to_scan_for = self.web3.toChecksumAddress("0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270")
            self.scan_token_value = 0.1
            self.minimum_scanned_transaction = 5
            self.swap_log_location_index = -2
        elif blockchain == "bsc":
            self.api_key = api_key
            #provider_url = "https://bsc-dataseed.binance.org/"
            provider_url = "https://speedy-nodes-nyc.moralis.io/0279106ed82b874b3e1b195d/bsc/mainnet"
            provider_ws = "wss://speedy-nodes-nyc.moralis.io/0279106ed82b874b3e1b195d/bsc/mainnet/ws"
            self.web3_ws = Web3(Web3.WebsocketProvider(provider_ws))
            self.web3 = Web3(Web3.HTTPProvider(provider_url))    
            router_contract_name = "pancake_router"
            factory_contract_name = "pancake_factory"  
            self.get_bep20_tokens()
            self.slippage = 0.99 
            self.default_gas_limit = 300000
            self.max_gas_price = self.web3.toWei('5','gwei')
            self.token_to_scan_for =  self.web3.toChecksumAddress("0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c")
            self.minimum_scanned_transaction = 1
            self.scan_token_value = 0.005
            self.swap_log_location_index = -1
        elif blockchain == "velas":
            self.api_key = api_key
            provider_url = "https://evmexplorer.velas.com/rpc"
            provider_ws = "wss://api.velas.com/"
            self.web3_ws = Web3(Web3.WebsocketProvider(provider_ws))
            self.web3 = Web3(Web3.HTTPProvider(provider_url)) 
            router_contract_name = "wagyu_router"
            factory_contract_name = "wagyu_factory"  
            self.get_velas_tokens()
            self.slippage = 0.995
            self.default_gas_limit = 300000
            self.max_gas_price = self.web3.toWei('5','gwei')
            self.token_to_scan_for =  self.web3.toChecksumAddress("0xc579D1f3CF86749E05CD06f7ADe17856c2CE3126")
            self.minimum_scanned_transaction = 1
            self.scan_token_value = 0.05
            self.swap_log_location_index = -1
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


    def get_velas_tokens(self):
        self.tokens_to_check = token_config.velas_tokens
        self.known_tokens = token_config.all_velas_tokens


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

                
#    def get_recent_transactions(self):
#
#        url = "https://deep-index.moralis.io/api/v2/{}?chain=polygon&limit=25".format(self.contract_address)
#        response = requests.get(url, headers={"X-API-Key":"0ZMgWQz5RlFhsFYBHOXJqvDCDdYmkZ1KzzY2304zUmsfmBpszfa0Bo3cBnxy1atV"})
#        json_reponse = json.loads(response.content)
#
#        for transaction in json_reponse["result"]:
#            print(transaction["block_timestamp"])
#            #print(transaction.keys())
#            txn_input = self.router_contract.decode_function_input(transaction["input"])
#            print(txn_input[1])
#            #self.toChecksumAddress(txn_input[1]["path"][1])
#            self.toChecksumAddress("USDT")