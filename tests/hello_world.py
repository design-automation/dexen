'''
Created on Aug 5, 2013

@author: Cihat Basol
'''


import sys
import time

from dexen.common.logger import DexenLogger

def func1():
    for i in xrange(10):
        print "Hello func1", i
        time.sleep(1)


def func2():
    for i in xrange(10):
        print "Hello func2", i
        time.sleep(1)


def main():
    #print sys.argv, len(sys.argv)
    #func1()
    logger = DexenLogger("HEELLO")
    logger.debug("AHA")
    logger = DexenLogger("HEELLO")
    logger.debug("WAHA")

if __name__ == '__main__':
    main()