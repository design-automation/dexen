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
"""
Cereate a job and start some tasks that read and write files.
"""
from time import gmtime, strftime
from dexen_libs.api import server_api, data_api

USERNAME = "user"
PASSWORD = "pswd"


class Condition(object):
    def __init__(self):
        self.selectors = {}
    def exists(self, name):
        self.selectors[name] = { "$exists" : True }
        return self
    def not_exists(self, name):
        self.selectors[name] = { "$exists" : False }
        return self
    def equals(self, name, value):
        self.selectors[name] = value
        return self
    def not_equals(self, name, value):
        self.selectors[name] = { "$ne" : value }
        return self
    def get(self):
        return self.selectors


def main():
    """
    The main func.
    """

    print "Connect to server"
    server = server_api.ServerAPI(username=USERNAME, password=PASSWORD, url="localhost", port=5000)
    assert isinstance(server, server_api.ServerAPI)

    print "Created job"
    job_name = "Job_"+strftime("%H_%M_%S", gmtime())
    job = server.create_job(job_name)
    assert isinstance(job, server_api.JobAPI)
    print "Job name = " + job_name

    print "Upload files"
    job.upload("ev_init.py")
    job.upload("df_write_file.py")
    job.upload("df_read_file.py")

    print "Initialize: event task"
    initialize_task = data_api.EventTask(
        name = "init_test",
        cmd_args = ["python", "ev_init.py"],
        event = data_api.JobStartedEvent())
    job.register_task(initialize_task)

    print "Dataflow task 1"
    develop_task = data_api.DataFlowTask(
        name = "df1",
        cmd_args = ["python", "df_write_file.py"],
        condition = Condition().exists("init_data").not_exists("data1").get(),
        input_size = 2)
    job.register_task(develop_task)

    print "Dataflow task 2"
    develop_task = data_api.DataFlowTask(
        name = "df2",
        cmd_args = ["python", "df_read_file.py"],
        condition = Condition().exists("data1").not_exists("data2").get(),
        input_size = 2)
    job.register_task(develop_task)

    print "Run job"
    job.run()

if __name__ == '__main__':
    main()
    