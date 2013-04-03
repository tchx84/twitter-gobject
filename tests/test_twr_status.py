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
from twitter.twr_status import TwrStatus
from twitter.twr_account import TwrAccount


consumer_key = ''
consumer_secret = ''

access_key = ''
access_secret = ''

TwrAccount.set_secrets(consumer_key, consumer_secret,
                       access_key, access_secret)


def random_status():
    return ''.join([random.choice(string.letters) for i in xrange(15)])


def __test_phase6_failed_cb(status, message):
    print '[FAILED] phase6: status-destroyed-failed with %s' % message
    loop.quit()


def __test_phase5_failed_cb(parent_status, message, child_status):
    print '[OK] phase5: retweet-created-failed with %s' % message

    parent_status.connect('status-destroyed', __test_phase6_cb)
    parent_status.connect('status-destroyed-failed', __test_phase6_failed_cb)
    parent_status.destroy()

    child_status.connect('status-destroyed', __test_phase6_cb)
    child_status.connect('status-destroyed-failed', __test_phase6_failed_cb)
    child_status.destroy()


def __test_phase4_failed_cb(parent_status, message):
    print '[FAILED] phase4: status-downloaded-failed with %s' % message
    loop.quit()


def __test_phase3_failed_cb(child_status, message):
    print '[FAILED] phase3: status-downloaded-failed with %s' % message
    loop.quit()


def __test_phase2_failed_cb(child_status, message):
    print '[FAILED] phase2: status-updated-failed with %s' % message
    loop.quit()


def __test_phase1_failed_cb(parent_status, message):
    print '[FAILED] phase1: status-updated-failed with %s' % message
    loop.quit()


def __test_phase6_cb(status, info):
    print '[OK] phase6: status-destroyed, _status_id: %s' % status._status_id
    loop.quit()


def __test_phase5_cb(parent_status, info):
    print '[FAILED] phase5: retweet-created, _status_id: %s' % \
          parent_status._status_id
    loop.quit()


def __test_phase4_cb(parent_status, info, child_status):
    print '[OK] phase4: status-downloaded, _status_id: %s' % \
          parent_status._status_id

    parent_status.connect('retweet-created', __test_phase5_cb)
    parent_status.connect('retweet-created-failed',
                          __test_phase5_failed_cb, child_status)
    parent_status.retweet()


def __test_phase3_cb(child_status, info, parent_status):
    print '[OK] phase3: status-downloaded, _status_id: %s' % \
          child_status._status_id

    parent_status.connect('status-downloaded', __test_phase4_cb, child_status)
    parent_status.connect('status-downloaded-failed', __test_phase4_failed_cb)
    parent_status.show()


def __test_phase2_cb(child_status, info, parent_status):
    print '[OK] phase2: status-updated (reply), _status_id: %s' % \
          child_status._status_id

    child_status.connect('status-downloaded', __test_phase3_cb, parent_status)
    child_status.connect('status-downloaded-failed', __test_phase3_failed_cb)
    child_status.show()


def __test_phase1_cb(parent_status, info):
    print '[OK] phase1: status-updated, _status_id: %s' % \
          parent_status._status_id

    parent_name = str(info['user']['name'])
    status = '@%s %s' % (parent_name, random_status())

    child_status = TwrStatus()
    child_status.connect('status-updated', __test_phase2_cb, parent_status)
    child_status.connect('status-updated-failed', __test_phase2_failed_cb)
    child_status.update(status, parent_status._status_id)


loop = GObject.MainLoop()

status = random_status()
print 'phase0: will update status with %s' % status

parent_status = TwrStatus()
parent_status.connect('status-updated', __test_phase1_cb)
parent_status.connect('status-updated-failed', __test_phase1_failed_cb)
parent_status.update_with_media(status, 'image.png')

loop.run()
