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
import logging

import requests

logger = logging.getLogger(__name__)


class ServerProxy(object):
    def __init__(self, username, password, url, port):
        if not url.startswith("http://"):
            url = "http://" + url
        self.server_url = "%s:%s"%(url, port)
        self.server_port = port
        self.session = requests.Session()
        self.login(username, password)

    def register_user(self, username, password):
        pass

    def login(self, username, password):
        logger.info("[POST]: /login username=%s password=%s",
                    username, password)
        url = "%s/login"%(self.server_url,)
        data = {"username" : username, 
                "password" : password}
        r = self.session.post(url, data)
        logger.debug("/login response text:%s", r.text)

    def logout(self):
        logger.info("[GET]: /logout")
        url = "%s/logout"%(self.server_url,)
        self.session.get(url)

    def upload_file(self, job_name, path):
        logger.info("[POST]: /upload_file job_name=%s filepath=%s",
                    job_name, path)
        assert os.path.isfile(path)
        url = "%s/upload_file/%s"%(self.server_url, job_name)
        filename = os.path.basename(path)
        files = {"file" : (filename, open(path, "rb"))}
        self.session.post(url, files=files)

    def get_executions(self, job_name, last_update):
        logger.info("[GET]: /get_executions job_name=%s", job_name)
        url = "%s/executions/%s"%(self.server_url, job_name)
        payload = { "last_update": last_update }
        r = self.session.get(url, params=payload)
        print "response: ", r
        return r.json().get("executions", [])

    def get_jobs(self):
        logger.info("[GET]: /get_jobs")
        url = "%s/jobs"%(self.server_url, )
        r = self.session.get(url)
        return r.json().get("jobs", [])

    def create_job(self, job_name):
        logger.info("[POST]: /create_job job_name=%s", job_name)
        url = "%s/create_job/%s"%(self.server_url, job_name)
        self.session.post(url)

    def delete_job(self, job_name):
        logger.info("[POST]: /delete_job job_name=%s", job_name)
        url = "%s/delete_job/%s"%(self.server_url, job_name)
        self.session.post(url)

    def run_job(self, job_name):
        logger.info("[POST]: /run_job job_name=%s", job_name)
        url = "%s/run_job/%s"%(self.server_url, job_name)
        self.session.post(url)

    def stop_job(self, job_name):
        logger.info("[POST]: /stop_job job_name=%s", job_name)
        url = "%s/stop_job/%s"%(self.server_url, job_name)
        self.session.post(url)

    def register_task(self, job_name, task):
        logger.info("[POST]: /register_task job_name=%s task_name=%s",
                    job_name, task.name)
        url = "%s/register_task/%s"%(self.server_url, job_name)
        header = { "content-type" : "application/json" }
        payload = task.json()
        self.session.post(url, data=json.dumps(payload), headers=header)

    def deregister_task(self, job_name, task_name):
        logger.info("[POST]: /deregister_task job_name=%s task_name=",
                    job_name, task_name)
        url = "%s/deregister_task/%s/%s"%(self.server_url, job_name, task_name)
        self.session.post(url)



