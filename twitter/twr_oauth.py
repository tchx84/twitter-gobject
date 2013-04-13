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

import logging

from gi.repository import GObject
from urlparse import parse_qsl

import twr_error
from twr_object_plus import TwrObjectPlus


class TwrOauth(TwrObjectPlus):

    REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
    AUTHORIZATION_URL = 'https://api.twitter.com/oauth/' \
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
        GObject.idle_add(self.get,
                         self.REQUEST_TOKEN_URL,
                         [],
                         'request-downloaded',
                         'request-downloaded-failed')

    def access_token(self, verifier):
        params = [('oauth_callback', ('oob')),
                  ('oauth_verifier', (verifier))]

        GObject.idle_add(self.post,
                         self.ACCESS_TOKEN_URL,
                         params,
                         None,
                         'access-downloaded',
                         'access-downloaded-failed')

    def _completed_cb(self, object, data, signal):
        try:
            info = dict(parse_qsl(data))

            if isinstance(info, dict) and ('errors' in info.keys()):
                message = '%s: %s' % ('TwrOauth', str(info['errors']))
                raise twr_error.TwrObjectError(message)

            self.emit(signal, info)
        except Exception, e:
            logging.error('TwrOauth: _completed_cb crashed with %s',
                          str(e))
