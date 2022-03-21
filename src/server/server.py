# Server side

import os
import pickle
import asyncio
import uuid
from pathlib import Path
from .loglib import Log
from .db import File_index, User_db
from .rsalib import Rsa
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import PKCS1_OAEP, AES


class Server:
    """Implementation of a Kryzbu server (Cryptographically Secure Storage)."""

    IP = "127.0.0.1"
    PORT = 60606
    EOM = '\n' # End of Message sign, should be same as in client.py
    SERVER_FOLDER = Path("server/_data/files/") # Universal Path object for multi OS path declaration


    @staticmethod
    def start():
        """Start Kryzbu server."""

        Server.init()
        asyncio.run(Server.run())


    @staticmethod
    async def run():
        server = await asyncio.start_server(
            Server.handle_connection, Server.IP, Server.PORT)

        addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
        print(f'Serving on {addrs}')

        async with server:
            await server.serve_forever()


    @staticmethod
    async def handle_connection(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Asynch funcion for handling clients requests."""

        # Recieve encrypted request from client
        data = await reader.readuntil(Server.EOM.encode())
        request = data.decode()[:-1]   # Decode and strip EOM symbol

        # Requests not requireing authentication
        if 'GETKEY' in request:
            # Request to get server public key
            await Server.send_pubkey(reader, writer)
        elif 'LOGIN' in request:
            # Start login handshake with client
            await Server.autenticate(reader, writer)
        
        user_name, c_len, tag_len, pad_len, nonce_len = request.split(';')
        c = await reader.read(int(c_len))
        tag = await reader.read(int(tag_len))
        pad = await reader.read(int(pad_len))
        nonce = await reader.read(int(nonce_len))

        # Decrypt request with aes_key linked to the user
        if User_db.name_exists(user_name):
            aes_key = User_db.get_record(user_name)[2]
        else:
            writer.write(f"ERROR;NotAuthenticatedError{Server.EOM}".encode())
        aes_instance = AES.new(aes_key, AES.MODE_EAX, nonce)
        m = aes_instance.decrypt_and_verify(c, tag)

        # Get firt 8 bytes of message = pad
        decryped_pad = m[0:8]

        # Decide if pad was successfully decripted
        if decryped_pad == pad:
            # Authenticated
            writer.write(f"OK;Authenticated{Server.EOM}".encode())
            command, file_name = m[8:].decode().split(';')

            if 'UPLOAD' in command:
                # Request to upload file, structure: 'UPLOAD FILENAME USERNAME'
                await Server.recieve_file(file_name, user_name, reader, writer)
            elif 'DOWNLOAD' in command:
                # Request to download file, structure: 'DOWNLOAD FILENAME USERNAME'
                await Server.serve_file(file_name, user_name, reader, writer)
            elif 'REMOVE' in command:
                # Request to delete file, structure: 'REMOVE FILENAME USERNAME'
                await Server.remove_file(file_name, user_name, reader, writer)
            elif 'LIST_DIR' in command:
                # Request to list available file for download, structure: 'LIST_DIR'
                await Server.list_files(user_name, reader, writer)
            else:
                writer.write(f"UN-KNOWN request, use [UPLOAD, DOWNLOAD, LIST_DIR]{Server.EOM}".encode())
                await writer.drain()
        else:
            # Not Authenticated
            writer.write(f"ERROR;NotAuthenticatedError{Server.EOM}".encode())

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
            
        file_path = Server.SERVER_FOLDER / file_name

        # Recieve encrypted request from client
        data = await reader.readuntil(Server.EOM.encode())
        request = data.decode()[:-1]   # Decode and strip EOM symbol

        c_len, tag_len, pad_len, nonce_len = request.split(';')

        # Save encrypted data to disk, plus tag, pad and nonce
        TEMP_FILE = Path("server/_data/cache_" + user_name + ".temp")
        with open(TEMP_FILE, "wb") as f:
                while True:
                    bytes_read = await reader.read()
                    if not bytes_read:
                        break
                    f.write(bytes_read)

        # Extract tag, pad and nonce from file
        f = os.open(TEMP_FILE, os.O_RDONLY)

        os.lseek(f, int(c_len), 0)
        tag = os.read(f, int(tag_len))
        
        os.lseek(f, int(c_len) + int(tag_len), 0)
        pad = os.read(f, int(pad_len))
        print(pad)

        os.lseek(f, int(c_len) + int(tag_len) + int(pad_len), 0)
        nonce = os.read(f, int(nonce_len))

        os.close(f)

        # Extract decryped_pad
        f = os.open(TEMP_FILE, os.O_RDONLY)

        os.lseek(f, 0, 0)
        encrypter_pad = os.read(f, int(pad_len))
        aes_instance = AES.new(User_db.get_record(user_name)[2], AES.MODE_EAX, nonce)
        decryped_pad = aes_instance.decrypt(encrypter_pad)

        os.close(f)
        
        # Decide if pad was successfully decripted
        if decryped_pad == pad:
            # Decrypt rest of the file and save it
            # Open new destination file df
            with open(file_path, "wb") as df:
                total_bytes_read = 0
                # Open temp file as source file sf
                sf = os.open(TEMP_FILE, os.O_RDONLY)
                # Skip pad
                os.lseek(sf, int(pad_len), 0)
                while True:
                    # How much we want to read (1024)
                    total_bytes_read += 1024
                    # If this amount is still available to read, read it
                    if total_bytes_read % (int(c_len) - int(pad_len)) == total_bytes_read:
                        # Read bytes
                        bytes_read = os.read(sf, 1024)
                        # Decrypt
                        m = aes_instance.decrypt(bytes_read)
                        # Save to new file df
                        df.write(m)
                    else:
                        # Read only remaining bytes
                        remaining_bytes = total_bytes_read % (int(c_len) - int(pad_len))
                        bytes_read = os.read(sf, remaining_bytes + 1)
                        # Decrypt
                        m = aes_instance.decrypt(bytes_read)
                        # Save to new file df
                        df.write(m)
                        break
                os.close(sf)

            Log.event(Log.Event.UPLOAD, 0, [file_name, user_name])
            File_index.add(file_name, user_name)

        if os.path.exists(TEMP_FILE):
            os.remove(TEMP_FILE)

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

        # Encrypt data before sending
        pad = get_random_bytes(8)
        m = pad + pickle.dumps(File_index.return_all())
        aes_key = User_db.get_record(user_name)[2]
        aes_instance = AES.new(aes_key, AES.MODE_EAX)
        c, tag = aes_instance.encrypt_and_digest(m)

        payload = (c, tag, pad, aes_instance.nonce)

        # Send data
        writer.write(f"{len(c)};{len(tag)};{len(pad)};{len(aes_instance.nonce)}".encode() + Server.EOM.encode())
        writer.writelines(payload)

    @staticmethod
    async def send_pubkey(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Send public key to client."""
        
        # Inform client about authentication
        writer.write(f"OK;{Server.EOM}".encode())
        await writer.drain()

        # Send file
        with open(Rsa.get_pub_key_location(), "rb") as f:
            while True:
                bytes_read = f.read(1024)
                if not bytes_read:
                    break
                writer.write(bytes_read)
                await writer.drain()
    
    @staticmethod
    async def autenticate(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Autenticate user via handshake."""

        # Inform client that server is ready for handshake
        writer.write(f"OK;Ready{Server.EOM}".encode())
        await writer.drain()

        # Await c = E(username, usr-nonce) from client
        paylen = await reader.readuntil(Server.EOM.encode())
        paylen = paylen.decode()[:-1]
        c = await reader.read(int(paylen))

        # Import server private key from file
        private_key = RSA.import_key(open(Rsa.get_priv_key_location()).read())

        # Create new instance of RSA cypher
        rsa_instance = PKCS1_OAEP.new(private_key)
        m = rsa_instance.decrypt(c)
        m = m.decode()

        # Prepare information about user requesting login
        username, usr_nonce = m.split(';')
        password = User_db.get_record(username)[1]
        byte_pas = bytes.fromhex(password)
        ser_nonce = uuid.uuid4().hex
        salt = User_db.get_record(username)[3]
        byte_salt = bytes.fromhex(salt)

        # Responde with E((usr-nonce, ser-nonce), hash(password)), salt
        m = f"{usr_nonce};{ser_nonce}".encode("utf-8")
        aes_instance = AES.new(byte_pas, AES.MODE_EAX)
        c, tag = aes_instance.encrypt_and_digest(m)

        payload = (c, tag, aes_instance.nonce, byte_salt)

        # Send data
        writer.write(f"{len(c)};{len(tag)};{len(aes_instance.nonce)};{len(byte_salt)}".encode() + Server.EOM.encode())
        writer.writelines(payload)

        # Await response and D((usr-nonce, ser-nonce), pub.key)
        paylen = await reader.readuntil(Server.EOM.encode())
        paylen = paylen.decode()[:-1]
        c = await reader.read(int(paylen))

        # Decypher message (usr-nonce, ser-nonce)
        m = rsa_instance.decrypt(c)
        m = m.decode()

        # Compare original ser-nonce and received ser-nonce from client
        _, rec_ser_nonce = m.split(';')
        if rec_ser_nonce == str(ser_nonce):
            print(f'INFO: User {username} has successfully loged in from client.')
            aes_key = User_db.get_record(username)[2]

            # Encrypt aes_key with password
            aes_instance = AES.new(byte_pas, AES.MODE_EAX)
            c, tag = aes_instance.encrypt_and_digest(aes_key)

            payload = (c, tag, aes_instance.nonce)

            # Send aes_key to client
            writer.write(f"{len(c)};{len(tag)};{len(aes_instance.nonce)}".encode() + Server.EOM.encode())
            writer.writelines(payload)

        else:
            print(f'WARNING: User {username} has failed to loged in from client.')
