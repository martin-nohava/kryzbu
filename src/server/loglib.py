# Loglib is library for event loging in kryzbu programmes
#
# Source code available on: https://github.com/martin-nohava/kryzbu.

from pathlib import Path
import datetime
from enum import Enum
from .rsalib import Rsa
from . import db
from Crypto.Hash import HMAC, SHA256


class Log:
    """The Log class provides system log management and log file integrity."""

    LOG_FOLDER = Path("server/_data/logs/")

    # Posible events
    class Event(Enum):
        """Class containing all defined events that can be logged."""
        UPLOAD = 1
        DOWNLOAD = 2
        DELETE = 3
        REGISTER = 4
        UNREGISTER = 5
        ACCESS_DENIED = 6

    @staticmethod
    # Function params definition:
    # type – type of log message, e.g. UPLOAD, DOWNLOAD, etc.
    # status – status, if success 0, else pass error message e here
    # payload – list of required information to log
    def event(type: Event, status, payload: list) -> None:
        """
        Writes any event passed in the parameters to a log file.

        :param type: an Enum from class Event defining type of event beeing logged
        :type type: Event
        :param status: if success 0, else pass an error message here
        :type status: any
        :param payload: list of required information to log, is different for every Event type.
        :type payload: list[str]

        .. attention::
           Each event requires different input data in the payload variable to be written to a file. This structure must be observed when passing data to the *write* function. **See below.**

        | **Every event requires different data input:**
        |
        | *UPLOAD*: file was uploaded to the server
        | **payload** [0] – filename, e.g. testfile.txt
        | **payload** [1] – username, e.g. john_doe, everyone

        | *DOWNLOAD*: file was downloaded from the server
        | **payload** [0] – filename, e.g. testfile.txt
        | **payload** [1] – username, e.g. john_doe, everyone

        | *DELETE*: file was deleted from the server
        | **payload** [0] – filename, e.g. testfile.txt
        | **payload** [1] – username, e.g. john_doe, everyone

        | *REGISTER*: user registered
        | **payload** [0] – username, e.g. john_doe, everyone

        | *UNREGISTER*: user un-registered (deleted)
        | **payload** [0] – username, e.g. john_doe, everyone

        | *ACCESS_DENIED*: Access to resources denied, Unauthorized user
        | **payload** [0] – resource
        | **payload** [1] - username requested for access
        | **payload** [2] - src socket
        """

        # Switch for finding correct event type,
        # every event requires different data input

        # UPLOAD: file was uploaded to the server
        # *********** payload ***********
        # [0] – filename, e.g. testfile.txt
        # [1] – username, e.g. john_doe, everyone
        if type == Log.Event.UPLOAD:
            suc = (
                datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                + " UPLOAD User "
                + payload[1]
                + " uploaded file "
                + payload[0]
                + ".\n"
            )
            err = (
                datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                + " UPLOAD ERROR "
                + payload[1]
                + " failed to upload file "
                + payload[0]
                + " with error "
                + str(status)
                + ".\n"
            )
            # SUCESS
            if status == 0:
                Log.write(suc)
            # ERROR
            else:
                Log.write(err)

        # DOWNLOAD: file was downloaded from the server
        # *********** payload ***********
        # [0] – filename, e.g. testfile.txt
        # [1] – username, e.g. john_doe, everyone
        elif type == Log.Event.DOWNLOAD:
            suc = (
                datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                + " DOWNLOAD User "
                + payload[1]
                + " downloaded file "
                + payload[0]
                + ".\n"
            )
            err = (
                datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                + " DOWNLOAD ERROR User "
                + payload[1]
                + " failed to download file "
                + payload[0]
                + " with error "
                + str(status)
                + ".\n"
            )
            # SUCESS
            if status == 0:
                Log.write(suc)
            # ERROR
            else:
                Log.write(err)

        # DELETE: file was deleted from the server
        # *********** payload ***********
        # [0] – filename, e.g. testfile.txt
        # [1] – username, e.g. john_doe, everyone
        elif type == Log.Event.DELETE:
            suc = (
                datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                + " DELETE User "
                + payload[1]
                + " deleted file "
                + payload[0]
                + ".\n"
            )
            err = (
                datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                + " DELETE ERROR User "
                + payload[1]
                + " failed to delete file "
                + payload[0]
                + " with error "
                + str(status)
                + ".\n"
            )
            # SUCESS
            if status == 0:
                Log.write(suc)
            # ERROR
            else:
                Log.write(err)

        # REGISTER: user registered
        # *********** payload ***********
        # [0] – username, e.g. john_doe, everyone
        elif type == Log.Event.REGISTER:
            suc = (
                datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                + " REGISTER User "
                + payload[0]
                + " was registered.\n"
            )
            err = (
                datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                + " REGISTER ERROR User "
                + payload[0]
                + " registration failed with error "
                + str(status)
                + ".\n"
            )
            # SUCESS
            if status == 0:
                Log.write(suc)
            # ERROR
            else:
                Log.write(err)

        # UNREGISTER: user un-registered (deleted)
        # *********** payload ***********
        # [0] – username, e.g. john_doe, everyone
        elif type == Log.Event.UNREGISTER:
            suc = (
                datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                + " UNREGISTER User "
                + payload[0]
                + " was unregistered.\n"
            )
            err = (
                datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                + " UNREGISTER ERROR User "
                + payload[0]
                + " unregistration failed with error "
                + str(status)
                + ".\n"
            )
            # SUCESS
            if status == 0:
                Log.write(suc)
            # ERROR
            else:
                Log.write(err)

        # ACCESS_DENIED: Access to resources denied, Unauthorized user
        # *********** payload ***********
        # [0] – resource
        # [1] - username requested for access
        # [2] - src socket
        elif type == Log.Event.ACCESS_DENIED:
            suc = (
                datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                + " ACCESS_DENIED Access to "
                + payload[0]
                + " denied for user: "
                + payload[1]
                + ".\n"
            )
            err = (
                datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                + " ACCESS_DENIED ERROR Access to "
                + payload[0]
                + " denied for user: "
                + payload[1]
                + " with error "
                + str(status)
                + ".\n"
            )
            # SUCESS
            if status == 0:
                Log.write(suc)
            # ERROR
            else:
                Log.write(err)

    @staticmethod
    # Function for appending lines to logfile
    def write(log: str) -> None:
        """
        Function for appending lines to a logfile. After each call new HMAC of updated log file is created and stored in Hmac_index database. Private server RSA key and SHA256 is used.

        :param log: Line of structured text to write to a file 
        :type log: str

        """
        FILE_NAME = "kryzbu.log"
        file_path = Log.LOG_FOLDER / FILE_NAME

        # Write new data to file
        with open(file_path, "a") as f:
            f.write(log)

        # Create new HMAC instance
        private_key = open(Rsa.get_priv_key_location()).read().encode()
        hmac_instance = HMAC.new(private_key, digestmod=SHA256)
        # Process entire file in chunks
        with open(file_path, "rb") as f:
            while True:
                bytes_read = f.read(1024)
                if not bytes_read:
                    break
                hmac_instance.update(bytes_read)
            # Write new log HMAC to Hmac_index database
            db.Hmac_index.add(FILE_NAME, hmac_instance.hexdigest())

    @staticmethod
    def verify(file_name: str) -> None:
        """
        Function for verifying log file integrity. Private server RSA key and SHA256 is used. Prints result to the console.

        :param file_name: Name of log file
        :type file_name: str

        """
        file_path = Log.LOG_FOLDER / file_name

        # Create new HMAC instance
        private_key = open(Rsa.get_priv_key_location()).read().encode()
        hmac_instance = HMAC.new(private_key, digestmod=SHA256)

        # Process entire file in chunks
        with open(file_path, "rb") as f:
            while True:
                bytes_read = f.read(1024)
                if not bytes_read:
                    break
                hmac_instance.update(bytes_read)

            # Check file integrity
            try:
                mac = db.Hmac_index.get_record(file_name)[1]
                hmac_instance.hexverify(mac)
                print(f"SUCCESS: The log file '{file_name}' integrity check succeded.")
            except ValueError:
                print(f"ERROR: The log file '{file_name}' integrity check failed!")
