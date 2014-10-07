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
Strat a dexen server frontend.
"""

import argparse

import dexen
from dexen.common import remoting, constants, utils
from dexen.server.frontend import endpoint


def parse_args():
    parser = argparse.ArgumentParser(description="Start Node")
    parser.add_argument("--log-path", help="log file path.")
    parser.add_argument("--backend-ip", default=remoting.get_my_ip(),
                        help="The server backend ip address.")
    parser.add_argument("--backend-port", type=int,
                        default=constants.SERVER_BACKEND_PORT,
                        help="The server backend port.")
    parser.add_argument("--db-ip", default=remoting.get_my_ip(),
                        help="The database ip address.")
    parser.add_argument("--db-port", type=int,
                        default=constants.MONGOD_PORT,
                        help="The database port.")
    return parser.parse_args()


def main():
    args = parse_args()
    utils.setup_logging(args.log_path)
    db_addr = remoting.EndPointAddress(args.db_ip, args.db_port)
    backend_addr = remoting.EndPointAddress(args.backend_ip, args.backend_port)
    endpoint.start_webserver(backend_addr, db_addr)


if __name__ == '__main__':
    main()