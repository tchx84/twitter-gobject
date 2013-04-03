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
from twr_object_helper import TwrObjectHelper


class TwrOauth(TwrObject):

    REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
    AUTHORIZATION_URL = 'https://api.twitter.com/oauth/'\
                        'authorize?oauth_token=%s'
    ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'

    __gsignals__ = {
        'request-downloaded':        (GObject.SignalFlags.RUN_FIRST,
                                      None, ([object])),
        'request-downloaded-failed': (GObject.SignalFlags.RUN_FIRST,
                                      None, ([str])),
        'access-downloaded':         (GObject.SignalFlags.RUN_FIRST,
                                      None, ([object])),
        'access-downloaded-failed':  (GObject.SignalFlags.RUN_FIRST,
                                      None, ([str]))}

    def request_token(self):
        GObject.idle_add(TwrObjectHelper.get,
                         self,
                         self.REQUEST_TOKEN_URL,
                         [],
                         self._completed_cb,
                         TwrObjectHelper._failed_cb,
                         'request-downloaded',
                         'request-downloaded-failed')

    def access_token(self, verifier):
        params = [('oauth_callback', ('oob')),
                  ('oauth_verifier', (verifier))]

        GObject.idle_add(TwrObjectHelper.post,
                         self,
                         self.ACCESS_TOKEN_URL,
                         params,
                         None,
                         self._completed_cb,
                         TwrObjectHelper._failed_cb,
                         'access-downloaded',
                         'access-downloaded-failed')

    def _completed_cb(self, object, data, signal):
        try:
            info = dict(parse_qsl(data))

            if isinstance(info, dict) and ('errors' in info.keys()):
                message = '%s: %s' % (instance.__class__, str(info['errors']))
                raise twr_error.TwrObjectError(message)

            self.emit(signal, info)
        except Exception, e:
            print 'TwrOauth: _completed_cb crashed with %s' % str(e)
