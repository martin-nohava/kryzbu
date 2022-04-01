# This is command-line based Client application for handling connection to Kryzbu server.
#
# Source code available on: https://github.com/martin-nohava/kryzbu.
# Path to this file can be added to PATH (Windows) to call it
# as a standard command-line tool from everywhere.

import argparse
import asyncio
from multiprocessing.connection import Client
from client import client

client.Client.init()

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
parser.add_argument("-i", "--info", help="show user information and client settings", action="store_true")
parser.add_argument("-l", "--list", help="list available files to download", action="store_true")
parser.add_argument("-s", "--switchusr", help="switch to different user account", action="store_true")
parser.add_argument("-la", "--listall", help="list available files to download including additional info", action="store_true")
parser.add_argument("-fk", "--flushkey", help="flush saved server public key", action="store_true")
parser.add_argument("-V", "--version", action='count', default=0)
group.add_argument("-u", "--upload", metavar="FILE", help="upload file to server", action="extend", nargs="+", type=str)
group.add_argument("-d", "--download", metavar="FILE", help="download file from server", action="extend", nargs="+", type=str)
group.add_argument("-r", "--remove", metavar="FILE", help="remove file from server", action="extend", nargs="+", type=str)
parser.add_argument("--setfolder", metavar="/path/to/file", help="set download folder", type=str)
args = parser.parse_args()

if args.upload:
    # Upload file to a server
    client.Client.online_operation(True)
    for file in args.upload:
        asyncio.run(client.Client.upload(file))
elif args.download:
    # Download file from server
    client.Client.online_operation(True)
    for file in args.download:
        asyncio.run(client.Client.download(file))
elif args.remove:
    # Remove file from server
    client.Client.online_operation(True)
    for file in args.remove:
        asyncio.run(client.Client.remove(file))
elif args.list:
    # List available files on server
    client.Client.online_operation(True)
    asyncio.run(client.Client.list_files(False))
elif args.listall:
    # List available files on server including additional info
    client.Client.online_operation(True)
    asyncio.run(client.Client.list_files(True))
elif args.info:
    # List user information
    client.Client.online_operation(False)
    client.Client.info()
elif args.switchusr:
    # Change user
    client.Client.online_operation(False)
    client.Client.change_user()
elif args.flushkey:
    # Delete saved server key
    client.Client.online_operation(False)
    client.Client.flush_key()
elif args.setfolder:
    client.Client.set_download_folder(args.setfolder)
elif args.version:
    # Show program version and info
    client.Client.info()
else:
    parser.print_help()
