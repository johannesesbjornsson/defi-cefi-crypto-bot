
import cfg as cfg
import itertools
import sys
import arbitrage
sys.path.insert(0,'../libraries')
from eth_fork_client import Client
from eth_fork_token import Token
from eth_fork_transaction import Transaction
from eth_fork_token_pair import TokenPair
from eth_fork_triggers import Triggers

import time

def main(blockchain):
    client = Client(blockchain,cfg.my_address, cfg.private_key)

    lists = list(itertools.combinations(client.tokens_to_check, 2))
    lists = [
        #["WETH", "WMATIC"],
        #["QUICK", "LINK"]
    ]
    
    triggers = Triggers(client)

    while True:
        intercepted_transaction = triggers.intercept_transactions()
        if intercepted_transaction:
            break
        #print("Taking a wee break")
        #time.sleep(2)
        #break


if __name__ == '__main__':
    blockchain=sys.argv[1]
    print("Starting application")
    print("Blockchain: ",blockchain)
    #import cProfile
    #import pstats
    #pr = cProfile.Profile()
    #pr.enable()
    #main()
    #pr.disable()
    #ps = pstats.Stats(pr)
    #ps.print_stats()
    main(blockchain)