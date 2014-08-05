'''
Created on Aug 5, 2013

@author: Cihat Basol
'''




import time
import unittest
import threading

from dexen.common.task import EventTask



class EventTaskTestCase(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_1(self):
        task1 = EventTask("task1", ["python", "hello_world.py"], None)
        exec_result = task1.execute()
        print "Stderr:\n", exec_result.stderr
        print "Stdout:\n", exec_result.stdout
        
    


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(EventTaskTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)





