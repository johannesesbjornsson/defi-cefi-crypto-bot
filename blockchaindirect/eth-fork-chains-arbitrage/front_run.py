
import cfg as cfg
import itertools
import sys
import arbitrage
import logic
import traceback
sys.path.insert(0,'../libraries')
from eth_fork_client import Client
from eth_fork_token import Token
from eth_fork_transaction import Transaction
from eth_fork_token_pair import TokenPair
from eth_fork_triggers import Triggers

import time

def main(blockchain, init_type):
    client = Client(blockchain, cfg.my_address, cfg.private_key, cfg.api_key)

    lists = list(itertools.combinations(client.tokens_to_check, 2))
    lists = [
        #["WETH", "WMATIC"],
        #["QUICK", "LINK"]
    ]
    
    triggers = Triggers(client,init_type)

    while True:
        intercepted_transaction = triggers.intercept_transactions()
        if intercepted_transaction:
            triggers.set_tx_filter()
            print("-------------------------------------------------")
            print("--------------END TRANSACTION INFO---------------")
            print("-------------------------------------------------")
        #print("Taking a wee break")
        #time.sleep(2)
        #break


if __name__ == '__main__':
    blockchain=sys.argv[1]
    init_type=sys.argv[2]
    print("Starting application")
    print("Blockchain: ",blockchain)
    print("Init type: ",init_type)

    try:
        main(blockchain,init_type)
    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        if init_type == "live":
            print("Sending email crash update")
            logic.send_email_update("I crashed :(",cfg.email_api_key)
    