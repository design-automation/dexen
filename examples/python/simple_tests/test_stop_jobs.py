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
Stops all jobs
"""
from dexen_libs.api import server_api

USERNAME = "user"
PASSWORD = "pswd"


def main():
    print "Connect to server"
    SERVER = server_api.ServerAPI(username=USERNAME, password=PASSWORD, url="localhost", port=5000)
    print "Get Jobs"

    JOBS_DATA = SERVER.get_jobs_data()
    for jd in JOBS_DATA:
        name = jd["job_name"]
        status = jd["status"]
        if status == "RUNNING":
            print "Stopping job ", name
            j = SERVER.get_job(name)
            j.stop()

if __name__ == '__main__':
    main()
    