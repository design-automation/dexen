"""
Script for running Houdini ea
"""
import time, random, sys

from dexen.client import api
from dexen.common import events, task
import settings as ss

DEBUG = True

def log(s):
    if DEBUG:
        print s

def main():

    log("Connect to server")
    server = api.ServerAPI(username="user", password="test", 
                           url="localhost", port=5000)
    assert isinstance(server, api.ServerAPI)
    
    log("Created job ")
    job_name = "JOB" + str(random.randint(0,1e6))
    job = server.create_job(job_name)
    assert isinstance(job, api.JobAPI)
    log("Job name = " + job_name)
    
    log("Upload python files")
    job.upload("tasks.py")
    job.upload("settings.py")

    log("Initialize task")
    initialize_task = task.EventTask("Initialize Task",
        ["python", "tasks.py", ss.INITIALIZE], 
        events.JobStartedEvent())
    job.register_task(initialize_task)

    log("Evaluate task")
    evaluate_task = task.DataFlowTask("Eval Function Task",
        ["python", "tasks.py", ss.EVALUATE_AREA], 
        ss.evaluate_executor.condition(), 
        ss.evaluate_executor.input_size())
    job.register_task(evaluate_area_task)

    log("Feedback task")
    feedback_task = task.DataFlowTask("Feedback Task",
        ["python", "tasks.py", ss.FEEDBACK], 
        ss.feedback_executor.condition(),   
        ss.feedback_executor.input_size())
    job.register_task(feedback_task)

    log("Run job")
    job.run()

if __name__ == '__main__':
    main()























