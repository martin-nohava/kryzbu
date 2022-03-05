# This is command-line based Client application for handling connection to Kryzbu server.
#
# Source code available on: https://github.com/martin-nohava/kryzbu.
# Path to this file can be added to PATH (Windows) to call it
# as a standard command-line tool from everywhere.

import argparse
from client import client

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
parser.add_argument("-l", "--list", help="list available files to download", action="store_true")
parser.add_argument("-la", "--listall", help="list available files to download including additional info", action="store_true")
group.add_argument("-u", "--upload", metavar="FILE", help="upload file to server", action="extend", nargs="+", type=str)
group.add_argument("-d", "--download", metavar="FILE", help="download file from server", action="extend", nargs="+", type=str)
group.add_argument("-r", "--remove", metavar="FILE", help="remove file from server", action="extend", nargs="+", type=str)
args = parser.parse_args()

if args.upload:
    # Upload file to a server
    for file in args.upload:
        client.Client.upload(file)
elif args.download:
    # Download file from server
    for file in args.download:
        client.Client.download(file)
elif args.remove:
    # Remove file from server
    for file in args.remove:
        client.Client.remove(file)
elif args.list:
    # List available files on server
    client.Client.list_files(False)
elif args.listall:
    # List available files on server including additional info
    client.Client.list_files(True)
else:
    parser.print_help()
