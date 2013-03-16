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

import json

from gi.repository import GObject

import twr_error
from twr_object import TwrObject


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

        GObject.idle_add(self._get,
                        self.MENTIONS_TIMELINE_URL,
                        params,
                        self.__completed_cb,
                        self.__failed_cb,
                        'mentions-downloaded',
                        'mentions-downloaded-failed')

    def home_timeline(self, count=None, since_id=None,
                      max_id=None, exclude_replies=None):
        params = self._params(count, since_id, max_id, exclude_replies)

        GObject.idle_add(self._get,
                        self.HOME_TIMELINE_URL,
                        params,
                        self.__completed_cb,
                        self.__failed_cb,
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

    def _get(self, url, params, completed_cb, failed_cb,
            completed_data, failed_data):

        object = TwrObject()
        object.connect('transfer-completed', completed_cb, completed_data)
        object.connect('transfer-failed', failed_cb, failed_data)
        object.request('GET', url, params)

    def __completed_cb(self, object, data, signal):
        try:
            info = json.loads(data)

            if isinstance(info, dict) and ('errors' in info.keys()):
                raise twr_error.TwrTimelineError(str(info['errors']))

            self.emit(signal, info)
        except Exception, e:
            print 'TwrTimeline.__completed_cb crashed with %s' % str(e)

    def __failed_cb(self, object, message, signal):
        self.emit(signal, message)
