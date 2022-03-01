# This is command-line based application for handling Kryzbu server.
#
# Source code available on: https://github.com/martin-nohava/kryzbu.
# Path to this file can be added to PATH (Windows) to call it
# as a standard command-line tool from everywhere.

from server import server


print('[*] Kryzbu server started...')
server.Server.run()
print('[*] Kryzbu server ended...')