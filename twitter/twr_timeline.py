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

from gi.repository import GObject

from twr_object import TwrObject
from twr_object_helper import TwrObjectHelper


class TwrTimeline(TwrObject):

    MENTIONS_TIMELINE_URL = 'https://api.twitter.com/1.1/statuses/'\
                            'mentions_timeline.json'
    HOME_TIMELINE_URL = 'https://api.twitter.com/1.1/statuses/'\
                        'home_timeline.json'

    __gsignals__ = {
        'mentions-downloaded':          (GObject.SignalFlags.RUN_FIRST,
                                         None, ([object])),
        'mentions-downloaded-failed':   (GObject.SignalFlags.RUN_FIRST,
                                         None, ([str])),
        'timeline-downloaded':          (GObject.SignalFlags.RUN_FIRST,
                                         None, ([object])),
        'timeline-downloaded-failed':   (GObject.SignalFlags.RUN_FIRST,
                                         None, ([str]))}

    def mentions_timeline(self, count=None, since_id=None, max_id=None):
        params = self._params(count, since_id, max_id)

        GObject.idle_add(TwrObjectHelper.get,
                         self,
                         self.MENTIONS_TIMELINE_URL,
                         params,
                         TwrObjectHelper._completed_cb,
                         TwrObjectHelper._failed_cb,
                         'mentions-downloaded',
                         'mentions-downloaded-failed')

    def home_timeline(self, count=None, since_id=None,
                      max_id=None, exclude_replies=None):
        params = self._params(count, since_id, max_id, exclude_replies)

        GObject.idle_add(TwrObjectHelper.get,
                         self,
                         self.HOME_TIMELINE_URL,
                         params,
                         TwrObjectHelper._completed_cb,
                         TwrObjectHelper._failed_cb,
                         'timeline-downloaded',
                         'timeline-downloaded-failed')

    def _params(self, count=None, since_id=None,
                max_id=None, exclude_replies=None):
        params = []

        if count is not None:
            params += [('count', (count))]
        if since_id is not None:
            params += [('since_id', (since_id))]
        if max_id is not None:
            params += [('max_id', (max_id))]
        if exclude_replies is not None:
            params += [('exclude_replies', (exclude_replies))]

        return params
