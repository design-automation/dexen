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
import os
import time
import zipfile

from dexen.common.constants import ENV_DB_IP, ENV_DB_PORT
from dexen.common.db import FileManager
from dexen.node import env_mgr

_last_update_time = 0

class TaskExecutor(object):
    """ Manages the environment in order to enable a task to be executed. One instance of this class
    gets created for every task execution. The task could be either an EventTaks or a DataFlowTask.

    Instances of this class get created by the run() method in dexen.node.worker.core.WorkerCore.

    Attributes
    ----------
    self.execution: dexen.common.task.Execution
    self.task: dexen.common.task.Task
    self.worker_name: str
    self.db_client: pymongo.MongoClient
    self.logger: logger
    self.file_mgr: dexen.common.db.FileManager
    """
    def __init__(self, execution, worker_name, db_client):
        """ Constructs an instance of TaskExecutor.
        """
        self.execution = execution
        self.task = execution.task
        self.worker_name = worker_name
        self.db_client = db_client
        self.logger = logging.getLogger(__name__+"."+self.__class__.__name__+"."+self.worker_name)
        self.file_mgr = FileManager(db_client, execution.user_name)

    def _extract_zip(self, f):
        """ Unzip a file in read mode.
        
        Parameters
        ----------
        f: file
            The file to unzip.
        """
        z = zipfile.ZipFile(f, mode="r")
        z.extractall()

    def _prepare_context(self):
        """

        TODO: add documentation
        """
        global _last_update_time
        rootdir = env_mgr.get_job_dir(self.worker_name,
                                      self.execution.user_name,
                                      self.execution.job_name, create=True)
        self.last_dir = os.getcwd()
        os.chdir(rootdir)
        self.logger.debug("The rootdir is: %s", rootdir)
        file_names = self.file_mgr.get_recent_files(self.execution.job_name, _last_update_time)
        _last_update_time = time.time()
        for file_name in file_names:
            self.logger.info("Retrieving file %s", file_name)
            remote_file = self.file_mgr.get_file(self.execution.job_name, file_name)
            if file_name.endswith(".zip"):
                self._extract_zip(remote_file)
            else:
                with open(file_name, "wb") as f:
                    f.write(remote_file.read())
                remote_file.close()

    def _restore_context(self):
        """

        TODO: add documentation
        """
        os.chdir(self.last_dir)

    def _setup_env(self):
        """
        
        TODO: add documentation
        """
        env = {}
        env[ENV_DB_IP] = str(self.db_client.host)
        env[ENV_DB_PORT] = str(self.db_client.port)
        for key, value in os.environ.iteritems():
            if key not in env:
                env[key] = value
        return env

    def execute(self):
        """ Sets up the environment and then calls the execute() method in 
        dexen.common.task.Execution. Once execution has completed, it will then put the results (
        i.e. and instance of dexen.common.task.ExecutionResult) into the results queue. 
        
        This method gets called in the run() method in dexen.node.worker.core.WorkerCore. The 
        results queue in instances of this class are actually the same as in WorkerCore. (When 
        WorkerCore constructs instances of this class, it passes in the results queue in the
        constructor.)
        """
        self.logger.info("executing %s", self.task.name)
        self._prepare_context()
        env = self._setup_env()
        exec_result = self.execution.execute(env) #this call is blocking
        self._restore_context()
        self.logger.info("executing %s is done", self.task.name)
        return exec_result
