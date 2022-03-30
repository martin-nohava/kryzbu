# This is command-line based application for handling Kryzbu server.
#
# Source code available on: https://github.com/martin-nohava/kryzbu.
# Path to this file can be added to PATH (Windows) to call it
# as a standard command-line tool from everywhere.

from server import server
from server.db import User_db
from server.loglib import Log
import argparse


parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
parser.add_argument("-l", "--list", help="list all users", action="store_true")
parser.add_argument("--remove" , metavar="username", nargs='+', help="remove users from user database")
parser.add_argument("--register", metavar="spec", nargs='+', help="register new user to server", action="extend")
parser.add_argument("-v", "--verbose", action='count', default=0)
group.add_argument("-i", "--integrity", metavar="FILE", help="check log file integrity", action="extend", nargs="+", type=str)
args = parser.parse_args()

if args.register:
    # Add new record to user database
    if len(args.register) == 2:
        User_db.add(args.register[0], args.register[1])
    else:
        raise Exception(f"flag: --register needs 2 positional arguments, {len(args.register)} was given. \nUsage: kryzbu_server.py --register <username> <password>")
elif args.remove:
    # Remove user from useres database
    for user_name in args.remove:
        User_db.delete(user_name)
elif args.list:
    # List all registered users (user table)
    User_db.show_all()
elif args.integrity:
    # Check integrity of selected logfile
    for file_name in args.integrity:
        Log.verify(file_name)
else:
    print('[*] Kryzbu server starting...')
    server.Server.VERBOSITY = args.verbose
    server.Server.start()

