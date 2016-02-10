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
Reads and writes some data.

The condition for this task should look something like this:

{
    "data1":{"$exists":True},
    "data2":{"$exists":False}
}

"""

from dexen_libs.api import data_api

print "executing task..."

data_objects = data_api.GetAssignedDataObjects()

for do in data_objects:
    value = float(do.get_value("data1"))
    do.set_value("data2", value * 2)




