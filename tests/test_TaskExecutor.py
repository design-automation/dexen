'''
Created on Aug 8, 2013

@author: Cihat Basol
'''
from dexen.node.worker.executor import TaskExecutor
from dexen.common.db import FileManager
from dexen.common.task import EventTask
from dexen.common.events import JobStartedEvent


'''
Created on Jul 30, 2013

@author: Cihat Basol
'''


import sys
import time
import unittest
import threading


from Queue import Queue

from dexen.common.execution import Execution


class TaskExecutorTestCase(unittest.TestCase):
    def setUp(self):
        file_mgr = FileManager()
        worker_name = "worker1"
        res_q = Queue()
        task1 = EventTask("task1", ["python", "hello_world.py"], JobStartedEvent())
        task1.job_name = "job1"
        execution = Execution(task1)
        self.executor = TaskExecutor(execution, res_q, worker_name, file_mgr)
    
    def tearDown(self):
        pass
    
    def test_1(self):
        self.executor._prepare_context()
    

def do_unittest():
    suite = unittest.TestLoader().loadTestsFromTestCase(TaskExecutorTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)


def main():
    if len(sys.argv) == 1:
        do_unittest()


if __name__ == '__main__':
    main()


