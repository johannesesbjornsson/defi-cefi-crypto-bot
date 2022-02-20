from eth_fork_transaction import Transaction, RouterTransaction
from eth_fork_token import Token

class Account(object):

    def __init__(self, client, address):
        if address == "0x0000000000000000000000000000000000000000":
            raise ValueError("Address cannot be '0x0000000000000000000000000000000000000000'")
        self.client = client
        self.address = self.client.web3.toChecksumAddress(address)
        self.set_token_balances()
        self.txn_list, self.router_txn_list =  self.get_latest_txns()

    def __str__(self):
        return self.address

    def set_token_balances(self):
        token_balances = {}
        for base_token in self.client.base_tokens:
            token = Token(self.client, base_token, "live")
            token_balances[token.address] = token.get_token_balance()
        
        self.token_balances = token_balances

    def get_transaction_count(self):
        transaction_count = self.client.web3.eth.get_transaction_count(self.address)
        return transaction_count

    def get_latest_txns(self):
        txn_list = []
        router_txn_list = []
        response_code, response_json  = self.client.get_account_transaction(self.address)
        if response_code == 200:
            for txn_raw in response_json["result"]:
                txn_raw["to"] = self.client.web3.toChecksumAddress(txn_raw["to"])
                txn = Transaction(self.client,txn_raw)
                txn_list.append(txn_list)
                if txn.to == self.client.router_contract_address:
                    router_txn = RouterTransaction(txn)
                    router_txn_list.append(router_txn)

        return txn_list, router_txn_list

    def get_next_txn(self, txn):
        next_txn = txn
        for router_txn in reversed(self.router_txn_list):
            if router_txn.transaction.nonce > txn.nonce:
                next_txn = router_txn.transaction
                break
        return next_txn

        
