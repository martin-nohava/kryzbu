# This is command-line based application for handling Kryzbu server.
#
# Source code available on: https://github.com/martin-nohava/kryzbu.
# Path to this file can be added to PATH (Windows) to call it
# as a standard command-line tool from everywhere.

from logging import exception
from server import server
from server.db import User_db
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("--register", metavar="spec", nargs='+' ,help="register new user to server", action="extend")
args = parser.parse_args()

if args.register:
    if len(args.register) == 4:
        User_db.add(args.register[0], args.register[1], args.register[2], args.register[3])
    else:
        raise Exception(f"flag: --register needs 4 positional arguments, {len(args.register)} was given. \nUsage: kryzbu_server.py --register <username> <pass_hash> <pub_key> <secrete>")
else:
    print('[*] Kryzbu server starting...')
    server.Server.run()

