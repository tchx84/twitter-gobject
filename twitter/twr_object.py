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

import pycurl
import urllib

from gi.repository import GObject

from twr_account import TwrAccount


class TwrObject(GObject.GObject):

    __gsignals__ = {
        'transfer-completed': (GObject.SignalFlags.RUN_FIRST, None, ([str])),
        'transfer-progress': (GObject.SignalFlags.RUN_FIRST, None, \
                             ([float, float, str])),
        'transfer-failed': (GObject.SignalFlags.RUN_FIRST, None, ([str])),
        'transfer-started': (GObject.SignalFlags.RUN_FIRST, None, ([]))}

    def __init__(self):
        GObject.GObject.__init__(self)

    def _gen_header(self, method, url):
        authorization = TwrAccount.authorization_header(method, url)
        headers = ['Host: api.twitter.com:443',
                   'Authorization: %s' % authorization]

        return headers

    def _update_cb(self, down_total, down_done, up_total, up_done, states):

        if 2 in states:
            return

        total = up_total
        done = up_done
        mode = 'upload'

        if 1 in states:
            total = down_total
            done = down_done
            mode = 'download'

        if total == 0:
            return

        if 0 not in states:
            self.emit('transfer-started')
            states.append(0)

        self.emit('transfer-progress', total, done, mode)

        state = states[-1]
        if total == done and state in states and len(states) == state + 1:
            states.append(state + 1)

    def _write_cb(self, buffer):
        self.emit('transfer-completed', buffer)

    def request(self, method, url, params, filepath=None):
        c = pycurl.Curl()
        c.setopt(c.HTTPHEADER, self._gen_header(method, url))

        if method == 'POST':
            c.setopt(c.POST, 1)

            if filepath is not None:
                params += [("media", (c.FORM_FILE, filepath))]
            c.setopt(c.HTTPPOST, params)
        else:
            c.setopt(c.HTTPGET,  1)
            url += '?%s' % urllib.urlencode(params)

        # XXX hack to trace transfer states
        states = []

        def pre_update_cb(*args):
            args = list(args) + [states]
            self._update_cb(*args)

        c.setopt(c.URL, url)
        c.setopt(c.NOPROGRESS, 0)
        c.setopt(c.PROGRESSFUNCTION, pre_update_cb)
        c.setopt(c.WRITEFUNCTION, self._write_cb)

        try:
            c.perform()
        except pycurl.error:
            message = 'Something went wrong'
            self.emit('transfer-failed', message)
        else:
            code = c.getinfo(c.HTTP_CODE)
            if code != 200:
                message = 'HTTP code %s' % code
                self.emit('transfer-failed', message)
        finally:
            c.close()
