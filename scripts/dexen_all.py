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
Start a dexen server backend, a server frontend, and a node.

This is a quick way to start dexen on a single computer. Also, the advantage of starting this way is
that you only end up with one command window.
"""

from multiprocessing import Process

import argparse

import dexen
from dexen.common import remoting, constants, utils
from dexen.server.backend import endpoint as back_endpoint
from dexen.server.frontend import endpoint as front_endpoint
from dexen.node import endpoint as node_endpoint

def parse_args():
    parser = argparse.ArgumentParser(description="Start Server Backend, Server Frontend, and one Node")
    parser.add_argument("--log-path", help="log file path.")
    #mongodb, used by backend and frontend
    parser.add_argument("--db-ip", default=remoting.get_my_ip(),
                        help="The database ip address.")
    parser.add_argument("--db-port", type=int,
                        default=constants.MONGOD_PORT,
                        help="The database port.")
    #for the frontend
    parser.add_argument("--backend-ip", default=remoting.get_my_ip(),
                        help="The server backend ip address.")
    parser.add_argument("--backend-port", type=int,
                        default=constants.SERVER_BACKEND_PORT,
                        help="The server backend port.")
    #for the node
    parser.add_argument("--server-ip", default=remoting.get_my_ip(),
                        help="The server backend ip address.")
    parser.add_argument("--server-port", type=int,
                        default=constants.SERVER_BACKEND_PORT,
                        help="The server backend port.")
    parser.add_argument("--max-workers", type=int, default=utils.cpu_count(),
                        help="Maximum number of workers allowed to run.")
    return parser.parse_args()

def start_server_backend(args):
    utils.setup_logging(args.log_path)
    db_addr = remoting.EndPointAddress(args.db_ip, args.db_port)
    back_endpoint.start(db_addr)

def start_server_frontend(args):
    utils.setup_logging(args.log_path)
    db_addr = remoting.EndPointAddress(args.db_ip, args.db_port)
    backend_addr = remoting.EndPointAddress(args.backend_ip, args.backend_port)
    front_endpoint.start_webserver(backend_addr, db_addr)
    
def start_node(args):
    utils.setup_logging(args.log_path)
    svr_addr = remoting.EndPointAddress(args.server_ip, args.server_port)
    node_endpoint.start(svr_addr, args.max_workers)
    
def main():
    args = parse_args()
    print "===== Start a process for the backend ====="
    server_backend = Process(target=start_server_backend, args=(args,))
    server_backend.start()

    print "===== Start a process for the frontend ====="
    server_frontend = Process(target=start_server_frontend, args=(args,))
    server_frontend.start()

    print "===== Start a process for the node ====="
    node = Process(target=start_node, args=(args,))
    node.start()


    
if __name__ == '__main__':
    main()