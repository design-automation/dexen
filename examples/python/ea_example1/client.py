'''
Created on Jul 25, 2013

@author: Cihat Basol
'''


import time, random, sys

from dexen.client import api
from dexen.common import events, task

from common import (INITIALIZE, DEVELOP, EVAL_1, EVAL_2, EVAL_3, FEEDBACK,
                    FEEDBACK_SIZE, DEVELOP_SIZE, EVAL_1_SIZE, EVAL_2_SIZE,
                    EVAL_3_SIZE, GENOTYPE, PHENOTYPE, SCORE_1, SCORE_2, SCORE_3,
                    IS_ALIVE)


def main():

    print "Connect to server"
    server = api.ServerAPI(username="user", password="test", 
                           url="localhost", port=5000)
    assert isinstance(server, api.ServerAPI)
    
    print "Created job "
    job_name = "JOB" + str(random.randint(0,1e6))
    job = server.create_job(job_name)
    assert isinstance(job, api.JobAPI)
    print "Job name = " + job_name
    
    print "Upload python files"
    job.upload("common.py")
    job.upload("main.py")
    job.upload("event_main.py")
    
    print "Create tasks"
    init_task = task.EventTask("Initialize Task",
                               ["python", "main.py", INITIALIZE],
                               events.JobStartedEvent())

    counter_task = task.EventTask("Counter task",
                                  ["python", "event_main.py"],
                                  events.PeriodicTimeEvent(10))

    development_cond = {
        GENOTYPE : { "$exists" : True },
        PHENOTYPE : { "$exists" : False }
    }
    eval_1_cond = {
        PHENOTYPE : { "$exists" : True },
        SCORE_1 : { "$exists" : False }
    }
    eval_2_cond = {
        PHENOTYPE : { "$exists" : True },
        SCORE_2 : { "$exists" : False }
    }
    eval_3_cond = {
        PHENOTYPE : { "$exists" : True },
        SCORE_3 : None
    }
    feedback_cond = {
        IS_ALIVE : True,
        SCORE_1 : { "$exists" : True },
        SCORE_2 : { "$exists" : True },
        SCORE_3 : { "$ne" : None }
    }
    development_task = task.DataFlowTask("Development Task",
                                         ["python", "main.py", DEVELOP],
                                         development_cond, DEVELOP_SIZE)
    eval_1_task = task.DataFlowTask("Eval1 Task",
                                    ["python", "main.py", EVAL_1],
                                    eval_1_cond, EVAL_1_SIZE)
    eval_2_task = task.DataFlowTask("Eval2 Task",
                                    ["python", "main.py", EVAL_2],
                                    eval_2_cond, EVAL_2_SIZE)
    eval_3_task = task.DataFlowTask("Eval3 Task",
                                    ["python", "main.py", EVAL_3],
                                    eval_3_cond, EVAL_3_SIZE)
    feedback_task = task.DataFlowTask("Feedback Task",
                                      ["python", "main.py", FEEDBACK],
                                      feedback_cond, FEEDBACK_SIZE)

    print "Register tasks"
    job.register_task(init_task)
    job.register_task(counter_task)
    job.register_task(development_task)
    job.register_task(eval_1_task)
    job.register_task(eval_2_task)
    job.register_task(eval_3_task)
    job.register_task(feedback_task)
    
    print "Run job"
    job.run()

    try:
        last_update = 0.0
        for _ in xrange(120000):
            time.sleep(10)
            print "Check if job is still running"
            jobs_data = server.get_jobs_data()
            for jd in jobs_data:
                if jd['job_name'] == job_name and jd['status'] == 'STOPPED':
                    print "Job has stopped, so exiting"
                    sys.exit(0)

            print "Get latest executions"
            for execution in job.get_executions(last_update):
                print "-------------- Execution ---------------"
                for key, value in execution.iteritems():
                    print "{0}: {1}".format(key, value)
                print ""
            last_update = time.time()
    except Exception as exc:
        print exc
        job.stop()
        print "Stopped job"


if __name__ == '__main__':
    main()























