from bittrex.bittrex import Bittrex
import os
from unittest import TestCase


def connect():
    return Bittrex(api_key=os.environ.get("BITTREX_API_KEY"), api_secret=os.environ.get("BITTREX_API_SECRET"))


my_bittrex = connect()


ticker = my_bittrex.markets_ticker('BTC-USD')
last_trade = float(ticker['lastTradeRate'])
budget = 50
quantity = round(budget / last_trade, 8)

buy_order = my_bittrex.buy(market_symbol='BTC-USD', quantity=quantity)
print(buy_order)
#sell_order = my_bittrex.sell('BTC-USD')