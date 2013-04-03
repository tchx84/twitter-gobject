# Copyright (c) 2013 Martin Abente Lahaye. - tch@sugarlabs.org
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301 USA.

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

        header = 'OAuth %s' % ', '.join(['%s="%s"' %
                              (k, TwrAccount._percent(v))
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
        key_values = [(TwrAccount._percent(TwrAccount._utf8(k)),
                      TwrAccount._percent(TwrAccount._utf8(v)))
                      for k, v in params.items()]
        key_values.sort()

        return '&'.join(['%s=%s' % (k, v) for k, v in key_values])
