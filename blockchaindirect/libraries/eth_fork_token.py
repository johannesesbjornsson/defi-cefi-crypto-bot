import contract_libarary
import token_config
from web3.logs import STRICT, IGNORE, DISCARD, WARN
from web3.exceptions import ContractLogicError, TransactionNotFound
import re

class Token(object):

    def __init__(self, client, token, use_standard_contracts=True):
        self.known_tokens = client.known_tokens
        self.client = client

        try:
            self.address = self.client.web3.toChecksumAddress(token)
            self.name = "Uknown"
        except ValueError as e:
            self.address = self.client.web3.toChecksumAddress(self.known_tokens[token])
            self.name = token

        if use_standard_contracts:
            self.token_contract = self.client.web3.eth.contract(
                address=self.address, 
                abi=contract_libarary.standard_contracts["token"])
        else:
            self.abi = self.client.get_abi(self.address)
            self.token_contract = self.client.web3.eth.contract(address=self.address, abi=self.abi)
            self.set_proxy_details()

        self.symbol = self.token_contract.functions.symbol().call()
        self.allowance_on_router =  self.token_contract.functions.allowance(self.client.my_address,self.client.router_contract_address).call()
        self.decimals = self.token_contract.functions.decimals().call()
    
    def __str__(self):
        return self.address

    def set_proxy_details(self):
        is_proxy = False
        token_contract = self.token_contract

        if "proxyType" in dir(token_contract.functions):
            proxy_contract_address = token_contract.functions.implementation().call()
            proxy_abi  = self.client.get_abi(proxy_contract_address)
            proxy_contract = self.client.web3.eth.contract(address=self.address, abi=proxy_abi)
            
            token_contract = proxy_contract
            is_proxy = True

        self.is_proxy =  is_proxy
        self.token_contract = token_contract

    def approve_token(self):
        if self.allowance_on_router == 0:
            value = self.client.web3.toWei(2**64-1,'ether')
            txn = self.token_contract.functions.approve(self.client.router_contract_address,value)
            transaction_receipt = self.client.sign_and_send_transaction(txn)

            self.allowance_on_router =  self.token_contract.functions.allowance(self.client.my_address,self.client.router_contract_address).call()

        return True

    def to_wei(self, n):
        wei = n * ( 10 ** self.decimals)
        return int(wei)

    def from_wei(self, n):
        non_wei = n / ( 10 ** self.decimals)
        return float(non_wei)


class Transaction(object):
    def __init__(self, client, transaction_info):
        self.client = client
        self.hash = self.client.web3.toHex(transaction_info["hash"])
        self.block_number = transaction_info["blockNumber"]
        self.gas = transaction_info["gas"]
        self.gas_price = transaction_info["gasPrice"]
        self.input = transaction_info["input"]
        self.nonce = transaction_info["nonce"]
        self.to = transaction_info["to"]

    def __str__(self):
        return self.hash

    def get_transaction_receipt(self, wait=True):
        transaction_receipt = None
        transaction_successful = None
        transaction_complete = False

        if wait:
            transaction_receipt = self.client.web3.eth.wait_for_transaction_receipt(self.hash)
            transaction_complete = True
            transaction_successful = transaction_receipt["status"]
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

        return transaction_complete

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

        self.input_data = txn_input[1]


    def __str__(self):
        return self.transaction.hash

    def get_transaction_amount_out(self, client, transaction):
        if not self.transaction.successful:
            raise LookupError(f"Transaction '{self.transaction.successful}' was not successful")

        if self.client.blockchain == "polygon":
            log_location_index = -2
        elif self.client.blockchain == "bsc":
            log_location_index = -1

        tx_dict = dict(self.transaction.receipt)
        data = tx_dict["logs"][log_location_index]["data"]
        address = tx_dict["logs"][log_location_index]["address"]
        
        address = self.client.web3.toChecksumAddress(address)
        abi = self.client.get_abi(address)
        contract = self.client.web3.eth.contract(address=address, abi=abi)
        events = contract.events.Swap().processReceipt(self.transaction.receipt,errors=IGNORE)
        decoded_data = dict(dict(list(events)[log_location_index])["args"])

        if decoded_data["amount0Out"] != 0:
            amount_out = decoded_data["amount0Out"]
        elif decoded_data["amount1Out"] != 0:
            amount_out = decoded_data["amount1Out"]
        return amount_out