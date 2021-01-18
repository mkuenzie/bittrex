from bittrex.bittrex import Bittrex
import os
from unittest import TestCase


def connect():
    return Bittrex(api_key=os.environ.get("BITTREX_API_KEY"), api_secret=os.environ.get("BITTREX_API_SECRET"))


my_bittrex = connect()


btc_candles = my_bittrex.markets_candle('BTC-USD')
print(btc_candles)