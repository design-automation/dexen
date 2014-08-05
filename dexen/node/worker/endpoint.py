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
import time

import rpyc
from rpyc.utils import server as rpyc_server
from pymongo.mongo_client import MongoClient

from dexen.common import remoting, constants, utils
from dexen.node import env_mgr
from dexen.node.worker import core

#===============================================================================
# Globals
#===============================================================================
_server_addr = None
_worker_name = ""
_job_name = None
_core = None

#===============================================================================
# The Worker interface that is called from the backend WorkerProxy.
#===============================================================================
class WorkerEndPoint(remoting.BaseEndPoint):
    """ An RpyC server that accepts incoming connections from the backend proxy. 
    See dexen.server.backend.proxy.WorkerProxy.
    """
    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    def get_associated_job(self):
        return _job_name

    def execute(self, execution):
        execution = rpyc.classic.obtain(execution)
        _core.execute(execution)

    def get_execution_result(self):
        return _core.get_execution_result()


# ----------------------------------------------------------------------------------------------TODO
#TODO: why can't this utility function be moved to env_mgr.py, seems to make sense there
def init_dir():
    """ Utility function 
    """
    worker_dir = env_mgr.get_worker_dir(_worker_name, create=True)
    utils.del_tree(worker_dir)


def start(server_addr, worker_name, job_name=None):
    """ Starts the core thread that contains the main loop and then starts an RyC threaded server. 
    This RPyC server spawns a thread to handle each incoming connection from the worker proxy.
    """

    # Start the core thread
    global _server_addr, _worker_name, _job_name, _core
    _server_addr = server_addr
    _worker_name = worker_name
    _job_name = job_name

    init_dir()

    db_client = MongoClient(server_addr.ip, constants.MONGOD_PORT)
    _core = core.WorkerCore(_worker_name, db_client, _job_name)
    _core.start()

    # Start the RPyC ThreadedServer
    worker_endpoint = rpyc_server.ThreadedServer(
            WorkerEndPoint,
            protocol_config=remoting.DEFAULT_CONFIG,
            logger=logging.getLogger(__name__+"."+_worker_name))
    server_conn = remoting.connect(server_addr)
    my_addr = remoting.EndPointAddress(remoting.get_my_ip(), worker_endpoint.port)
    _node_name = server_conn.root.register_worker(my_addr, _worker_name)
    time.sleep(5)
    server_conn.close()
    worker_endpoint.start()

