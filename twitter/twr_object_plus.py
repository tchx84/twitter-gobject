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

import json
import logging

import twr_error
from twr_object import TwrObject


class TwrObjectPlus(TwrObject):

    def get(self, url, params, completed_data, failed_data):
        completed_id = self.connect('transfer-completed',
                                    self._completed_cb, completed_data)
        failed_id = self.connect('transfer-failed',
                                 self._failed_cb, failed_data)
        self.request('GET', url, params)
        self.disconnect(completed_id)
        self.disconnect(failed_id)

    def post(self, url, params, filepath, completed_data, failed_data):
        completed_id = self.connect('transfer-completed',
                                    self._completed_cb, completed_data)
        failed_id = self.connect('transfer-failed',
                                 self._failed_cb, failed_data)
        self.request('POST', url, params, filepath)
        self.disconnect(completed_id)
        self.disconnect(failed_id)

    def _completed_cb(self, object, data, signal):
        try:
            info = json.loads(data)

            if isinstance(info, dict):
                self._check_errors(info)
                self._check_hacks(info)

            self.emit(signal, info)
        except Exception, e:
            logging.error('%s: _completed_cb crashed with %s',
                          self.__class__.__name__, str(e))

    def _check_errors(self, info):
        if 'errors' in info.keys():
            message = '%s: %s' % (self.__class__.__name__, str(info['errors']))
            raise twr_error.TwrObjectError(message)

    # XXX hmmm, hacks we do for love.
    def _check_hacks(self, info):
        if hasattr(self, '_status_id') and 'id_str' in info.keys():
            self._status_id = str(info['id_str'])

    def _failed_cb(self, object, message, signal):
        self.emit(signal, message)
