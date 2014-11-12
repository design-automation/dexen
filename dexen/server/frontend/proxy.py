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

from dexen.common import remoting, exceptions
from dexen.common.remoting import remote_api

class ServerBackendProxy(remoting.BaseEndPointProxy):
    """ Class that communicates with the the backend server via the endpoint RPyC server.
    See dexen.server.backend.endpoint.ServerBackendEndPoint.
    """
    def __init__(self, server_addr):
        super(ServerBackendProxy, self).__init__(server_addr)
        if self._conn is None:
            raise exceptions.DexenConnectionException("Connection to server backend failed.")

    def on_connection_broken(self):
        self.logger.error("Connection to server backend is broken.")
        raise exceptions.DexenConnectionException("Connection to server backend is broken.")

    @remote_api()
    def create_job(self, user_name, job_name):
        self._conn.root.create_job(user_name, job_name)

    @remote_api()
    def delete_job(self, user_name, job_name):
        self._conn.root.delete_job(user_name, job_name)

    @remote_api()
    def run_job(self, user_name, job_name):
        self._conn.root.run_job(user_name, job_name)

    @remote_api()
    def stop_job(self, user_name, job_name):
        self._conn.root.stop_job(user_name, job_name)

    @remote_api()
    def get_jobs(self, user_name):
        return self._conn.root.get_jobs(user_name)

    @remote_api()
    def export_job(self, user_name, job_name):
        return self._conn.root.export_job(user_name, job_name)

    @remote_api()
    def get_tasks(self, user_name, job_name):
        return self._conn.root.get_tasks(user_name, job_name)

    @remote_api()
    def register_task(self, user_name, job_name, task):
        self._conn.root.register_task(user_name, job_name, task)

    @remote_api()
    def deregister_task(self, user_name, job_name, task_name):
        self._conn.root.deregister_task(user_name, job_name, task_name)

    @remote_api()
    def get_executions(self, user_name, job_name, last_update):
        return self._conn.root.get_executions(user_name, job_name, last_update)
