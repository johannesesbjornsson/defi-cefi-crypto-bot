import os


bsc_scan_api_key = os.environ['bsc_scan_api_key']
my_bep20_address=os.environ['my_bep20_address']
private_key=os.environ['private_key']


tokens = {
    "CAKE" : "0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82",
    "BAKE" : "0xe02df9e3e622debdd69fb838bb799e3f168902c5",
    #Cant use these
    #"SXP" : "0x47bead2563dcbf3bf2c9407fea4dc236faba485a",
    #"VLX" : "0xE9C803F48dFFE50180Bd5B01dC04DA939E3445Fc",
    #"PLSPAD" : "0x8a74bc8c372bc7f0e9ca3f6ac0df51be15aec47a",
    #"SCAR" : "0x8d9fb713587174ee97e91866050c383b5cee6209"
}
base_tokens = {
    "BUSD" : "0xe9e7cea3dedca5984780bafc599bd69add087d56",
    "WBNB": "0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c"
}

all_tokens = tokens.copy()
all_tokens.update(base_tokens)