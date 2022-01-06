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
    "XRP",
    #"USDT",
    #"USDC",
    #"UNI",
    #"MATIC",
    #"SCAR",
    #"FLOKI"

]

bep20_all_tokens = bep20_tokens.copy()
bep20_all_tokens.update(bep20_base_tokens)


polygon_tokens = {
    #"AAVE" : "0xd6df932a45c0f255f85145f286ea0b292b21c90b",
    #"ATOM": "0xac51c4c48dc3116487ed4bc16542e27b5694da1b",
    #"AVAX": "0x2C89bbc92BD86F8075d1DEcc58C7F4E0107f286b",
    #"LUNA": "0x24834bbec7e39ef42f4a75eaf8e5b6486d3f0e57",
    "WETH": "0x7ceb23fd6bc0add59e62ac25578270cff1b9f619",
    "WMATIC": "0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270",
    "LINK": "0x53e0bca35ec356bd5dddfebbd1fc0fd03fabad39",
    "QUICK": "0x831753dd7087cac61ab5644b308642cc1c33dc13",
    "WBTC": "0x1bfd67037b42cf73acf2047067bd4f2c47d9bfd6",
    "TEL": "0xdf7837de1f2fa4631d716cf2502f8b230f1dcc32",
    "UNI": "0xb33eaad8d922b1083446dc23f610c2567fb5180f",
    #"USDT": "0xc2132d05d31c914a87c6611c10748aeb04b58e8f",
    #"MANA": "0xa1c57f48f0deb89f569dfbe6e2b7f46d33606fd4",
    #"SAND": "0xBbba073C31bF03b8ACf7c28EF0738DeCF3695683"
    
}
polygon_base_tokens = {
    "USDC": "0x2791bca1f2de4661ed88a30c99a7a9449aa84174",
    "USDT": "0xc2132d05d31c914a87c6611c10748aeb04b58e8f",
    "WMATIC": "0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270",
    "DAI": "0x8f3cf7ad23cd3cadbd9735aff958023239c6a063"
}

polygon_all_tokens = polygon_tokens.copy()
polygon_all_tokens.update(polygon_base_tokens)

velas_tokens = {
    "WAG" : "0xaBf26902Fd7B624e0db40D31171eA9ddDf078351",
    "WVLX" : "0xc579D1f3CF86749E05CD06f7ADe17856c2CE3126",
    "VLXPAD": "0xa065e0858417Dfc7abC6f2BD4D0185332475C180",
    "SCAR": "0x8d9fB713587174Ee97e91866050c383b5cEE6209",
    #"ETH": "0x85219708c49aa701871Ad330A94EA0f41dFf24Ca",
    #"ASTRO": "0x72eB7CA07399Ec402c5b7aa6A65752B6A1Dc0C27",
    #"SWAPZ": "0x9b6fbF0ea23faF0d77B94d5699B44062e5E747Ac"
}
velas_base_tokens = {
    "BUSD" : "0xc111c29A988AE0C0087D97b33C6E6766808A3BD3",
    "USDC": "0xe2C120f188eBd5389F71Cf4d9C16d05b62A58993",
    "USDT": "0x01445C31581c354b7338AC35693AB2001B50b9aE"
}
all_velas_tokens = velas_tokens.copy()
all_velas_tokens.update(velas_base_tokens)
