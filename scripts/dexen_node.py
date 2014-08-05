"""
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
