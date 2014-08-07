"""
Stop the job
"""
from dexen_libs.api import server_api


print "Connect to server"
server = server_api.ServerAPI(username="user", password="test", url="localhost", port=5000)
print "Get Jobs"

jobs_data = server.get_jobs_data()
for jd in jobs_data:
	name = jd["job_name"]
	status = jd["status"]
	if status == "RUNNING":
		print "Stopping job ", name
		j = server.get_job(name)
		j.stop()























