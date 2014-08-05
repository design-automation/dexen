"""
Cereate a job with a random name and start a task.
"""
import random
from dexen_libs.api import server_api, data_api

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
    server = server_api.ServerAPI(username="xyz", password="abc", url="localhost", port=5000)
    assert isinstance(server, server_api.ServerAPI)

    print "Created job"
    job_name = "JOB" + str(random.randint(0, 1e6))
    job = server.create_job(job_name)
    assert isinstance(job, server_api.JobAPI)
    print "Job name = " + job_name

    print "Upload a file"
    job.upload("simple_event_task.py")
    job.upload("simple_dataflow_task.py")

    print "Initialize task"
    initialize_task = data_api.EventTask(
        name = "init_test",
        cmd_args = ["python", "simple_event_task.py"],
        event = data_api.JobStartedEvent())
    job.register_task(initialize_task)

    print "Develop task"
    develop_task = data_api.DataFlowTask(
        name = "dev_test",
        cmd_args = ["python", "simple_dataflow_task.py"],
        condition = Condition().exists("genotype").not_exists("phenotype").get(),
        input_size = 2)
    job.register_task(develop_task)


    print "Run job"
    job.run()

if __name__ == '__main__':
    main()
    