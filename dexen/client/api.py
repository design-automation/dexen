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

import logging
logger = logging.getLogger(__name__)

import os
import tempfile

import pymongo

from dexen.common import remoting, utils
from dexen.common.remoting import DEFAULT_SERVER_PORT, EndPointAddress
from dexen.client.proxy import ServerProxy


class JobAPI(object):
    def __init__(self, job_name, svr_proxy):
        self.job_name = job_name
        self._svr_proxy = svr_proxy
    
    def upload(self, path):
        if os.path.isfile(path):
            self._svr_proxy.upload_file(self.job_name, path)
        else: # TODO: remove the else the path should always be file
            file_path = tempfile.mktemp(prefix="dexen_")
            print "file_path: ", file_path
            utils.zipfolder(file_path, target_dir=path)
            zip_path = file_path + ".zip"
            self._svr_proxy.upload_file(self.job_name, path=zip_path)
            os.remove(zip_path)
    
    def get_executions(self, last_update):
        return self._svr_proxy.get_executions(self.job_name, last_update)
    
    def run(self):
        self._svr_proxy.run_job(self.job_name)
    
    def stop(self):
        self._svr_proxy.stop_job(self.job_name)

    def register_task(self, task):
        self._svr_proxy.register_task(self.job_name, task)
    
    def deregister_task(self, task_name):
        self._svr_proxy.deregister_task(self.job_name, task_name)


class ServerAPI(object):
    def __init__(self, username, password, url="localhost", port="5000"):
        self._svr_proxy = ServerProxy(username, password, url, port)

    def login(self, username, password):
        """
        Log onto the server, using username and password. The user must have 
        first registered on the server to be able to login. 
        To register, the url is /register
        To login, the url is /login
        """
        self._svr_proxy.login(username, password)

    def logout(self):
        """
        Logout from the server"
        """
        self._svr_proxy.logout()

    def get_jobs_data(self): #changed from get_jobs to get_jobs_data
        """
        Returns a set of dicts, where each dict describes one job.
        """
        return self._svr_proxy.get_jobs()

    def create_job(self, job_name):
        """
        Create a new job on the server.
        """
        self._svr_proxy.create_job(job_name)
        return JobAPI(job_name, self._svr_proxy)

    def delete_job(self, job_name):
        """
        Delete a job on the server. 
        """
        raise NotImplementedException

    def get_job(self, job_name):
        """
        Returns an instance of JobAPI.
        """
        return JobAPI(job_name, self._svr_proxy)


def connect(ip, port=DEFAULT_SERVER_PORT):
    addr = EndPointAddress(ip, port)
    conn = remoting.connect(addr)
    db_conn = pymongo.Connection(host=ip)
    return ServerAPI(conn, db_conn)


def test():
    logger.info("I am in test")
    logger.debug("What is going on over here")


