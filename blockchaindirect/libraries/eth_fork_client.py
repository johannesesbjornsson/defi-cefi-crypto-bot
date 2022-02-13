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
#import nest_asyncio
#nest_asyncio.apply()

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
        self.provider_url = provider.provider_url
        self.web3 = provider.web3
        self.web3_asybc = provider.web3_asybc
        self.router_swap_fee = provider.router_swap_fee  
        self.max_gas_price = provider.max_gas_price
        self.gas_price_frontrunning_increase = provider.gas_price_frontrunning_increase
        self.default_gas_price = provider.default_gas_price
        self.default_gas_limit = provider.default_gas_limit
        self.minimum_gas_price = provider.minimum_gas_price
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
        self.api_url = provider.api_url

        self.chain_id = self.web3.eth.chain_id

        self.settings_dir = os.path.dirname(os.path.realpath(__file__)) + '/settings/'+self.blockchain
        self.load_token_json_from_file()
        self.load_pair_json_from_file()
        

    def get_abi(self,address):
        url = "{}/api?module=contract&action=getsourcecode&address={}&apikey={}".format(self.api_url,address, self.api_key)
        response = requests.get(url)
        json_reponse = json.loads(response.content)

        return response.status_code, json_reponse

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

    def load_token_json_from_file(self):
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
        return True

    def write_token_info_to_file(self):
        with open(self.settings_dir+'/tokens.json', "w") as f:
            json.dump(self.token_info, f)
        return True


    def load_pair_json_from_file(self):
        with open(self.settings_dir+'/pairs.json', 'r') as f: 
        	data = json.load(f)
        self.pair_info = data

    def get_pair_info(self, pair):
        pair_info = None
        pair_key = "_".join(sorted(pair))
        if pair_key in self.pair_info:
            pair_info = self.pair_info[pair_key]
        return pair_info

    def add_pair_info(self, pair, info):
        pair_key = "_".join(sorted(pair))
        if pair_key not in self.pair_info:
            self.pair_info[pair_key] = info
        return True

    def write_pair_info_to_file(self):
        with open(self.settings_dir+'/pairs.json', 'w') as f:
            json.dump(self.pair_info, f)
        return True

    def get_contract_source_code(self, address):
        url = "{}/api?module=contract&action=getsourcecode&address={}&apikey={}".format(self.api_url,address, self.api_key)
        response = requests.get(url)
        json_reponse = json.loads(response.content)
        return response.status_code, json_reponse

    def get_account_transaction(self, address):
        url = "{}/api?module=account&action=txlist&address={}&page=1&offset=50&sort=desc&apikey={}".format(self.api_url,address, self.api_key)
        response = requests.get(url)
        json_reponse = json.loads(response.content)
        return response.status_code, json_reponse


    def get_token_transfers(self, address):
        url = "{}/api?module=account&action=txlistinternal&address={}&page=1&offset=50&sort=desc&apikey={}".format(self.api_url,address, self.api_key)
        response = requests.get(url)
        json_reponse = json.loads(response.content)
        return response.status_code, json_reponse

    def get_address_logs(self, address, topic=None):
        if topic == "swap":
            topic = "&topic0=0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822&topic1=0x000000000000000000000000a5e0829caced8ffdd4de3c43696c57f7d7a678ff"
        else:
            topic = ""
        url = "{}/api?module=logs&action=getLogs&address={}&page=1&offset=150&sort=desc&apikey={}{}".format(self.api_url,address, self.api_key, topic)
        response = requests.get(url)
        json_reponse = json.loads(response.content)
        return response.status_code, json_reponse

#        #params = liquidity_pool_contract.encodeABI(fn_name="getReserves",args=[])
#        #data = {"jsonrpc": "2.0", "method": "eth_call", "params": [{"to": self.liquidity_pool_address, "data": params}, "latest"], "id": 1}
#        #response = await client.post(url="https://polygon-rpc.com",headers={"Content-Type":"application/json"},json=data)
#        #hex_str = response.json()["result"]
#        #decoded = decode_abi(['uint112','uint112','uint32'], to_bytes(hexstr=hex_str))
#        #self.reserves_raw = decoded

    def send_raw_txn(self,txn_data):
        data = {"jsonrpc": "2.0", "method": "eth_sendRawTransaction", "params": [ txn_data ], "id": 1}
        response = requests.post(url=self.provider_url,headers={"Content-Type":"application/json"}, json=data)
        print(response.content)