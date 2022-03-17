# Client side

import hashlib
import asyncio
import os
import re
from pathlib import Path
import uuid
import tqdm
import pickle
import getpass


class Client:
    """Implementation of a Kryzbu client."""

    SERVER_IP = "127.0.0.1"
    SERVER_PORT = 60606
    USER_CONF = Path("client/_data/config/user.conf")
    SERVER_PUBLIC_KEY = Path("client/_data/serkey/rsa.pub")
    EOM = "\n"  # End of Message sign

    @staticmethod
    async def upload(file_path: str):
        """Upload file to a server."""

        if os.path.exists(file_path):
            try:
                reader, writer = await asyncio.open_connection(
                    Client.SERVER_IP, Client.SERVER_PORT
                )
            except ConnectionRefusedError as e:
                print(e)
                print("Server probably ins't running!!!")
                exit(1)

            file_name = os.path.basename(file_path)

            # Send UPLOAD request
            writer.write(
                f"UPLOAD;{file_name};{Client.get_username()}{Client.EOM}".encode()
            )

            # Receive aswer
            data = await reader.readuntil(Client.EOM.encode())
            answer = data.decode()

            if "OK" in answer:
                # Answer: 'OK;Authenticated'
                file_size = os.path.getsize(file_path)
                progress = tqdm.tqdm(
                    range(file_size),
                    f"Sending {file_name}",
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                )

                # Send file
                with open(file_path, "rb") as f:
                    while True:
                        bytes_read = f.read(1024)
                        if not bytes_read:
                            break
                        progress.update(len(bytes_read))
                        writer.write(bytes_read)
                        await writer.drain()

            elif "NotAuthenticated" in answer:
                # Answer: 'ERROR;NotAuthenticated'
                print(
                    f"User '{Client.get_username()}' can't be authenticated, CANNOT upload"
                )
            else:
                # Answer: Any
                print("client.py: Unknown exeption")

            writer.close()
            await writer.wait_closed()

        else:
            # Client FileNotFoundError
            print(f"File '{file_path}' can't be reached, No action taken...")
            print(f"Check correct file name and path and try again ")

    @staticmethod
    async def download(file_name: str):
        """Download file from a server."""

        try:
            reader, writer = await asyncio.open_connection(
                Client.SERVER_IP, Client.SERVER_PORT
            )
        except ConnectionRefusedError as e:
            print(e)
            print("Server probably ins't running!!!")
            exit(1)

        # Send DOWNLOAD request
        writer.write(
            f"DOWNLOAD;{file_name};{Client.get_username()}{Client.EOM}".encode()
        )

        # Receive aswer: 'OK;Authenticated' or 'ERROR;FileNotFoundError' or 'ERROR;NotAuthenticatedError'
        data = await reader.readuntil(Client.EOM.encode())
        answer = data.decode()[:-1]  # Decode and strip EOM symbol

        if "OK" in answer:
            # Answer: 'OK;Authenticated'
            data = await reader.readuntil(Client.EOM.encode())
            file_info = data.decode()[:-1]  # Decode and strip EOM symbol
            file_name, file_size = file_info.split(";")

            progress = tqdm.tqdm(
                range(int(file_size)),
                f"Receiving {file_name}",
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            )

            # Receive file
            with open(
                str(os.path.join(Client.get_download_folder(), file_name)), "wb"
            ) as f:
                while True:
                    bytes_read = await reader.read(1024)
                    if not bytes_read:
                        break
                    f.write(bytes_read)
                    progress.update(len(bytes_read))

        elif "FileNotFoundError" in answer:
            # Answer: 'ERROR;FileNotFoundError'
            print(f"File '{file_name}' does NOT exist, CANNOT download")
            print("Check correct file name and try again")

        elif "NotAuthenticatedError" in answer:
            # Answer: 'ERROR;NotAuthenticatedError'
            print(
                f"User '{Client.get_username()}' can't be authenticated, CANNOT downdload"
            )

        else:
            # Answer: Any
            print("client.py: Unknown exeption")

        writer.close()
        await writer.wait_closed()

    @staticmethod
    async def remove(file_name: str):
        """Remove file from a server."""

        try:
            reader, writer = await asyncio.open_connection(
                Client.SERVER_IP, Client.SERVER_PORT
            )
        except ConnectionRefusedError as e:
            print(e)
            print("Server probably ins't running!!!")
            exit(1)

        # Send REMOVE request
        writer.write(f"REMOVE;{file_name};{Client.get_username()}{Client.EOM}".encode())

        # Receive answer: 'OK;Authenticated' or 'ERROR;FileNotFoundError' or 'ERROR;NotAuthenticatedError'
        data = await reader.readuntil(Client.EOM.encode())
        answer = data.decode()[:-1]  # Decode and strip EOM symbol

        if "OK" in answer:
            # Answer: 'OK;Authenticated'
            data = await reader.readuntil(Client.EOM.encode())
            delete_info = data.decode()[:-1]  # Decode and strip EOM symbol

            if "FileDeleted" in delete_info:
                # delete_info: 'OK;FileDeleted'
                print(f"File '{file_name}' successfully removed")

        elif "FileNotFoundError" in answer:
            # Answer: 'ERROR;FileNotFoundError'
            print(f"File '{file_name}' does NOT exist, CANNOT remove")
            print("Check correct file name and try again")

        elif "NotAuthenticatedError" in answer:
            # Answer: 'ERROR;NotAuthenticatedError'
            print(
                f"User '{Client.get_username()}' can't be authenticated, CANNOT remove"
            )

        else:
            # Answer: Any
            print("client.py: Unknown exeption")

        writer.close()
        await writer.wait_closed()

    @staticmethod
    async def list_files(detailed: bool):
        """List stored files on server. True: detailed view, False: basic view"""

        try:
            reader, writer = await asyncio.open_connection(
                Client.SERVER_IP, Client.SERVER_PORT
            )
        except ConnectionRefusedError as e:
            print(e)
            print("Server probably ins't running!!!")
            exit(1)

        # Send LIST_DIR request
        writer.write(f"LIST_DIR;{Client.get_username()}{Client.EOM}".encode())

        # Receive answer: 'OK;Authenticated' or 'ERROR;NotAuthenticatedError'
        data = await reader.readuntil(Client.EOM.encode())
        answer = data.decode()[:-1]  # Decode and strip EOM symbol

        if "OK" in answer:
            # Answer: 'OK;Authenticated'
            list = pickle.loads(await reader.read())
            if detailed:
                # Detailed list
                print(
                    "{:<15} {:<12} {:<12} {:<15}".format(
                        "Owner", "Created", "Downloads", "File"
                    )
                )
                print("{:–<60}".format("–"))
                if len(list) != 0:
                    for row in list:
                        print(
                            "{:<15} {:<15} {:<9} {:<15}".format(
                                row[1], row[2], str(row[3]), row[0]
                            )
                        )
                else:
                    print("{:^65}".format("Nothing here"))
            else:
                # Short list
                if len(list) != 0:
                    for row in list:
                        print(row[0], end="\t")
                else:
                    print("Nothing here")

        elif "NotAuthenticatedError" in answer:
            # Answer: 'ERROR;NotAuthenticatedError'
            print(
                f"User '{Client.get_username()}' can't be authenticated, CANNOT list files"
            )

        else:
            # Answer: Any
            print("client.py: Unknown exeption")

        writer.close()
        await writer.wait_closed()

    @staticmethod
    def init() -> None:
        PATHS = ("client/_data/config/", "client/_data/serkey/")
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
            print("INFO: No server key found, requesting new...")
            try:
                reader, writer = await asyncio.open_connection(
                    Client.SERVER_IP, Client.SERVER_PORT
                )
            except ConnectionRefusedError as e:
                print(e)
                print("Server probably ins't running!!!")
                exit(1)

            # Send GETKEY request
            writer.write(f"GETKEY{Client.EOM}".encode())

            # Receive aswer: 'OK;Authenticated' or 'ERROR;FileNotFoundError' or 'ERROR;NotAuthenticatedError'
            data = await reader.readuntil(Client.EOM.encode())
            answer = data.decode()[:-1]  # Decode and strip EOM symbol

            if "OK" in answer:
                # Answer: 'OK;Authenticated'
                # Receive file
                with open(str(Client.SERVER_PUBLIC_KEY), "wb") as f:
                    while True:
                        bytes_read = await reader.read(1024)
                        if not bytes_read:
                            break
                        f.write(bytes_read)
                print("INFO: Key downloaded sucessfully.")

            else:
                # Answer: Any
                print("client.py: Unknown exeption while obtaining server public key")

            writer.close()
            await writer.wait_closed()

    @staticmethod
    def user_exists():
        required = ("USERNAME=.+", "PASSWORD=.+", "SALT=.+")
        # Check if config file exists
        if os.path.exists(Client.USER_CONF):
            # Check required user data are filled in
            with open(Client.USER_CONF, "r") as f:
                lines = f.read()
                for ex in required:
                    if not re.search(ex, lines):
                        Client.login()
                        return
        # Else create file and ask for data
        else:
            Client.login()

    @staticmethod
    def login():
        print("INFO: No user account found! Please login first.")
        for i in range(3):
            print("Username:", end=" ")
            username = str(input())
            password = getpass.getpass()
            passwordCheck = getpass.getpass()
            if password == passwordCheck:
                salt = uuid.uuid4().hex
                with open(Client.USER_CONF, "w") as f:
                    f.write(
                        f"USERNAME={username}\n"
                        f"PASSWORD={str(hashlib.sha256(salt.encode() + password.encode()).hexdigest())}\n"
                        f"SALT={salt}\n"
                        f"DOWNLOAD_FOLDER={Path(os.path.expanduser('~/Downloads'))}"
                    )
                print("INFO: You are now logged in as " + username)
                return
            else:
                print("Passwords does not match! ")
                print("Try again!")
        print("You failed 3 times, get the fuck out")

    @staticmethod
    def get_download_folder() -> str:
        """Get location of download folder from User config file."""

        with open(Client.USER_CONF, "r") as f:
            for line in f.readlines():
                download_folder = re.search("(?<=DOWNLOAD_FOLDER=).+", line)
                if download_folder:
                    return Path(download_folder.group())
            # No line with DOWNLOAD_FOLDER=/path/to/file in user configuration file
            raise Exception(
                f"Did NOT find DOWLOAD_FOLDER configuration in user configuration, config file: {Client.USER_CONF}"
            )

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
            with open(Client.USER_CONF, "r") as f:
                config = f.readlines()

            # Chanche only DOWNLOAD_FOLDER line
            with open(Client.USER_CONF, "w") as f:
                for line in config:
                    if "DOWNLOAD_FOLDER" in line:
                        f.write(f"DOWNLOAD_FOLDER={folder_path}\n")
                    else:
                        f.write(line)
            print(f"INFO: Download folder successfully changed to {folder_path}")
        else:
            print(
                f"WARING, Client.set_download_folder(): File path NOT exists, no action taken, path: {folder_path}"
            )

    @staticmethod
    def info():
        print("User account and client preferences information:\n")
        # Check if user exists, create user
        Client.user_exists()
        # Display available info
        f = open(Client.USER_CONF, "r")
        lines = f.readlines()
        for line in lines:
            items = line.split("=")
            print(items[0] + ": " + items[1], end="")

    @staticmethod
    def get_username() -> str:
        ex = "USERNAME=.+"
        f = open(Client.USER_CONF, "r")
        lines = f.readlines()
        for line in lines:
            result = re.match(ex, line)
            if result:
                break
        return result.group().split("=")[1]

    @staticmethod
    def change_user():
        # os.remove(Client.USER_CONF)
        Client.login()

    @staticmethod
    def flush_key():
        try:
            os.remove(Client.SERVER_PUBLIC_KEY)
        except FileNotFoundError as e:
            print("WARN: Key allready flushed!")
