'''
Created on Aug 1, 2013

@author: Cihat Basol
'''


import os
import sys
import time


def main():
    print "I am in temp2"
    print "Args:", sys.argv
    print os.environ
    print os.environ['DENEME']
    time.sleep(100)

if __name__ == '__main__':
    main()
