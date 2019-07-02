#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function, unicode_literals

import threading

from .httpsrv import HttpSrv
from .broker_util import *


class BrokerThr(object):
    """external api; behaves like BrokerMP but using plain threads"""

    def __init__(self, hub):
        self.hub = hub
        self.log = hub.log
        self.args = hub.args

        self.mutex = threading.Lock()

        # instantiate all services here (TODO: inheritance?)
        self.httpsrv = HttpSrv(self)
        self.httpsrv.disconnect_func = self.httpdrop

    def shutdown(self):
        # self.log("broker", "shutting down")
        pass

    def put(self, want_retval, dest, *args):
        if dest == "httpconn":
            sck, addr = args
            self.log(str(addr), "-" * 4 + "C-qpop")
            self.httpsrv.accept(sck, addr)

        else:
            # new ipc invoking managed service in hub
            obj = self.hub
            for node in dest.split("."):
                obj = getattr(obj, node)

            # TODO will deadlock if dest performs another ipc
            rv = try_exec(obj, *args, want_retval=want_retval)
            if not want_retval:
                return

            # pretend we're broker_mp
            retq = ExceptionalQueue(1)
            retq.put(rv)
            return retq

    def httpdrop(self, addr):
        self.hub.tcpsrv.num_clients.add(-1)
