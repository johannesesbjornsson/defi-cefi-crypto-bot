
import cfg as cfg
import sys
import arbitrage
import logic
import traceback
sys.path.insert(0,'../libraries')
from blockchain_client import Client
from tokens import Token
from transaction import Transaction
from token_pair import TokenPair
from triggers import Triggers

import time

def main(blockchain, init_type):
    client = Client(blockchain, cfg.my_address, cfg.private_key, cfg.node_key, cfg.api_key)
    
    triggers = Triggers(client,init_type)

    while True:
        intercepted_transaction = triggers.intercept_transactions()
        if intercepted_transaction:
            triggers.txn_scanner.set_tx_filter()
            print("-------------------------------------------------")
            print("--------------END TRANSACTION INFO---------------")
            print("-------------------------------------------------")


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
    