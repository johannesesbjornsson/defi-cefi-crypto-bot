
import cfg as cfg
import sys
import arbitrage
import logic
import traceback
import logging
sys.path.insert(0,'../libraries')
from blockchain_client import Client
from tokens import Token
from transaction import Transaction
from token_pair import TokenPair
from triggers import Triggers

import time

def main(blockchain, init_type):

    logging.basicConfig()
    logger = logging.getLogger("front_runner")
    logger.setLevel(logging.INFO)

    logger.info("Starting application")
    logger.info(f"Blockchain: {blockchain}")
    logger.info(f"Init type: {init_type}")
    


    client = Client(blockchain, cfg.my_address, cfg.private_key, cfg.node_key, logger, cfg.api_key)
    
    triggers = Triggers(client,init_type)

    while True:
        intercepted_transaction = triggers.intercept_transactions()
        if intercepted_transaction:
            triggers.txn_scanner.set_tx_filter()
            logger.info("-------------------------------------------------")
            logger.info("--------------END TRANSACTION INFO---------------")
            logger.info("-------------------------------------------------")
            logger.info("--------------------------------------------------------------------------------------------------")


if __name__ == '__main__':
    blockchain=sys.argv[1]
    init_type=sys.argv[2]
    try:
        main(blockchain, init_type)
    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        if init_type == "live":
            print("Sending email crash update")
            logic.send_email_update("I crashed :(",cfg.email_api_key)
    