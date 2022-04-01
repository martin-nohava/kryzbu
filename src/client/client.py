# Client side

import hashlib
import asyncio
import os
import re
from pathlib import Path
import ssl
from typing import Tuple
import uuid
import tqdm
import pickle
import getpass
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import PKCS1_OAEP, AES
import climage

class Client:
    """Implementation of a Kryzbu client."""

    SERVER_IP = "127.0.0.1"
    SERVER_PORT = 60606
    USER_CONF = Path('client/_data/config/user.conf')
    SERVER_PUBLIC_KEY = Path('client/_data/keys/publ.pem')
    USER_AES_KEY_BASE_PATH = Path('client/_data/keys')
    EOM = '\n' # End of Message sign

    @staticmethod
    async def open_connection() -> Tuple:
        """Open connection to the server. 
        
        Returns 'reader' and 'writer' objects."""

        try:
            ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile='server.cert')
            ssl_context.check_hostname = False      # No common name in creation -> need False
            reader, writer = await asyncio.open_connection(Client.SERVER_IP, Client.SERVER_PORT, ssl=ssl_context)
            return reader, writer
        except ConnectionRefusedError as e:
            print(e)
            print("ERROR: Failed to contact server!")
            exit(1)

    @staticmethod
    def load_aes_key() -> bytes:
        file_path = Client.USER_AES_KEY_BASE_PATH.joinpath('aes_' + Client.get_username() + '.key')
        with open(file_path, "rb") as f:  
            aes_key = f.read()
            return aes_key

    @staticmethod
    def send_request(type: str, writer: asyncio.StreamWriter, file_name: str ='empty') -> None:
        # Prepare request
        pad = get_random_bytes(8)
        m = pad + f"{type};{file_name}".encode()
        aes_key = Client.load_aes_key()
        aes_instance = AES.new(aes_key, AES.MODE_EAX)
        c, tag = aes_instance.encrypt_and_digest(m)

        payload = (c, tag, pad, aes_instance.nonce)

        # Send request
        writer.write(f"{Client.get_username()};{len(c)};{len(tag)};{len(pad)};{len(aes_instance.nonce)}".encode() + Client.EOM.encode())
        writer.writelines(payload)

    @staticmethod
    async def upload(file_path: str):
        """Upload file to the server."""

        if os.path.exists(file_path):
            
            reader, writer = await Client.open_connection()
 
            file_name = os.path.basename(file_path)

            # Send UPLOAD request
            Client.send_request("UPLOAD", writer, file_name)

            # Receive aswer
            data = await reader.readuntil(Client.EOM.encode())
            answer = data.decode()

            if 'OK' in answer:
                # Answer: 'OK;Authenticated'

                # Prepare loading bar
                file_size = os.path.getsize(file_path)
                progress = tqdm.tqdm(range(file_size), f"Sending {file_name}", unit="B", unit_scale=True, unit_divisor=1024)

                # Send file
                with open(file_path, "rb") as f:
                    while True:
                        bytes_read = f.read(1024)
                        if not bytes_read:
                            break
                        progress.update(len(bytes_read))
                        writer.write(bytes_read)
                        await writer.drain()

            elif 'NotAuthenticated' in answer:
                # Answer: 'ERROR;NotAuthenticated'
                print(f"User '{Client.get_username()}' can't be authenticated, CANNOT upload")
            else:
                # Answer: Any
                print("client.py: Unknown exeption")
            
            writer.close()
            await writer.wait_closed()

        else:
            # Client FileNotFoundError
            print(f"ERROR: File '{file_path}' can't be reached! No action taken.")
            print(f"Check correct file name and path and try again.")


    @staticmethod
    async def download(file_name: str):
        """Download file from a server."""

        reader, writer = await Client.open_connection()

        # Send DOWNLOAD request
        Client.send_request("DOWNLOAD", writer, file_name)

        # Receive aswer: 'OK;Authenticated' or 'ERROR;FileNotFoundError' or 'ERROR;NotAuthenticatedError'
        data = await reader.readuntil(Client.EOM.encode())
        answer = data.decode()[:-1] # Decode and strip EOM symbol

        if 'OK' in answer:
            # Answer: 'OK;Authenticated'
            data = await reader.readuntil(Client.EOM.encode())
            file_info = data.decode()[:-1] # Decode and strip EOM symbol
            file_name, file_size = file_info.split(';')

            if 'FileNotFoundError' in file_info:
                # Answer: 'ERROR;FileNotFoundError'
                print(f"Requested file does NOT exist, CANNOT download")
                print("Check if file name is correct and try again")
            
            else:
                progress = tqdm.tqdm(range(int(file_size)), f"Receiving {file_name}", unit="B", unit_scale=True, unit_divisor=1024)

                # Receive file
                with open(str(os.path.join(Client.get_download_folder(), file_name)), "wb") as f:
                    while True:
                        bytes_read = await reader.read(1024)
                        if not bytes_read:
                            break
                        f.write(bytes_read)
                        progress.update(len(bytes_read))

        elif 'NotAuthenticatedError' in answer:
            # Answer: 'ERROR;NotAuthenticatedError'
            print(f"User '{Client.get_username()}' can't be authenticated, CANNOT downdload")

        else:
            # Answer: Any
            print("client.py: Unknown exeption")      

        writer.close()
        await writer.wait_closed()


    @staticmethod
    async def remove(file_name: str):
        """Remove file from a server."""

        reader, writer = await Client.open_connection()

        # Send request to server
        Client.send_request("REMOVE", writer, file_name)

        # Receive answer: 'OK;Authenticated' or 'ERROR;FileNotFoundError' or 'ERROR;NotAuthenticatedError'
        data = await reader.readuntil(Client.EOM.encode())
        answer = data.decode()[:-1]   # Decode and strip EOM symbol

        if 'OK' in answer:
            # Answer: 'OK;Authenticated'
            data = await reader.readuntil(Client.EOM.encode())
            delete_info = data.decode()[:-1]   # Decode and strip EOM symbol

            if 'FileDeleted' in delete_info:
                # delete_info: 'OK;FileDeleted'
                print(f"File '{file_name}' successfully removed")

            if 'FileNotFoundError' in delete_info:
                # Answer: 'ERROR;FileNotFoundError'
                print(f"File '{file_name}' does NOT exist, CANNOT remove")
                print("Check correct file name and try again")

        elif 'NotAuthenticatedError' in answer:
            # Answer: 'ERROR;NotAuthenticatedError'
            print(f"User '{Client.get_username()}' can't be authenticated, CANNOT remove")

        else:
            # Answer: Any
            print("client.py: Unknown exeption")

        writer.close()
        await writer.wait_closed()


    @staticmethod
    async def list_files(detailed: bool):
        """List stored files on server. True: detailed view, False: basic view"""

        # Open connection with server
        reader, writer = await Client.open_connection()

        # Send request to server
        Client.send_request("LIST_DIR", writer)

        # Receive answer: 'OK;Authenticated' or 'ERROR;NotAuthenticatedError'
        data = await reader.readuntil(Client.EOM.encode())
        answer = data.decode()[:-1]   # Decode and strip EOM symbol

        if 'OK' in answer:
            # Answer: 'OK;Authenticated'
            list = pickle.loads(await reader.read())
                
            if detailed:
                # Detailed list
                print ("{:<15} {:<12} {:<12} {:<15}".format('Owner','Created','Downloads', 'File'))
                print ("{:–<60}".format('–'))
                if len(list) != 0:
                    for row in list:
                        print ("{:<15} {:<15} {:<9} {:<15}".format(row[1], row[2], str(row[3]), row[0]))
                else:
                    print ("{:^65}".format('Nothing here'))
            else:
                # Short list
                if len(list) != 0:
                    for row in list:
                        print(row[0], end='\t')
                else:
                    print ('Nothing here')

        elif 'NotAuthenticatedError' in answer:
            # Answer: 'ERROR;NotAuthenticatedError'
            print(f"User '{Client.get_username()}' can't be authenticated, CANNOT list files")
            
        else:
            # Answer: Any
            print("client.py: Unknown exeption")
            
        writer.close()
        await writer.wait_closed()
            

    @staticmethod
    def init() -> None:
        PATHS = (
        'client/_data/config/',
        'client/_data/keys/'
        )
        for path in PATHS:
            # Any missing parents of this path are created as needed, if folder already exists nothing happens
            Path(path).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def online_operation(online) -> None:
        """Checks user information and folder structure. Obtains server public key."""

        if online:
            # Get server's public key rsa.pub
            asyncio.run(Client.get_server_publickey())

            # Before any action can be taken user has to be loged in
            Client.user_exists()

    @staticmethod
    async def get_server_publickey():
        if not os.path.exists(Client.SERVER_PUBLIC_KEY):
            print('INFO: No server key found, requesting new...')

            reader, writer = await Client.open_connection()

            # Send GETKEY request
            writer.write(f"GETKEY{Client.EOM}".encode())

            # Receive aswer: 'OK;Authenticated' or 'ERROR;FileNotFoundError' or 'ERROR;NotAuthenticatedError'
            data = await reader.readuntil(Client.EOM.encode())
            answer = data.decode()[:-1] # Decode and strip EOM symbol

            if 'OK' in answer:
                # Answer: 'OK;Authenticated'
                # Receive file
                with open(str(Client.SERVER_PUBLIC_KEY), "wb") as f:
                    while True:
                        bytes_read = await reader.read(1024)
                        if not bytes_read:
                            break
                        f.write(bytes_read)
                print('INFO: Key downloaded sucessfully.')

            else:
                # Answer: Any
                print("client.py: Unknown exeption while obtaining server public key")      

            writer.close()
            await writer.wait_closed()

    @staticmethod
    def user_exists():
        required = ('USERNAME=.+', 'KEY_PATH=.+')
        # Check if config file exists
        if os.path.exists(Client.USER_CONF):
            # Check required user data are filled in
            with open(Client.USER_CONF, 'r') as f:
                lines = f.read()
                for ex in required:
                    if not re.search(ex, lines):
                        asyncio.run(Client.login())
                        return
            # Check if key file exists
            ex = 'KEY_PATH=.+'
            f = open(Client.USER_CONF, 'r')
            lines = f.readlines()
            for line in lines:
                result = re.match(ex, line)
                if result:
                    key_path = result.group().split('=')[1]
                    if not os.path.exists(key_path):
                        asyncio.run(Client.login())
        # Else create file and ask for data
        else:
            asyncio.run(Client.login())


    @staticmethod
    async def login():
        print('INFO: No user account found! Please login first.')
        
        print('Username:', end=' ')
        username = str(input())
        password = getpass.getpass()
        usr_nonce = uuid.uuid4().hex
        
        # Open connection
        reader, writer = await Client.open_connection()

        # Get public key from file
        pub_key = RSA.import_key(open(Client.SERVER_PUBLIC_KEY).read())

        # Create new RSA instance using pub_key
        rsa_instance = PKCS1_OAEP.new(pub_key)

        # Encrypt message E(username, usr-nonce) with pub.key
        m = f"{username};{usr_nonce}".encode()
        c = rsa_instance.encrypt(m)
        
        # Request start of login session
        writer.write(f"LOGIN{Client.EOM}".encode())

        # Receive answer: 'OK;Ready'
        data = await reader.readuntil(Client.EOM.encode())
        answer = data.decode()[:-1]

        # If server is ready send E(username, usr-nonce)
        if 'OK' in answer:
            writer.write(str(len(c)).encode() + Client.EOM.encode())
            writer.write(c)
        
        # Await E((usr-nonce, ser-nonce), hash(password)), salt
        paylen = await reader.readuntil(Client.EOM.encode())
        paylen = paylen.decode()[:-1]

        c_len, tag_len, nonce_len, byte_salt_len = paylen.split(';')
        c = await reader.read(int(c_len))
        tag = await reader.read(int(tag_len))
        nonce = await reader.read(int(nonce_len))
        byte_salt = await reader.read(int(byte_salt_len))

        # Decrypt D((usr-nonce, ser-nonce), hash(password)), salt
        pass_hash = str(hashlib.sha256(byte_salt.hex().encode() + password.encode()).hexdigest())
        byte_pass = bytes.fromhex(pass_hash)

        aes_instance = AES.new(byte_pass, AES.MODE_EAX, nonce)
        m = aes_instance.decrypt_and_verify(c, tag)

        # Send E((usr-nonce, ser-nonce), pub.key)
        c = rsa_instance.encrypt(m)
        writer.write(str(len(c)).encode() + Client.EOM.encode())
        writer.write(c)

        # Await response with symetric key
        paylen = await reader.readuntil(Client.EOM.encode())
        paylen = paylen.decode()[:-1]

        c_len, tag_len, nonce_len = paylen.split(';')
        c = await reader.read(int(c_len))
        tag = await reader.read(int(tag_len))
        nonce = await reader.read(int(nonce_len))
        
        # Decrypt incoming aes_key
        aes_instance = AES.new(byte_pass, AES.MODE_EAX, nonce)
        aes_key = aes_instance.decrypt_and_verify(c, tag)

        print('INFO: Received key ' + str(aes_key.hex()))

        # Save aes_key to file
        key_path = Client.USER_AES_KEY_BASE_PATH.joinpath('aes_' + username + '.key')
        with open(key_path, "wb") as f:
            f.write(aes_key)

        # Update user settings with username, location of aes_key and default downloads folder
        with open(Client.USER_CONF, "w") as f:
            f.write(f"USERNAME={username}\n"\
                    f"KEY_PATH={key_path}\n"\
                    f"DOWNLOAD_FOLDER={Path(os.path.expanduser('~/Downloads'))}")

        writer.close()
        await writer.wait_closed()

        print('INFO: You are now logged in as ' + username)
        return


    @staticmethod
    def get_download_folder() -> str:
        """Get location of download folder from User config file."""
        
        with open(Client.USER_CONF, 'r') as f:
            for line in f.readlines():
                download_folder = re.search('(?<=DOWNLOAD_FOLDER=).+', line)
                if download_folder:
                    return Path(download_folder.group())
            # No line with DOWNLOAD_FOLDER=/path/to/file in user configuration file
            raise Exception(f"Did NOT find DOWLOAD_FOLDER configuration in user configuration, config file: {Client.USER_CONF}")


    @staticmethod
    def set_download_folder(folder_path: str):
        """Set folder location for files to be downloaded from server."""

        # In order to re-write config file, we firt read all config file
        # and save it. Than we write same content back line by line except
        # line with DOWNLOAD_FOLER specification. Only that line we change
        # to store new downdload foler location.

        config: str = None

        # Transfer to default path format
        folder_path = Path(folder_path)

        if os.path.exists(folder_path):
            # Read and save content of config file
            with open(Client.USER_CONF, 'r') as f:
                config = f.readlines()
            
            # Chanche only DOWNLOAD_FOLDER line
            with open(Client.USER_CONF, 'w') as f:
                for line in config:
                    if 'DOWNLOAD_FOLDER' in line:
                        f.write(f"DOWNLOAD_FOLDER={folder_path}\n")
                    else:
                        f.write(line)
            print(f"INFO: Download folder successfully changed to {folder_path}")
        else:
            print(f"WARING, Client.set_download_folder(): File path NOT exists, no action taken, path: {folder_path}")

    
    @staticmethod
    def info():
        print('User account and client preferences information:\n')
        # Check if user exists, create user
        Client.user_exists()
        # Display available info
        f = open(Client.USER_CONF, 'r')
        lines = f.readlines()
        for line in lines:
            items = line.split('=')
            print(items[0] + ': ' + items[1], end='')
    

    @staticmethod
    def get_username() -> str:
        ex = 'USERNAME=.+'
        f = open(Client.USER_CONF, 'r')
        lines = f.readlines()
        for line in lines:
            result = re.match(ex, line)
            if result:
                break
        return result.group().split('=')[1]


    @staticmethod
    def change_user():
        # os.remove(Client.USER_CONF)
        asyncio.run(Client.login())

    @staticmethod
    def flush_key():
        try:
            os.remove(Client.SERVER_PUBLIC_KEY)
        except FileNotFoundError as e:
            print('WARN: Key allready flushed!')
    
    @staticmethod
    def info():
        image = climage.convert("../graphics/console.png", width=80)
        print(image, end="")
        image = climage.convert("../graphics/console-text.png", width=80)
        print(image)
        print ("{:█^80}".format(' CLIENT INFORMATION: '))
        print("\nVersion: 0.9 pre-release")
        print("Contributors: martin-nohava, Bloc3k, Kaspis123, ikachuu")
        print("More on: https://github.com/martin-nohava/kryzbu")
        print("License: MIT\n")
        print ("{:█^80}".format(' © 2022 – kryzbu '))
