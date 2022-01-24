import contract_libarary
import time

import asyncio
from asyncio.exceptions import TimeoutError
from socket import gaierror
from aiohttp.client_exceptions import ClientConnectorError, ClientResponseError
from web3.logs import STRICT, IGNORE, DISCARD, WARN
from web3.exceptions import TransactionNotFound
from web3.middleware import geth_poa_middleware
from eth_fork_token import Token
from eth_fork_transaction import Transaction, RouterTransaction
from eth_fork_token_pair import TokenPair


class Triggers(object):

    def __init__(self, client):
        self.successful_requests = 0
        self.failed_requests = 0
        self.client = client
        self.token_to_scan_for = self.client.token_to_scan_for
        self.minimum_scanned_transaction = self.client.minimum_scanned_transaction
        self.minimum_liquidity_impact = self.client.minimum_liquidity_impact
        self.scan_token_value = self.client.scan_token_value
        self.token_1 = Token(self.client,self.token_to_scan_for)
        self.client.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        #eth_newPendingTransactionFilter
        self.tx_filter = self.client.web3_ws.eth.filter('pending')
        self.performing_transaction = False
        self.current_nonce = self.client.get_transaction_count()

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
                #start = time.perf_counter()
                token_2 = Token(self.client, out_token)
                token_pair = TokenPair(self.client, self.token_1, token_2)
                #end = time.perf_counter()
                #print("Token init time elapsed: ", end - start)
                
            else:
                token_pair = None
        except ValueError as e:
            token_pair = None

        if token_pair:
            liquidity_impact, txn_value = token_pair.quick_router_transction_analysis(router_txn)

            if liquidity_impact > self.minimum_liquidity_impact and txn_value > self.minimum_scanned_transaction:
                amount_in = self.token_1.to_wei(self.scan_token_value)
                amount_out = token_pair.get_amount_token_2_out(amount_in, offline_calculation=True)
                my_gas_price = router_txn.transaction.gas_price + self.client.gas_price_frontrunning_increase

                
                if self.performing_transaction == False and amount_in is not None and  amount_out is not None:
                    self.performing_transaction = True
                    my_router_transaction = token_pair.swap_token_1_for_token_2(amount_in, amount_out, gas_price=my_gas_price, nonce=self.current_nonce)
                    function_end = time.perf_counter()
                    print("Function time elapsed: ", function_end - function_start,"\n-------")
                #my_router_transaction = "dummy val"
                #function_end = time.perf_counter()
                #print("Function time elapsed: ", function_end - function_start,"\n-------")

        return my_router_transaction, liquidity_impact, token_pair


    def filter_transaction(self, txn, compare_transaction=None):
        matching_txn = None
        if not compare_transaction and txn.to == self.client.router_contract_address and txn.block_number is None and txn.gas_price > self.client.min_gas_price_of_scanned_txn:
        #if not compare_transaction and txn.to == self.client.router_contract_address and txn.block_number is not None and txn.gas_price > self.client.min_gas_price_of_scanned_txn:
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


    async def watch_competing_transaction(self, transaction):
        transaction_complete, transaction_successful = transaction.get_transaction_receipt(wait=False)
        time_started = time.time()
        while transaction_successful == False and 360 > time.time() - time_started:
            pending_transactions = self.tx_filter.get_new_entries()
            if len(pending_transactions) == 0:
                time.sleep(1)
                continue
            
            done, pending = await asyncio.wait(
                [self.fetch_single_transaction(arg,compare_transaction=transaction) for arg in pending_transactions]
            )

            for result in done:
                txn = result.result()
                if not txn:
                    continue
                print("Overwriting transaction found")
                print(txn)
                print(txn.gas_price)
                transaction = txn
            
            
            print("wathcing....", time.time() - time_started)
            time.sleep(5)
            transaction_complete, transaction_successful = transaction.get_transaction_receipt(wait=False)
            if transaction_complete == True and transaction_successful == False:
                print("Scanned transaction failed, increasing nonce")
                transaction.nonce += 1
    
        return transaction_complete, transaction_successful

    def intercept_transactions(self):
        #eth_newPendingTransactionFilter
        #tx_filter = self.client.web3_ws.eth.filter('pending')
        intercepted_transaction = False
        self.performing_transaction = False

    
        #time.sleep(0.2)
        if self.client.web3.eth.gas_price > self.client.max_gas_price:
            print("Gas prices to high atm...")
            time.sleep(60)
            return False

        self.current_nonce = self.client.get_transaction_count()

        pending_transactions = self.tx_filter.get_new_entries()

        #start = time.perf_counter()
        pending_router_transactions = asyncio.run(self.get_router_contract_interaction(pending_transactions))
        #end = time.perf_counter()
        #print("Scan Time elapsed: ", str(end - start), "\nFailed Req: "+ str(self.failed_requests),"\nSuccessful req:" + str(self.successful_requests), "\nToken length:", str(len(pending_transactions)))

        for hande_tuple in pending_router_transactions:
            router_txn = hande_tuple[0]
            my_router_transaction = hande_tuple[1]
            token_pair = hande_tuple[2]
            liquidity_impact = hande_tuple[3]
            
    
            
            #txn =  asyncio.run(self.fetch_single_transaction(router_txn.transaction.hash))
            #if not txn:
            #    continue


            if 1 == 2:
            #print(txn.transaction.block_number)
            #if txn.transaction.block_number:
                print("Too slow....")
                #print("Transaction successful: ",router_txn.transaction.successful)
                #print("Txn hash", router_txn.transaction.hash)
                #print("Gas price", router_txn.transaction.gas_price)
                #print("Sender address", router_txn.transaction.from_address)
            else:
            #if not transaction_complete:    
                print("Winning!!")
                print("Txn hash", router_txn.transaction.hash)
                print("Gas price", router_txn.transaction.gas_price)
                print("Sender address", router_txn.transaction.from_address)
                print("Liquidity impact", '{0:.20f}'.format(liquidity_impact))
                intercepted_transaction = True

                ##my_router_transaction = token_pair.swap_token_1_for_token_2(amount_in, amount_out, gas_price=gas_price)
                transaction_complete, transaction_successful = my_router_transaction.transaction.get_transaction_receipt(wait=True)
                print("Initial swap status", transaction_successful)
                if transaction_successful:
                    token_pair.token_2.approve_token()
                    asyncio.run(self.watch_competing_transaction(router_txn.transaction))
                    amount_out_from_token_2 = my_router_transaction.get_transaction_amount_out()
                    amount_out_from_token_1 = token_pair.get_amount_token_1_out(amount_out_from_token_2)
                    my_router_return_transaction = token_pair.swap_token_2_for_token_1(amount_out_from_token_2, amount_out_from_token_1)
                    transaction_complete, transaction_successful = my_router_return_transaction.transaction.get_transaction_receipt(wait=True)
                    if transaction_successful:
                        print("It all went swimmingly")
                    else:
                        raise StopIteration(f"{my_router_return_transaction.transaction.hash} was not successful")


                
                print("--------")
                print("Successsful requests", self.successful_requests)
                print("Failed requests", self.failed_requests)
                print("--------")
        

        return intercepted_transaction
