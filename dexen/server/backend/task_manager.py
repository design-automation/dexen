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

import collections
import logging
import threading
import time

from dexen.common import events, exceptions, task

logger = logging.getLogger(__name__)

class _TimeEventThread(threading.Thread):
    """ A thread that fires events at certain points in time. 

    Attributes
    ----------
    self.daemon: bool
    self.event_mgr: ???
    self.task: dexen.common.task.EventTask
    self.event: dexen.common.event.DexenEvent
    self.task_name: str
    self._lock: threading.???
    self.state: str
        _TimeEventThread.RUNNING, STOPPED, or NOT_RUNNING
    """
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    NOT_RUNNING = "NOT_RUNNING" 

    def __init__(self, event_mgr, task):
        super(_TimeEventThread, self).__init__()
        self.daemon = True
        self.event_mgr = event_mgr
        self.task = task
        self.event = task.event
        self.task_name = self.task.name
        self._lock = threading.RLock()
        self.state = _TimeEventThread.NOT_RUNNING

    @property
    def is_running(self):
        with self._lock:
            return self.state == _TimeEventThread.RUNNING

    @property
    def is_periodic(self):
        return isinstance(self.event, events.PeriodicTimeEvent)

    @property
    def was_stopped(self):
        with self._lock:
            return self.state == _TimeEventThread.STOPPED

    def _one_shot(self, after):
        time.sleep(after)
        if self.is_running:
            self.event_mgr.put_task(self.task)

    def _periodic(self, period):
        while True:
            time.sleep(period)
            if not self.is_running:
                break
            self.event_mgr.put_task(self.task)

    def run(self):
        with self._lock:
            self.state = _TimeEventThread.RUNNING
        if self.is_periodic:
            self._periodic(self.event.period)
        else:
            assert isinstance(self.event, events.OneShotTimeEvent)
            self._one_shot(self.event.after)

    def stop(self):
        with self._lock:
            self.state = _TimeEventThread.STOPPED


class _TaskQueue(collections.deque):
    """ Class for representing a queue of tasks.

    Subclasses collections.deque (which is part of the Python standard library). This is a double 
    ended queue that supports adding and removing elements from either end. The subclass just adds 
    a single method to check if the queue is empty.
    """
    def __init__(self, *args, **kwargs):
        """ Constructs a _TaskQueue by calling the constructor for collections.deque.
        """
        super(_TaskQueue, self).__init__(*args, **kwargs)

    def empty(self):
        """ Checks if the queue is empty.

        Returns
        -------
        bool
        """
        try:
            if self[0]:
                pass
        except IndexError:
            return True
        return False

#-----------------------------------------------------------------------------------------------TODO
#TODO: How come we don't keep track of failed executions like we do with data flow tasks?
class EventTaskInfo(object):
    """ Maintains information related to a registered event task. For each registered task, one 
    instance of this class is created. So a task may be executed many times (resulting in many 
    instances of the task being created), but only one task info object is created.

    This task info maintains three counters: num_pending, num_scheduled, and num_executions. The 
    num_pending counter is the number of instances of the task that are waiting to be executed. 
    The num_scheduled counter is the number of instances of the task that have been scheduled (so
    they are either executing now or are about to get executed). The num_executions counter is the
    total number of instances of the task that have been executed. 

    Each time an instance of the task is created, the num_pending counter is incremented. When
    a worker becomes available, the task is then scheduled, resulting in the num_pending counter
    being decremented, and the num_scheduled counter being incremented. Once the task has completed 
    executing, the num_scheduled counter is decremented and the num_Executions in incremented. 

    Instances of this class are created by dexen.server.backend.task_manager.EventTaskManager.

    Attributes
    ----------
    self.task_name: str 
    self.num_executions: int 
    self.total_execution_time: int
    self.registration_time: float, timestamp, seconds since Epoch.
    self.num_pending: int
    self.num_scheduled: int

    """
    def __init__(self, task):
        self.task = task
        self.num_executions = 0
        self.total_execution_time = 0.0
        self.registration_time = time.time()
        self.num_pending = 0
        self.num_scheduled = 0

    #-------------------------------------------------------------------------------------------TODO
    #TODO: why no execution_failed method?

    def on_execution_completed(self, execution_result):
        self.num_executions += 1
        self.num_scheduled -= 1
        self.total_execution_time += execution_result.execution_time

    def on_execution_scheduled(self):
        self.num_pending -= 1
        self.num_scheduled += 1

    def on_task_added(self):
        self.num_pending += 1

    def json(self):
        """

        Returns
        -------
        str
        """
        doc = {}
        doc["task_name"] = self.task.name
        doc["registration_time"] = self.registration_time
        doc["num_executions"] = self.num_executions
        if self.num_executions != 0:
            doc["avg_execution_time"] = self.total_execution_time / self.num_executions
        else:
            doc["avg_execution_time"] = "NONE"
        doc["num_pending"] = self.num_pending
        doc["num_scheduled"] = self.num_scheduled
        return doc

#-----------------------------------------------------------------------------------------------TODO
# TODO: Why is this different from the event based task info. In that case, we just use the task 
# name, while in this case the task info keeps an instance of the task, and then makes clones of 
# this instance.
class DataFlowTaskInfo(object):
    """ Maintains information related to a registered dataflow task. For each registered dataflow 
    task, one instance of this class is created. A task may be executed many times (resulting in 
    many instances of the task being created), but only one task info object is created.

    This task info has an attribute called 'task' that is an instance of 
    dexen.common.task.DataFlowTask. However, this is not an actual task - it is just a task object
    without any input data. Whenever actual task needs to be executed (with input data), the dummy
    task object gets used to make a clone of itself with input data. 

    This info class also handles the data management for dataflow tasks. To do this, 
    it maintains to sets of data (i.e. set() objects): pending_data and scheduled_data. These sets 
    contain object IDs. The pending_data set contains object IDs of objects that have data that is 
    valid (i.e. the task condition returns True) for the registered dataflow task associated with 
    this task info. Once a worker becomes available, a group of IDs get randomly selected and taken 
    out of the pending_data set and put into the scheduled_data set. The size of this group is 
    determined by the input_size setting for the associated dataflow task. Once execution has 
    finished, the group of IDs will get taken out of the scheduled_data set. 

    Instances of this class get created by dexen.server.backend.task_manager.DataFlowTaskManager.

    Attributes
    ----------
    self.task: dexen.common.task.DataFlowTask
    self.registration_time: float, timestamp, seconds since Epoch
    self.num_executions: int
    self.num_scheduled_executions: int
    self.total_execution_time: int
    self.num_failed_executions: int
    self.pending_data: set() of dexen.common.db.DataObjectId
    self.scheduled_data: set() of dexen.common.db.DataObjectId

    """
    def __init__(self, task):
        """ Constructs a DataFlowTaskInfo.
        task is an instance of dexen.common.task.DataFlowTask, to be used for cloning. This task
        should contain no input data.
        """
        self.task = task
        self.registration_time = time.time()
        self.num_executions = 0
        self.num_scheduled_executions = 0
        self.total_execution_time = 0
        self.num_failed_executions = 0
        # The two sets are and must be mutually exclusive.
        self.pending_data = set() # set of DataObjectId
        self.scheduled_data = set() # set of DataObjectId

    def in_scheduled(self, data_id):
        """ Checks to see if the id for a data object is in the self.scheduled_data set.
        Returns
        -------
        bool
        """
        return data_id in self.scheduled_data

    def add_to_pending(self, data_id):
        """ Adds the id of a data object to self.pending_data.

        Parameters
        ----------
        data_id: int
            The id of the data object to be added.
        """
        self.pending_data.add(data_id)

    def remove_from_pending(self, data_ids):
        """ Removes a list of ids for data objects from self.pending_data.

        Parameters
        ----------
        data_id: list of int
            A list of data object ids to be removed.
        """
        self.pending_data.difference_update(set(data_ids))

    def remove_from_scheduled(self, data_ids):
        """ Removes a list of ids for data objects from self.scheduled_data.

        Parameters
        ----------
        data_id: list of int
            A list of data object ids to be removed.
        """
        self.scheduled_data.difference_update(set(data_ids))

    def has_sufficient_data(self):
        """
        Returns
        -------
        bool
        """
        return len(self.pending_data) >= self.task.input_size

    def create_task_with_data(self):
        """ Creates a new task object, and sets the input data. The new task object actually gets 
        created by cloning a dummy task object that has no input data. 

        Returns
        -------
        dexen.common.task.DataFlowTask
        """
        data = list(self.pending_data)[:self.task.input_size]
        data_set = set(data)
        self.pending_data.difference_update(data_set)
        self.scheduled_data.update(data_set)
        return self.task.clone_with_data(data)

    def undo_create_task_with_data(self, data):
        """
        """
        self.pending_data.update(set(data))
        self.scheduled_data.difference_update(set(data))

    def on_execution_scheduled(self):
        """ Increments self.num_scheduled_executions.
        """
        self.num_scheduled_executions += 1

    def on_execution_completed(self, execution_result):
        """ Increments self.num_executions and decrements self.num_scheduled_executions.

        Parameters
        ----------
        execution_result: dexen.common.task.ExecutionResult
            Currently not being used.
        """
        self.num_executions += 1
        self.num_scheduled_executions -= 1
        self.total_execution_time += execution_result.execution_time

    def on_execution_failed(self):
        """ Decrements self.num_scheduled_executions and increments self.num_failed_executions.
        """
        self.num_scheduled_executions -= 1
        self.num_failed_executions += 1

    def __str__(self):
        """ Creates a simple string representation of this task info.

        Returns
        -------
        str
        """
        return """
            task_name: %s
            num_executions: %d
            num_scheduled_executions: %d
            pending data: %s
            processing data: %s\n"""\
            % (self.task.name, self.num_executions, self.num_scheduled_executions,
               self.pending_data, self.scheduled_data)

    def json(self):
        """ Creates a JSON representation of the data in this dataflow task info. 

        Returns
        -------
        str
        """
        info = {}
        info["task_name"] = self.task.name
        info["registration_time"] = self.registration_time
        info["num_executions"] = self.num_executions
        info['num_scheduled_executions'] = self.num_scheduled_executions
        info["num_failed_executions"] = self.num_failed_executions
        if self.num_executions != 0:
            info["avg_execution_time"] = self.total_execution_time / self.num_executions
        else:
            info["avg_execution_time"] = "NONE"
        info["num_pending_data"] = len(self.pending_data)
        info["num_scheduled_data"] = len(self.scheduled_data)
        return info


class TaskManager(object):
    """ Class for managing tasks. This class is suppsed to be subclassed - it contains dummy 
    methods, to be overridden by subclasses.
    """
    def __init__(self):
        pass

    def get_task(self):
        pass

    def undo_get_task(self):
        pass

    def register_task(self, task):
        pass

    def deregister_task(self, task_name):
        pass

    def on_execution_completed(self, scheduled_execution, execution_result):
        pass

    def on_execution_failed(self, execution):
        pass

    def on_execution_scheduled(self, execution):
        pass

    def json_info(self):
        pass


class EventTaskManager(TaskManager):
    """ Manages data related to all registered event tasks. It maintains a queue of tasks, and 
    three dictionaries: one for taks, one for event threads, and one for task infos. 

    The queue is a simple double-ended queue of task objects. Tasks are added to the right of
    the queue, and removed from the left of the queue, so a FIFO queue. These are the actual tasks 
    waiting for execution. 

    The dictionary of tasks is a list of tasks that have been registered. The key is the task name, 
    and the value is the task object. However, these task objects have no input data, they are
    like dummy tasks storing the settings of the registered task, such as command line args and
    input size. 

    A dictionary of event threads...  TODO

    A dictionary of task infos... TODO

    It maintains a dictionary, where 
    the key is the task name, and the value is an instance of 
    dexen.server.backend.task_manager.EventTaskInfo. Each time a new event task gets 
    registered, a new event task info object will be created and added to the dict, 
    and each time a event task is created, scheduled, or executed, the appropriate info object in 
    the dict is updated. 

    One instance of this class gets created in dexen.server.backend.job_manager.

    Attributes
    ----------
    self.queue: _TaskQueue 
        A double ended queue of dexen.common.task.EventTask
    self.tasks: {task_name: dexen.common.task.EventTask, ...}
    self.time_threads: {task_name, dexen.server.backend.task_manager._TimeEventThread}
    self.state: str, either JOB_STARTED or JOB_STARTED
    self.tasks_info: {task_name: dexen.server.backend.task_manager._Task_Info, ...}

    """
    JOB_STARTED = "JobStarted"
    JOB_STOPPED = "JobStopped"

    def __init__(self):
        """ Constructs an EventTaskManager.
        """
        super(EventTaskManager, self).__init__()
        self._lock = threading.RLock()
        self.queue = _TaskQueue()
        self.time_threads = {}
        self.state = EventTaskManager.JOB_STOPPED
        self.tasks_info = {} # task_name : {}

    def put_task(self, task):
        """ Adds an event task to the end (right side) of the task queue.

        Parameters
        ----------
        task: dexen.common.task.EventTask
            The task to be added.
        """
        if self.is_task_registered(task.name):
            self.queue.append(task)
            self.tasks_info[task.name].on_task_added()

    def get_task(self):
        """ Removes and returns an event task from the beginning (left side) of the task queue. 

        Returns
        -------
        dexen.common.task.EventTask
        """
        while not self.queue.empty():
            task = self.queue.popleft()
            if self.is_task_registered(task.name):
                return task
        return None

    def undo_get_task(self, task):
        """ Adds an event task to the beginning (left side) of the task queue. This is used to undo 
        a call to get_task.

        Parameters
        ----------
        task: dexen.common.task.EventTask
            The task to be added.
        """
        self.queue.appendleft(task)

    def has_task(self):
        """ Returns true if the task queue is not empty.  
        """
        return not self.queue.empty()
        #---------------------------------------------------------------------------------------TODO
        #TODO: implement

    def is_task_registered(self, task_name):
        """ Returns true if the name matches one of the registered event tasks.

        Parameters
        ----------
        task_name: str
            The name of the task.
        """
        with self._lock:
            return task_name in self.tasks_info
        #---------------------------------------------------------------------------------------TODO
        #TODO: Clean up time_threads

    def register_task(self, task):
        """ Register a task. If a task with the given name already exists, this task will silently
        overwrite the existing task. 

        Parameters
        ----------
        task: dexen.common.task.EventTask
            The task to register.
        """
        with self._lock:
            if self.is_task_registered(task.name):
                msg = "Task %s already registered" % task.name
                raise exceptions.TaskAlreadyRegisteredException(msg)
            self.tasks_info[task.name] = EventTaskInfo(task)
            if isinstance(task.event, events.TimeBasedEvent):
                self.time_threads[task.name] = _TimeEventThread(self, task)
                if self.state == EventTaskManager.JOB_STARTED:
                    self.time_threads[task.name].start()

    def deregister_task(self, task_name):
        """ Deregister a task.

        Parameters
        ----------
        task_name: str
            The name of the task to deregister.
        """
        with self._lock:
            if not self.is_task_registered(task_name):
                raise exceptions.NonExistentTaskException("Task %s does not exist" % task_name)
            del self.tasks_info[task_name]
            if task_name in self.time_threads:
                self.time_threads[task_name].stop()
                del self.time_threads[task_name]

    def on_job_start(self):
        """ Starts all tasks that are registered to start on a job start event. 
        """
        self.state = EventTaskManager.JOB_STARTED
        for task_info in self.tasks_info.values():
            if isinstance(task_info.task.event, events.JobStartedEvent):
                self.put_task(task_info.task)
        for task_name in self.time_threads:
            if self.time_threads[task_name].was_stopped:
                self.time_threads[task_name] = _TimeEventThread(self, self.tasks_info[task_name].task)
            self.time_threads[task_name].start()

    def on_job_stop(self):
        """ Starts all tasks that are registered to start on a job stop event.
        """
        self.state = EventTaskManager.JOB_STOPPED
        for task_info in self.tasks_info.values():
            if isinstance(task_info.task.event, events.JobStoppedEvent):
                self.put_task(task_info.task)
        for task_name in self.time_threads:
            self.time_threads[task_name].stop()

    def on_execution_scheduled(self, execution):
        """ Updates the data for the event tasks. Calls the on_execution_scheduled() method on the 
        task info object, which updates the counters.

        This method gets called by the on_execution_scheduled() method in 
        dexen.server.backend.job_manager JobManager

        Parameters
        ----------
        execution: dexen.common.task.Execution
        """
        self.tasks_info[execution.task_name].on_execution_scheduled()

    #-------------------------------------------------------------------------------------------TODO
    # TODO: the scheduled_execution arg is not used???
    def on_execution_completed(self, scheduled_execution, execution_result):
        """ Updates the data for the event tasks. Calls the on_execution_completed() method on the 
        task info object for the task that completed execution, which updates the counters and 
        the total execution time.

        Parameters
        ----------
        scheduled_execution: dexen.common.task.Execution
        execution_result: dexen.common.task.ExecutionResult
            The result of the execution, which wraps that task object that was executed. 
        """
        task_name = execution_result.task_name
        assert task_name in self.tasks_info
        self.tasks_info[task_name].on_execution_completed(execution_result)

    def on_execution_failed(self, execution):
        """ Not implemented.

        Parameters
        ----------
        execution: dexen.common.task.Execution
        """
        #---------------------------------------------------------------------------------------TODO
        pass

    def json_info(self):
        """ Creates a json representation of all the task_info objects in the tasks_info dict.

        Returns
        -------
        str
        """
        res = []
        for task_info in self.tasks_info.values():
            res.append(task_info.json())
        return res



class DataFlowTaskManager(TaskManager):
    """ Manages data related to all registered dataflow tasks. It maintains a dictionary, where 
    the key is the task name, and the value is an instance of 
    dexen.server.backend.task_manager.DataFlowTaskInfo. Each time a new dataflow task gets 
    registered, a new dataflow task info object will be created and added to the dict, 
    and each time a dataflow task is created, scheduled, or executed, the appropriate info object 
    in the dict is updated. 

    One instance of this class gets created in dexen.server.backend.job_manager.

    Attributes
    ----------
    self.data_mgr: dexen.common.db.JobDataManager
        Used to connect with the mongodb database.
    self.tasks_info: dict
        {task_name: dexen.server.backend.task_manager.DataFlowTaskInfo, ...}
    self.logger: 
    """
    def __init__(self, job_data_mgr):
        """ Construct a DataFlowTaskManager.
        """
        super(DataFlowTaskManager, self).__init__()
        self.data_mgr = job_data_mgr
        self.tasks_info = {}  # task_name: DataFlowTaskInfo
        self.logger = logging.getLogger(__name__+"."+self.__class__.__name__)

    def get_task(self):
        """ Return the first dataflow task with sufficient data. 
        """
        self.logger.debug("Trying to get a Dataflow task.")
        for task_info in self.tasks_info.values():
            if task_info.has_sufficient_data():
                self.logger.debug("returning the DataFlow task.")
                return task_info.create_task_with_data()
        self.logger.debug("There is not sufficient to create a DataFlow task.")
        return None

    def undo_get_task(self, task):
        """ 

        TODO: document this - must be to do with roll back

        Parameters
        ----------
        task: dexen.common.task.Task
        """
        self.logger.debug("Could not schedule the dataflow task so putting it back.")
        self.tasks_info[task.name].undo_create_task_with_data(task.input_data)

    def is_task_registered(self, task_name):
        return task_name in self.tasks_info

    def register_task(self, task):
        """ Register a new task. The task must have a unique name. A dataflow task info will be 
        created and added to the dict of task infos. 

        Parameters
        ----------
        task: dexen.common.task.Task
        """
        if self.is_task_registered(task.name):
            msg = "Task %s already registered." % task.name
            raise exceptions.TaskAlreadyRegisteredException(msg)
        self.tasks_info[task.name] = DataFlowTaskInfo(task)

    def deregister_task(self, task_name):
        """ Deregister an existing task. The dataflow task info object will be removed from the dict 
        of task infos. 

        Parameters
        ----------
        task_name: str
        """
        if not self.is_task_registered(task_name):
            raise exceptions.NonExistentTaskException("Task %s does not exist" % task_name)
        del self.tasks_info[task_name]

    def _add_to_pending_if_valid(self, task_info, ids):
        """ Checks if a list of data objects are valid for the condition of a dataflow task, and
        oif they are valid, adds the IDs to the pending set for that dataflow task.  

        Parameters
        ----------
        task_info: dexen.common.task.DataFlowTaskInfo
            The task info for the dataflow task.
        ids: list of int
            A list of IDs of data objects.

        """
        task_condition = task_info.task.condition
        filtered_ids = self.data_mgr.filter_ids(ids, task_condition)
        self.logger.debug("filtered ids still valid for %s: %s",
                          task_info.task.name, filtered_ids)
        for data_id in filtered_ids:
            if not task_info.in_scheduled(data_id):
                task_info.add_to_pending(data_id)

    def on_execution_scheduled(self, execution):
        """ Updates the data for the event tasks. Calls the on_execution_scheduled() method on the 
        task info object, which updates the counters.

        This method gets called by the on_execution_scheduled() method in 
        dexen.server.backend.job_manager JobManager

        Parameters
        ----------
        execution: dexen.common.task.Execution
        """
        self.logger.info("on execution %s with task: %s scheduled",
                         execution.execution_id, execution.task.name)
        self.tasks_info[execution.task.name].on_execution_scheduled()

    def on_execution_completed(self, scheduled_execution, execution_result):
        """ Updates the data for the event tasks. Calls the on_execution_completed() method on the 
        task info object for the task that completed execution, which updates the counters and 
        the total execution time.

        TODO: more documentation to explain what is happening
        The matching process starts here... 

        Parameters
        ----------
        scheduled_execution: dexen.common.task.Execution
        execution_result: dexen.common.task.ExecutionResult
        """
        execution_id = execution_result.execution_id
        self.logger.info("on execution %s with task: %s completed",
                         execution_id, scheduled_execution.task.name)
        # Check that input_data still holds the original data ids sent for execution.
        if scheduled_execution.task.is_dataflow_task:
            input_ids = scheduled_execution.task.input_data
            task_info = self.tasks_info[execution_result.task_name]
            task_info.on_execution_completed(execution_result)
            task_info.remove_from_scheduled(input_ids)
            # Do the data object matching process
            self._add_to_pending_if_valid(task_info, input_ids)

        modified_ids = self.data_mgr.get_ids_being_modified(execution_id)
        self.logger.debug("Modified ids by execution %s: %s", execution_id, modified_ids)
        self.data_mgr.remove_execution_ids(modified_ids, execution_id)
        # Remove all the modified ids from all the pending queues.
        for task_info in self.tasks_info.values():
            task_info.remove_from_pending(modified_ids)
        # Put back the modified ids into the pending queues that still satisfies the task condition.
        for task_info in self.tasks_info.values():
            # Do the data object matching process
            self._add_to_pending_if_valid(task_info, modified_ids)

        self.logger.debug("Listing all the tasks info.")
        for task_info in self.tasks_info.values():
            self.logger.info(task_info)

    def on_execution_failed(self, execution):
        """

        TODO: more documentation

        Parameters
        ----------
        execution: dexen.common.task.Execution
        """
        self.logger.info("on execution %s with task: %s failed.",
                         execution.execution_id, execution.task.name)

        execution_id = execution.execution_id

        self.data_mgr.rollback(execution_id)

        if execution.task.is_dataflow_task:
            input_ids = execution.task.input_data
            task_info = self.tasks_info[execution.task_name]
            task_info.on_execution_failed()
            task_info.remove_from_scheduled(input_ids)
            # Do the data object matching process
            self._add_to_pending_if_valid(task_info, input_ids)

    def json_info(self):
        """ Creates a json representation of all the dataflow task info objects in the dict of task 
        infos. 

        Returns
        -------
        str
        """
        return [task_info.json() for task_info in self.tasks_info.values()]
