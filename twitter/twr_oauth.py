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

from gi.repository import GObject
from urlparse import parse_qsl

import twr_error
from twr_object import TwrObject


class TwrOauth(GObject.GObject):

    REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
    AUTHORIZATION_URL = 'https://api.twitter.com/oauth/'\
                        'authorize?oauth_token=%s'
    ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'

    __gsignals__ = {
        'request-downloaded':       (GObject.SignalFlags.RUN_FIRST,
                                    None, ([object])),
        'request-downloaded-failed': (GObject.SignalFlags.RUN_FIRST,
                                    None, ([str])),
        'access-downloaded':        (GObject.SignalFlags.RUN_FIRST,
                                    None, ([object])),
        'access-downloaded-failed': (GObject.SignalFlags.RUN_FIRST,
                                    None, ([str]))}

    def request_token(self):
        GObject.idle_add(self._get,
                        self.REQUEST_TOKEN_URL,
                        [],
                        self.__completed_cb,
                        self.__failed_cb,
                        'request-downloaded',
                        'request-downloaded-failed')

    def access_token(self, verifier):
        params = [('oauth_callback', ('oob')),
                  ('oauth_verifier', (verifier))]

        GObject.idle_add(self._post,
                        self.ACCESS_TOKEN_URL,
                        params,
                        None,
                        self.__completed_cb,
                        self.__failed_cb,
                        'access-downloaded',
                        'access-downloaded-failed')

    def _get(self, url, params,
            completed_cb, failed_cb, completed_data, failed_data):

        object = TwrObject()
        object.connect('transfer-completed', completed_cb, completed_data)
        object.connect('transfer-failed', failed_cb, failed_data)
        object.request('GET', url, params)

    def _post(self, url, params, filepath,
            completed_cb, failed_cb, completed_data, failed_data):

        object = TwrObject()
        object.connect('transfer-completed', completed_cb, completed_data)
        object.connect('transfer-failed', failed_cb, failed_data)
        object.request('POST', url, params, filepath)

    def __completed_cb(self, object, data, signal):
        try:
            info = dict(parse_qsl(data))

            if isinstance(info, dict) and ('errors' in info.keys()):
                raise twr_error.TwrOauthError(str(info['errors']))

            self.emit(signal, info)
        except Exception, e:
            print 'TwrOauth.__completed_cb crashed with %s' % str(e)

    def __failed_cb(self, object, message, signal):
        self.emit(signal, message)
