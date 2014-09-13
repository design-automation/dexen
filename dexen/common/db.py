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

"""DB Module that contains wrapper classes for collections in mongodb.

The structure of the main database:
    main_db
        users

    <username>_db
        <jobname>.data
        <jobname>.files
        <jobname>.executions

"""
import collections
import datetime
import logging
import time

import bson
from flask.ext import login
import gridfs
import pymongo
from pymongo import collection as coll

from dexen.common import constants, task


Datetime = datetime.datetime
LOGGER = logging.getLogger(__name__)  # This only used once, but not used in any of the classes

# ==================================================================================================
# Constants
# ==================================================================================================

ATTRS_BEING_MODIFIED = "_attrs_being_modified"
JSON_ID_VALUE = "id_value"
JSON_IS_WRAPPED = "is_wrapped"
FIELD_ROLLBACK = "_rollback"
NON_EXISTENT_VALUE = "NonExistent"

EXECUTION_ID = "execution_id"
TASK_NAME = "task_name"
WORKER_NAME = "worker_name"
CREATION_TIME = "creation_time"
STATUS = "status"
LAST_UPDATE_TIME = "last_update_time"
BEGIN_TIME = "begin_time"
END_TIME = "end_time"
STDOUT = "stdout"
STDERR = "stderr"

STATUS_FINISHED = "Finished"
STATUS_FAILED = "Failed"
STATUS_SCHEDULED = "Scheduled"

# ==================================================================================================
# Functions for getting mongoDB databases and collections.
# db_client refers to an instance of pymongo.MongoClient
# ==================================================================================================

# ----------------------------------------------------------------------------------------------TODO
# TDOD - why are these functions starting with capitals - pylint is complaining

def GetMainDB(db_client):
    """
    """
    return db_client["main_db"]


def GetUserDB(db_client, user_name):
    """
    """
    return db_client[user_name+"_db"]


def GetUserCollection(db_client):
    """
    """
    return coll.Collection(GetMainDB(db_client), "users")


def GetJobDataCollection(db_client, user_name, job_name):
    """
    """
    return coll.Collection(GetUserDB(db_client, user_name), job_name+".data")


def GetJobExecutionCollection(db_client, user_name, job_name):
    """
    """
    return coll.Collection(GetUserDB(db_client, user_name), job_name+".executions")

# ==================================================================================================
# Functions for working with attributes, used in the JobDataManager class.
# ==================================================================================================

def rollback_doc_field(execution_id, op=None, attr_name=None):
    """
    """
    if op is None:
        return "%s.%s.rollback_doc" % (FIELD_ROLLBACK, execution_id)
    return "%s.%s.rollback_doc.%s.%s" % (FIELD_ROLLBACK, execution_id, op, attr_name)


def rollback_set_field(execution_id, attr_name):
    """
    """
    return "%s.%s.set.%s" % (FIELD_ROLLBACK, execution_id, attr_name)


def rollback_insert_field(execution_id):
    """
    """
    return "%s.%s.insert" % (FIELD_ROLLBACK, execution_id)


def rollback_inc_field(execution_id):
    """
    """
    return "%s.%s.inc" % (FIELD_ROLLBACK, execution_id)


def attr_being_modified_field(execution_id):
    """
    """
    return "%s.%s" % (ATTRS_BEING_MODIFIED, execution_id)

# ==================================================================================================
# Utility functions
# ==================================================================================================


def unix_time(dt):
    """Utility function to get a time stamp
    """
    if dt is None:
        return None
    epoch = Datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()

# ==================================================================================================
# Classes
# ==================================================================================================


class DataObjectId(object):
    """Serializable wrapper class for object ids in a mongo collection.

    This is created in the server side and later delivered to nodes.

    Note: ObjectId is not serializable therefore a custom json format is
    specified in via to_json_dict method.
    """
    def __init__(self, data_id):
        """Constructor.
        Args:
            data_id: Either a built-in immutable type (e.g. str, int)
            or ObjectId.
        Note: ObjectId("5"), "5" and 5 are different ids in mongodb.
        """
        if isinstance(data_id, bson.ObjectId):
            self.id = str(data_id)
            self.is_wrapped = True  # is wrapped by ObjectId
        else:
            self.id = data_id
            self.is_wrapped = False

    def to_json_dict(self):
        """
        """
        json_dict = {}
        json_dict[JSON_ID_VALUE] = self.id
        json_dict[JSON_IS_WRAPPED] = self.is_wrapped
        return json_dict

    def get_value(self):
        """
        """
        if self.is_wrapped:
            return bson.ObjectId(self.id)
        return self.id

    def __eq__(self, obj):
        if isinstance(obj, DataObjectId):
            this_obj = (self.id, self.is_wrapped)
            other_obj = (obj.id, obj.is_wrapped)
            return this_obj == other_obj
        return False

    def __hash__(self):
        return hash((self.id, self.is_wrapped))

    def __repr__(self):
        if self.is_wrapped:
            return "ObjectId(%s)" % self.id
        return "%s" % self.id

    def __str__(self):
        return self.__repr__()


class FileManager(object):
    """ Class for managing files linked to jobs, for example the dependencies. 

    Files are saved in the user's mongoDB database, in a GridFS. Each job that the user is running
    has its own GridFS.

    self.db - a mongodb database
    self.colls - {job_name: gridfs.GridFS, ...}
    """
    def __init__(self, db_client, user_name):
        self.user_db = GetUserDB(db_client, user_name)
        self.colls = {}

    def put_data(self, job_name, file_name, data):
        """
        """
        if job_name not in self.colls:
            self.colls[job_name] = gridfs.GridFS(self.user_db, job_name)
        self.colls[job_name].put(data, filename=file_name)

    def put_file(self, job_name, file_name, path):
        """
        """
        if job_name not in self.colls:
            self.colls[job_name] = gridfs.GridFS(self.user_db, job_name)
        with open(path) as f:
            return self.colls[job_name].put(f, filename=file_name)

    def get_file(self, job_name, file_name):
        """
        """
        if job_name not in self.colls:
            self.colls[job_name] = gridfs.GridFS(self.user_db, job_name)
        return self.colls[job_name].get_last_version(filename=file_name)

    def list(self, job_name):
        """
        """
        if job_name not in self.colls:
            self.colls[job_name] = gridfs.GridFS(self.user_db, job_name)
        return self.colls[job_name].list()

    def delete(self, job_name, file_name):
        """
        """
        pass  # TODO

    def get_recent_files(self, job_name, elapsed_time):
        """
        """
        if isinstance(elapsed_time, Datetime):
            elapsed_time2 = elapsed_time
        else:
            elapsed_time2 = Datetime.utcfromtimestamp(elapsed_time)
        # col = Collection(self.user_db, job_name + ".files")
        col = self.user_db[job_name + ".files"]
        res = set()
        for elem in col.find({"uploadDate": {"$gte": elapsed_time2}}):
            res.add(elem["filename"])
        return list(res)

    def get_files_metadata(self, job_name):
        """
        """
        col = self.user_db[job_name + ".files"]
        fields = {"filename":True, "_id": False, "length":True, "uploadDate":True}
        res = {}
        for elem in col.find(fields=fields):
            LOGGER.debug("files metadata: %s", elem)
            file_name = elem["filename"]
            upload_time = unix_time(elem["uploadDate"])
            if file_name not in res or upload_time > res[file_name]["upload_time"]:
                item = {}
                item["file_name"] = file_name
                item["size"] = elem["length"]
                item["upload_time"] = upload_time
                res[file_name] = item
        return res.values()


class User(login.UserMixin):
    """ Class for authenticating users. 

    Extends flask.ext.login.UserMixin, which provides default 
    implementations for the methods that Flask-Login expects user objects to have. For more details,
    see here: https://flask-login.readthedocs.org/en/latest/_modules/flask/ext/login.html#UserMixin

    self.username - string
    self.password - string
    """
    def __init__(self, _id, username, password):
        """
        """
        self.id = _id
        self.username = username
        self.password = password


class UserManager(object):
    """ Class for managing users. The get_user method will return an instance of type User.

    self.col - a pymongo.collection.Collection that contains data for all users
    """
    def __init__(self, host="localhost", port=constants.MONGOD_PORT):
        self.col = GetUserCollection(pymongo.MongoClient(host, port))

    def exists(self, username):
        """
        """
        spec = {}
        spec["username"] = username
        if self.col.find_one(spec):
            return True
        return False

    def register_user(self, username, password):
        """
        """
        if self.exists(username):
            return None
        doc = {}
        doc["username"] = username
        doc["password"] = password
        oid = self.col.insert(doc)
        return str(oid)

    def get_user(self, id=None, username=None):
        """
        """
        if id is None and username is None:
            return None
        spec = {}
        if id:
            spec["_id"] = bson.ObjectId(id)
        if username:
            spec["username"] = username

        res = self.col.find_one(spec)
        if not res:
            return None
        return User(str(res["_id"]), res["username"], res["password"])

    def validate_user(self, username, password):
        """
        """
        spec = {}
        spec["username"] = username
        spec["password"] = password
        if self.col.find_one(spec):
            return True
        return False


class ExecutionManager(object):
    """ Class for managing the executions for a specific job.
    Executions are instances of task.Execution.
    Execution results are instances of task.ExecutionResult. 

    self.user_name - a string
    self.jon_name - a string
    self.col - a pymongo.collection.Collection that contains data for the job executions
    """
    def __init__(self, db_client, user_name, job_name):
        """
        """
        self.user_name = user_name
        self.job_name = job_name
        self.col = GetJobExecutionCollection(db_client, user_name, job_name)
        self._id = 0

    def create_execution(self, worker_name, task_obj):
        """
        """
        return task.Execution(self.next_id(), self.user_name, self.job_name, worker_name, task_obj)

    def prev_id(self):
        """
        """
        self._id -= 1
        return str(self._id)

    def next_id(self):
        """
        """
        self._id += 1
        return str(self._id)

    def save_execution(self, execution):
        """
        """
        doc = {}
        doc[EXECUTION_ID] = execution.execution_id
        doc[TASK_NAME] = execution.task_name
        doc[WORKER_NAME] = execution.worker_name
        doc[CREATION_TIME] = Datetime.utcfromtimestamp(execution.creation_time)
        doc[STATUS] = STATUS_SCHEDULED
        doc[LAST_UPDATE_TIME] = time.time()
        self.col.insert(doc)

    def update_execution(self, execution_result):
        """
        """
        spec = {EXECUTION_ID: execution_result.execution_id}
        doc = {}
        doc[STDOUT] = execution_result.stdout
        doc[STDERR] = execution_result.stderr
        doc[BEGIN_TIME] = Datetime.utcfromtimestamp(execution_result.begin_time)
        doc[END_TIME] = Datetime.utcfromtimestamp(execution_result.end_time)
        doc[STATUS] = STATUS_FINISHED
        doc[LAST_UPDATE_TIME] = time.time()
        self.col.update(spec, {"$set": doc})

    def update_failed_execution(self, execution):
        """
        """
        spec = {EXECUTION_ID: execution.execution_id}
        doc = {}
        doc[STATUS] = STATUS_FAILED
        doc[LAST_UPDATE_TIME] = time.time()
        self.col.update(spec, {"$set": doc})

    def get_executions(self, after_time):
        """
        """
        executions = []
        for execution in self.col.find({LAST_UPDATE_TIME: {"$gte": after_time}}):
            del execution["_id"]
            executions.append(execution)
        return executions


class JobDataManager(object):
    """ Class for managing job data. 

    TODO: More documentation required

    self.coll - a pymongo.collection.Collection that contains the job data
    self.logger - a logger object
    """
    def __init__(self, db_client, user_name, job_name):
        """Constructs a JobDataManager.
        """
        self.coll = GetJobDataCollection(db_client, user_name, job_name)
        self.logger = logging.getLogger(__name__+"."+self.__class__.__name__)

    def _attrs_being_modified_field(self, execution_id):
        """
        """
        return "{0}.{1}".format(ATTRS_BEING_MODIFIED, execution_id)

    def _rollback_field(self, execution_id):
        """
        """
        return "{0}.{1}".format(FIELD_ROLLBACK, execution_id)

    def get_ids_being_modified(self, execution_id):
        """
        """
        spec = {
            self._attrs_being_modified_field(execution_id): {
                "$exists": True
            }
        }
        return [DataObjectId(data["_id"]) for data in self.coll.find(spec, fields=["_id"])]

    def remove_execution_ids(self, data_ids, execution_id):
        """
        """
        spec = {
            "_id": {
                "$in": [data.get_value() for data in data_ids]
            },
            "$isolated": 1
        }
        update_doc = {
            "$unset": {
                self._attrs_being_modified_field(execution_id): "",
                self._rollback_field(execution_id): ""
            }
        }
        self.coll.update(spec, update_doc, multi=True)

    def _extract_all_attrs(self, doc):
        """
        """
        result = set()
        if not isinstance(doc, dict):
            return set()
        for key in doc:
            if key[0] != '$':
                result.add(key)
            result.update(self._extract_all_attrs(doc[key]))
        return result

    def filter_ids(self, data_ids, condition):
        """
        """
        spec = {
            "_id": {
                "$in": [data.get_value() for data in data_ids]
            }
        }
        for key in condition:
            spec[key] = condition[key]
        result = []
        for data in self.coll.find(spec, fields=["_id", ATTRS_BEING_MODIFIED]):
            data["_id"] = DataObjectId(data["_id"])
            condition_attrs_set = self._extract_all_attrs(condition)
            modified_set = set()
            for modified_attrs in data[ATTRS_BEING_MODIFIED].values():
                modified_set.update(set(modified_attrs))
            if len(condition_attrs_set) == len(condition_attrs_set.difference(modified_set)):
                result.append(data["_id"])
        return result

    def get_modified_attrs(self, data_id, execution_id):
        """
        """
        self.logger.debug("Get modified attributes for execution: %s",
                          execution_id)
        field = self._attrs_being_modified_field(execution_id)
        result = self.coll.find_one(
            {"_id": data_id.get_value(), field: {"$exists": 1}}, fields=[field])
        self.logger.debug("Modified attributes result: %s", result)
        if result:
            return result[ATTRS_BEING_MODIFIED][execution_id]
        return []

    def get_inc_doc(self, data_id, execution_id):
        """
        """
        self.logger.debug("Getting inc doc")
        field = rollback_inc_field(execution_id)
        result = self.coll.find_one({"_id": data_id.get_value(),
                                     field: {"$exists": 1}}, fields=[field])
        self.logger.debug("Inc doc: %s", result)
        return result

    def _get_dict_value(self, nested_dicts, compound_attr):
        """Return a value in a nested set of dicts. The keys are specified by a compound_attr,
        a string of keys seperated by '.'.
        """
        attr_list = compound_attr.split(".")
        if not attr_list:
            return None
        res = nested_dicts
        for attr in attr_list:
            res = res[attr]
        return res

    def rollback(self, execution_id):
        """Rollback
        """
        self.logger.info("Rolling back execution: %s", execution_id)
        modified_ids = self.get_ids_being_modified(execution_id)
        self.logger.debug("modified ids: %s", modified_ids)
        for modified_id in modified_ids:
            doc = collections.defaultdict(dict)
            field = rollback_doc_field(execution_id)
            res = self.coll.find_one({
                "_id": modified_id.get_value(), field: {"$exists": 1}
            }, fields=[field])
            rollback_doc = self._get_dict_value(res, field) if res else {}
            self.logger.info("Rollback doc from db: %s", rollback_doc)
            self.logger.info("Processing rollback doc to prepare update doc...")
            for key in ["unset", "inc"]:
                if key in rollback_doc:
                    doc["$"+key] = rollback_doc[key]

            if "rename" in rollback_doc:
                for field in rollback_doc["rename"]:
                    if "unset" not in rollback_doc or \
                            rollback_doc["rename"][field] not in rollback_doc["unset"]:
                        doc["$rename"][field.replace("/", ".")] = rollback_doc["rename"][field]
            self.logger.info("Prepared update doc: %s", doc)
            self.coll.update({"_id": modified_id.get_value()}, doc)
        self.logger.debug("Removing execution ids.")
        self.remove_execution_ids(modified_ids, execution_id)

    def get_all_data(self):
        result = []
        for data in self.coll.find({}, fields={ATTRS_BEING_MODIFIED : False, FIELD_ROLLBACK : False}):
            result.append(data)
        return result

    def get_data_value(self, data_id, attr_name):
        res = self.coll.find_one(data_id, fields=[attr_name])
        if not res is None:
            return res.get(attr_name)
        return None