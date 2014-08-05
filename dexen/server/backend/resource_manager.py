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


_next_node_num = 1
_next_worker_num = 1
_new_nodes = []
_new_workers = []


class ResourceManager(object):
    def __init__(self):
        pass

    def next_node_name(self):
        global _next_node_num
        node_name = "NODE%d"%(_next_node_num, )
        _next_node_num += 1
        return node_name

    def next_worker_name(self):
        global _next_worker_num
        worker_name = "WORKER%d"%(_next_worker_num, )
        _next_worker_num += 1
        return worker_name

    def register_node(self, address):
        node_name = self.next_node_name()
        _new_nodes.append((node_name, address))
        return node_name

    def register_worker(self, address, worker_name):
        _new_workers.append((worker_name, address))

    def get_new_nodes(self):
        global _new_nodes
        nodes = _new_nodes
        _new_nodes = []
        return nodes

    def get_new_workers(self):
        global _new_workers
        workers = _new_workers
        _new_workers = []
        return workers

