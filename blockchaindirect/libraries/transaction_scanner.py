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

    def __init__(self, client, txn_filter):
        self.client = client
        self.client.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.txn_filter = txn_filter
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


    async def fetch_single_transaction(self, transaction, handler=None):
        matching_txn = None
        handler_response = None
        if isinstance(transaction, str):
            transaction_hash = transaction
        else:
            transaction_hash = self.client.web3.toHex(transaction)

        for i in range(5):
            try:
                transaction_info = await self.client.web3_asybc.eth.get_transaction(transaction_hash)
                txn = Transaction(self.client, transaction_info)
                matching_txn = self.txn_filter.get_single_matching_transaction(txn)
                if matching_txn is not None and handler is not None:
                    handler_response = handler(matching_txn)
                else:
                    handler_response = matching_txn
                break
            except TransactionNotFound as e:
                txn = None
            except TimeoutError as e:
                self.client.logger.debug(e.__class__.__name__)
                break
            except Exception as e:
                self.client.logger.debug(e.__class__.__name__)
                txn = None

        return handler_response


    async def scan_for_txns(self, handler, filter=None):
        scan_result = []  
        pending_transactions = self.get_pending_txn()
        if len(pending_transactions) == 0:
            return []

        done, pending = await asyncio.wait(
            [self.fetch_single_transaction(txn,handler) for txn in pending_transactions]
        )

        for result in done:
            res = result.result()
            if res:
                scan_result.append(res)
        
        return scan_result


class TransactionFilter(object):
    def __init__(self, client):
        self.client = client
        self.filter = None

    def match_function(self, txn_function):
        if self.function_matcher_method == "is":
            return self.function_name.__eq__(txn_function)
        elif self.function_matcher_method == "startswith":
            return txn_function.startswith(self.function_name)
        elif self.function_matcher_method == "contains":
            return self.function_name in txn_function
        else:
            raise ValueError(f"function_matcher_method '{self.function_matcher_method}' not supported")

    def create_router_filter(self, block_number=None, minimum_gas_price=None, contract_address=None, function_matcher_method="is", function_name=None, token_hash=None):
        self.block_number = block_number
        self.minimum_gas_price = minimum_gas_price
        self.contract_address = contract_address 
        self.filter = RouterTransactionFilter(function_matcher_method, function_name, token_hash)
  

    def get_single_matching_transaction(self,txn):
        matching_txn = None
        if txn.to == self.client.router_contract_address and txn.block_number == self.block_number and txn.gas_price >= self.minimum_gas_price:
            matching_txn = self.filter.get_single_matching_transaction(txn)
        return matching_txn

class RouterTransactionFilter(TransactionFilter):
    def __init__(self,function_matcher_method, function_name, token_hash):
        self.function_matcher_method = function_matcher_method
        self.function_name = function_name
        self.token_hash = token_hash

    def get_single_matching_transaction(self,txn):
        matching_txn = None
        router_txn = RouterTransaction(txn)
        if self.match_function(router_txn.function_called) and self.token_hash in router_txn.path:
            matching_txn = router_txn

        return matching_txn