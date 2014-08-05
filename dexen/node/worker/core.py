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
import threading
from Queue import Queue, Empty

from dexen.node.worker.executor import TaskExecutor

class WorkerCore(threading.Thread):
    """ The core of each worker. It is a subclass of threading.Thread and has 
    a run method that loops forever, getting pending executions and executing them.

    Attributes
    ----------
    self.daemon: bool
    self._lock: threading.RLock()
    self.pending_executions: Queue()
    self.execution_results:Queue()
    self.worker_name: str
    self.db_client: pymongo.MongoClient
    self.associated_job: str
    self.logger: logger
    """
    def __init__(self, worker_name, db_client, associated_job=None):
        """ Constructs an instance of WorkerCore.
        """
        super(WorkerCore, self).__init__()
        self.daemon = True
        self._lock = threading.RLock()
        self.pending_executions = Queue()
        self.execution_results = Queue()
        self.worker_name = worker_name
        self.db_client = db_client
        self.associated_job = associated_job
        self.logger = logging.getLogger(__name__+"."+self.__class__.__name__+"."+self.worker_name)

    def execute(self, execution):
        """ Puts the execution object into the queue of pending executions. 

        Parameters
        ----------
        execution: dexen.common.task.Execution
        """
        self.logger.debug("queuing execution for task: %s", execution.task.name)
        self.pending_executions.put(execution)

    def get_execution_result(self):
        """ Retrieves the execution result object from the queue of execution results. 

        Returns
        -------
        dexen.common.task.ExecutionResult
        """
        try:
            result = self.execution_results.get_nowait()
        except Empty:
            self.logger.debug("execution result is not ready.")
            return None
        return result

    def run(self):
        """ The run method that loops forever. In the loop, it 
        1) get a pending execution, i.e. dexen.common.task.Execution
        2) creates an instance of dexen.node.worker.executor.TaskExecutor.
        3) calls the execute() method on the task_executor object.
        """
        while True:
            execution = self.pending_executions.get()
            task_executor = TaskExecutor(execution, self.worker_name, self.db_client)
            execution_result = task_executor.execute()
            self.execution_results.put(execution_result)

