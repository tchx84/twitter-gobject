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
