'''
Created on Jul 30, 2013

@author: Cihat Basol
'''


import sys
import time
import unittest
import threading


from dexen.common.task import EventTask
from dexen.common.execution import Execution, ExecutionResult
from dexen.node.worker.core import WorkerCore



def test_func(num):
    for _ in xrange(num):
        print "I am in test_func", num
        time.sleep(1)
    return num*2


class WorkerCoreTestCase(unittest.TestCase):
    def setUp(self):
        self.core = WorkerCore()
    
    def tearDown(self):
        pass
    
    def test_execute(self):
        self.core.start()
        self.assertEqual(threading.active_count(), 2)
        task = EventTask("task1", ["python", "test_WorkerCore.py", "3"], None)
        #execution = Execution("job1", task)
        task.job_name = "job1"
        execution = Execution(task)
        self.core.execute(execution)
        self.assertIsNone(self.core.get_execution_result())
        time.sleep(1)
        self.assertIsNone(self.core.get_execution_result())
        time.sleep(3)
        exec_result = self.core.get_execution_result()
        self.assertIsInstance(exec_result, ExecutionResult)
        #self.assertEqual(exec_result.result, 6)
    

def do_unittest():
    suite = unittest.TestLoader().loadTestsFromTestCase(WorkerCoreTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)


def main():
    if len(sys.argv) == 1:
        do_unittest()
    else:
        num = int(sys.argv[1])
        test_func(num)


if __name__ == '__main__':
    main()


