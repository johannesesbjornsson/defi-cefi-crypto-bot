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

    def __init__(self, client,  init_type):
        self.successful_requests = 0
        self.failed_requests = 0
        self.client = client
        self.token_to_scan_for = self.client.token_to_scan_for
        self.minimum_gas_price = self.client.minimum_gas_price
        self.minimum_liquidity_impact = self.client.minimum_liquidity_impact
        self.scan_token_value = self.client.scan_token_value
        self.token_1 = Token(self.client,self.token_to_scan_for)
        self.client.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        #eth_newPendingTransactionFilter
        self.performing_transaction = False
        self.current_nonce = self.client.get_transaction_count()
        self.current_gas_price = 30
        self.set_tx_filter()
        self.init_type = init_type

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
        slippage = None
        attacking_txn_max_amount_in = None

        function_start = time.perf_counter()

        try:
            input_token, out_token = router_txn.path[-2:]
            if input_token == self.token_to_scan_for:
                token_start = time.perf_counter()
                token_2 = Token(self.client, out_token, self.init_type)
                if token_2.verified == False or token_2.safe_code == False:
                    return my_router_transaction, liquidity_impact, token_pair, None, None

                token_pair = TokenPair(self.client, self.token_1, token_2, self.init_type)

                if token_pair.has_token_fees:
                    return my_router_transaction, liquidity_impact, None, None, None
                token_end = time.perf_counter()
            else:
                token_pair = None
        except ValueError as e:
            token_pair = None

        if token_pair:
            liquidity_impact, txn_value, slippage, attacking_txn_max_amount_in = token_pair.quick_router_transction_analysis(router_txn)

            #if liquidity_impact > self.minimum_liquidity_impact and txn_value > self.minimum_scanned_transaction and attacking_txn_max_amount_in > self.scan_token_value:
            if liquidity_impact > self.minimum_liquidity_impact and attacking_txn_max_amount_in > self.scan_token_value:
                amount_in = self.token_1.to_wei(self.scan_token_value)
                amount_out = token_pair.get_amount_token_2_out(amount_in, offline_calculation=True)
                my_gas_price = router_txn.transaction.gas_price + self.client.gas_price_frontrunning_increase
                
                time_elapsed = time.perf_counter() - function_start
                if self.performing_transaction == False and amount_in is not None and  amount_out is not None and time_elapsed < 0.4:
                    self.performing_transaction = True
                    send_txn_start = time.perf_counter()
                    if self.init_type == "live":
                        my_router_transaction = token_pair.swap_token_1_for_token_2(amount_in, amount_out, gas_price=my_gas_price, nonce=self.current_nonce)
                    send_txn_end = time.perf_counter()
                    function_end = time.perf_counter()
                    print("Sending txn time elapsed: ", send_txn_end - send_txn_start)
                    print("Token init time elapsed: ", token_end - token_start )
                    print("Function time elapsed: ", function_end - function_start,"\n-------")
                    #my_router_transaction = "dummy val"
                #function_end = time.perf_counter()
                #print("Function time elapsed: ", function_end - function_start,"\n-------")

        return my_router_transaction, liquidity_impact, token_pair, slippage, attacking_txn_max_amount_in


    def filter_transaction(self, txn, compare_transaction=None):
        matching_txn = None
        if not compare_transaction and txn.to == self.client.router_contract_address and txn.block_number is None and txn.gas_price >= self.current_gas_price:
        #if not compare_transaction and txn.to == self.client.router_contract_address and txn.block_number is None and txn.gas_price >= self.minimum_gas_price:
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

        for i in range(5):
            try:
                transaction_info = await self.client.web3_asybc.eth.get_transaction(transaction_hash)
                self.successful_requests += 1
                txn = Transaction(self.client, transaction_info)
                matching_txn = self.filter_transaction(txn, compare_transaction)
                break
            except Exception as e:
                txn = None

        if handle_transaction and matching_txn:
            my_txn, liquidity_impact, token_pair, slippage, attacking_txn_max_amount_in = self.handle_swap_transaction(matching_txn)
            if my_txn and liquidity_impact and token_pair:
                matching_txn = (matching_txn, my_txn, liquidity_impact, token_pair, slippage, attacking_txn_max_amount_in)
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

    def watch_transactions(self,txn,look_for_next_txn=True,token_swap_info=None):
        time_started = time.time()
        while txn is not None:
            time_passed = time.time() - time_started
            try:
                transaction_info = self.client.web3.eth.get_transaction(txn.hash)
                txn = Transaction(self.client, transaction_info)
            except TransactionNotFound as e:
                if txn.from_address != "0x0000000000000000000000000000000000000000" and 10 > time_passed:
                    account = Account(self.client,txn.from_address)
                    txn = account.get_next_txn(txn)
            
            if txn.block_number:
                transaction_complete, transaction_successful = txn.get_transaction_receipt(wait=False)
                if transaction_complete and transaction_successful:
                    time.sleep(1)
                    txn = None
                    pass
                elif transaction_complete and not look_for_next_txn:
                    txn = None
                elif transaction_complete and not transaction_successful and look_for_next_txn:
                    account = Account(self.client,txn.from_address)
                    latest_txn = account.get_next_txn(txn)
                    txn = latest_txn
                
            if 360 > time_passed:
                if token_swap_info:
                    token_pair = token_swap_info[0]
                    amount_in = token_swap_info[1]
                    orginal_amount_in = token_swap_info[2]
                    amount_out = token_pair.get_amount_token_1_out(amount_in)
                    ratio = amount_out/orginal_amount_in
                    if ratio > 1.03:
                        txn = None
                if txn:
                    time.sleep(5)
            else:
                print("Giving up....txn not finishing")
                txn = None

    def get_pending_txn(self):
        try:
            pending_transactions = self.tx_filter.get_new_entries()
        except ValueError as e:
            print(e)
            self.set_tx_filter()
            pending_transactions = self.tx_filter.get_new_entries()
        except Exception as e:
            print(e)
            time.sleep(0.1)
            pending_transactions = []
        return pending_transactions


    def intercept_transactions(self):
        intercepted_transaction = False
        self.performing_transaction = False

        self.current_gas_price = self.client.web3.eth.gas_price 
        if self.current_gas_price > self.client.max_gas_price:
            print("Gas prices too high atm...")
            time.sleep(30)
            self.set_tx_filter()
            return False

        self.current_nonce = self.client.get_transaction_count()

        pending_transactions = self.get_pending_txn()
        pending_router_transactions = asyncio.run(self.get_router_contract_interaction(pending_transactions))

        for hande_tuple in pending_router_transactions:
            router_txn = hande_tuple[0]
            my_router_transaction = hande_tuple[1]
            liquidity_impact = hande_tuple[2]
            token_pair = hande_tuple[3]
            slippage = hande_tuple[4]
            attacking_txn_max_amount_in = hande_tuple[5]
            
            intercepted_transaction = True

            self.watch_transactions(my_router_transaction.transaction, False)
            transaction_complete, transaction_successful = my_router_transaction.transaction.get_transaction_receipt(wait=True)
            print("Txn hash", router_txn.transaction.hash)
            print("Initial swap status", transaction_successful)
            print("My txn", my_router_transaction)
            if transaction_successful:
                print("-------------------------------------------------")
                print("Liquidity impact", '{0:.20f}'.format(liquidity_impact))
                print("Max attacking txn value", '{0:.20f}'.format(attacking_txn_max_amount_in))
                amount_out_from_token_2 = my_router_transaction.get_transaction_amount_out()

                approve_token_txn = token_pair.token_2.approve_token()
                if approve_token_txn:
                    self.watch_transactions(approve_token_txn, False)
                self.watch_transactions(router_txn.transaction,True, [token_pair, amount_out_from_token_2, my_router_transaction.amount_in ])
                
                amount_out_from_token_1 = token_pair.get_amount_token_1_out(amount_out_from_token_2)
                my_router_return_transaction = token_pair.swap_token_2_for_token_1(amount_out_from_token_2, amount_out_from_token_1)
                self.watch_transactions(my_router_return_transaction.transaction, False)
                transaction_complete, transaction_successful = my_router_return_transaction.transaction.get_transaction_receipt(wait=True)
                if transaction_successful:
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
