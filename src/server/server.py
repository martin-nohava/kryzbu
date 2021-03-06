# Server side

import os
import pickle
import asyncio
import uuid
from pathlib import Path
import ssl
from .loglib import Log
from .db import File_index, Hmac_index, User_db
from .rsalib import Rsa
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
import climage


class Server:
    """
    | Implementation of a Kryzbu server (Cryptographically Secure Storage).
    |
    | **Global variables in this class:**
    | **IP** (*str*) – IPv4 address of the host system
    | **PORT** (*int*) – server binds to this port on the host system
    | **EOM** (*str*) – End of Message sign, should be same as in *client.py*, helps in byte stream signaling
    | **SERVER_FOLDER** (*Path*) – defines where to store user files on server
    | **VERBOSITY** (*int*) – verbosity level set by user
    """

    IP: str = "127.0.0.1"
    PORT: int = 60606
    EOM: str = "\n"  # End of Message sign, should be same as in client.py
    SERVER_FOLDER: Path = Path(
        "server/_data/files/"
    )  # Universal Path object for multi OS path declaration
    VERBOSITY: int = None  # Verbosity level set by console-app (kryzbu_server.py)

    @staticmethod
    def start():
        """
        Starts Kryzbu server, calls initialization checks before it continues.

        """

        Server.init()
        try:
            asyncio.run(Server.run())
        except KeyboardInterrupt:
            print("\nShutting down server...")
            print("Bye!")

    @staticmethod
    async def run():
        """
        Creates server instance, SSL context and starts listening for connections on selected port and IP address. Handles establishing new secure connections with clients.

        """
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.check_hostname = False
        ssl_context.load_cert_chain("server.cert", "server.key")

        server = await asyncio.start_server(
            Server.handle_connection, Server.IP, Server.PORT, ssl=ssl_context
        )

        addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
        print(f"Serving on {addrs}")

        async with server:
            await server.serve_forever()

    @staticmethod
    async def handle_connection(
        reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        """

        | Async function for handling client connections.
        |
        | **Accepts several types of requests:**
        | For any clients:
        | *GETKEY:* client requests server public key
        | *LOGIN:* client (user) requests authentication
        |
        | For authenticated clients only:
        | *UPLOAD:* client requests to upload a file
        | *DOWNLOAD:* client requests to download a file
        | *REMOVE:* client requests to delete a file
        | *LIST_DIR:* client requests to list all files he owns

        Authenticated clients own *Session ID* in form of symetric user unique AES key. This key is used for *request* encryption. 
        If client requests any action from server, he encrypts this request using AES key and sends this cyphertext *c* and his username.

        .. math::
                c = E(aeskey_{username}, request)

        Server then tries to decrypt the request from cyphertext *c*, using user specific key from *users.db*. On success performs the requested action.

        .. math::
                m = D(aeskey_{username}, c)

        :param reader: reader instance
        :type reader: asyncio.StreamReader
        :param writer: writer instance
        :type writer: asyncio.StreamWriter

        """

        # Recieve encrypted request from client
        data = await reader.readuntil(Server.EOM.encode())
        request = data.decode()[:-1]  # Decode and strip EOM symbol

        if Server.VERBOSITY > 0:
            addr = writer.get_extra_info("peername")
            print(f"Incoming request: '{request}', from: {addr}")

        # Requests not requireing authentication
        if "GETKEY" in request:
            # Request to get server public key
            await Server.send_pubkey(reader, writer)
            return
        elif "LOGIN" in request:
            # Start login handshake with client
            await Server.autenticate(reader, writer)
            return

        user_name, c_len, tag_len, pad_len, nonce_len = request.split(";")
        c = await reader.read(int(c_len))
        tag = await reader.read(int(tag_len))
        pad = await reader.read(int(pad_len))
        nonce = await reader.read(int(nonce_len))

        # Decrypt request with aes_key linked to the user
        if User_db.name_exists(user_name):
            aes_key = User_db.get_record(user_name)[2]
        else:
            writer.write(f"ERROR;NotAuthenticatedError{Server.EOM}".encode())
            return
        aes_instance = AES.new(aes_key, AES.MODE_EAX, nonce)
        m = aes_instance.decrypt_and_verify(c, tag)

        # Get firt 8 bytes of message = pad
        decryped_pad = m[0:8]

        # Decide if pad was successfully decripted
        if decryped_pad == pad:
            # Authenticated
            writer.write(f"OK;Authenticated{Server.EOM}".encode())
            command, file_name = m[8:].decode().split(";")

            if "UPLOAD" in command:
                # Request to upload file, structure: 'UPLOAD FILENAME USERNAME'
                await Server.recieve_file(file_name, user_name, reader, writer)
            elif "DOWNLOAD" in command:
                # Request to download file, structure: 'DOWNLOAD FILENAME USERNAME'
                await Server.serve_file(file_name, user_name, reader, writer)
            elif "REMOVE" in command:
                # Request to delete file, structure: 'REMOVE FILENAME USERNAME'
                await Server.remove_file(file_name, user_name, reader, writer)
            elif "LIST_DIR" in command:
                # Request to list available file for download, structure: 'LIST_DIR'
                await Server.list_files(user_name, reader, writer)
            else:
                writer.write(
                    f"UN-KNOWN request, use [UPLOAD, DOWNLOAD, LIST_DIR]{Server.EOM}".encode()
                )
                await writer.drain()
        else:
            # Not Authenticated
            writer.write(f"ERROR;NotAuthenticatedError{Server.EOM}".encode())

        writer.close()
        await writer.wait_closed()

    @staticmethod
    def init() -> None:
        """
        Runs initialization checks before starting Kryzbu server instace.

        | 1. Checks if required folder structure for server exists, if not creates new one.
        | 2. Initializes *hmac.db* database.
        | 3. Checks integrity of filesystem for every user, makes sure all files are either indexed or deleted.
        | 4. Initializes *users.db* database.
        | 5. Initializes RSA key-pair
        """

        PATHS = ("server/_data/files/", "server/_data/logs/", "server/_data/keys/")
        for path in PATHS:
            # Any missing parents of this path are created as needed, if folder already exists nothing happens
            Path(path).mkdir(parents=True, exist_ok=True)

        # Initiate user database
        Hmac_index.init()

        # Initiate file index
        for user in User_db.return_all():
            # Check filesystem integrity for every user
            File_index.init(Server.SERVER_FOLDER / user[0])

        # Initiate user database
        User_db.init()

        # Initialize RSA key-pair
        Rsa.init()

        print("[*] Kryzbu server started successfully...")

    @staticmethod
    async def recieve_file(
        file_name: str,
        user_name: str,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ):
        """
        Function receiving files from client, storing them on server filesystem and indexing.

        :param file_name: Name of uploaded file
        :type file_name: str
        :param user_name: Name of owner
        :type user_name: str
        :param reader: reader instance
        :type reader: asyncio.StreamReader
        :param writer: writer instance
        :type writer: asyncio.StreamWriter

        """

        file_path = Server.SERVER_FOLDER / user_name / file_name

        with open(file_path, "wb") as f:
            while True:
                bytes_read = await reader.read()
                if not bytes_read:
                    break
                f.write(bytes_read)

        Log.event(Log.Event.UPLOAD, 0, [file_name, user_name])
        File_index.add(file_name, user_name)

    @staticmethod
    async def serve_file(
        file_name: str,
        user_name: str,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ):
        """
        Function for sending files to client.

        :param file_name: Name of requested file
        :type file_name: str
        :param user_name: Name of user making request
        :type user_name: str
        :param reader: reader instance
        :type reader: asyncio.StreamReader
        :param writer: writer instance
        :type writer: asyncio.StreamWriter
        
        """

        file_path = Server.SERVER_FOLDER / user_name / file_name

        if os.path.exists(file_path):
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

    @staticmethod
    async def remove_file(
        file_name: str,
        user_name: str,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ):
        """
        Function for removing files from server filesystem.

        :param file_name: Name of requested file
        :type file_name: str
        :param user_name: Name of user making request
        :type user_name: str
        :param reader: reader instance
        :type reader: asyncio.StreamReader
        :param writer: writer instance
        :type writer: asyncio.StreamWriter
        
        """

        file_path = Server.SERVER_FOLDER / user_name / file_name

        if os.path.exists(file_path):
            # Delete file
            os.remove(file_path)
            writer.write(f"OK;FileDeleted;{file_name}{Server.EOM}".encode())

            Log.event(Log.Event.DELETE, 0, [file_name, user_name])
            File_index.delete(file_name)
        else:
            # Requested file does NOT exist
            writer.write(f"ERROR;FileNotFoundError{Server.EOM}".encode())

    @staticmethod
    async def list_files(
        user_name: str, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        """
        Function for sending list of available files to a user.

        :param user_name: Name of user making request
        :type user_name: str
        :param reader: reader instance
        :type reader: asyncio.StreamReader
        :param writer: writer instance
        :type writer: asyncio.StreamWriter
        
        """

        # Send file database data
        writer.write(pickle.dumps(File_index.user_files(user_name)))

    @staticmethod
    async def send_pubkey(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """
        Function for sending server's RSA public key to client on request.

        :param reader: reader instance
        :type reader: asyncio.StreamReader
        :param writer: writer instance
        :type writer: asyncio.StreamWriter
        
        """

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
        """
        This function handles users authentication on *LOGIN* request from client via custom defined handshake using symetric and asymetric cryptography.

        **Client–Server handshake:** (servers point of view)

        1. Server sends 'OK' ready to the client
        2. Awaits encryped response *c* from client

            .. math::
                c = E(pubkey_{server}, (username, nonce_{user}))

        3. Server decrypts cyphertext *c* creating plaintext message *m*. From this message server obtains users username and nonce.

            .. math::
                m = D(privkey_{server}, c)

        4. Server fetches from *user.db* users password in form of salted hash, using it as symetric key. (If user with this username wasn't registered authentization fails.)
        5. Server sends cyphertext *c* and *salt*, containing server and user nonce, encrypted with users hashed password.

            .. math::
                c = E(h(password_{username} || salt), (nonce_{user}, nonce_{server}))

        6. Awaits client response. Client by knowing plaintext *password* from user should be able to decrypt cyphertext *c* and obtain server nonce. Then encrypt it again with server's RSA public key and send it to server thus prove knowledge of the correct password.
        7. Server receives cypher text *c* and recovers plaintext *m*. If plaintext contains same server nonce as has been sent in step no. 5 client has been sucessfully authenticated, otherwise access is denied.

            .. math::
                m = D(privkey_{server}, c)

        8. To sucessfully authenticated clients AES symetric key is sent as *c*. This AES key is unique for every user and is stored in the *user.db* database. Acts as *Session ID* granting access to server functions limited to authenticated users. (*UPLOAD, DOWNLOAD, LIST_DIR...*)

            .. math::
                c = E(h(password_{username} || salt), aeskey_{username})

        More details on acessing of server functions limited to authenticated users in handle_connection section.

        :param reader: reader instance
        :type reader: asyncio.StreamReader
        :param writer: writer instance
        :type writer: asyncio.StreamWriter
        
        """

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
        username, usr_nonce = m.split(";")
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
        writer.write(
            f"{len(c)};{len(tag)};{len(aes_instance.nonce)};{len(byte_salt)}".encode()
            + Server.EOM.encode()
        )
        writer.writelines(payload)

        # Await response and D((usr-nonce, ser-nonce), pub.key)
        paylen = await reader.readuntil(Server.EOM.encode())
        paylen = paylen.decode()[:-1]
        c = await reader.read(int(paylen))

        # Decypher message (usr-nonce, ser-nonce)
        m = rsa_instance.decrypt(c)
        m = m.decode()

        # Compare original ser-nonce and received ser-nonce from client
        _, rec_ser_nonce = m.split(";")
        if rec_ser_nonce == str(ser_nonce):
            print(f"INFO: User {username} has successfully loged in from client.")
            aes_key = User_db.get_record(username)[2]

            # Encrypt aes_key with password
            aes_instance = AES.new(byte_pas, AES.MODE_EAX)
            c, tag = aes_instance.encrypt_and_digest(aes_key)

            payload = (c, tag, aes_instance.nonce)

            # Send aes_key to client
            writer.write(
                f"{len(c)};{len(tag)};{len(aes_instance.nonce)}".encode()
                + Server.EOM.encode()
            )
            writer.writelines(payload)

        else:
            print(f"WARNING: User {username} has failed to loged in from client.")

    @staticmethod
    def version():
        """Prints version information."""
        image = climage.convert("../graphics/console.png", width=80)
        print(image, end="")
        image = climage.convert("../graphics/console-text.png", width=80)
        print(image)
        print("{:█^80}".format(" SERVER INFORMATION: "))
        print("\nVersion: 0.9 pre-release")
        print("Contributors: martin-nohava, Bloc3k, Kaspis123, ikachuu")
        print("More on: https://github.com/martin-nohava/kryzbu")
        print("License: MIT\n")
        print("{:█^80}".format(" © 2022 – kryzbu "))
