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
import multiprocessing as mp

from rpyc.utils import server as rpyc_server

from dexen.common import remoting
from dexen.node.worker import endpoint as worker_endpoint

#===============================================================================
# 
#===============================================================================
_workers = {} # worker_name : process
_server_addr = None
_job_name = None
_node_name = None
_max_workers = None

logger = logging.getLogger(__name__)
#===============================================================================
# NodeEndPoint
#===============================================================================
class NodeEndPoint(remoting.BaseEndPoint):
    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    def start_worker(self, worker_name):
        if worker_name in _workers:
            logger.info("Worker: %s has already been started.", worker_name)
            return
        logger.info("Starting worker: %s", worker_name)
        _workers[worker_name] = mp.Process(name=worker_name,
                                           target=worker_endpoint.start,
                                           args=(_server_addr, worker_name))
        _workers[worker_name].start()

    def stop_worker(self, worker_name):
        if worker_name not in _workers:
            logger.info("Could not stop worker: %s. It does not exist.")
            return
        logger.info("Stopping worker: %s", worker_name)
        _workers[worker_name].terminate()
        del _workers[worker_name]

    def num_workers(self):
        print "Num workers get called"
        logger.info("Num workers on Node: %s is %d", _node_name, _max_workers)
        return _max_workers

    def get_associated_job(self):
        return _job_name


#===============================================================================
# 
#===============================================================================
def start(server_addr, max_workers, job_name=None):
    global _server_addr, _job_name, _node_name, _max_workers

    _server_addr = server_addr
    _max_workers = max_workers
    _job_name = job_name

    node_endpoint = rpyc_server.ThreadedServer(
            NodeEndPoint,
            protocol_config=remoting.DEFAULT_CONFIG)

    server_conn = remoting.connect(server_addr)
    my_addr = remoting.EndPointAddress(remoting.get_my_ip(), node_endpoint.port)
    logger.info("Registering node with backend server...")
    _node_name = server_conn.root.register_node(my_addr)
    logger.info("%s is assigned as node name.", _node_name)
    node_endpoint.logger = logging.getLogger(__name__+"."+_node_name)
    logger.info("Sleeping for 5 seconds...")
    time.sleep(5)
    logger.info("Closing connection to the backend server...")
    server_conn.close()
    logger.info("Starting node endpoint...")
    node_endpoint.start()

