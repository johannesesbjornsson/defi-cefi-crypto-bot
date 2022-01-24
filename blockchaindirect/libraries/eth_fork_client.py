import requests
import json
import contract_libarary
#from web3 import Web3
import time
import os
from web3.logs import STRICT, IGNORE, DISCARD, WARN
#from web3.eth import AsyncEth

from eth_abi import decode_abi
from eth_utils import to_bytes
import asyncio
import nest_asyncio
nest_asyncio.apply()

from settings.polygon.client import Polygon
from settings.bsc.client import Bsc
from settings.fantom.client import Fantom

class Client(object):

    def __init__(self, blockchain, my_address, private_key, api_key=None):
        if blockchain == "polygon":
            provider = Polygon()
        elif blockchain == "bsc":
            provider = Bsc()
        elif blockchain == "fantom":
            provider = Fantom()
        else:
            raise ValueError(blockchain + " is not a supported blockchain")

        self.web3_ws = provider.web3_ws
        self.web3 = provider.web3
        self.web3_asybc = provider.web3_asybc
        self.router_swap_fee = provider.router_swap_fee  
        self.max_gas_price = provider.max_gas_price
        self.min_gas_price_of_scanned_txn = provider.min_gas_price_of_scanned_txn
        self.gas_price_frontrunning_increase = provider.gas_price_frontrunning_increase
        self.default_gas_price = provider.default_gas_price
        self.default_gas_limit = provider.default_gas_limit
        self.slippage = provider.slippage
        self.token_to_scan_for = provider.token_to_scan_for
        self.scan_token_value = provider.scan_token_value
        self.minimum_scanned_transaction = provider.minimum_scanned_transaction
        self.minimum_liquidity_impact = provider.minimum_liquidity_impact
        self.swap_log_location_index = provider.swap_log_location_index
        self.tokens_to_check = provider.tokens_to_check
        self.known_tokens = provider.known_tokens
        self.router_contract_address = provider.router_contract_address
        self.router_contract = provider.router_contract
        self.factory_contract = provider.factory_contract
        self.factory_contract_address = provider.factory_contract_address
        self.api_key = api_key
        self.blockchain = blockchain
        self.my_address = self.web3.toChecksumAddress(my_address)
        self.private_key = private_key

        self.settings_dir = os.path.dirname(os.path.realpath(__file__)) + '/settings/'+self.blockchain
        self.load_token_json_file()
        

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

    def get_transaction_count(self):
        transaction_count = self.web3.eth.get_transaction_count(self.my_address)
        return transaction_count

    async def eth_call_raw_async(self, contract, contract_address, fn_name, fn_arguments_format, args):
        params = contract.encodeABI(fn_name=fn_name, args=args)
        output = await self.web3_asybc.eth.call({"to": contract_address, "data": params})
        decoded = decode_abi(fn_arguments_format, output)
        return decoded

    def eth_call_raw(self, contract, contract_address , fn_name, fn_arguments_format, args):
        params = contract.encodeABI(fn_name=fn_name, args=args)
        output = self.web3.eth.call({"to": contract_address, "data": params})
        decoded = decode_abi(fn_arguments_format, output)
        return decoded

    def load_token_json_file(self):
        with open(self.settings_dir+'/tokens.json', 'r') as f: 
        	data = json.load(f)
        self.token_info = data

    def get_token_info(self, token):
        token_info = None
        if token in self.token_info:
            token_info = self.token_info[token]
        return token_info

    def add_token_info(self, token, info):
        if token not in self.token_info:
            self.token_info[token] = info
            with open(self.settings_dir+'/tokens.json', "w") as f:
                json.dump(self.token_info, f)
        return True          



#        #params = liquidity_pool_contract.encodeABI(fn_name="getReserves",args=[])
#        #data = {"jsonrpc": "2.0", "method": "eth_call", "params": [{"to": self.liquidity_pool_address, "data": params}, "latest"], "id": 1}
#        #response = await client.post(url="https://polygon-rpc.com",headers={"Content-Type":"application/json"},json=data)
#        #hex_str = response.json()["result"]
#        #decoded = decode_abi(['uint112','uint112','uint32'], to_bytes(hexstr=hex_str))
#        #self.reserves_raw = decoded