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

import json
import logging
import shlex
import subprocess
import tempfile
import time

from dexen.common import constants
from dexen.common import events


logger = logging.getLogger(__name__)

#-----------------------------------------------------------------------------------------------TODO
#TODO: can't this be a method in the Task class, or its subclasses
def TaskFromJSON(json):
    """ Creates an instance of either EventTask or DataFlowTask from a json representation.
    """
    task_name = json.get("task_name", None)
    cmd_args = json.get("cmd_args", None)
    assert task_name is not None
    assert cmd_args is not None
    event_json = json.get("event", None)
    if event_json:
        event = events.EventFromJSON(event_json)
        return EventTask(task_name, cmd_args, event)
    # Else it is a dataflow task
    condition = json.get("condition", None)
    input_size = json.get("input_size", None)
    assert condition is not None
    assert input_size is not None
    return DataFlowTask(task_name, cmd_args, condition, input_size)

#-----------------------------------------------------------------------------------------------TODO
#TODO: why not put this in DataFlowTask.clone_with_data()
def CreateDataFlowTaskWithData(self, dataflow_task, input_data):
    """ Clones an new DataFlowTask from an existing DataFlowTask, an sets the input data. 
    """
    result = DataFlowTask(dataflow_task.name, dataflow_task.cmd_args,
                          dataflow_task.condition, dataflow_task.input_size)
    result.set_input_data(input_data)
    return result


class Task(object):
    """ A task to be executed. 

    Attributes
    ----------
    self.name: str 
        A unique name for the task.
    self.cmd_args: list of str 
        Command line args for executing the task.
    """
    EVENT_TASK = "EVENT_TASK"
    DATAFLOW_TASK = "DATAFLOW_TASK"

    def __init__(self, name, cmd_args):
        """ Constructs a Task. This constructor gets called by the subclass constructors for both 
        EventTask and DataFlowTask. 

        Parameters
        ----------
        name: str
            A unique name for the task
        cmd_args: list of str
            A list of command line arguments used to execute the task. 
        """
        self.name = name
        # print "cmd args type:", type(cmd_args)
        if isinstance(cmd_args, str) or isinstance(cmd_args, unicode):
            # print "splitting cmd args"
            cmd_args = shlex.split(cmd_args)
        # print "cmd args type:", type(cmd_args)
        assert isinstance(cmd_args, list)
        self.cmd_args = cmd_args

    @property
    def is_event_task(self):
        return self.type == Task.EVENT_TASK

    @property
    def is_dataflow_task(self):
        return self.type == Task.DATAFLOW_TASK

    def execute(self, env):
        """ Executes this task by creating a sub-process, executing the command line args, and then 
        polling the process to see if it has finished. 

        Parameters
        ----------
        env: dict
            A dict of env parameters. See the _setup_env() method in 
            dexen.node.worker.executor.TaskExecutor.

        """
        self.stdout = ""
        self.stderr = ""
        self.begin_time = time.time()

        # Temporary fix for unicode problem on windows
        # http://stackoverflow.com/questions/12253014/why-does-popen-fail-on-windows-if-the-env-parameter-contains-a-unicode-object
        # http://stackoverflow.com/questions/13101653/python-convert-complex-dictionary-of-strings-from-unicode-to-ascii
        """
        # Only works with 2.7 and above
        def convert(input):
            if isinstance(input, dict):
                return {convert(key): convert(value) for key, value in input.iteritems()}
            elif isinstance(input, list):
                return [convert(element) for element in input]
            elif isinstance(input, unicode):
                return input.encode('utf-8')
            else:
                return input
        """
        def convert(input):
            if isinstance(input, dict):
                return dict((convert(key), convert(value)) for key, value in input.iteritems())
            elif isinstance(input, list):
                return [convert(element) for element in input]
            elif isinstance(input, unicode):
                return input.encode('utf-8')
            else:
                return input
        env = convert(env)

        try:
            # Note that when the with block exits, the tempfile will be automatically closed and
            # deleted.
            with tempfile.TemporaryFile() as err_file, tempfile.TemporaryFile() as out_file:
                # The nameless temporary files are used instead of pipes as pipe may lead to
                # deadlock when internal pipe buffer overflows.
                proc = subprocess.Popen(self.cmd_args, stdout=out_file, stderr=err_file, env=env)
                unused_stdout, unused_stderr = proc.communicate()
                # The tempfiles are open in both read/write mode. At this point the cursor in the
                # file points to byte after the last written byte, therefore we need to seek the
                # cursor to the beginning of the file.
                out_file.seek(0)
                err_file.seek(0)
                self.stdout = out_file.read()
                self.stderr= err_file.read()
        except Exception as exc:
            self.stderr = str(exc)
            logger.exception("Exception occurred.")
        finally:
            self.end_time = time.time()


class EventTask(Task):
    """ An event based task that subclasses dexen.common.Task. 

    Attributes
    ----------
    self.name: str 
        A unique name for the task.
    self.cmd_args: list of str 
        Command line args for executing the task.
    self.type: str
        Set to Task.EVENT_TASK
    self.event: dexen.common.events.Event 
        The event that will trigger this task. 
    """
    def __init__(self, name, cmd_args, event):
        """ Constructs an instance of EventTask.

        Parameters
        ----------
        name: str
            A unique name for the task.
        cmd_args: list of str
            Command line args for executing the task.
        event: dexen.common.events.Event 
            The event that will trigger this task. 
        """
        super(EventTask, self).__init__(name, cmd_args)
        self.type = Task.EVENT_TASK
        self.event = event

    def execute(self, env):
        """ Executes this task by calling the superclass execute() method. The superclass execute 
        creates a sub-process and executes the command line args.

        Parameters
        ----------
        env: dict
            A dict of env parameters. See the _setup_env() method in 
            dexen.node.worker.executor.TaskExecutor.
        """
        super(EventTask, self).execute(env)

    def json(self):
        """ Creates a json representation of the name, command line args, and the event. 

        Returns
        -------
        dict
        """
        return {
            "task_name" : self.name,
            "cmd_args" : self.cmd_args,
            "event" : self.event.json()
        }


class DataFlowTask(Task):
    """ An dataflow task that subclasses dexen.common.Task.

    Attributes
    ----------
    self.name: str 
        A unique name for the task.
    self.cmd_args: list of str 
        Command line args for executing the task.
    self.condition: dict
        The condition that data objects must satisfy in order to be processed by this task. 
    self.type: str
        Set to Task.DATAFLOW_TASK
    self.input_size: int
        The total number of data objects required to be processed by this task. 
    self.input_data: list of int
        List of IDs of data objects.
    """
    def __init__(self, name, cmd_args, condition, input_size):
        """ Constructs a DataFlowTask. 

        Parameters
        ----------
        name: str
            A unique name for the task. 
        cmd_args: list of str
            A list of command line arguments used to execute the task. 
        condition: dict
            The condition that data objects must satisfy in order to be processed by this task. 
        input_size: int
            The total number of data objects required to be processed by this task. 
        """
        super(DataFlowTask, self).__init__(name, cmd_args)
        self.condition = condition
        self.type = Task.DATAFLOW_TASK
        self.input_size = input_size
        self.input_data = [] # list of DataObjectId

    def set_input_data(self, input_data):
        """ Sets the ids of the data objects to be processed by this task.

        Parameters
        ----------
        input_data: list of int
            A list of ids of data objects
        """
        self.input_data = input_data

    def clone_with_data(self, input_data):
        """ Create a clone of this dataflow task, and set the input data. The cloned task will have
        the same name, command line args, condition, and input size as this task, but the input data
        will be different.

        Parameters
        ----------
        input_data: list of int
            A list of ids of data objects
        """
        cloned_task = DataFlowTask(self.name, self.cmd_args, self.condition, self.input_size)
        cloned_task.set_input_data(input_data)
        return cloned_task

    def execute(self, env):
        """ Execute this task. The input data is saved as jason data and added to the env dict. 
        This env dict is then passed onto the execute method of the superclass. The superclass 
        execute creates a sub-process and executes the command line args.

        Parameters
        ----------
        env: dict
            A dict of env parameters. See the _setup_env() method in 
            dexen.node.worker.executor.TaskExecutor.
        """
        input_data = [data.to_json_dict() for data in self.input_data]
        env[constants.ENV_TASK_INPUT_JSON] = json.dumps(input_data)
        super(DataFlowTask, self).execute(env)

    def json(self):
        """ Creates a json representation of the name, command line args, condition, and the input
        size. The input data is not included.

        Returns
        -------
        dict
        """
        return {
            "task_name" : self.name,
            "cmd_args" : self.cmd_args,
            "condition" : self.condition,
            "input_size" : self.input_size
        }


class Execution(object):
    """ Warps a task instance and provides an execute method. 

    The ServerCore in the backend creates instances of this class. In ServerCore, the run() method
    calls the _distribute_tasks() method, which then loops doing the following. It gets a job 
    manager, asks the job manager for a task object, get the execution manager (see 
    dexen.common.db.ExecutionManager), and calls the create_execution() method, passing in the 
    task object as one of the arguments (but leaving task_data as None). This then creates an 
    execution object, i.e. an instance of this Execution class.

    The _distribute_tasks() method then gets an idle worker object (an instance of 
    dexen.server.backend.proxy.WorkerProxy). It then calls the execute method, passing in the
    execution object.

    TODO: explain how the execution object then gets serialized and sent to the actual worker and
    executed.

    self.execution_id: int
        A unique ID for each execution. The IDs are managed by dexen.common.db.ExecutionManager.
    self.user_name: str
    self.job_name: str
    self.worker_name: str
    self.task: dexen.common.task.Task
        The task that was executed, either EventTask or DataFlowTask.
    self.task_name: str
    self.creation_time: int, timestamp
    """
    # ------------------------------------------------------------------------------------------TODO
    # It seems that task_data arg in the constructor is never used.
    def __init__(self, execution_id, user_name, job_name, worker_name, task):
        """ Constructs an instance of Execution.

        Parameters
        ----------
        execution_id: int
            A unique id for each execution. (Created by dexen.common.db.ExecutionManager.)
        user_name: str
        job_name: str
        worker_name: str
            The name of an idle worker.
        task: dexen.common.task.Task
            Could be either dexen.common.task.EventTask or DataFlowTask. 
        """
        self.execution_id = execution_id
        self.user_name = user_name
        self.job_name = job_name
        self.worker_name = worker_name
        self.task = task
        self.task_name = self.task.name
        self.creation_time = time.time()

    def execute(self, env):
        """Execute the assigned task.
        
        Invoked in dexen.node.worker.Worker but the object is originally created in the ServerCore.

        Parameters
        ----------
        env: dict
            A dict of env parameters. See the _setup_env() method in 
            dexen.node.worker.executor.TaskExecutor.
        """
        env[constants.ENV_USER_NAME] = self.user_name
        env[constants.ENV_JOB_NAME] = self.job_name
        env[constants.ENV_EXECUTION_ID] = str(self.execution_id)
        self.task.execute(env)
        return ExecutionResult(self.execution_id, self.user_name, self.job_name, self.task)


class ExecutionResult(object):
    """The result of a task execution. Wraps the task object that was executed. The data that was 
    generated when executing the task is written straight to the mongodb database and is therefore 
    not stored in instances of this class. Only the stdout and stderr resulting from executing the 
    task are stored.

    Instances of this class get created by the execute() method in the dexen.common.task.Execution 
    class.

    self.execution_id: int
        A unique id for each execution. (Created by dexen.common.db.ExecutionManager.)
    self.user_name: str 
    self.job_name: str 
    self.task: dexen.common.task.Task
        The task that was executed, either EventTask or DataFlowTask
    self.task_name: str 
    self.begin_time: int, timestamp
    self.end_time: int, timestamp
    self.stdout: str 
    self.stderr: str 
    """
    def __init__(self, execution_id, user_name, job_name, task):
        """ Constructs an instance of ExecutionResult.

        Parameters
        ----------
        execution_id: int
        user_name: str
        job_name: str
        task: dexen.common.task.Task
            The task that was executed. Could be either dexen.common.task.EventTask or DataFlowTask.

        """
        self.execution_id = execution_id
        self.user_name = user_name
        self.job_name = job_name
        self.task = task
        self.task_name = task.name
        self.begin_time = task.begin_time
        self.end_time = task.end_time
        self.stdout = task.stdout
        self.stderr = task.stderr
    
    @property
    def execution_time(self):
        return self.end_time - self.begin_time
