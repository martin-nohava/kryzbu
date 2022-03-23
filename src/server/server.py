# Server side

from audioop import add
import os
import pickle
import asyncio
from pathlib import Path
import ssl
from .loglib import Log
from .db import File_index, User_db
from .rsalib import Rsa


class Server:
    """Implementation of a Kryzbu server (Cryptographically Secure Storage)."""

    IP: str = "127.0.0.1"
    PORT: int = 60606
    EOM: str = '\n' # End of Message sign, should be same as in client.py
    SERVER_FOLDER: Path = Path("server/_data/files/") # Universal Path object for multi OS path declaration
    VERBOSITY: int = None      # Verbosity level set by console-app (kryzbu_server.py)


    @staticmethod
    def start():
        """Start Kryzbu server."""

        Server.init()
        asyncio.run(Server.run())


    @staticmethod
    async def run():
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.check_hostname = False
        ssl_context.load_cert_chain('server.cert', 'server.key')

        server = await asyncio.start_server(
            Server.handle_connection, Server.IP, Server.PORT, ssl=ssl_context)

        addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
        print(f'Serving on {addrs}')

        async with server:
            await server.serve_forever()


    @staticmethod
    async def handle_connection(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Asynch funcion for handling clients requests."""

        data = await reader.readuntil(Server.EOM.encode())
        request = data.decode()[:-1]   # Decode and strip EOM symbol

        if Server.VERBOSITY > 0:
            addr = writer.get_extra_info('peername')
            print(f"Incoming request: '{request}', from: {addr}")

        if 'UPLOAD' in request:
            # Request to upload file, structure: 'UPLOAD FILENAME USERNAME'
            _, file_name, user_name = request.split(';')
            await Server.recieve_file(file_name, user_name, reader, writer)
        elif 'DOWNLOAD' in request:
            # Request to download file, structure: 'DOWNLOAD FILENAME USERNAME'
            _, file_name, user_name = request.split(';')
            await Server.serve_file(file_name, user_name, reader, writer)
        elif 'REMOVE' in request:
            # Request to delete file, structure: 'REMOVE FILENAME USERNAME'
            _, file_name, user_name = request.split(';')
            await Server.remove_file(file_name, user_name, reader, writer)
        elif 'LIST_DIR' in request:
            # Request to list available file for download, structure: 'LIST_DIR'
            _, user_name = request.split(';')
            await Server.list_files(user_name, reader, writer)
        elif 'GETKEY' in request:
            # Request to get server public key
            await Server.send_pubkey(reader, writer)
        else:
            writer.write(f"UN-KNOWN request, use [UPLOAD, DOWNLOAD, LIST_DIR]{Server.EOM}".encode())
            await writer.drain()

        writer.close()
        await writer.wait_closed()


    @staticmethod
    def init() -> None:
        """Checks if required folder structure for server exists, any other initialization stuf should be here."""

        PATHS = (
        'server/_data/files/',
        'server/_data/logs/',
        'server/_data/keys/'
        )
        for path in PATHS:
            # Any missing parents of this path are created as needed, if folder already exists nothing happens
            Path(path).mkdir(parents=True, exist_ok=True)

        # Initiate file index
        File_index.init(Server.SERVER_FOLDER)
        
        #Initiate user database
        User_db.init()

        # Initialize RSA key-pair
        Rsa.init()

        print('[*] Kryzbu server started successfully...')


    @staticmethod
    async def recieve_file(file_name: str, user_name: str, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Receive file from a client."""

        if User_db.name_exists(user_name):
            # User authenticated based on username
            writer.write(f"OK;Authenticated{Server.EOM}".encode())
            await writer.drain()
            
            file_path = Server.SERVER_FOLDER / file_name

            with open(file_path, "wb") as f:
                while True:
                    bytes_read = await reader.read()
                    if not bytes_read:
                        break
                    f.write(bytes_read)
            
            Log.event(Log.Event.UPLOAD, 0, [file_name, user_name])
            File_index.add(file_name, user_name)
        else:
            # User not-authenticated
            writer.write(f"ERROR;NotAuthenticated{Server.EOM}".encode())
            await writer.drain()


    @staticmethod
    async def serve_file(file_name: str, user_name: str, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Send file to a client."""

        if User_db.name_exists(user_name):
            # User authenticated based on username
            file_path = os.path.join(Server.SERVER_FOLDER, file_name)

            if os.path.exists(file_path):
                # Inform client about authentication
                writer.write(f"OK;Authenticated{Server.EOM}".encode())
                await writer.drain()
                
                # Send file info
                file_size = os.path.getsize(file_path)
                writer.write(f"{file_name};{file_size}{Server.EOM}".encode())
                await writer.drain()


                # Send file
                with open(file_path, "rb") as f:
                    while True:
                        bytes_read = f.read(1024)
                        if not bytes_read:
                            break
                        writer.write(bytes_read)
                        await writer.drain()

                Log.event(Log.Event.DOWNLOAD, 0, [file_name, user_name])
                File_index.download(file_name)
            else:
                # Requested file does NOT exist
                writer.write(f"ERROR;FileNotFoundError{Server.EOM}".encode())
        else:
            # User not-authenticated
            writer.write(f"ERROR;NotAuthenticatedError{Server.EOM}".encode())


    @staticmethod
    async def remove_file(file_name: str, user_name: str, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Remove file."""

        if User_db.name_exists(user_name):
            # User authenticated based on username
            file_path = os.path.join(Server.SERVER_FOLDER, file_name)

            if os.path.exists(file_path):
                # Inform client about authentication
                writer.write(f"OK;Authenticated{Server.EOM}".encode())

                os.remove(file_path)
                Log.event(Log.Event.DELETE, 0, [file_name, user_name])
                File_index.delete(file_name)
                writer.write(f"OK;FileDeleted;{file_name}{Server.EOM}".encode())
            else:
                # Requested file does NOT exist
                writer.write(f"ERROR;FileNotFoundError{Server.EOM}".encode())
        else:
            #User not_authenticated
            writer.write(f"ERROR;NotAuthenticatedError{Server.EOM}".encode())

    @staticmethod
    async def list_files(user_name:str, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Send available files for download."""
        
        if User_db.name_exists(user_name):
            # User authenticated based on username
            writer.write(f"OK;Authenticated{Server.EOM}".encode())
            # Send availabe files
            writer.write(pickle.dumps(File_index.return_all()))
        else:
            #User not_authenticated
            writer.write(f"ERROR;NotAuthenticatedError{Server.EOM}".encode())

    @staticmethod
    async def send_pubkey(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Send public key to client."""
        
        # Inform client about authentication
        writer.write(f"OK;Authenticated{Server.EOM}".encode())
        await writer.drain()
        
        # Send file info
        file_size = os.path.getsize(Rsa.get_pub_key_location())
        writer.write(f"{os.path.basename(Rsa.get_pub_key_location())};{file_size}{Server.EOM}".encode())
        await writer.drain()


        # Send file
        with open(Rsa.get_pub_key_location(), "rb") as f:
            while True:
                bytes_read = f.read(1024)
                if not bytes_read:
                    break
                writer.write(bytes_read)
                await writer.drain()
