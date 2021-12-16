
import bsc_client
import cfg as cfg
import itertools

client = bsc_client.Client(cfg.my_bep20_address, cfg.private_key, cfg.bsc_scan_api_key)

lists = list(itertools.combinations(client.tokens_to_check, 2))
#lists = list(itertools.combinations(cfg.tokens.keys(), 2))
lists = [
    ["FLOKI","XRP"]
]
debug_mode = True
from_range = [2, 4]
for li in lists:
    token_0 = "BUSD"
    token_1 = li[0]
    token_2 = li[1]
    #print("Checking",token_0, token_1, token_2 )
    client.test("FLOKI")
    client.test("CAKE")
    
    #arbitrage = bsc_client.Arbitrage(client=client,token_0=token_0,token_1=token_1,token_2=token_2,from_range=from_range, debug_mode=debug_mode)
    #found_arbitrage =  arbitrage.find_arbitrage()
    #if found_arbitrage:
    #    arbitrage.execute_arbitrage()

    
    # ------------------- Hepful transactions -------------------
    #  IMPORTANT: Need to enable token->token for each pair
    #
    #Approve a contract: 0x700eed1e9386214f1967db7df390276535309b85fa890471de800fbe1bfca6d8
    #VLX -> to CAKE : 0x8323d05365136928f4a404ca2b2f6081355fd75ca63cb93759ff88e00c5812b1
    #BUSD -> BAKE (python): 0x17299def9e8922f5fba890623de5590a23735c39f2a529c0fe72737abb122779
    #BUSD -> VLX (python): 0x9c5e9f5621a1bb5f479535448b9fbea1e4a592c05766155ec521223f7b8bf4a1
    #BAKE -> CAKE (python): 0xcdde2e6e068aebc0d9fa662c68445f45cac69f4fbb2c7ee47d017b3e76eed88c
    #BUSD -> ADA (python): 0x87c3a4d71b833754f344429ed2eb0f3f5194878d6c0b8e7b3747d2e3cb162095
    #CAKE -> BAKE: 0xa41e6f834b091e3dfaa4daa1c22759b9c9b0fe5cac27668b382982cf4eaf3a43
    
    