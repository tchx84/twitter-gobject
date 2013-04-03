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

            # XXX hmmm, things we do for love.
            if hasattr(instance, '_status_id') and 'id_str' in info.keys():
                instance._status_id = str(info['id_str'])

            instance.emit(signal, info)
        except Exception, e:
            print '%s: _completed_cb crashed with %s' % \
                (instance.__class__.__name__, str(e))

    @staticmethod
    def _failed_cb(instance, message, signal):
        instance.emit(signal, message)
