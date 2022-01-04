#https://medium.com/coinmonks/python-scripts-for-ccxt-crypto-candlestick-ohlcv-charting-data-83926fa16a13wave
#%%
# import json
import ccxt
import os
import pandas as pd

PublicKey = os.environ.get('WavesPublicKey')
PrivateKey = os.environ.get('WavesPrivateKey')

we = ccxt.wavesexchange({
    'rateLimit': 1000,
    'enableRateLimit': True,
    'apiKey': PublicKey,
    'secret': PrivateKey,
})

#------------------- END IMPORTS ----------------------------
#%%
print("WAVES EXCHANGE")
print()
#-------------------- PRELOAD DATA -------------------
we.load_markets() #Preload list of markets and currencies and caches the info into .markets, .symbol, and .currency
we.load_markets(reload=False)
# Create DF from  dictionaries
#we.verbose = True
df_currencies = pd.DataFrame(list(we.currencies))
df_symbols = pd.DataFrame(list(we.symbols),columns=['SYMBOL'])
# Clean up balance df
balance = we.fetch_balance()
print(balance)
df_balance = pd.DataFrame(we.fetch_balance(),columns=['used','free','total'])
df_balance.index.name = 'coin'
df_balance.reset_index(inplace=True)
df_balance['symbol'] = ''
df_balance['price'] = ""
df_balance['value'] = ""
df_balance
base = 'USDN'
#%%
## ----- CREATE ACCOUNT BALANCE DF
# FUNCTION TO FIND SYMBOL FOR ASSET
def symbol_pair(fsymbol):
    pairlength = len(base) + len(fsymbol) +1
    df_symbols_fsymbol = df_symbols[df_symbols['SYMBOL'].str.contains(fsymbol)]# Reduce symbol list to only containing fsymbol
    df_shortlist = df_symbols_fsymbol[df_symbols_fsymbol['SYMBOL'].str.contains(base)]# Reduce symbol list further to only base_currency fsymbol pairs
    asset_symbol = 'no go'
    if df_shortlist.size >= 1:
        for int in df_shortlist.index:#Cycle through each item by index
            symbol_index = df_shortlist['SYMBOL'][int]#assign current symbol to variable
            if len(symbol_index) == pairlength:#if same length as symbol we are looking for keep it
                asset_symbol = symbol_index
    if fsymbol == base:
        asset_symbol = base
    return asset_symbol

# FUNCTION - GET BID PRICE FROM SYMBOL PAIR
def symbol_price(fsymbolpair):
    try:
        ticker = we.fetch_order_book(fsymbolpair)
        bidlist = ticker['bids'][0]
        bid = bidlist[0]
    except:
        bid = 0
        print('Symbol Error')
    return bid

#%%
#--------- ADD SYMBOL AND PRICE COLUMN
for int in df_balance.index:
    coinrow = df_balance['coin'][int]
    symbolpair = symbol_pair(coinrow)
    if symbolpair == coinrow:
        symbolprice = 1
    else:
        symbolprice = symbol_price(symbolpair)
    df_balance.at[int,'used'] = round(df_balance['used'][int],4)
    df_balance.at[int,'free'] = round(df_balance['free'][int],4)
    df_balance.at[int,'total'] = round(df_balance['total'][int],4)
    df_balance.at[int,'symbol'] = symbolpair
    df_balance.at[int,'price'] = round(symbolprice,3)
    df_balance.at[int,'value'] = round(df_balance['price'][int] * df_balance['total'][int],2)
pd.set_option('display.max_rows', 10)
print(df_balance)
total = round(df_balance['value'].sum(),2)
print('--------------------------------------------------------------------------------')
print()
print('Total :',total)
print()
print()
print()
input('Click Any Key')
# %%
y