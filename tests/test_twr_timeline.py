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
import random
import string

from gi.repository import GObject

sys.path.append("..")
from twitter.twr_timeline import TwrTimeline
from twitter.twr_account import TwrAccount


consumer_key = ''
consumer_secret = ''

access_key = ''
access_secret = ''

TwrAccount.set_secrets(consumer_key, consumer_secret,
                       access_key, access_secret)


def __phase2_failed_cb(timeline, message):
    print '[FAILED] phase2: timeline-downloaded-failed with %s' % message
    loop.quit()


def __phase1_failed_cb(timeline, message):
    print '[FAILED] phase1: mentions-downloaded-failed with %s' % message
    loop.quit()


def __phase2_cb(timeline, info):
    print '[OK] phase2: timeline-downloaded, count: %d' % len(info)
    loop.quit()


def __phase1_cb(timeline, info):
    print '[OK] phase1: mentions-downloaded, count: %d' % len(info)
    loop.quit()


timeline = TwrTimeline()

timeline.connect('mentions-downloaded', __phase1_cb)
timeline.connect('mentions-downloaded-failed', __phase1_failed_cb)
timeline.mentions_timeline()

timeline.connect('timeline-downloaded', __phase2_cb)
timeline.connect('timeline-downloaded-failed', __phase2_failed_cb)
timeline.home_timeline()

loop = GObject.MainLoop()
loop.run()
