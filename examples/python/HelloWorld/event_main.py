'''
Created on Aug 13, 2013

@author: Cihat Basol
'''


import os
import sys

from dexen.common import constants


def main():
    print "\n=============================================="
    msg = ""
    if len(sys.argv) > 2:
        msg = sys.argv[2]
    print "Hello World", msg
    print "Job Name is: ", os.environ[constants.ENV_JOB_NAME]
    print "User Name is: ", os.environ[constants.ENV_USER_NAME]
    print "Execution id: ", os.environ[constants.ENV_EXECUTION_ID]
    print "================================================"

if __name__ == '__main__':
    main()
