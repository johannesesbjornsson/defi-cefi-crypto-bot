import os


bsc_scan_api_key = os.environ['bsc_scan_api_key']
my_bep20_address=os.environ['my_bep20_address']
private_key=os.environ['private_key']


bep20_tokens = {
    "CAKE" : "0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82",
    "BAKE" : "0xe02df9e3e622debdd69fb838bb799e3f168902c5",
    "MATIC": "0xcc42724c6683b7e57334c4e856f4c9965ed682bd",
    "SCAR" : "0x8d9fb713587174ee97e91866050c383b5cee6209"
}
bep20_base_tokens = {
    "BUSD" : "0xe9e7cea3dedca5984780bafc599bd69add087d56",
    "WBNB": "0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c",
    "USDT": "0x55d398326f99059ff775485246999027b3197955",
    "USDC": "0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d"
}

bep20_tokens_to_check = [
    "WBNB",
    "CAKE",
    "LINK",
    "DOT",
    "ADA",
    "ETH",
    "DOGE",
    "XRP",
    "USDT",
    "USDC",
    "UNI",
    "MATIC",
    #"SCAR",
    #"FLOKI"

]

bep20_all_tokens = bep20_tokens.copy()
bep20_all_tokens.update(bep20_base_tokens)


polygon_tokens = {
    "AAVE" : "0xd6df932a45c0f255f85145f286ea0b292b21c90b",
    "ATOM": "0xac51c4c48dc3116487ed4bc16542e27b5694da1b",
    "AVAX": "0x2C89bbc92BD86F8075d1DEcc58C7F4E0107f286b",
    "LUNA": "0x24834bbec7e39ef42f4a75eaf8e5b6486d3f0e57",
    "WETH": "0x7ceb23fd6bc0add59e62ac25578270cff1b9f619",
    "WMATIC": "0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270",
    "LINK": "0x53e0bca35ec356bd5dddfebbd1fc0fd03fabad39",
    "QUICK": "0x831753dd7087cac61ab5644b308642cc1c33dc13",
    "WBTC": "0x1bfd67037b42cf73acf2047067bd4f2c47d9bfd6",
    "TEL": "0xdf7837de1f2fa4631d716cf2502f8b230f1dcc32",
    "USDT": "0xc2132d05d31c914a87c6611c10748aeb04b58e8f",
    
}
polygon_base_tokens = {
    "USDC": "0x2791bca1f2de4661ed88a30c99a7a9449aa84174",
    "USDT": "0xc2132d05d31c914a87c6611c10748aeb04b58e8f",
    "WMATIC": "0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270",
}

polygon_tokens_extra_decimals = {
    "USDC" : 1000000000000,
    "USDT" : 1000000000000,
    "ATOM" : 1000000000000,
    "WBTC" : 1000000000000,
    "TEL" : 1000000000000
}

polygon_all_tokens = polygon_tokens.copy()
polygon_all_tokens.update(polygon_base_tokens)