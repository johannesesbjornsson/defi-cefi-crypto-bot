import sys
sys.path.insert(0,'../libraries')
from pancakeswap_client import Client

class Arbitrage(object):

    def __init__(self, client, token_0, token_1, from_range=[20,50], debug_mode=False):
        if type(client) != Client:
            raise ValueError("Argument must be object type Client")
        self.client = client
        self.debug_mode = debug_mode
        self.token_0 = token_0
        self.token_1 = token_1
        self.from_range = from_range
        self.token_0_hash = self.client.known_tokens[token_0]
        self.token_1_hash = self.client.known_tokens[token_1]

