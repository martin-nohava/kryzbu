# This is command-line based application for handling Kryzbu server.
#
# Source code available on: https://github.com/martin-nohava/kryzbu.
# Path to this file can be added to PATH (Windows) to call it
# as a standard command-line tool from everywhere.

from server import server
from server.db import User_db
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-l", "--list", help="list all users", action="store_true")
parser.add_argument("--remove" , metavar="username", nargs='+', help="remove users from user database")
parser.add_argument("--register", metavar="spec", nargs='+', help="register new user to server", action="extend")
args = parser.parse_args()

if args.register:
    # Add new record to user database
    if len(args.register) == 4:
        User_db.add(args.register[0], args.register[1], args.register[2], args.register[3])
    else:
        raise Exception(f"flag: --register needs 4 positional arguments, {len(args.register)} was given. \nUsage: kryzbu_server.py --register <username> <pass_hash> <pub_key> <secrete>")
elif args.remove:
    # Remove user from useres database
    for user_name in args.remove:
        User_db.delete(user_name)
elif args.list:
    # List all registered users (user table)
    User_db.show_all()
else:
    print('[*] Kryzbu server starting...')
    server.Server.run()

