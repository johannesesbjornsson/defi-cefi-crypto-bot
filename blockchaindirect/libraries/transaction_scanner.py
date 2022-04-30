import contract_libarary
import time

import asyncio
from asyncio.exceptions import TimeoutError
from socket import gaierror
from aiohttp.client_exceptions import ClientConnectorError, ClientResponseError
from websockets.exceptions import ConnectionClosedError
from web3.logs import STRICT, IGNORE, DISCARD, WARN
from web3.exceptions import TransactionNotFound
from web3.middleware import geth_poa_middleware
from tokens import Token
from transaction import Transaction, RouterTransaction

class TransactionScanner(object):

    def __init__(self, client,  init_type):
        self.client = client
        self.client.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.set_tx_filter()


    def set_tx_filter(self):
        try:
            self.tx_filter = self.client.web3_ws.eth.filter('pending')
        except Exception as e:
            self.tx_filter = self.client.web3_ws.eth.filter('pending')


    def get_pending_txn(self):
        try:
            pending_transactions = self.tx_filter.get_new_entries()
        except ValueError as e:
            self.set_tx_filter()
            pending_transactions = self.tx_filter.get_new_entries()
        except Exception as e:
            time.sleep(0.1)
            pending_transactions = []
        return pending_transactions


    def filter_transaction(self, txn, compare_transaction=None):
        matching_txn = None
        if not compare_transaction and txn.to == self.client.router_contract_address and txn.block_number is None and txn.gas_price >= self.current_gas_price:
            router_txn = RouterTransaction(txn)
            if router_txn.function_called.startswith('swap'):
                matching_txn = router_txn
            
        elif compare_transaction and compare_transaction == txn:
            matching_txn = txn
    
        return matching_txn


    async def fetch_single_transaction(self, transaction, compare_transaction=None):
        matching_txn = None
        if isinstance(transaction, str):
            transaction_hash = transaction
        else:
            transaction_hash = self.client.web3.toHex(transaction)

        for i in range(5):
            try:
                transaction_info = await self.client.web3_asybc.eth.get_transaction(transaction_hash)
                txn = Transaction(self.client, transaction_info)
                matching_txn = self.filter_transaction(txn, compare_transaction)
                break
            except Exception as e:
                txn = None
        
        return matching_txn


    async def get_pending_txns(self, filter=None):
        pending_router_transactions = []
        
        if len(pending_transactions) == 0:
            return []

        done, pending = await asyncio.wait(
            [self.fetch_single_transaction(arg,compare_transaction=None,handle_transaction=True) for arg in pending_transactions]
        )
        for result in done:
            router_txn = result.result()
            if router_txn:
                pending_router_transactions.append(router_txn)
                break
        
        return pending_router_transactions