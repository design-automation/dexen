"""
Stops all jobs
"""
from dexen_libs.api import server_api


print "Connect to server"
SERVER = server_api.ServerAPI(username="xyz", password="abc", url="localhost", port=5000)
print "Get Jobs"

JOBS_DATA = SERVER.get_jobs_data()
for jd in JOBS_DATA:
    name = jd["job_name"]
    status = jd["status"]
    if status == "STOPPED":
        print "Deleting job ", name
        SERVER.delete_job(name)
