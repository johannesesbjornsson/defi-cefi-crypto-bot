import contract_libarary
import time

import asyncio
from socket import gaierror
from aiohttp.client_exceptions import ClientConnectorError, ClientResponseError
from websockets.exceptions import ConnectionClosedError
from web3.logs import STRICT, IGNORE, DISCARD, WARN
from web3.exceptions import TransactionNotFound
from web3.middleware import geth_poa_middleware
from tokens import Token
from transaction import Transaction, RouterTransaction
from transaction_scanner import TransactionScanner, TransactionFilter
from token_pair import TokenPair
from account import Account

class Triggers(object):

    def __init__(self, client,  init_type):
        self.client = client
        self.token_to_scan_for = self.client.token_to_scan_for
        self.minimum_gas_price = self.client.minimum_gas_price
        self.minimum_liquidity_impact = self.client.minimum_liquidity_impact
        self.scan_token_value = self.client.scan_token_value
        self.token_1 = Token(self.client,self.token_to_scan_for)
        self.performing_transaction = False
        self.current_nonce = self.client.account.get_transaction_count()
        self.current_gas_price = 30
        self.txn_filter = TransactionFilter(client)
        self.txn_filter.create_router_filter(function_matcher_method="startswith",function_name="swap",block_number=None,minimum_gas_price=client.minimum_gas_price, token_hash=client.token_to_scan_for)
        self.txn_scanner = TransactionScanner(client, self.txn_filter)
        self.init_type = init_type

    def get_attacking_txn_amount_in(self,token_pair, attacking_txn_max_amount_in):
        amount_in = None
        attacking_txn_max_amount_in = attacking_txn_max_amount_in * 0.90

        token_1_balance = self.client.account.token_balances[token_pair.token_1.address]
        txn_value_cap = token_pair.token_1.to_wei(self.client.minimum_scanned_transaction)
        min_value = token_pair.token_1.to_wei(self.scan_token_value)
        max_value = token_pair.token_1.to_wei(attacking_txn_max_amount_in)
        if min_value > token_1_balance:
            raise RuntimeError(f"Not enough balance of {token_pair.token_1.symbol}, needs at least {self.scan_token_value}")

        if max_value > token_1_balance:
            max_value = token_1_balance
        elif max_value > txn_value_cap:
            max_value = txn_value_cap

        amount_in = max_value

        return amount_in

    def get_safe_token_pair(self, router_txn):
        input_token = None
        out_token = None
        try:
            if self.token_to_scan_for in router_txn.path:
                index = router_txn.path.index(self.token_to_scan_for)
                if index == 0 or index == (len(router_txn.path) - 2):
                    input_token = router_txn.path[index]
                    out_token = router_txn.path[index+1]

            if input_token == self.token_to_scan_for:
                token_2 = Token(self.client, out_token, self.init_type)
                if token_2.verified == False or token_2.safe_code == False:
                    return None

                token_pair = TokenPair(self.client, self.token_1, token_2, self.init_type)

                if token_pair.has_token_fees:
                    return None
                
            else:
                token_pair = None
        except ValueError as e:
            token_pair = None
    
        return token_pair
        
    def handle_swap_transaction(self, router_txn):
        return_value = None

        function_start = time.perf_counter()

        token_pair = self.get_safe_token_pair(router_txn)

        token_end = time.perf_counter()

        if token_pair:
            liquidity_impact, txn_value, slippage, attacking_txn_max_amount_in = token_pair.quick_router_transction_analysis(router_txn)

            if liquidity_impact > self.minimum_liquidity_impact and attacking_txn_max_amount_in > self.scan_token_value and txn_value > self.client.minimum_scanned_transaction:
                amount_in = self.get_attacking_txn_amount_in(token_pair, attacking_txn_max_amount_in)
                

                amount_out = token_pair.get_amount_token_2_out(amount_in, offline_calculation=True)
                my_gas_price = router_txn.transaction.gas_price + self.client.gas_price_frontrunning_increase
                
                time_elapsed = time.perf_counter() - function_start
                print("Txn analysis time:",time_elapsed)
                if self.performing_transaction == False and amount_in is not None and  amount_out is not None and time_elapsed < 0.4:
                    self.performing_transaction = True
                    send_txn_start = time.perf_counter()
                    if self.init_type == "live":
                        my_router_transaction = token_pair.swap_token_1_for_token_2(amount_in, amount_out, gas_price=my_gas_price, nonce=self.current_nonce)
                        return_value = (router_txn, my_router_transaction, liquidity_impact, token_pair, slippage, attacking_txn_max_amount_in)

        return return_value


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


    def intercept_transactions(self):
        intercepted_transaction = False
        self.performing_transaction = False

        self.current_gas_price = self.client.web3.eth.gas_price 
        if self.current_gas_price > self.client.max_gas_price:
            print("Gas prices too high atm...")
            time.sleep(30)
            self.txn_scanner.set_tx_filter()
            return False

        self.current_nonce = self.client.account.get_transaction_count()

        pending_router_transactions = asyncio.run(self.txn_scanner.scan_for_txns(self.handle_swap_transaction))

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
                if not transaction_successful:
                    print("Retrying sending return txn")
                    amount_out_from_token_1 = token_pair.get_amount_token_1_out(amount_out_from_token_2)
                    my_router_return_transaction = token_pair.swap_token_2_for_token_1(amount_out_from_token_2, amount_out_from_token_1)
                    self.watch_transactions(my_router_return_transaction.transaction, False)
                    transaction_complete, transaction_successful = my_router_return_transaction.transaction.get_transaction_receipt(wait=True)

                if transaction_successful:
                    print("My return txn", my_router_return_transaction)
                    amount_out = my_router_return_transaction.get_transaction_amount_out()
                    print("Amount in", token_pair.token_1.from_wei(my_router_transaction.amount_in))
                    print("Amount out", token_pair.token_1.from_wei(amount_out))
                else:
                    raise StopIteration(f"{my_router_return_transaction.transaction.hash} was not successful")
        
        self.client.write_pair_info_to_file()  
        self.client.write_token_info_to_file()  
        self.client.account.set_token_balances()

        return intercepted_transaction
