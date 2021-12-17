import sys
sys.path.insert(0,'../libraries')
from pancakeswap_client import Client

class Arbitrage(object):

    def __init__(self, client, token_0, token_1, token_2, from_range=[20,50], debug_mode=False):
        if type(client) != Client:
            raise ValueError("Argument must be object type Client")
        self.client = client
        self.debug_mode = debug_mode
        self.token_0 = token_0
        self.token_1 = token_1
        self.token_2 = token_2
        self.from_range = from_range
        self.token_0_hash = self.client.known_tokens[token_0]
        self.token_1_hash = self.client.known_tokens[token_1]
        self.token_2_hash = self.client.known_tokens[token_2]


    def get_sequence_amount_out(self, amount_in, sequence):
        for pair in sequence:
            from_token = pair["from_token"]
            to_token = pair["to_token"]
            amount_out = self.client.get_token_amount_out(from_token,to_token,amount_in)
            if amount_out is None:
                return 0
            amount_in = amount_out
        return amount_out


    def find_arbitrage(self):
        self.available_arbitrage = None
        self.initial_swap_amount = None
        minimal_initial_offset = self.client.web3.toWei(self.from_range[0] * 1.02,'ether')
        found_arbitrage = False

        potential_arbitrage = {
            "option_1" : [
                {"from_token": self.token_0, "to_token": self.token_1 },
                {"from_token": self.token_1, "to_token": self.token_2 },
                {"from_token": self.token_2, "to_token": self.token_0 }
            ],
            "option_2" : [
                {"from_token": self.token_0, "to_token": self.token_2 },
                {"from_token": self.token_2, "to_token": self.token_1 },
                {"from_token": self.token_1, "to_token": self.token_0 }
            ]
        }

        for option in potential_arbitrage:
            initial_swap_amount = self.client.web3.toWei(self.from_range[0],'ether')
            amount_out = self.get_sequence_amount_out(initial_swap_amount,potential_arbitrage[option])
            max_profit = amount_out - initial_swap_amount

            if amount_out > minimal_initial_offset:
                self.available_arbitrage = potential_arbitrage[option]
                found_arbitrage = True
                optimal_swap_amount = initial_swap_amount
                
                # Finding the optimal amount to buy
                for starting_option in range(self.from_range[0]+1,self.from_range[1]):
                    initial_swap_amount = self.client.web3.toWei(starting_option,'ether')
                    amount_out = self.get_sequence_amount_out(initial_swap_amount,potential_arbitrage[option])
                    profit = amount_out - initial_swap_amount
                    
                    if profit > max_profit:
                        optimal_swap_amount = initial_swap_amount
                        max_profit = profit
                        
                    else:
                        break
                self.initial_swap_amount = optimal_swap_amount

                print(self.available_arbitrage)
                print("Profit", self.client.web3.fromWei(max_profit,'ether'))
                print("Intial Swap sum", self.client.web3.fromWei(initial_swap_amount,'ether'))
                print("--------------------------------------------")

        return found_arbitrage

        
        
    def execute_arbitrage(self):
        from_token_amount = self.initial_swap_amount
        for pair in self.available_arbitrage:
            if self.debug_mode:
                print("Execute order on pair", pair)
            from_token = pair["from_token"]
            to_token = pair["to_token"]
            
            self.client.approve_token(from_token)
            self.client.approve_token(to_token)

            to_token_amount = self.client.get_token_amount_out(from_token=from_token,to_token=to_token, from_token_amount=from_token_amount)
            transaction_hash, order = self.client.execute_buy_order(from_token, to_token, from_token_amount, to_token_amount)
            if self.debug_mode:
                print(order)
            data = self.client.get_transaction_final_data(transaction_hash)
            if data["amount0Out"] != 0:
                from_token_amount = data["amount0Out"]
            elif data["amount1Out"] != 0:
                from_token_amount = data["amount1Out"]
        