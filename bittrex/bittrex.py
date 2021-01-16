import hashlib, hmac, time
import requests

class bittrex(object):
    
    def __init__(self, apiKey, apiSecret, apiVersion='v3'):
        self.apiVersion = 'v3'
        self.baseUrl = 'https://api.bittrex.com'
        self.apiKey = apiKey
        self.apiSecret = apiSecret

    def _getHeaders(self, fullUrl, content, method):
        apiContentHash = hashlib.sha512(bytearray(content,'utf-8')).hexdigest()
        apiTimestamp = round(time.time()*1000)
        preSignList = apiTimestamp, fullUrl, method.upper(), apiContentHash
        preSign = ''.join(preSignList)
        apiSignature = hmac.new(self.apiSecret, bytearray(preSign, 'utf-8'), hashlib.sha512).hexdigest()
        headers = {
            'API-Key' : self.apiKey,
            'API-Timestamp' : apiTimestamp,
            'API-Content-Hash' : apiContentHash,
            'API-Signature' : apiSignature
        }
        return headers

    def _apiCall(self, route, content='', method='GET'):
        fullUrl = self.baseUrl + '/' + self.apiVersion + '/' + route
        headers = self._getHeaders(fullUrl, content, method)
        response = getattr(requests, method)(fullUrl, headers=headers, data=content)
        return response

    def balances(self):
        r = self._apiCall('balances')
        return r
        
        

