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
Start a dexen node.
"""

import argparse

import dexen
from dexen.common import remoting, constants, utils
from dexen.node import endpoint


def parse_args():
    parser = argparse.ArgumentParser(description="Start Node")
    parser.add_argument("--log-path", help="log file path.")
    parser.add_argument("--server-ip", default=remoting.get_my_ip(),
                        help="The server backend ip address.")
    parser.add_argument("--server-port", type=int,
                        default=constants.SERVER_BACKEND_PORT,
                        help="The server backend port.")
    parser.add_argument("--max-workers", type=int, default=utils.cpu_count(),
                        help="Maximum number of workers allowed to run.")
    return parser.parse_args()


def main():
    args = parse_args()
    utils.setup_logging(args.log_path)
    svr_addr = remoting.EndPointAddress(args.server_ip, args.server_port)
    endpoint.start(svr_addr, args.max_workers)


if __name__ == '__main__':
    main()
