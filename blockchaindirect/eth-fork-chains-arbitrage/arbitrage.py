import sys
sys.path.insert(0,'../libraries')
from eth_fork_client import Client

class Arbitrage(object):

    def __init__(self, client, token_pair_1, token_pair_2, token_pair_3, from_range=[20,50]):
        if type(client) != Client:
            raise ValueError("Argument must be object type Client")
        self.client = client
        self.token_pair_1 = token_pair_1
        self.token_pair_2 = token_pair_2
        self.token_pair_3 = token_pair_3
        self.from_range = from_range
        
        if self.client.blockchain == "bsc":
            self.minimum_profit = self.from_range[0] + 0.2
        elif self.client.blockchain == "polygon":
            self.minimum_profit =  self.from_range[0] #+ 0.01

    def get_sequence_1_amount_out(self, amount_in):
        amount_out = self.token_pair_1.get_amount_token_2_out(amount_in)
        amount_out = self.token_pair_2.get_amount_token_2_out(amount_out)
        amount_out = self.token_pair_3.get_amount_token_1_out(amount_out)

        return amount_out

    def get_sequence_2_amount_out(self, amount_in):
        amount_out = self.token_pair_3.get_amount_token_2_out(amount_in)
        amount_out = self.token_pair_2.get_amount_token_1_out(amount_out)
        amount_out = self.token_pair_1.get_amount_token_1_out(amount_out)
        return amount_out

    def execute_sequence_1_amount_out(self, amount_in):
        amount_out = self.token_pair_1.get_amount_token_2_out(amount_in)
        amount_in = self.token_pair_1.swap_token_1_for_token_2(amount_in,amount_out)

        amount_out = self.token_pair_2.get_amount_token_2_out(amount_out)
        amount_in = self.token_pair_2.swap_token_1_for_token_2(amount_in,amount_out)

        amount_out = self.token_pair_3.get_amount_token_1_out(amount_out)
        amount_in = self.token_pair_3.swap_token_2_for_token_1(amount_in,amount_out)
        return amount_in

    def execute_sequence_2_amount_out(self, amount_in):
        amount_out = self.token_pair_3.get_amount_token_2_out(amount_in)
        amount_in = self.token_pair_3.swap_token_1_for_token_2(amount_in,amount_out)

        amount_out = self.token_pair_2.get_amount_token_1_out(amount_out)
        amount_in = self.token_pair_2.swap_token_2_for_token_1(amount_in,amount_out)

        amount_out = self.token_pair_1.swap_token_2_for_token_1(amount_out)
        amount_in = self.token_pair_1.get_amount_token_1_out(amount_in,amount_out)

        return amount_in


    def find_arbitrage(self):
        found_arbitrage = False
        initial_swap_amount = 1

        amount_out_sequence_1 = self.get_sequence_1_amount_out(initial_swap_amount)
        amount_out_sequence_2 = self.get_sequence_2_amount_out(initial_swap_amount)

        print("amount_out_sequence_1:", amount_out_sequence_1)
        print("amount_out_sequence_2:", amount_out_sequence_2)

        if amount_out_sequence_1 > amount_out_sequence_2 and amount_out_sequence_1 > self.minimum_profit:
            found_arbitrage = True
            self.available_arbitrage = "sequence_1"
        elif amount_out_sequence_2 > amount_out_sequence_1 and amount_out_sequence_2 > self.minimum_profit:
            found_arbitrage = True
            self.available_arbitrage = "sequence_2"       


        self.initial_swap_amount = initial_swap_amount
        self.found_arbitrage = found_arbitrage
        return found_arbitrage
        
    def execute_arbitrage(self):
        
        if self.available_arbitrage == "sequence_1":
            amount_out = self.execute_sequence_1_amount_out(self.initial_swap_amount)
        elif self.available_arbitrage == "sequence_2":
            amount_out = self.execute_sequence_2_amount_out(self.initial_swap_amount)

        return amount_out


        