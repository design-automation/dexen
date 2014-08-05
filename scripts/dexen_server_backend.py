

import argparse

import dexen
from dexen.common import remoting, constants, utils
from dexen.server.backend import endpoint


def parse_args():
    parser = argparse.ArgumentParser(description="Start Node")
    parser.add_argument("--log-path", help="log file path.")
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
    endpoint.start(db_addr)


if __name__ == '__main__':
    main()
