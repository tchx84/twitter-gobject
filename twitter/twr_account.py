#!/usr/bin/env python
#
# Copyright (c) 2013 Martin Abente Lahaye. - tch@sugarlabs.org

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

import urllib
import time
import random
import hashlib
import hmac
import binascii


class TwrAccount:

    @classmethod
    def set_secrets(cls, c_key, c_secret, a_key, a_secret):
        cls._consumer_key = c_key
        cls._consumer_secret = c_secret
        cls._access_key = a_key
        cls._access_secret = a_secret

    @classmethod
    def _oauth_signature(cls, method, url, params):
        recipe = (
            method,
            TwrAccount._percent(url),
            TwrAccount._percent(TwrAccount._string_params(params)))

        raw = '&'.join(recipe)
        key = '%s&%s' % (TwrAccount._percent(cls._consumer_secret),
                         TwrAccount._percent(cls._access_secret))

        hashed = hmac.new(key, raw, hashlib.sha1)
        signature = binascii.b2a_base64(hashed.digest())[:-1]

        return signature

    @classmethod
    def authorization_header(cls, method, url, request_params):
        oauth_params = {
            'oauth_nonce': TwrAccount._nonce(),
            'oauth_timestamp': TwrAccount._timestamp(),
            'oauth_consumer_key': cls._consumer_key,
            'oauth_version': '1.0',
            'oauth_token': cls._access_key,
            'oauth_signature_method': 'HMAC-SHA1'}

        params = dict(oauth_params.items() + request_params)
        params['oauth_signature'] = cls._oauth_signature(method, url, params)

        header = 'OAuth %s' % ', '.join(['%s="%s"' % \
                              (k, TwrAccount._percent(v)) \
                              for k, v in sorted(params.iteritems())])

        return header

    @staticmethod
    def _percent(string):
        return urllib.quote(str(string), safe='~')

    @staticmethod
    def _utf8(string):
        return str(string).encode("utf-8")

    @staticmethod
    def _nonce(length=8):
        return ''.join([str(random.randint(0, 9)) for i in range(length)])

    @staticmethod
    def _timestamp():
        return int(time.time())

    @staticmethod
    def _string_params(params):
        key_values = [(TwrAccount._percent(TwrAccount._utf8(k)), \
                       TwrAccount._percent(TwrAccount._utf8(v))) \
                       for k, v in params.items()]
        key_values.sort()

        return '&'.join(['%s=%s' % (k, v) for k, v in key_values])
