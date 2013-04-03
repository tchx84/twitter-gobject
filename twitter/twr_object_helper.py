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

import twr_error


class TwrObjectHelper:

    @staticmethod
    def get(instance, url, params,
            completed_cb, failed_cb, completed_data, failed_data):

        completed_id = instance.connect('transfer-completed',
                                        completed_cb, completed_data)
        failed_id = instance.connect('transfer-failed',
                                     failed_cb, failed_data)
        instance.request('GET', url, params)
        instance.disconnect(completed_id)
        instance.disconnect(failed_id)

    @staticmethod
    def post(instance, url, params, filepath,
             completed_cb, failed_cb, completed_data, failed_data):

        completed_id = instance.connect('transfer-completed',
                                        completed_cb, completed_data)
        failed_id = instance.connect('transfer-failed',
                                     failed_cb, failed_data)
        instance.request('POST', url, params, filepath)
        instance.disconnect(completed_id)
        instance.disconnect(failed_id)

    @staticmethod
    def _completed_cb(instance, data, signal):
        try:
            info = json.loads(data)

            if isinstance(info, dict) and ('errors' in info.keys()):
                message = '%s: %s' % \
                    (instance.__class__.__name__, str(info['errors']))
                raise twr_error.TwrObjectError(message)

            # XXX hmmm, hacks we do for love.
            if hasattr(instance, '_status_id') and 'id_str' in info.keys():
                instance._status_id = str(info['id_str'])

            instance.emit(signal, info)
        except Exception, e:
            print '%s: _completed_cb crashed with %s' % \
                (instance.__class__.__name__, str(e))

    @staticmethod
    def _failed_cb(instance, message, signal):
        instance.emit(signal, message)
