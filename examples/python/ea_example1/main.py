'''
Created on Dec 26, 2013

@author: kafkef
'''


import sys
import time

from dexen.common import data_api

from common import (IS_ALIVE, GENOTYPE, PHENOTYPE, SCORE_1, SCORE_2, SCORE_3,
                    INITIALIZE, DEVELOP, EVAL_1, EVAL_2, EVAL_3, FEEDBACK,
                    POP_SIZE, FEEDBACK_SIZE)


def initialize():
    print "I am in initialize"
    for _ in xrange(POP_SIZE):
        do = data_api.DataObject()
        do.set_value(IS_ALIVE, True)
        do.set_value(GENOTYPE, "genotype blob")
        do.set_value(SCORE_3, None)


def develop():
    print "I am development"
    data_objects = data_api.GetAssignedDataObjects()
    for do in data_objects:
        do.set_value(PHENOTYPE, "phenotype value")
    time.sleep(10)


def eval1():
    print "I am in eval1"
    data_objects = data_api.GetAssignedDataObjects()
    for do in data_objects:
        do.set_value(SCORE_1, 45.7)
    time.sleep(10)


def eval2():
    print "I am in eval2"
    data_objects = data_api.GetAssignedDataObjects()
    for do in data_objects:
        do.set_value(SCORE_2, 49.7)
    time.sleep(10)


def eval3():
    print "I am in eval3"
    data_objects = data_api.GetAssignedDataObjects()
    for do in data_objects:
        do.set_value(SCORE_3, 49.7)
    time.sleep(10)


def feedback():
    print "I am in feedback"
    data_objects = data_api.GetAssignedDataObjects()

    for do in data_objects[:FEEDBACK_SIZE/2]:
        do.set_value(IS_ALIVE, False)

    for _ in xrange(FEEDBACK_SIZE/2):
        do = data_api.DataObject()
        do.set_value(IS_ALIVE, True)
        do.set_value(GENOTYPE, "genotype blob")
        do.set_value(SCORE_3, None)
    time.sleep(10)


def main():
    if sys.argv[1] == INITIALIZE:
        initialize()
    elif sys.argv[1] == DEVELOP:
        develop()
    elif sys.argv[1] == EVAL_1:
        eval1()
    elif sys.argv[1] == EVAL_2:
        eval2()
    elif sys.argv[1] == EVAL_3:
        eval3()
    elif sys.argv[1] == FEEDBACK:
        feedback()
    else:
        print "wrong argument"


if __name__ == '__main__':
    main()
