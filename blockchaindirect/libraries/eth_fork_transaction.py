import contract_libarary

from web3.logs import STRICT, IGNORE, DISCARD, WARN
from web3.exceptions import ContractLogicError, TransactionNotFound, TimeExhausted
import re
import time

class Transaction(object):
    def __init__(self, client, transaction_info=None):
        self.client = client
        if transaction_info:
            self.hash = self.client.web3.toHex(transaction_info["hash"])
            self.block_number = transaction_info["blockNumber"]
            self.gas_limit = transaction_info["gas"]
            self.gas_price = transaction_info["gasPrice"]
            self.input = transaction_info["input"]
            self.nonce = transaction_info["nonce"]
            self.to = transaction_info["to"]
            self.from_address = transaction_info["from"]
        else:
            self.hash = ""


    def __str__(self):
        return self.hash

    def __eq__(self, other_transaction):
        if (isinstance(other_transaction, Transaction)):
            return self.nonce == other_transaction.nonce and self.from_address == other_transaction.from_address
        return False

    def get_transaction_receipt(self, wait=True):
        transaction_receipt = None
        transaction_successful = None
        transaction_complete = False

        if wait:
            try:
                transaction_receipt = self.client.web3.eth.wait_for_transaction_receipt(self.hash)
                transaction_complete = True
                transaction_successful = transaction_receipt["status"]
            except TimeExhausted as e:
                transaction_complete = False
        else:
            try:
                transaction_receipt = self.client.web3.eth.get_transaction_receipt(self.hash)
                transaction_complete = True
                transaction_successful = transaction_receipt["status"]
            except TransactionNotFound as e:
                transaction_complete = False
        
        if transaction_successful == 0:
            transaction_successful = False
        elif transaction_successful == 1:
            transaction_successful = True

        self.successful = transaction_successful
        self.complete = transaction_complete
        self.receipt = transaction_receipt

        return transaction_complete, transaction_successful

    def create_transaction(self, transaction, gas_price=None):
        if gas_price is None:
            #gas_price = self.client.default_gas_price
            gas_price = self.client.web3.eth.gas_price
            if gas_price > self.client.max_gas_price:
                raise ValueError(f"Gas prices are currently to expensive: {gas_price}")

        self.nonce = self.client.web3.eth.get_transaction_count(self.client.my_address)
        self.gas_limit = self.client.default_gas_limit
        self.gas_price = gas_price
        self.from_address = self.client.my_address
        self.built_transaction = transaction

    def sign_and_send_transaction(self):
        built_txn = self.built_transaction.buildTransaction({
                'from': self.from_address,
                'value': 0,
                'gas': self.gas_limit, 
                'gasPrice': self.gas_price,
                'nonce': self.nonce,
            })

        signed_txn = self.client.web3.eth.account.sign_transaction(built_txn, private_key=self.client.private_key)
        txn_hash = self.client.web3.eth.send_raw_transaction(signed_txn.rawTransaction)

        for i in range(10):
            time.sleep(0.2)
            try: 
                transaction_info = self.client.web3.eth.get_transaction(txn_hash)
                break
            except TransactionNotFound as e:
                transaction_info = None

        self.hash = self.client.web3.toHex(txn_hash) 
        self.block_number = transaction_info["blockNumber"]
        self.to = transaction_info["to"]
        self.input = transaction_info["input"]

        return transaction_info

class RouterTransaction(Transaction):
    def __init__(self, transaction):
        self.client = transaction.client
        self.transaction = transaction
        txn_input = self.client.router_contract.decode_function_input(self.transaction.input)

        function_called = re.search("^<Function ([^\(]*)", str(txn_input[0]))
        if function_called:
          self.function_called = function_called.group(1)
        else:
          self.function_called =  txn_input[0]

        if "path" in txn_input[1]:
            self.path = txn_input[1]["path"]
        else:
            self.path = None

        if "amountIn" in txn_input[1]:
            self.amount_in = txn_input[1]["amountIn"]
        elif "amountInMax" in txn_input[1]:
            self.amount_in = txn_input[1]["amountInMax"]
        else:
            self.amount_in = None

        if "amountOut" in txn_input[1]:
            self.amount_out = txn_input[1]["amountOut"]
        elif "amountOutMin" in txn_input[1]:
            self.amount_out = txn_input[1]["amountOutMin"]
        else:
            self.amount_out = None

        self.input_data = txn_input[1]


    def __str__(self):
        return self.transaction.hash

    def get_transaction_amount_out(self):
        if not self.transaction.successful:
            raise LookupError(f"Transaction '{self.transaction.hash}' was not successful")

        log_location_index = self.client.swap_log_location_index

        tx_dict = dict(self.transaction.receipt)
        data = tx_dict["logs"][log_location_index]["data"]
        address = tx_dict["logs"][log_location_index]["address"]
        
        address = self.client.web3.toChecksumAddress(address)
        
        abi=contract_libarary.standard_contracts["liquidity_pool"]

        contract = self.client.web3.eth.contract(address=address, abi=abi)
        events = contract.events.Swap().processReceipt(self.transaction.receipt,errors=IGNORE)
        decoded_data = dict(dict(list(events)[log_location_index])["args"])

        if decoded_data["amount0Out"] != 0:
            amount_out = decoded_data["amount0Out"]
        elif decoded_data["amount1Out"] != 0:
            amount_out = decoded_data["amount1Out"]
        return amount_out