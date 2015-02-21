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

import time

from dexen.common import db, task
from dexen.server.backend import task_manager as tm

import json

class JobManager(object):
    """ Manages a specific job, including runing and stopping the job, and
    registering and deregistering tasks.

    Attributes
    ----------
    self.user_name: string 
    self.job_name: string
    self.creation_time: int
        A timestamp.
    self.start_time: int
        A timestamp.
    self.stop_time: int
        A timestamp.
    self.state: string
        JobManager.RUNNING or JobManager.STOPPED
    self.event_task_mgr: dexen.server.backend.task_manager.EventTaskManager
        Used for managing all even tasks. 
    self.dataflow_task_mgr: dexen.server.backend.task_manager.DataFlowTaskManager
        Used for managing all dataflow tasks.
    """
    RUNNING = "JOB_RUNNING"
    STOPPING = "JOB_STOPPING"
    STOPPED = "JOB_STOPPED"

    def __init__(self, user_name, job_name, db_client):
        """ Constructs a JobManager. The initial state will be JobManager.STOPPED. 

        db_client is an instance of pymongo.MongoClient. This gets used to create the job data 
        manager, which needs access to the pymongo database.
        """
        self.user_name = user_name
        self.job_name = job_name
        self.db_client = db_client
        self.creation_time = time.time()
        self.start_time = None
        self.stop_time = None
        self.state = JobManager.STOPPED
        self.event_task_mgr = tm.EventTaskManager()
        self.dataflow_task_mgr = tm.DataFlowTaskManager(
                db.JobDataManager(db_client, user_name, job_name))
        self.executions = set()
        self._add_job_info()
        self._read_tasks()

    @property
    def is_running(self):
        """ Return True if this job is running. 
        """
        return self.state == JobManager.RUNNING

    @property
    def is_stopped(self):
        """ Return True if this job is stopped. 
        """
        return self.state == JobManager.STOPPED

    def run(self):
        """ Start this job. 
        """
        self.state = JobManager.RUNNING
        self.start_time = time.time()
        self.event_task_mgr.on_job_start()

    def stop(self):
        """ Stop this job. The job cannot be restarted.
        """
        if self.state == JobManager.RUNNING:
            self.state = JobManager.STOPPING
            self.stop_time = time.time()
            self.event_task_mgr.on_job_stop()

            if len(self.executions) == 0:
                self.state = JobManager.STOPPED

    def delete(self):
        """ Delete this job.
        """
        if self.state != JobManager.STOPPED:
            return False

        db.DeleteAllJobData(self.db_client, self.user_name, self.job_name)
        self._remove_job_info()

        return True

    def register_task(self, task, persist=True):
        """ Register a task. It can be either an event task or a dataflow task. 

        Parameters
        ----------
        task: dexen.common.task.Task
            The task to be registered. It could be an instance of either dexen.common.task.EventTask 
            or dexen.common.task.DataFlowTask. If it is a dataflow task, it will have no input data. 
        """
        if task.is_event_task:
            self.event_task_mgr.register_task(task)
        else:
            self.dataflow_task_mgr.register_task(task)

        if persist:
            self._write_task(task)

    def deregister_task(self, task_name):
        """ Deregisters a task. It can be either an event task or a dataflow task. 

        If the task name is not found,  ???

        Parameters
        ----------
        task_name: string
            The name of the task to be deregistered.
        """
        self.event_task_mgr.deregister_task(task_name)
        self.dataflow_task_mgr.deregister_task(task_name)

    def get_task(self):
        """ Returns the first task that is ready to be executed,
        giving priority to event tasks.

        Returns
        -------
        dexen.common.task.Task
            Could be either dexen.common.task.EventTask or DataFlowTask
        """
        task = self.event_task_mgr.get_task()
        if not task:
            task = self.dataflow_task_mgr.get_task()
        return task

    def undo_get_task(self, task):
        """
        TODO: explain what this is ... rollback?

        Parameters
        ----------
        task: dexen.comon.task.Task
        """
        if task.is_event_task:
            self.event_task_mgr.undo_get_task(task)
        else:
            self.dataflow_task_mgr.undo_get_task(task)

    def on_execution_scheduled(self, execution):
        """ Updates the number of executions that are scheduled.

        This calls on_execution_scheduled() in both the event_task_mgr and the
        dataflow_task_mgr, which increments a counter for the number of
        scheduled executions.

        This method gets called by the _distribute_tasks() method in
        dexen.server.backend.core.ServerCore.

        Parameters
        ----------
        execution: dexen.common.task.Execution
        """
        if execution.task.is_event_task:
            self.event_task_mgr.on_execution_scheduled(execution)
        else:
            self.dataflow_task_mgr.on_execution_scheduled(execution)

        self._add_execution(execution)

    def on_execution_completed(self, scheduled_execution, execution_result):
        """

        This gets called by the _update_workers() method in dexen.server.backend.core.ServerCore.

        TODO: explain what this does ...

        Parameters
        ----------
        scheduled_execution: dexen.common.task.Execution
        execution_result: dexen.common.task.ExecutionResult
        """
        if execution_result.task.is_event_task:
            self.event_task_mgr.on_execution_completed(scheduled_execution,
                                                       execution_result)
        # The even task might have generated data which is used by DataFlow task.
        # Therefore, we still handle the event task in dataflow task manager.
        self.dataflow_task_mgr.on_execution_completed(scheduled_execution,
                                                      execution_result)

        self._remove_execution(scheduled_execution)

    def on_execution_failed(self, execution):
        """
        TODO: explain what this does ... rollback

        Parameters
        ----------
        execution: dexen.common.task.Execution
        """
        if execution.task.is_event_task:
            self.event_task_mgr.on_execution_failed(execution)
        # The even task might have generated data which is used by DataFlow task.
        # Therefore, we still handle the event task in dataflow task manager.
        self.dataflow_task_mgr.on_execution_failed(execution)

        self._remove_execution(execution)

    def json_info(self):
        """ Creates a json representation of this job. 

        Returns
        -------
        dict
        """
        info = {
                "job_name": self.job_name,
                "creation_time": self.creation_time,
                "start_time": self.start_time,
                "stop_time": self.stop_time}
        if self.state == JobManager.RUNNING:
            info["status"] = "RUNNING"
        elif self.state == JobManager.STOPPING:
            info["status"] = "STOPPING"
        else:
            info["status"] = "STOPPED"

        info["event_tasks"] = self.event_task_mgr.json_info()
        info["dataflow_tasks"] = self.dataflow_task_mgr.json_info()
        return info

    def initDataIdCounter(self):
        coll = db.GetJobDataIdCounterCollection(self.db_client, self.user_name, self.job_name)
        coll.insert({"_id" : "data_id", "seq" : 0})

    def _add_execution(self, execution):
        self.executions.add(execution.execution_id);

    def _remove_execution(self, execution):
        self.executions.remove(execution.execution_id);
        if self.state == JobManager.STOPPING and len(self.executions) == 0:
            self.state = JobManager.STOPPED

    def _add_job_info(self):
        doc = {"_id" : self.job_name}
        db.GetJobsInfoCollection(self.db_client, self.user_name).update(doc, doc, True)

    def _remove_job_info(self):
        doc = {"_id" : self.job_name}
        db.GetJobsInfoCollection(self.db_client, self.user_name).remove(doc)

    def _write_task(self, task_obj):
        json_task = task_obj.json(True)

        db.GetJobTasksCollection(self.db_client, self.user_name, self.job_name).insert(json_task)

    def _read_tasks(self):
        task_col = db.GetJobTasksCollection(self.db_client, self.user_name, self.job_name)
        for json_task in task_col.find():
            task_obj = task.TaskFromJSON(json_task, True)
            self.register_task(task_obj, False)

