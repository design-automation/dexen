'''
Created on Dec 26, 2013

@author: kafkef
'''

import os

import pymongo

from dexen.common import constants, data_api, db, remoting


def print_ids_being_modified(job_mgr, execution_id):
    print "ids being modified by %s"%execution_id
    for data_id in job_mgr.get_ids_being_modified(execution_id):
        assert isinstance(data_id, db.DataObjectId)
        print "data_id: %r"%data_id


def main():
    ip = os.environ[constants.ENV_DB_IP] = remoting.get_my_ip()
    port = os.environ[constants.ENV_DB_PORT] = str(constants.MONGOD_PORT)
    user_name = os.environ[constants.ENV_USER_NAME] = "test_user_1"
    job_name = os.environ[constants.ENV_JOB_NAME] = "test_job_1"

    os.environ[constants.ENV_EXECUTION_ID] = "execution_3"

    #do = data_api.DataObject()
    #do.set_value("attr_1", 5)

    #assert do.value("attr_1") == 5

    """
    do = data_api.DataObject("test_obj_1")
    do.set_value("attr_1", "hello world")
    do.set_value("attr_3", 456)
    
    assert do.value("attr_3") == 456
    assert do.value("attr_1") == "hello world"
    """
    
    db_client = pymongo.MongoClient(ip, int(port))

    job_mgr = db.JobDataManager(db_client, user_name, job_name)

    print_ids_being_modified(job_mgr, "execution_1")
    print_ids_being_modified(job_mgr, "execution_2")
    print_ids_being_modified(job_mgr, "execution_3")

    data_ids = job_mgr.get_ids_being_modified("execution_5")
    #job_mgr.remove_execution_ids(data_ids, "execution_1")
    print "modified ids", data_ids
    condition = {"test_attr2" : { "$exists" : True }}
    data_ids = job_mgr.filter_ids(data_ids, condition)
    print "filtered data_ids", data_ids

if __name__ == '__main__':
    main()

