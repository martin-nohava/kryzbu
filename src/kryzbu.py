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
group.add_argument("-u", "--upload", metavar="FILE", help="upload file to server", action="extend", nargs="+", type=str)
group.add_argument("-d", "--download", metavar="FILE", help="download file from server", action="extend", nargs="+", type=str)
args = parser.parse_args()

if args.upload:
    """Upload file to a server."""
    for file in args.upload:
        client.Client.send_file(file)
elif args.download:
    """Download file from server."""
    print("Download not implemented yet!!!")
elif args.list:
    print("Listing is not implemented yet!!!")
else:
    parser.print_help()


