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

from twr_object_plus import TwrObjectPlus


class TwrStatus(TwrObjectPlus):
    UPDATE_URL = 'https://api.twitter.com/1.1/statuses/update.json'
    UPDATE_WITH_MEDIA_URL = 'https://api.twitter.com/1.1/statuses/' \
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
        TwrObjectPlus.__init__(self)
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

        GObject.idle_add(self.post,
                         url,
                         params,
                         filepath,
                         'status-updated',
                         'status-updated-failed')

    def show(self):
        self._check_is_created()
        GObject.idle_add(self.get,
                         self.SHOW_URL,
                         [('id', (self._status_id))],
                         'status-downloaded',
                         'status-downloaded-failed')

    def destroy(self):
        self._check_is_created()
        GObject.idle_add(self.post,
                         self.DESTROY_URL % self._status_id,
                         None,
                         None,
                         'status-destroyed',
                         'status-destroyed-failed')

    def retweet(self):
        self._check_is_created()
        GObject.idle_add(self.post,
                         self.RETWEET_URL % self._status_id,
                         None,
                         None,
                         'retweet-created',
                         'retweet-created-failed')

    def retweets(self):
        self._check_is_created()
        GObject.idle_add(self.get,
                         self.RETWEETS_URL % self._status_id,
                         [],
                         'retweets-downloaded',
                         'retweets-downloaded-failed')

    def _check_is_not_created(self):
        if self._status_id is not None:
            raise twr_error.TwrStatusAlreadyCreated('Status already created')

    def _check_is_created(self):
        if self._status_id is None:
            raise twr_error.TwrStatusNotCreated('Status not created')
