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

import pymongo
import rpyc
from rpyc.utils import server as rpyc_server

from dexen.common import remoting, constants
from dexen.server.backend import core, resource_manager as res_mgr

_core = None

class ServerBackendEndPoint(remoting.BaseEndPoint):
    """ Acts as an RpyC server that accepts incoming connections from the
    frontend proxy.

    See dexen.server.frontend.proxy.ServerBackendProxy.
    """
    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    def create_job(self, user_name, job_name):
        _core.create_job(user_name, job_name)

    def delete_job(self, user_name, job_name):
        _core.delete_job(user_name, job_name)

    def run_job(self, user_name, job_name):
        _core.run_job(user_name, job_name)

    def stop_job(self, user_name, job_name):
        _core.stop_job(user_name, job_name)

    def get_jobs(self, user_name):
        return _core.get_jobs(user_name)

    def export_jobs(self, user_name):
        return _core.export_jobs(user_name)

    def get_tasks(self, user_name, job_name):
        return _core.get_tasks(user_name, job_name)

    def register_task(self, user_name, job_name, task):
        task = rpyc.classic.obtain(task)
        _core.register_task(user_name, job_name, task)

    def deregister_task(self, user_name, job_name, task_name):
        _core.deregister_task(user_name, job_name, task_name)

    def register_node(self, address):
        address = rpyc.classic.obtain(address)
        return _core.register_node(address)

    def register_worker(self, address, worker_name):
        address = rpyc.classic.obtain(address)
        _core.register_worker(address, worker_name)


def start(db_addr):
    """ Starts the core thread that contains the main loop and then starts an
    RPyC threaded server. This RPyC server spawns a thread to handle each 
    incoming connection from the frontend proxy.
    """
    # Start the core thread
    global _core
    db_client = pymongo.MongoClient(db_addr.ip, db_addr.port)
    _core = core.ServerCore(res_mgr.ResourceManager(), db_client)
    _core.setDaemon(True)
    _core.start()

    # Start the RPyC ThreadedServer
    server_backend_endpoint = rpyc_server.ThreadedServer(
            ServerBackendEndPoint,
            port=constants.SERVER_BACKEND_PORT,
            protocol_config=remoting.DEFAULT_CONFIG,
            logger=logging.getLogger(__name__+".ServerBackendEndPoint"))

    server_backend_endpoint.start()
