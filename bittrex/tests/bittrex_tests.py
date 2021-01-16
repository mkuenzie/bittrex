import bittrex, os
from unittest import TestCase

def connect():
    mybittrex = bittrex(os.environ.get("BITTREX_API_KEY"), os.environ.get("BITTREX_API_SECRET"))
    return mybittrex

