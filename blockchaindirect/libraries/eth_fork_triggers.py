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
from eth_fork_token import Token
from eth_fork_transaction import Transaction, RouterTransaction
from eth_fork_token_pair import TokenPair
from eth_fork_account import Account

class Triggers(object):

    def __init__(self, client):
        self.successful_requests = 0
        self.failed_requests = 0
        self.client = client
        self.token_to_scan_for = self.client.token_to_scan_for
        self.minimum_liquidity_impact = self.client.minimum_liquidity_impact
        self.scan_token_value = self.client.scan_token_value
        self.token_1 = Token(self.client,self.token_to_scan_for)
        self.client.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        #eth_newPendingTransactionFilter
        self.performing_transaction = False
        self.current_nonce = self.client.get_transaction_count()
        self.current_gas_price = 30
        self.set_tx_filter()

    def set_tx_filter(self):
        try:
            self.tx_filter = self.client.web3_ws.eth.filter('pending')
        except ConnectionResetError as e:
            print("up here")

    def handle_swap_transaction(self, router_txn):
        token_pair = None
        amount_in = None
        amount_out = None
        my_gas_price = None
        liquidity_impact = None
        my_router_transaction = None
        function_start = time.perf_counter()
        try:
            input_token, out_token = router_txn.path[-2:]
            if input_token == self.token_to_scan_for:
                token_start = time.perf_counter()
                token_2 = Token(self.client, out_token, "local")
                if token_2.verified == False or token_2.safe_code == False:
                    return my_router_transaction, liquidity_impact, token_pair

                token_pair = TokenPair(self.client, self.token_1, token_2,"local")

                if token_pair.has_token_fees:
                    return my_router_transaction, liquidity_impact, None
                token_end = time.perf_counter()
            else:
                token_pair = None
        except ValueError as e:
            token_pair = None

        if token_pair:
            liquidity_impact, txn_value, slippage, attacking_txn_max_amount_in = token_pair.quick_router_transction_analysis(router_txn)
            #print("impact", '{0:.20f}'.format(liquidity_impact))
            #print("Value",txn_value)
            #print("slippage",slippage)
            #print("Max value",attacking_txn_max_amount_in)
            #print(router_txn)
            #print("------")

            #if liquidity_impact > self.minimum_liquidity_impact and txn_value > self.minimum_scanned_transaction and attacking_txn_max_amount_in > self.scan_token_value:
            if liquidity_impact > self.minimum_liquidity_impact and attacking_txn_max_amount_in > self.scan_token_value:
                amount_in = self.token_1.to_wei(self.scan_token_value)
                amount_out = token_pair.get_amount_token_2_out(amount_in, offline_calculation=True)
                my_gas_price = router_txn.transaction.gas_price + self.client.gas_price_frontrunning_increase
                
                time_elapsed = time.perf_counter() - function_start
                print(time_elapsed)
                if self.performing_transaction == False and amount_in is not None and  amount_out is not None and time_elapsed < 0.4:
                    self.performing_transaction = True
                    send_txn_start = time.perf_counter()
                    my_router_transaction = token_pair.swap_token_1_for_token_2(amount_in, amount_out, gas_price=my_gas_price, nonce=self.current_nonce)
                    send_txn_end = time.perf_counter()
                    function_end = time.perf_counter()
                    print("Sending txn time elapsed: ", send_txn_end - send_txn_start)
                    print("Token init time elapsed: ", token_end - token_start )
                    print("Function time elapsed: ", function_end - function_start,"\n-------")
                    #my_router_transaction = "dummy val"
                #function_end = time.perf_counter()
                #print("Function time elapsed: ", function_end - function_start,"\n-------")

        return my_router_transaction, liquidity_impact, token_pair


    def filter_transaction(self, txn, compare_transaction=None):
        matching_txn = None
        if not compare_transaction and txn.to == self.client.router_contract_address and txn.block_number is None and txn.gas_price >= self.current_gas_price:
        #if not compare_transaction and txn.to == self.client.router_contract_address and txn.block_number is not None and txn.gas_price >= self.current_gas_price:
            router_txn = RouterTransaction(txn)
            #if router_txn.function_called == "swapExactETHForTokens" or router_txn.function_called == "swapETHForExactTokens":
            #    matching_txn = router_txn
            if router_txn.function_called.startswith('swap'):
                matching_txn = router_txn
            
        elif compare_transaction and compare_transaction == txn:
            matching_txn = txn
    
        return matching_txn

    async def fetch_single_transaction(self, transaction, compare_transaction=None, handle_transaction=False):
        matching_txn = None
        if isinstance(transaction, str):
            transaction_hash = transaction
        else:
            transaction_hash = self.client.web3.toHex(transaction)

        try:
            transaction_info = await self.client.web3_asybc.eth.get_transaction(transaction_hash)
            self.successful_requests += 1
            txn = Transaction(self.client, transaction_info)
            matching_txn = self.filter_transaction(txn, compare_transaction)

        except TransactionNotFound as e:
            self.failed_requests += 1
            txn = None
        except gaierror as e:
            self.failed_requests += 1
            txn = None
        except ClientConnectorError as e:
            self.failed_requests += 1
            txn = None
        except ClientResponseError as e:
            self.failed_requests += 1
            txn = None
        except TimeoutError as e:
            self.failed_requests += 1
            txn = None
        except ValueError as e:
            self.failed_requests += 1
            txn = None

        if handle_transaction and matching_txn:
            my_txn, liquidity_impact, token_pair = self.handle_swap_transaction(matching_txn)
            if my_txn and liquidity_impact and token_pair:
                matching_txn = (matching_txn, my_txn, token_pair, liquidity_impact)
            else:
                matching_txn = None
                
        return matching_txn
        
    async def get_router_contract_interaction(self, pending_transactions):
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

#    def watch_transactions(self,txns,look_for_next_txn=True):
#        time_started = time.time()
#        txns_left = txns
#        while len(txns_left) > 0:
#            txns_not_yet_complete = []
#            for txn in txns_left:
#                if txn:
#                    try:
#                        transaction_info = self.client.web3.eth.get_transaction(txn.hash)
#                        txn = Transaction(self.client, transaction_info)
#                    except TransactionNotFound as e:
#                        if txn.from_address == "0x0000000000000000000000000000000000000000":
#                            continue
#                        account = Account(self.client,txn.from_address)
#                        txn = account.get_next_txn(txn)
#
#                    if txn.block_number:
#                        transaction_complete, transaction_successful = txn.get_transaction_receipt(wait=False)
#                        if transaction_complete and transaction_successful:
#                            time.sleep(1)
#                            pass
#                        elif transaction_complete and not transaction_successful and look_for_next_txn:
#                            account = Account(self.client,txn.from_address)
#                            latest_txn = account.get_next_txn(txn)
#                            txns_not_yet_complete.append(latest_txn)
#
#                    else:
#                        txns_not_yet_complete.append(txn)
#                
#            if 360 > time.time() - time_started:
#                txns_left = txns_not_yet_complete
#                if txns_left:
#                    time.sleep(5)
#            else:
#                print("Giving up....txn not finishing")
#                txns_left = []
#            
#        
#        return txns_left


    def watch_transactions(self,txn,look_for_next_txn=True):
        time_started = time.time()
        while txn is not None:
            try:
                transaction_info = self.client.web3.eth.get_transaction(txn.hash)
                txn = Transaction(self.client, transaction_info)
            except TransactionNotFound as e:
                if txn.from_address == "0x0000000000000000000000000000000000000000":
                    continue
                account = Account(self.client,txn.from_address)
                txn = account.get_next_txn(txn)
            if txn.block_number:
                transaction_complete, transaction_successful = txn.get_transaction_receipt(wait=False)
                if transaction_complete and transaction_successful:
                    time.sleep(1)
                    txn = None
                    pass
                elif transaction_complete and not transaction_successful and look_for_next_txn:
                    account = Account(self.client,txn.from_address)
                    latest_txn = account.get_next_txn(txn)
                    txn = latest_txn
                
            if 360 > time.time() - time_started:
                if txn:
                    time.sleep(5)
            else:
                print("Giving up....txn not finishing")
                txn = None

    def get_pending_txn(self):
        try:
            pending_transactions = self.tx_filter.get_new_entries()
        except ValueError as e:
            self.set_tx_filter()
            pending_transactions = self.tx_filter.get_new_entries()
        except ConnectionResetError as e:
            print("here1")
            pending_transactions = []
        except ConnectionClosedError as e:
            time.sleep(0.2)
            pending_transactions = []
        return pending_transactions


    def intercept_transactions(self):
        intercepted_transaction = False
        self.performing_transaction = False

        self.current_gas_price = self.client.web3.eth.gas_price 
        if self.current_gas_price > self.client.max_gas_price:
            print("Gas prices too high atm...")
            time.sleep(60)
            return False

        self.current_nonce = self.client.get_transaction_count()

        pending_transactions = self.get_pending_txn()

        pending_router_transactions = asyncio.run(self.get_router_contract_interaction(pending_transactions))

        for hande_tuple in pending_router_transactions:
            router_txn = hande_tuple[0]
            my_router_transaction = hande_tuple[1]
            token_pair = hande_tuple[2]
            liquidity_impact = hande_tuple[3]
   

            intercepted_transaction = True

            self.watch_transactions(my_router_transaction.transaction, False)
            transaction_complete, transaction_successful = my_router_transaction.transaction.get_transaction_receipt(wait=True)
            print("Txn hash", router_txn.transaction.hash)
            print("Initial swap status", transaction_successful)
            print("My txn", my_router_transaction)
            if transaction_successful:
                print("Winning!!")
                print("Liquidity impact", '{0:.20f}'.format(liquidity_impact))

                approve_token_txn = token_pair.token_2.approve_token()
                if approve_token_txn:
                    self.watch_transactions(approve_token_txn, False)
                self.watch_transactions(router_txn.transaction)
                amount_out_from_token_2 = my_router_transaction.get_transaction_amount_out()
                amount_out_from_token_1 = token_pair.get_amount_token_1_out(amount_out_from_token_2)
                my_router_return_transaction = token_pair.swap_token_2_for_token_1(amount_out_from_token_2, amount_out_from_token_1)
                self.watch_transactions(my_router_return_transaction.transaction, False)
                transaction_complete, transaction_successful = my_router_return_transaction.transaction.get_transaction_receipt(wait=True)
                if transaction_successful:
                    print("It all went swimmingly")
                    print("My return txn", my_router_return_transaction)
                    amount_out = my_router_return_transaction.get_transaction_amount_out()
                    print("Amount out", token_pair.token_1.from_wei(amount_out))
                else:
                    raise StopIteration(f"{my_router_return_transaction.transaction.hash} was not successful")
                
            #print("--------")
            #print("Successsful requests", self.successful_requests)
            #print("Failed requests", self.failed_requests)
            #print("--------")
        
        self.client.write_pair_info_to_file()  
        self.client.write_token_info_to_file()  

        return intercepted_transaction
