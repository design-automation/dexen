'''
Created on Aug 12, 2013

@author: Cihat Basol
'''

import sys
import time
import unittest

from mock import MagicMock

from dexen.server.proxy import ResourceManagerProxy


class ResourceManagerProxyTestCase(unittest.TestCase):
    def setUp(self):
        self.conn = MagicMock()
        self.res_mgr = ResourceManagerProxy(self.conn)
    
    def tearDown(self):
        pass
    
    def test_1(self):
        self.conn.root.get_new_nodes = MagicMock(side_effect=EOFError("Boom!"))
        self.assertEqual(self.res_mgr.get_new_nodes(), [])
        self.assertNotEqual(self.res_mgr.get_new_nodes(), None)
        self.assertEqual(self.res_mgr.is_alive, False)
        self.assertEqual(self.res_mgr.is_dead, True)
    
    def test_2(self):
        self.conn.root.get_new_nodes.return_value = ["ali", "veli"]
        nodes = self.res_mgr.get_new_nodes()
        self.assertEqual(len(nodes), 2)
        self.assertEqual(nodes[0], "ali")
        self.assertEqual(nodes[1], "veli")
        self.assertEqual(self.res_mgr.is_alive, True)
        self.assertEqual(self.res_mgr.is_dead, False)



def do_unittest():
    suite = unittest.TestLoader().loadTestsFromTestCase(ResourceManagerProxyTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)


def main():
    if len(sys.argv) == 1:
        do_unittest()

if __name__ == '__main__':
    main()
