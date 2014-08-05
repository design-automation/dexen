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
import threading

from dexen.common import db
from dexen.server.backend import job_manager as jm, proxy


logger = logging.getLogger(__name__)


class ServerCore(threading.Thread):
    """ The core of the Dexen backend. It is a subclass of threading.Thread and has 
    a run method that loops forever, checking on nodes and wrokers and distributing tasks.

    Attributes
    ----------
    self.name - a string
    self.resource_mgr - dexen.server.backend.resource_manager.ResouceManager
    self.db_client - pymongo.MongoClient
    self.nodes - [dexen.server.backend.proxy.NodeProxy, ...]
    self.generic_workers - [dexen.server.backend.proxy.WorkerProxy, ...]
    self.job_mgrs - {(user_name, job_name) : dexen.server.backend.job_manager.JobManager, ...}
    self.execution_mgrs - {(user_name, job_name) : dexen.common.db.ExecutionManager, ...}
    """
    def __init__(self, resource_mgr, db_client):
        super(ServerCore, self).__init__()
        self._lock = threading.RLock()
        self.name = "ServerCore"
        self.resource_mgr = resource_mgr
        self.db_client = db_client
        self.nodes = [] # NodeProxy
        self.generic_workers = [] # WorkerProxy
        self.job_mgrs = {} # (user_name, job_name) : JobManager
        self.execution_mgrs = {} # (user_name, job_name) : ExecutionManager


    def run(self):
        """The run method that loops forever. In the loop, it 
        1) discovers new nodes and workers
        2) retrieves results from busy workers
        3) distributes new tasks to idle workers 
        """
        while True:
            with self._lock:
                self._discover_resource()
                self._update_workers()
                self._distribute_tasks()
            time.sleep(1)

    def _discover_resource(self):
        """
        Looks for new nodes and workers using the resource manager. If a new node is found, then 
        a new node proxy is created and appended to the list of node proxies. If a new worker is 
        found, the a worker proxy is created and appended to the list of worker proxies. 
        """
        logger.info("Discovering Nodes and Workers...")
        # Discover nodes
        for node_name, node_addr in self.resource_mgr.get_new_nodes():
            logger.info("Node: %s is discovered.", node_name)
            node_proxy = proxy.NodeProxy(node_name, node_addr)
            num_workers = node_proxy.num_workers()
            logger.info("Starting %d worker on %s", num_workers, node_name)
            for _ in xrange(num_workers):
                node_proxy.start_worker(self.resource_mgr.next_worker_name())
            self.nodes.append(node_proxy)
        # Discover workers
        for worker_name, worker_addr in self.resource_mgr.get_new_workers():
            worker_proxy = proxy.WorkerProxy(worker_name, worker_addr)
            self.generic_workers.append(worker_proxy)

    def _update_workers(self):
        """
        Looks at each worker that is currenly busy and get the execution result. If the result is
        None, then it means the worker has not finished execution yet. If it is not None, then the 
        worker has finished and retrieving the result will set the state of the worker to idle. In
        the latter case, the execution manager and the job manager are then updated with the new 
        execution result.

        The job manager is in dexen.server.backend.job_manager.JobManager. It includes instances 
        of EventTaskManager and DataFlowTaskManager (both in dexen.server.backend.task_mamager). 
        """
        for worker in self.generic_workers:
            assert isinstance(worker, proxy.WorkerProxy)
            if worker.is_busy:
                scheduled_execution = worker.scheduled_execution
                key = (scheduled_execution.user_name, scheduled_execution.job_name)
                job_mgr = self.job_mgrs[key]
                execution_mgr = self.execution_mgrs[key]
                execution_result = worker.get_execution_result() #changes worker to idle
                if execution_result:
                    assert worker.is_idle
                    assert scheduled_execution.user_name == execution_result.user_name
                    assert scheduled_execution.job_name == execution_result.job_name
                    execution_mgr.update_execution(execution_result)
                    job_mgr.on_execution_completed(scheduled_execution,
                                                   execution_result)
                if worker.is_dead:
                    execution_mgr.update_failed_execution(scheduled_execution)
                    job_mgr.on_execution_failed(scheduled_execution)

    def _find_available_generic_worker(self):
        """ Returns the first idle worker it finds, an instance of 
        dexen.server.backend.proxy.WorkerProxy.
        """
        for worker in self.generic_workers:
            if worker.is_idle:
                return worker
        return None

    def _distribute_tasks(self):
        """ Method that send tasks to workers.

        TODO: Needs more dcumentation.
        """
        #---------------------------------------------------------------------------------------TODO
        jobs_for_generic = [job for job in self.job_mgrs.values()]
                            #if job.job_name not in self.job_specific_workers]

        workers_available = True
        while workers_available:
            task_available = False
            for job_mgr in jobs_for_generic:
                if not job_mgr.is_running:
                    continue
                task = job_mgr.get_task()
                if task is None:
                    continue
                # Has task to execute
                logger.info("Job %s has task to execute", job_mgr.job_name)
                task_available = True
                # Trying to send the task to a worker for execution
                while True:
                    worker = self._find_available_generic_worker()
                    if not worker:
                        logger.info("No worker available")
                        workers_available = False
                        break

                    exec_mgr = self.execution_mgrs[(job_mgr.user_name,
                                                    job_mgr.job_name)]
                    execution = exec_mgr.create_execution(worker.name, task)
                    if worker.execute(execution):
                        exec_mgr.save_execution(execution)
                        job_mgr.on_execution_scheduled(execution)
                        break
                    else:
                        exec_mgr.prev_id() # decrement the id back.

                # If no workers available, put back the task
                if not workers_available:
                    job_mgr.undo_get_task(task)
                    break
            if not task_available:
                break


    #===========================================================================
    # INVOKED BY THE ENDPOINT THREAD
    #===========================================================================
    def create_job(self, user_name, job_name):
        with self._lock:
            field = (user_name, job_name)
            logger.info("create_job: user_name=%s job_name=%s", user_name,
                        job_name)
            if field in self.job_mgrs:
                logger.info("%s is already created so not creating job.",
                            job_name)
                return False
            self.job_mgrs[field] = jm.JobManager(user_name, job_name,
                                              self.db_client)
            self.execution_mgrs[field] = db.ExecutionManager(self.db_client,
                                                             user_name,
                                                             job_name)

    def delete_job(self, user_name, job_name):
        pass

    def run_job(self, user_name, job_name):
        with self._lock:
            field = (user_name, job_name)
            logger.info("run_job: user_name=%s job_name=%s", user_name,
                        job_name)
            if field not in self.job_mgrs:
                logger.info("%s does not exist so cannot run job.", job_name)
                return
            self.job_mgrs[field].run()

    def stop_job(self, user_name, job_name):
        with self._lock:
            field = (user_name, job_name)
            logger.info("stop_job: user_name=%s job_name=%s", user_name,
                        job_name)
            if field not in self.job_mgrs:
                logger.info("%s does not exist so cannot stop job.", job_name)
                return
            self.job_mgrs[field].stop()

    def get_jobs(self, user_name):
        with self._lock:
            logger.info("get_jobs for user: %s", user_name)
            jobs = []
            for job_mgr in self.job_mgrs.values():
                if job_mgr.user_name == user_name:
                    jobs.append(job_mgr.json_info())
            return jobs

    def get_tasks(self, user_name, job_name):
        with self._lock:
            res = {}
            logger.info("get_tasks for user: %s, job: %s", user_name, job_name)
            info = self.job_mgrs[(user_name, job_name)].json_info()
            res["dataflow_tasks"] = info["dataflow_tasks"]
            res["event_tasks"] = info["event_tasks"]
            return res

    def register_task(self, user_name, job_name, task):
        with self._lock:
            logger.info("register_task: user_name=%s job_name=%s task_name:%s",
                        user_name, job_name, task.name)
            field = (user_name, job_name)
            task.job_name = job_name
            if field not in self.job_mgrs:
                logger.info("job:%s does not exist so cannot register task.",
                            job_name)
                return
            self.job_mgrs[field].register_task(task)

    def deregister_task(self, user_name, job_name, task_name):
        with self._lock:
            logger.info("deregister_task: user_name=%s job_name=%s task_name:%s",
                        user_name, job_name, task_name)
            field = (user_name, job_name)
            if field not in self.job_mgrs:
                logger.info("job:%s does not exist so cannot deregister task.",
                            job_name)
                return
            self.job_mgrs[field].deregister_task(task_name)

    def register_node(self, address):
        with self._lock:
            return self.resource_mgr.register_node(address)

    def register_worker(self, address, worker_name):
        with self._lock:
            self.resource_mgr.register_worker(address, worker_name)

