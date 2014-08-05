# ==================================================================================================
#
#    Copyright (c) 2008, Patrick Janssen (patrick@janssen.name)
#
#    This file is part of Dexen.
#
#    Dexen is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Dexen is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Dexen.  If not, see <http://www.gnu.org/licenses/>.
#
# ==================================================================================================


import logging
import socket
import time

import rpyc
from rpyc.core import netref

from dexen.common.exceptions import DexenConnectionException

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
        "allow_pickle": True,
        "instantiate_custom_exceptions": True,
        "instantiate_oldstyle_exceptions": True}

DEFAULT_SERVER_PORT = 9999


def is_immutable(obj):
    if obj is None:
        return True
    immutable_types = [int, float, str, tuple, bool, long]
    return any([isinstance(obj, t) for t in immutable_types])

#===============================================================================
# Decorators
#===============================================================================
class remote_api(object):
    def __init__(self, default_val=None):
        self.default_val = default_val

    def __call__(self, func):
        def wrapper(self_, *args, **kwargs):
            try:
                ret_val = self.default_val
                ret_val = func(self_, *args, **kwargs)
                if not is_immutable(ret_val):
                    # Verify that the return value is a remote proxy wrapper object.
                    assert isinstance(ret_val, netref.BaseNetref)
                if isinstance(ret_val, netref.BaseNetref):
                    ret_val = rpyc.classic.obtain(ret_val)
            except EOFError:
                logger.exception("EOFError on remote invocation.")
                self_.on_connection_broken()
            except Exception:
                logger.exception("Exception has occured during remote call.")
            finally:
                return ret_val
        return wrapper


def connect(address, timeout=5):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            conn = rpyc.connect(address.ip, address.port, config=DEFAULT_CONFIG)
            if conn:
                return conn
        except:
            pass
        time.sleep(1)
    err_msg = "Connection to ip:%s, port:%d couldn't be established." % (address.ip, address.port)
    raise DexenConnectionException(err_msg)


def get_my_ip(is_local=False):
    if is_local: return "127.0.0.1"
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("gmail.com", 80))
    except socket.gaierror:
        return "127.0.0.1"
    return s.getsockname()[0]


def is_local(reg_host):
    if reg_host == "local":
        return True
    return False


def is_ip_valid(host):
    temp = host.split(".")
    if len(temp) != 4:
        return False
    for elem in temp:
        if not elem.isdigit():
            return False
    return True


class EndPointAddress(object):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port


class BaseEndPointProxy(object):
    def __init__(self, address):
        self.address = address
        self._conn = None
        self.logger = logging.getLogger(__name__+"."+self.__class__.__name__)
        try:
            self._conn = connect(address)
        except DexenConnectionException:
            logging.exception("Exception has occured when connecting to remote endpoint.")
            self.on_connection_broken()

    def on_connection_broken(self):
        raise NotImplementedError()


#===============================================================================
# Base Class for RPYC Services
#===============================================================================
class BaseEndPoint(rpyc.Service):
    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    def _rpyc_getattr(self, name):
        if not name.startswith("_"):
            return getattr(self, name)
        else:
            raise AttributeError("private attributes are not accessible.")

    def _rpyc_setattr(self, name, value):
        if not name.startswith("_"):
            return setattr(self, name, value)
        else:
            raise AttributeError("private data attributes cannot be set.")
