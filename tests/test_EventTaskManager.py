'''
Created on Jul 30, 2013

@author: Cihat Basol
'''



import time
import unittest
import threading

from dexen.common.task import EventTask
from dexen.server.task_manager import EventTaskManager
from dexen.common.events import (JobStartedEvent, JobStoppedEvent,
                                 PeriodicTimeEvent)



class EventTaskManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.event_mgr = EventTaskManager()
    
    def tearDown(self):
        pass
    
    def test_jobstartedevent(self):
        task1 = EventTask("task1", ["python", "hello_world.py"], JobStartedEvent())
        self.event_mgr.register_task(task1)
        self.assertIsNone(self.event_mgr.get_task())
        self.event_mgr.on_job_start()
        task = self.event_mgr.get_task()
        self.assertEqual(task, task1)
    
    def test_jobstoppedevent(self):
        task1 = EventTask("task1", ["python", "hello_world.py"], JobStoppedEvent())
        self.event_mgr.register_task(task1)
        self.assertIsNone(self.event_mgr.get_task())
        self.event_mgr.on_job_start()
        self.assertIsNone(self.event_mgr.get_task())
        self.event_mgr.on_job_stop()
        task = self.event_mgr.get_task()
        self.assertEqual(task, task1)

    def test_periodictimeevent(self):
        task1 = EventTask("task1", ["python", "hello_world.py"], PeriodicTimeEvent(1))
        self.event_mgr.register_task(task1)
        time.sleep(2)
        self.assertIsNone(self.event_mgr.get_task())
        self.assertEqual(threading.active_count(), 1)
        self.event_mgr.on_job_start()
        self.assertEqual(threading.active_count(), 2)
        self.assertIsNone(self.event_mgr.get_task())
        self.event_mgr.on_job_stop()
        time.sleep(2)
        self.assertIsNone(self.event_mgr.get_task())
        self.assertEqual(threading.active_count(), 1)
        
        self.event_mgr.on_job_start()
        self.assertEqual(threading.active_count(), 2)
        self.assertIsNone(self.event_mgr.get_task())
        self.event_mgr.deregister_task(task1.name)
        time.sleep(2)
        self.assertEqual(threading.active_count(), 1)
        self.assertIsNone(self.event_mgr.get_task())
        self.event_mgr.on_job_stop()
        
"""
    def test_periodictimeevent2(self):
        task1 = EventTask("job1", "task1", func1, PeriodicTimeEvent(1), args=[])
        self.event_mgr.register_task(task1)

        task = self.event_mgr.get_task()
        self.assertEqual(task, task1)
        self.event_mgr.on_job_stop()
        #time.sleep()
"""

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(EventTaskManagerTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)




