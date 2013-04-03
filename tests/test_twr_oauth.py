#!/usr/bin/env python
#
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

import sys

from gi.repository import GObject

sys.path.append("..")
from twitter.twr_oauth import TwrOauth
from twitter.twr_account import TwrAccount


consumer_key = ''
consumer_secret = ''

access_key = ''
access_secret = ''

TwrAccount.set_secrets(consumer_key, consumer_secret,
                       access_key, access_secret)


def __phase2_failed_cb(oauth, info):
    print '[FAILED] phase2: access-downloaded-failed, with %s' % info
    loop.quit()


def __phase1_failed_cb(oauth, info):
    print '[FAILED] phase1: request-downloaded-failed, with %s' % info
    loop.quit()


def __phase2_cb(oauth, info):
    print '[OK] phase2: access-downloaded, with %s' % info

    TwrAccount.set_secrets(consumer_key, consumer_secret,
                           info['oauth_token'], info['oauth_token_secret'])
    loop.quit()


def __phase1_cb(oauth, info):
    print '[OK] phase1: request-downloaded'

    url = TwrOauth.AUTHORIZATION_URL % info['oauth_token']
    print 'Please visit %s' % url
    verifier = raw_input('verifier: ')

    TwrAccount.set_secrets(consumer_key, consumer_secret,
                           info['oauth_token'], info['oauth_token_secret'])

    oauth.connect('access-downloaded', __phase2_cb)
    oauth.connect('access-downloaded-failed', __phase2_failed_cb)
    oauth.access_token(verifier)

oauth = TwrOauth()
oauth.connect('request-downloaded', __phase1_cb)
oauth.connect('request-downloaded-failed', __phase1_failed_cb)
oauth.request_token()

loop = GObject.MainLoop()
loop.run()
