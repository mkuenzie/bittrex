import hashlib
import hmac
import time
import requests
import json
from enum import Enum
from datetime import timedelta


class CandleInterval(Enum):
    MINUTE_1 = timedelta(minutes=1)
    MINUTE_5 = timedelta(minutes=5)
    HOUR_1 = timedelta(hours=1)
    DAY_1 = timedelta(days=1)


valid_times = 'FILL_OR_KILL', 'IMMEDIATE_OR_CANCEL', 'GOOD_TIL_CANCELLED', 'POST_ONLY_GOOD_TIL_CANCELLED'
valid_market_ceiling_times = valid_times[0:2]
valid_order_types = 'MARKET', 'LIMIT'


def _decode_json_bytes(json_bytes):
    json_content_str = json_bytes.content.decode('utf-8')
    return json.loads(json_content_str)


class CachedResponse(object):
    def __init__(self, sequence_num, value):
        self.value = value
        self.sequence_num = sequence_num


class Bittrex(object):

    def __init__(self, api_key, api_secret, api_version='v3'):
        self.apiVersion = 'v3'
        self.baseUrl = 'https://api.bittrex.com'
        self.apiKey = api_key
        self.apiSecret = api_secret
        self.cache = {}

    def _getheaders(self, fullurl, content, method):
        apiContentHash = hashlib.sha512(bytearray(content, 'utf-8')).hexdigest()
        apiTimestamp = str(round(time.time() * 1000))
        preSignList = apiTimestamp, fullurl, method.upper(), apiContentHash
        preSign = ''.join(preSignList)
        apiSignature = hmac.new(bytearray(self.apiSecret, 'utf-8'), bytearray(preSign, 'utf-8'),
                                hashlib.sha512).hexdigest()
        headers = {
            'API-Key': self.apiKey,
            'API-Timestamp': apiTimestamp,
            'API-Content-Hash': apiContentHash,
            'API-Signature': apiSignature
        }
        return headers

    def _cache(self, endpoint):
        r = self._api(endpoint, method='HEAD')
        sequence_num = int(r.headers['Sequence'])
        if endpoint in self.cache:
            cached_value = self.cache[endpoint]
            if cached_value.sequence_num >= sequence_num:
                return cached_value.value
        r = self._api(endpoint)
        sequence_num = int(r.headers['Sequence'])
        value = _decode_json_bytes(r)
        self.cache[endpoint] = CachedResponse(sequence_num, value)
        return value

    def _api(self, route, content='', method='GET', auth_required=False, success_status=200):
        full_url = self.baseUrl + '/' + self.apiVersion + '/' + route
        if auth_required:
            headers = self._getheaders(full_url, content, method)
            if content != '':
                headers['Content-Type'] = 'application/json'
            response = getattr(requests, method.lower())(full_url, headers=headers, data=content)
        else:
            response = getattr(requests, method.lower())(full_url, data=content)

        if response.status_code == success_status:
            return response
        else:
            raise Exception("You haven't implemented error handling!")

    def balances(self, currency_symbol=''):
        if currency_symbol != '':
            endpoint = 'balances/' + currency_symbol
        else:
            endpoint = 'balances'
        r = self._api(endpoint, auth_required=True)
        return _decode_json_bytes(r)

    def currencies(self, symbol=''):
        if symbol != '':
            endpoint = 'currencies/' + symbol
        else:
            endpoint = 'currencies'
        r = self._api(endpoint)
        return _decode_json_bytes(r)

    def markets(self, market_symbol=''):
        if market_symbol == '':
            endpoint = 'markets'
        else:
            endpoint = 'markets/' + market_symbol
        r = self._api(endpoint)
        return _decode_json_bytes(r)

    def markets_ticker(self, market_symbol=''):
        if market_symbol == '':
            endpoint = 'markets/tickers'
        else:
            endpoint = 'markets/' + market_symbol + '/ticker'
        r = self._api(endpoint)
        return _decode_json_bytes(r)

    def markets_candle(self, market_symbol, interval=timedelta(minutes=1)):
        interval = CandleInterval(interval)
        endpoint = 'markets/' + market_symbol + '/candles/' + interval.name + '/recent'
        return self._cache(endpoint)

    def get_orders(self, id):
        endpoint = 'orders/' + id
        r = self._api(endpoint, auth_required=True)
        return _decode_json_bytes(r)

    def get_open_orders(self):
        endpoint = 'orders/open'
        r = self._api(endpoint, auth_required=True)
        return _decode_json_bytes(r)

    def get_closed_orders(self):
        endpoint = 'orders/closed'
        r = self._api(endpoint, auth_required=True)
        return _decode_json_bytes(r)

    def buy(self, market_symbol, quantity, order_type='MARKET', time_in_force='FILL_OR_KILL'):
        if time_in_force not in valid_times:
            raise ValueError(time_in_force + "is not a valid value for time_in_force")
        if order_type not in valid_order_types:
            raise ValueError(order_type + "is not a valid value for order_type")
        if order_type == 'MARKET':
            content = {'marketSymbol': market_symbol, 'direction': 'BUY', 'type': 'MARKET', 'quantity': quantity,
                       'timeInForce': time_in_force}
        r = self._api('orders', json.dumps(content), method='POST', auth_required=True, success_status=201)
        return _decode_json_bytes(r)

    def sell(self, market_symbol, quantity, order_type='MARKET', time_in_force='FILL_OR_KILL'):
        if time_in_force not in valid_times:
            raise ValueError(time_in_force + "is not a valid value for time_in_force")
        if order_type not in valid_order_types:
            raise ValueError(order_type + "is not a valid value for order_type")
        if order_type == 'MARKET':
            content = {'marketSymbol': market_symbol, 'direction': 'SELL', 'type': 'MARKET', 'quantity': quantity,
                       'timeInForce': time_in_force}
        r = self._api('orders', json.dumps(content), method='POST', auth_required=True, success_status=201)
        return _decode_json_bytes(r)
