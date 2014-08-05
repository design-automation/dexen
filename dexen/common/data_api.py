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

import json
import os

import bson
import pymongo

from dexen.common import constants, db


def DataObject(key=None):
    """Factory function for the user code to consume.
    
    Returns:
        A new _DataObject if key is not specified or the key is not found in
        the collection. Otherwise, the corresponding object.
    Note:
        The db, collection and etc. are implicitly determined by making use of
        the os environment.
        The assumption here is that when the user code runs, the os environment
        is already set by the dexen system run time.
    """
    db_client = pymongo.MongoClient(host=os.environ[constants.ENV_DB_IP],
                                    port=int(os.environ[constants.ENV_DB_PORT]))
    user_name = os.environ[constants.ENV_USER_NAME]
    job_name = os.environ[constants.ENV_JOB_NAME]
    execution_id = os.environ[constants.ENV_EXECUTION_ID]
    coll = db.GetJobDataCollection(db_client, user_name, job_name)
    return _DataObject(coll, execution_id, key)


def GetAssignedDataObjects():
    """Get the list of data objects assigned by Dexen system.

    This function is to be invoked by user code.

    Returns:
        List of _DataObject.
    """
    data_ids = json.loads(os.environ.get(constants.ENV_TASK_INPUT_JSON, []))

    result = []
    for data_id in data_ids:
        if data_id[db.JSON_IS_WRAPPED]:
            key = bson.ObjectId(data_id[db.JSON_ID_VALUE])
        else:
            key = data_id[db.JSON_ID_VALUE]
        result.append(DataObject(key))
    return result


"""
def _is_immutable(obj):
    return (isinstance(obj, int) or isinstance(obj, float) or 
           isinstance(obj, str) or isinstance(obj, tuple) or
           isinstance(obj, bool) or isinstance(obj, long))


class Singleton(object):
    def __init__(self, val):
        if _is_immutable(val):
            self.val = val
            self.serialized = False
        else:
            self.val = pickle.dumps(self.val)
            self.serialized = True

    def set(self, val):

    def value(self):
        if self.serialized:
            return pickle.loads(self.val)
        return self.val
"""


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
        return "{0}.{1}".format(db.ATTRS_BEING_MODIFIED, self._execution_id)

    @property
    def _rollback_field(self):
        return "{0}.{1}".format(db.FIELD_ROLLBACK, self._execution_id)

    def get_value(self, attr_name):
        doc = self.coll.find_one(self._id, fields=[attr_name])
        return doc.get(attr_name, None)

    def set_value(self, attr_name, value):
        res = self.coll.find_one({"_id": self._id}, fields=[attr_name])
        old_value = res.get(attr_name, db.NON_EXISTENT_VALUE)

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
        if old_value is db.NON_EXISTENT_VALUE:
            field = db.rollback_doc_field(self._execution_id, "unset",
                                          attr_name)
            doc["$set"][field] = ""
        else:
            field = db.rollback_set_field(self._execution_id, attr_name)
            doc["$set"][field] = old_value
            field = field.replace(".", "/")
            field = db.rollback_doc_field(self._execution_id, "rename", field)
            doc["$set"][field] = attr_name
        self.coll.update(spec, doc)
    
    def inc_value(self, attr_name, value):
        spec = {"_id" : self._id}
        doc = {
            "$inc" : {
                attr_name : value,
                db.rollback_doc_field(self._execution_id, "inc", attr_name) : -value
            },
            "$addToSet" : {
                self._attrs_being_modified_field : attr_name
            }
        }
        self.coll.update(spec, doc)

