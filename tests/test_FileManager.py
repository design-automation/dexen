'''
Created on Aug 7, 2013

@author: Cihat Basol
'''


import sys
import time
import unittest
import threading
from datetime import datetime

from dexen.common.db import FileManager
from dexen.common import constants





class FileManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.filemgr = FileManager("User1", "localhost", constants.MONGOD_PORT)
    
    def tearDown(self):
        pass
    
    def test_1(self):
        job_name = "job1"
        file_name = "test1.txt"
        self.filemgr.put_data(job_name, file_name, "deniyorum")
        f = self.filemgr.get_file(job_name, file_name)
        data = f.read()
        self.assertEqual(data, "deniyorum")
        
        job_name = "job2"
        self.filemgr.put_data(job_name, file_name, "deniyorum2")
        f = self.filemgr.get_file(job_name, file_name)
        data = f.read()
        self.assertEqual(data, "deniyorum2")
        
        self.assertEqual(len(self.filemgr.list("job1")), 1)
        self.assertEqual(len(self.filemgr.list("job2")), 1)
    
    def test_2(self):
        files = self.filemgr.get_recent_files("job1", time.time())
        self.assertEqual(len(files), 0)
        files = self.filemgr.get_recent_files("job1", time.time()-50000)
        self.assertEqual(len(files), 1)
        files = self.filemgr.get_recent_files("job1", datetime(2013, 8, 7, 13, 1, 20, 771000))
        self.assertEqual(len(files), 1)
        files = self.filemgr.get_recent_files("job1", datetime(2013, 8, 7, 13, 10, 5, 771000))
        self.assertEqual(len(files), 0)

    """    
    def test_3(self):
        import zipfile
        job_name = "temp_job"
        file_name = "deneme2.zip"
        self.filemgr.put_file(job_name, file_name, "rpyc.zip")
        remote_file = self.filemgr.get_file(job_name, file_name)
        z = zipfile.ZipFile(remote_file)
        z.extractall()
    """

def do_unittest():
    suite = unittest.TestLoader().loadTestsFromTestCase(FileManagerTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)


def main():
    do_unittest()
    """
    if len(sys.argv) == 1:
        do_unittest()
    else:
        num = int(sys.argv[1])
        test_func(num)
    """

if __name__ == '__main__':
    main()
    
    
