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

import os
import tempfile


DEXEN_DIR = os.path.join(tempfile.gettempdir(), "dexen")


def create_dir(path, *args):
    if not os.path.exists(path):
        os.mkdir(path)
    for arg in args:
        path = os.path.join(path, arg)
        if not os.path.exists(path):
            os.mkdir(path)
    return path


def get_node_dir(node_name, create=False):
    if create:
        create_dir(DEXEN_DIR, node_name)
    return os.path.join(DEXEN_DIR, node_name)


def get_job_dir(worker_name, user_name, job_name, create=False):
    if create:
        create_dir(DEXEN_DIR, worker_name, user_name, job_name)
    return os.path.join(DEXEN_DIR, worker_name, user_name, job_name)


def get_worker_dir(worker_name, create=False):
    if create:
        create_dir(DEXEN_DIR, worker_name)
    return os.path.join(DEXEN_DIR, worker_name)
