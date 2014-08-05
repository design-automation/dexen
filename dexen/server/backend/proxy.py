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


from dexen.common import remoting
from dexen.common.remoting import remote_api

#===============================================================================
# 
#===============================================================================
class NodeProxy(remoting.BaseEndPointProxy):
    ALIVE = "NODE_ALIVE"
    DEAD = "NODE_DEAD"

    def __init__(self, node_name, node_addr):
        super(NodeProxy, self).__init__(node_addr)
        self.name = node_name
        if self._conn is None:
            self.state = NodeProxy.DEAD
        else:
            self.state = NodeProxy.ALIVE

    def on_connection_broken(self):
        self.state = NodeProxy.DEAD
        self.logger.info("Connection to Node:%s is broken.", self.name)

    @property
    def is_alive(self):
        return self.state == NodeProxy.ALIVE

    @remote_api(default_val=0)
    def num_workers(self):
        return self._conn.root.num_workers()

    @remote_api()
    def start_worker(self, worker_name):
        self._conn.root.start_worker(worker_name)

    @remote_api()
    def stop_worker(self, worker_name):
        self._conn.root.stop_worker(worker_name)


class WorkerProxy(remoting.BaseEndPointProxy):
    IDLE = "WORKER_IDLE"
    BUSY = "WORKER_BUSY"
    DONE = "WORKER_DONE"
    DEAD = "WORKER_DEAD"

    def __init__(self, worker_name, worker_addr):
        super(WorkerProxy, self).__init__(worker_addr)
        self.name = worker_name
        if self._conn is None:
            self.state = WorkerProxy.DEAD
        else:
            self.state = WorkerProxy.IDLE
        self.scheduled_execution = None

    def on_connection_broken(self):
        self.state = WorkerProxy.DEAD
        self.logger.info("Worker %s is dead", self.name)

    @property
    def is_idle(self):
        return self.state == WorkerProxy.IDLE

    @property
    def is_busy(self):
        return self.state == WorkerProxy.BUSY

    @property
    def is_dead(self):
        return self.state == WorkerProxy.DEAD

    @remote_api()
    def execute(self, execution):
        """

        TODO: more documentation
        """
        self._conn.root.execute(execution)
        if not self.is_dead:
            self.state = WorkerProxy.BUSY
            self.scheduled_execution = execution
            return True
        return False

    @remote_api()
    def get_execution_result(self):
        """

        TODO: more documentation
        """
        execution_result = self._conn.root.get_execution_result()
        if execution_result:
            self.state = WorkerProxy.IDLE
            return execution_result
        return None

