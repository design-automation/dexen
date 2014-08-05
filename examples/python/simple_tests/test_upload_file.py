"""
Cereate a job with a random name and start a task.
"""
import random
from dexen_libs.api import server_api


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
    job.upload("simple_task.py")


if __name__ == '__main__':
    main()