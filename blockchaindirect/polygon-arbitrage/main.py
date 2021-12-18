
import cfg as cfg
import itertools
import sys
#import arbitrage
sys.path.insert(0,'../libraries')
from polygon import Client
import token_config

from web3 import Web3

#pancakeswap_client = Client(cfg.my_bep20_address, cfg.private_key, cfg.bsc_scan_api_key)
#binance_client = BinanceClient(cfg.api_key,cfg.api_secret,cfg.my_bep20_address)
#token_list = token_config.tokens_to_check
#token_list = ["DOGE", "XRP"]

client = Client(cfg.my_polygon_address, cfg.private_key)

provier_url = "https://speedy-nodes-nyc.moralis.io/0279106ed82b874b3e1b195d/polygon/mainnet"
web3 = Web3(Web3.HTTPProvider(provier_url))

print(web3.isConnected())
balance = web3.eth.getBalance(web3.toChecksumAddress(cfg.my_polygon_address))
print(web3.fromWei(balance, "ether"))

client.get_token_amount_out("0xac51c4c48dc3116487ed4bc16542e27b5694da1b","0xdab529f40e671a1d4bf91361c21bf9f0c9712ab7",1000000000000000000)