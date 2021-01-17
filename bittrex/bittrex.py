import hashlib
import hmac
import time
import requests


class Bittrex(object):
    
    def __init__(self, api_key, api_secret, api_version='v3'):
        self.apiVersion = 'v3'
        self.baseUrl = 'https://api.bittrex.com'
        self.apiKey = api_key
        self.apiSecret = api_secret

    def _getheaders(self, fullurl, content, method):
        apiContentHash = hashlib.sha512(bytearray(content,'utf-8')).hexdigest()
        apiTimestamp = str(round(time.time()*1000))
        preSignList = apiTimestamp, fullurl, method.upper(), apiContentHash
        preSign = ''.join(preSignList)
        apiSignature = hmac.new(bytearray(self.apiSecret, 'utf-8'), bytearray(preSign, 'utf-8'), hashlib.sha512).hexdigest()
        headers = {
            'API-Key': self.apiKey,
            'API-Timestamp': apiTimestamp,
            'API-Content-Hash': apiContentHash,
            'API-Signature': apiSignature
        }
        return headers

    def _apicall(self, route, content='', method='GET'):
        full_url = self.baseUrl + '/' + self.apiVersion + '/' + route
        headers = self._getheaders(full_url, content, method)
        response = getattr(requests, method.lower())(full_url, headers=headers, data=content)
        return response

    def balances(self):
        r = self._apicall('balances')
        return r
        
        

