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


class TwrStatus(GObject.GObject):
    UPDATE_URL = 'https://api.twitter.com/1.1/statuses/update.json'
    UPDATE_WITH_MEDIA_URL = 'https://api.twitter.com/1.1/statuses/'\
                            'update_with_media.json'
    SHOW_URL = 'https://api.twitter.com/1.1/statuses/show.json'
    RETWEET_URL = 'https://api.twitter.com/1.1/statuses/retweet/%s.json'
    RETWEETS_URL = 'https://api.twitter.com/1.1/statuses/retweets/%s.json'
    DESTROY_URL = 'https://api.twitter.com/1.1/statuses/destroy/%s.json'

    __gsignals__ = {
        'status-updated':             (GObject.SignalFlags.RUN_FIRST,
                                      None, ([object])),
        'status-updated-failed':      (GObject.SignalFlags.RUN_FIRST,
                                      None, ([str])),
        'status-downloaded':          (GObject.SignalFlags.RUN_FIRST,
                                      None, ([object])),
        'status-downloaded-failed':   (GObject.SignalFlags.RUN_FIRST,
                                      None, ([str])),
        'status-destroyed':           (GObject.SignalFlags.RUN_FIRST,
                                      None, ([object])),
        'status-destroyed-failed':    (GObject.SignalFlags.RUN_FIRST,
                                      None, ([str])),
        'retweet-created':            (GObject.SignalFlags.RUN_FIRST,
                                      None, ([object])),
        'retweet-created-failed':     (GObject.SignalFlags.RUN_FIRST,
                                      None, ([str])),
        'retweets-downloaded':        (GObject.SignalFlags.RUN_FIRST,
                                      None, ([object])),
        'retweets-downloaded-failed': (GObject.SignalFlags.RUN_FIRST,
                                      None, ([str]))}

    def __init__(self, status_id=None):
        GObject.GObject.__init__(self)
        self._status_id = status_id

    def update(self, status, reply_status_id=None):
        self._update(self.UPDATE_URL,
                    status,
                    None,
                    reply_status_id)

    def update_with_media(self, status, filepath, reply_status_id=None):
        self._update(self.UPDATE_WITH_MEDIA_URL,
                    status,
                    filepath,
                    reply_status_id)

    def _update(self, url, status, filepath=None, reply_status_id=None):
        self._check_is_not_created()

        params = [('status', (status))]
        if reply_status_id is not None:
            params += [('in_reply_to_status_id', (reply_status_id))]

        GObject.idle_add(self._post,
                        url,
                        params,
                        filepath,
                        self.__completed_cb,
                        self.__failed_cb,
                        'status-updated',
                        'status-updated-failed')

    def show(self):
        self._check_is_created()
        GObject.idle_add(self._get,
                        self.SHOW_URL,
                        [('id', (self._status_id))],
                        self.__completed_cb,
                        self.__failed_cb,
                        'status-downloaded',
                        'status-downloaded-failed')

    def destroy(self):
        self._check_is_created()
        GObject.idle_add(self._post,
                        self.DESTROY_URL % self._status_id,
                        None,
                        None,
                        self.__completed_cb,
                        self.__failed_cb,
                        'status-destroyed',
                        'status-destroyed-failed')

    def retweet(self):
        self._check_is_created()
        GObject.idle_add(self._post,
                        self.RETWEET_URL % self._status_id,
                        None,
                        None,
                        self.__completed_cb,
                        self.__failed_cb,
                        'retweet-created',
                        'retweet-created-failed')

    def retweets(self):
        self._check_is_created()
        GObject.idle_add(self._get,
                        self.RETWEETS_URL % self._status_id,
                        [],
                        self.__completed_cb,
                        self.__failed_cb,
                        'retweets-downloaded',
                        'retweets-downloaded-failed')

    def _check_is_not_created(self):
        if self._status_id is not None:
            raise twr_error.TwrStatusAlreadyCreated('Status already created')

    def _check_is_created(self):
        if self._status_id is None:
            raise twr_error.TwrStatusNotCreated('Status not created')

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
            info = json.loads(data)

            if 'errors' in info.keys():
                raise twr_error.TwrStatusError(str(info['errors']))

            if self._status_id is None and 'id_str' in info.keys():
                self._status_id = str(info['id_str'])

            self.emit(signal, info)
        except Exception, e:
            print '__completed_cb crashed with %s' % str(e)

    def __failed_cb(self, object, message, signal):
        self.emit(signal, message)
