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

    print "Connect to server"
    server = api.ServerAPI(username="user", password="test", url="localhost", port=5000)
    assert isinstance(server, api.ServerAPI)
    
    print "Created job "
    job_name = "JOB" + str(random.randint(0,1e6))
    job = server.create_job(job_name)
    assert isinstance(job, api.JobAPI)
    print "Job name = " + job_name
    
    print "Upload python files"
    job.upload("tasks.py")
    job.upload("settings.py")

    print "Initialize task"
    initialize_task = task.EventTask(
        name = ss.INITIALIZE,
        cmd_args = ss.INITIALIZE_ARGS, 
        event = events.JobStartedEvent())
    job.register_task(initialize_task)
    
    print "Develop task"
    develop_task = task.DataFlowTask(
        name = ss.DEVELOP,
        cmd_args = ss.DEVELOP_ARGS,
        condition = ss.DEVELOP_COND,
        input_size = ss.DEVELOP_INPUT_SIZE)
    job.register_task(develop_task)
    
    print "Evaluate area task"
    evaluate_area_task = task.DataFlowTask(
        name = ss.EVALUATE_AREA,
        cmd_args = ss.EVALUATE_AREA_ARGS,
        condition = ss.EVALUATE_AREA_COND,
        input_size = ss.EVALUATE_AREA_INPUT_SIZE)
    job.register_task(evaluate_area_task)
    
    print "Evaluate volume task"
    evaluate_volume_task = task.DataFlowTask(
        name = ss.EVALUATE_VOLUME,
        cmd_args = ss.EVALUATE_VOLUME_ARGS, 
        condition = ss.EVALUATE_VOLUME_COND, 
        input_size = ss.EVALUATE_VOLUME_INPUT_SIZE)
    job.register_task(evaluate_volume_task)

    print "Feedback task"
    feedback_task = task.DataFlowTask(
        name = ss.FEEDBACK,
        cmd_args = ss.FEEDBACK_ARGS, 
        condition = ss.FEEDBACK_COND,   
        input_size = ss.FEEDBACK_INPUT_SIZE)
    job.register_task(feedback_task)

    print "Run job"
    job.run()

if __name__ == '__main__':
    main()























