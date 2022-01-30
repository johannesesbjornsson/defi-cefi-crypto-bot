from web3 import Web3

bsc = "https://bsc-dataseed.binance.org/"
#bsc = "https://data-seed-prebsc-1-s1.binance.org:8545"
web3 = Web3(Web3.HTTPProvider(bsc))
price =  1 
price =   5000000000
#amount = web3.fromWei(price,'ether')
amount = web3.fromWei(price,'gwei')
#amount = web3.toWei(price,'ether')
print(amount)
print(web3.fromWei(1525647347,'gwei'))
# Hexstrings https://web3py.readthedocs.io/en/stable/web3.main.html

#1 -> 1000000000000000000
print(web3.toHex(text='(<Function token1()>, {})'))