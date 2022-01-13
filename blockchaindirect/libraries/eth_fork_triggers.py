import contract_libarary
import time
import token_config
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
        self.scan_token_value = self.client.scan_token_value
        self.token_1 = Token(self.client,self.token_to_scan_for)
        self.client.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        #eth_newPendingTransactionFilter
        self.tx_filter = self.client.web3_ws.eth.filter('pending')

    def handle_swap_transaction(self, gas_price, router_txn):
        token_pair = None
        amount_in = None
        amount_out = None
        my_gas_price = None
        try:
            input_token, out_token = router_txn.path[-2:]
            if input_token == self.token_to_scan_for:
                token_2 = Token(self.client,out_token)
                token_pair = TokenPair(self.client, self.token_1, token_2)

            else:
                token_pair = None
        except ValueError as e:
            token_pair = None
        
        if token_pair:
            if len(router_txn.path) == 2 and router_txn.amount_in:
                txn_amount = self.token_1.from_wei(router_txn.amount_in)
                liquidity_impact = token_pair.get_liquidity_impact_of_token_1_for_token_2(txn_amount)
            elif router_txn.amount_out:
                txn_amount = self.token_1.from_wei(token_pair.get_amount_token_1_out(router_txn.amount_out))
                liquidity_impact = token_pair.get_liquidity_impact_of_token_1_for_token_2(txn_amount)
            else: 
                txn_amount = 0
                liquidity_impact = 0

            #if txn_amount > self.minimum_scanned_transaction:
            if liquidity_impact > 0.005:
                print("Transaction value:", liquidity_impact)
                print("Liquidty impact ",txn_amount)
                amount_in = self.token_1.to_wei(self.scan_token_value)
                amount_out = token_pair.get_amount_token_2_out(amount_in)
                my_gas_price = gas_price + self.client.web3.toWei('2','gwei')

        return token_pair, amount_in, amount_out, my_gas_price


    async def fetch_single_transaction(self, transaction, compare_transaction=None):
        #start = time.perf_counter()
        router_txn = None
        if isinstance(transaction, str):
            transaction_hash = transaction
        else:
            transaction_hash = self.client.web3.toHex(transaction)

        try:
            transaction_info = await self.client.web3_asybc.eth.get_transaction(transaction_hash)
            self.successful_requests += 1
            txn = Transaction(self.client, transaction_info)
            if not compare_transaction and txn.to == self.client.router_contract_address and txn.block_number is None and txn.gas_price > self.client.web3.toWei('29','gwei'):
                router_txn = RouterTransaction(txn)
            elif compare_transaction and compare_transaction == txn:
                router_txn = txn
        except TransactionNotFound as e:
            self.failed_requests += 1
            txn = None
        except gaierror as e:
            #print("Socker error")
            self.failed_requests += 1
            txn = None
        except ClientConnectorError as e:
            self.failed_requests += 1
            #print("Network error")
            txn = None
        except ClientResponseError as e:
            self.failed_requests += 1
            txn = None
        except TimeoutError as e:
            self.failed_requests += 1
            txn = None
        #end = time.perf_counter()
        #print("Time elapsed",end - start)  
        return router_txn
        
    async def get_router_contract_interactions(self, pending_transactions):
        pending_router_transactions = []
        
        if len(pending_transactions) == 0:
            return []

        done, pending = await asyncio.wait(
            [self.fetch_single_transaction(arg,compare_transaction=None) for arg in pending_transactions]
        )
        for result in done:
            router_txn = result.result()
            if not router_txn:
                continue
            if router_txn.function_called.startswith("swap"):
                pending_router_transactions.append(router_txn)
        return pending_router_transactions


    async def watch_competing_transaction(self, transaction):
        transaction_complete, transaction_successful = transaction.get_transaction_receipt(wait=False)
        time_started = time.time()
        while transaction_complete != True and 360 < time.time() - time_started:
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
                print(txn.hash)
                print(txn.gas)
                
            
            
            print("wathcing....", time.time() - time_started)
            time.sleep(5)
            transaction_complete, transaction_successful = transaction.get_transaction_receipt(wait=False)
    
        return transaction_complete, transaction_successful

    def intercept_transactions(self):
        #eth_newPendingTransactionFilter
        #tx_filter = self.client.web3_ws.eth.filter('pending')
        intercepted_transaction = False

        
        print("Taking a wee break")
        time.sleep(0.2)

        pending_transactions = self.tx_filter.get_new_entries()

        pending_router_transactions = asyncio.run(self.get_router_contract_interactions(pending_transactions))



        for router_txn in pending_router_transactions:
            start = time.perf_counter()
            token_pair, amount_in, amount_out, gas_price = self.handle_swap_transaction(router_txn.transaction.gas_price, router_txn)
            if not token_pair or not amount_in or not amount_out or not gas_price:
                continue

    
            
            #txn =  asyncio.run(self.fetch_single_transaction(router_txn.transaction.hash))
            #if not txn:
            #    continue

            end = time.perf_counter()
            print("Time elapsed",end - start)  

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
                print("Raw input data", router_txn.function_called, router_txn.input_data)
                intercepted_transaction = True

                
    
                #asyncio.run(self.watch_competing_transaction(router_txn.transaction))

                my_router_transaction = token_pair.swap_token_1_for_token_2(amount_in, amount_out, gas_price=gas_price)
                transaction_complete, transaction_successful = my_router_transaction.transaction.get_transaction_receipt(wait=True)
                if transaction_successful:
                    #txn =  asyncio.run(self.fetch_single_transaction(router_txn.transaction.hash))
                    token_pair.token_2.approve_token()

                    #transaction_complete, transaction_successful = router_txn.transaction.get_transaction_receipt(wait=True)
                    asyncio.run(self.watch_competing_transaction(router_txn.transaction))

                    amount_out_from_token_2 = my_router_transaction.get_transaction_amount_out()
                    amount_out_from_token_1 = token_pair.get_amount_token_1_out(amount_out_from_token_2)
                    token_pair.swap_token_2_for_token_1(amount_out_from_token_2, amount_out_from_token_1)
                
                print("--------")
                print("Successsful requests", self.successful_requests)
                print("Failed requests", self.failed_requests)
                print("--------")
        

        return intercepted_transaction