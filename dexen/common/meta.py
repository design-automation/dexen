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


import cPickle


class TaskMeta(object):
    def __init__(self, job_name, task_name, task_func, task_cond=None, 
                input_size=None, task_event=None):
        self.job_name = job_name
        self.task_name = task_name
        self._task_func = cPickle.dumps(task_func)
        self._task_cond = cPickle.dumps(task_cond)
        self._task_event = cPickle.dumps(task_event)
        self.input_size = input_size
    
    @property
    def task_func(self):
        return cPickle.loads(self._task_func)

    @property
    def task_cond(self):
        return cPickle.loads(self._task_cond)
    
    @property
    def task_event(self):
        return cPickle.loads(self._task_event)
