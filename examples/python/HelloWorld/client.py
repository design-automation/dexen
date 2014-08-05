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

import random
import time

import dexen
from dexen import remoting
from dexen.common import events
from dexen.client.api import ServerAPI, JobAPI
from dexen.common.task import EventTask


def main():
    server = ServerAPI(username="user", password="test", url="localhost", port=5000)
    assert isinstance(server, ServerAPI)

    job_name = "JOB_%d" % random.randint(0, 1e6)
    job = server.create_job(job_name)
    assert isinstance(job, JobAPI)

    start_time = time.time()

    job.upload("event_main.py")

    task1 = EventTask("PeriodicTask5", ["python", "event_main.py"], events.PeriodicTimeEvent(5))
    task2 = EventTask("InitTask", ["python", "event_main.py"], events.JobStartedEvent())
    task3 = EventTask("PeriodicTask10", ["python", "event_main.py"], events.PeriodicTimeEvent(10))
    task4 = EventTask("OneShotTask20", ["python", "event_main.py"], events.OneShotTimeEvent(20))
    task5 = EventTask("FinalizeTask", ["python", "event_main.py"], events.JobStoppedEvent())

    job.register_task(task1)
    job.register_task(task2)
    job.register_task(task3)
    job.register_task(task4)
    job.register_task(task5)
    job.run()

    last_update = 0.0
    for _ in xrange(6): 
        time.sleep(5)
        for execution in job.get_executions(last_update):
            print "-------------- Execution ---------------"
            for key, value in execution.iteritems():
                print "{0}: {1}".format(key, value)
            print ""
        last_update = time.time()

    job.stop()


if __name__ == '__main__':
    main()

