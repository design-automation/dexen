# ==================================================================================================
#
#    Copyright (c) 2008, Patrick Janssen (patrick@janssen.name)
#
#    This file is part of Dexen.
#
#    Dexen is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Dexen is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Dexen.  If not, see <http://www.gnu.org/licenses/>.
#
# ==================================================================================================

import os
import json
import bson
import pymongo

import constants as con


# Event Classes

class DexenEvent(object):
    def __init__(self):
        pass

class JobStoppedEvent(DexenEvent):
    def __init__(self):
        super(JobStoppedEvent, self).__init__()

    def json(self):
        return {"name" : self.__class__.__name__}

class JobStartedEvent(DexenEvent):
    def __init__(self):
        super(JobStartedEvent, self).__init__()

    def json(self):
        return {"name" : self.__class__.__name__}

class TimeBasedEvent(DexenEvent):
    def __init__(self):
        super(TimeBasedEvent, self).__init__()

class PeriodicTimeEvent(TimeBasedEvent):
    def __init__(self, period):
        super(PeriodicTimeEvent, self).__init__()
        self.period = period # in seconds

    def json(self):
        return {"name" : self.__class__.__name__,
                "period" : self.period}

class OneShotTimeEvent(TimeBasedEvent):
    def __init__(self, after):
        super(OneShotTimeEvent, self).__init__()
        self.after = after

    def json(self):
        return {"name" : self.__class__.__name__,
                "after" : self.after}

# Task Classes

class Task(object):
    EVENT_TASK = "EVENT_TASK"
    DATAFLOW_TASK = "DATAFLOW_TASK"
    def __init__(self, name, cmd_args):
        self.name = name
        self.cmd_args = cmd_args

    @property
    def is_event_task(self):
        return self.type == Task.EVENT_TASK

    @property
    def is_dataflow_task(self):
        return self.type == Task.DATAFLOW_TASK


class EventTask(Task):
    def __init__(self, name, cmd_args, event):
        super(EventTask, self).__init__(name, cmd_args)
        self.type = Task.EVENT_TASK
        self.event = event

    def json(self):
        return {
            "task_name" : self.name,
            "cmd_args" : self.cmd_args,
            "event" : self.event.json()
        }

class DataFlowTask(Task):
    def __init__(self, name, cmd_args, condition, input_size):
        super(DataFlowTask, self).__init__(name, cmd_args)
        self.condition = condition
        self.type = Task.DATAFLOW_TASK
        self.input_size = input_size
        self.input_data = [] # list of DataObjectId

    def json(self):
        return {
            "task_name" : self.name,
            "cmd_args" : self.cmd_args,
            "condition" : self.condition,
            "input_size" : self.input_size
        }

# Mongodb functions

def rollback_doc_field(execution_id, op=None, attr_name=None):
    if op is None:
        return "%s.%s.rollback_doc"%(con.FIELD_ROLLBACK, execution_id)
    return "%s.%s.rollback_doc.%s.%s"%(con.FIELD_ROLLBACK, execution_id, op,
                                       attr_name)

def rollback_set_field(execution_id, attr_name):
    return "%s.%s.set.%s"%(con.FIELD_ROLLBACK, execution_id, attr_name)


def rollback_insert_field(execution_id): #NOT USED
    return "%s.%s.insert"%(con.FIELD_ROLLBACK, execution_id)


def rollback_inc_field(execution_id): #NOT USED
    return "%s.%s.inc"%(con.FIELD_ROLLBACK, execution_id)


def attr_being_modified_field(execution_id): #NOT USED
    return "%s.%s"%(con.ATTRS_BEING_MODIFIED, execution_id)


def GetMainDB(db_client): #NOT USED
    return db_client["main_db"]


def GetUserDB(db_client, user_name): 
    return db_client[user_name+"_db"]


def GetUserCollection(db_client): #NOT USED
    return pymongo.collection.Collection(GetMainDB(db_client), "users")


def GetJobDataCollection(db_client, user_name, job_name):
    return pymongo.collection.Collection(GetUserDB(db_client, user_name), job_name+".data")


def GetJobExecutionCollection(db_client, user_name, job_name):
    return pymongo.collection.Collection(GetUserDB(db_client, user_name),
                           job_name+".executions")

# Data object stuff

def DataObject(key=None): #NOT USED
    """Factory function for the user code to consume. Connects to mongodb and gets 
    a data object.
    
    Returns:
        A new _DataObject if key is not specified or the key is not found in
        the collection. Otherwise, the corresponding object.
    Note:
        The db, collection and etc. are implicitly determined by making use of
        the os environment.
        The assumption here is that when the user code runs, the os environment
        is already set by the dexen system run time.
    """
    db_client = pymongo.MongoClient(host=os.environ[con.ENV_DB_IP],
                                    port=int(os.environ[con.ENV_DB_PORT]))
    user_name = os.environ[con.ENV_USER_NAME]
    job_name = os.environ[con.ENV_JOB_NAME]
    execution_id = os.environ[con.ENV_EXECUTION_ID]
    coll = GetJobDataCollection(db_client, user_name, job_name)
    return _DataObject(coll, execution_id, key)


def GetAssignedDataObjects():
    """Get the list of data objects assigned by Dexen system.

    This function is to be invoked by user code.

    Returns:
        List of _DataObject.
    """
    data_ids = json.loads(os.environ.get(con.ENV_TASK_INPUT_JSON, []))

    result = []
    for data_id in data_ids:
        if data_id[con.JSON_IS_WRAPPED]:
            key = bson.ObjectId(data_id[con.JSON_ID_VALUE])
        else:
            key = data_id[con.JSON_ID_VALUE]
        result.append(DataObject(key))
    return result

class _DataObject(object):
    def __init__(self, coll, execution_id, data_id):
        self.coll = coll
        self._id = data_id  # _id field in mongodb.
        self._execution_id = execution_id
        doc = {}
        if not self._id:
            self._id = self.coll.insert(doc)
        elif not self.coll.find_one(self._id):
            doc["_id"] = self._id
            self.coll.insert(doc)

    @property
    def _attrs_being_modified_field(self):
        return "{0}.{1}".format(con.ATTRS_BEING_MODIFIED, self._execution_id)

    @property
    def _rollback_field(self):
        return "{0}.{1}".format(con.FIELD_ROLLBACK, self._execution_id)

    def get_value(self, attr_name):
        doc = self.coll.find_one(self._id, fields=[attr_name])
        return doc.get(attr_name, None)

    def set_value(self, attr_name, value):
        res = self.coll.find_one({"_id": self._id}, fields=[attr_name])
        old_value = res.get(attr_name, con.NON_EXISTENT_VALUE)

        spec = {
            "_id" : self._id
        }
        doc = {
            "$set" : {
                attr_name : value,
             },
            "$addToSet" : {
                self._attrs_being_modified_field : attr_name
            }
        }
        if old_value is con.NON_EXISTENT_VALUE:
            field = rollback_doc_field(self._execution_id, "unset",
                                          attr_name)
            doc["$set"][field] = ""
        else:
            field = rollback_set_field(self._execution_id, attr_name)
            doc["$set"][field] = old_value
            field = field.replace(".", "/")
            field = rollback_doc_field(self._execution_id, "rename", field)
            doc["$set"][field] = attr_name
        self.coll.update(spec, doc)
    
    def inc_value(self, attr_name, value):
        spec = {"_id" : self._id}
        doc = {
            "$inc" : {
                attr_name : value,
                rollback_doc_field(self._execution_id, "inc", attr_name) : -value
            },
            "$addToSet" : {
                self._attrs_being_modified_field : attr_name
            }
        }
        self.coll.update(spec, doc)

