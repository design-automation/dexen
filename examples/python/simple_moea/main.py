'''
Script for running ea
'''
from time import gmtime, strftime

from dexen_libs.api import server_api, data_api
import settings as ss

USERNAME = "phtj"
PASSWORD="phtj"

DEBUG = True

def log(s):
    if DEBUG:
        print s

def main():

    print "Connect to server"
    server = server_api.ServerAPI(username=USERNAME, password=PASSWORD, url="localhost", port=5000)
    assert isinstance(server, server_api.ServerAPI)
    
    print "Created job "
    job_name = "Job_"+strftime("%H_%M_%S", gmtime())
    job = server.create_job(job_name)
    assert isinstance(job, server_api.JobAPI)
    print "Job name = " + job_name
    
    print "Upload python files"
    job.upload("tasks.py")
    job.upload("settings.py")

    print "Initialize task"
    initialize_task = data_api.EventTask(
        name = ss.INITIALIZE,
        cmd_args = ss.INITIALIZE_ARGS, 
        event = data_api.JobStartedEvent())
    job.register_task(initialize_task)
    
    print "Develop task"
    develop_task = data_api.DataFlowTask(
        name = ss.DEVELOP,
        cmd_args = ss.DEVELOP_ARGS,
        condition = ss.DEVELOP_COND,
        input_size = ss.DEVELOP_INPUT_SIZE)
    job.register_task(develop_task)
    
    print "Evaluate area task"
    evaluate_area_task = data_api.DataFlowTask(
        name = ss.EVALUATE_AREA,
        cmd_args = ss.EVALUATE_AREA_ARGS,
        condition = ss.EVALUATE_AREA_COND,
        input_size = ss.EVALUATE_AREA_INPUT_SIZE)
    job.register_task(evaluate_area_task)
    
    print "Evaluate volume task"
    evaluate_volume_task = data_api.DataFlowTask(
        name = ss.EVALUATE_VOLUME,
        cmd_args = ss.EVALUATE_VOLUME_ARGS, 
        condition = ss.EVALUATE_VOLUME_COND, 
        input_size = ss.EVALUATE_VOLUME_INPUT_SIZE)
    job.register_task(evaluate_volume_task)

    print "Feedback task"
    feedback_task = data_api.DataFlowTask(
        name = ss.FEEDBACK,
        cmd_args = ss.FEEDBACK_ARGS, 
        condition = ss.FEEDBACK_COND,   
        input_size = ss.FEEDBACK_INPUT_SIZE)
    job.register_task(feedback_task)

    print "Run job"
    job.run()

if __name__ == '__main__':
    main()

