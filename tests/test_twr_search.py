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
from twitter.twr_search import TwrSearch
from twitter.twr_account import TwrAccount


consumer_key = ''
consumer_secret = ''

access_key = ''
access_secret = ''

TwrAccount.set_secrets(consumer_key, consumer_secret,
                       access_key, access_secret)


def __phase1_failed_cb(search, info):
    print '[FAILED] phase1: tweets-downloaded-failed, with %s' % info
    loop.quit()


def __phase1_cb(search, info):
    print '[OK] phase1: tweets-downloaded, count: %s' % len(info['statuses'])
    loop.quit()


search = TwrSearch()
search.connect('tweets-downloaded', __phase1_cb)
search.connect('tweets-downloaded-failed', __phase1_failed_cb)
search.tweets('@twr_object', count=1)

loop = GObject.MainLoop()
loop.run()
