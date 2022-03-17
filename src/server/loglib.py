# Loglib is library for event loging in kryzbu programmes
#
# Source code available on: https://github.com/martin-nohava/kryzbu.

from multiprocessing import Event
from pathlib import Path
import datetime
from enum import Enum


class Log:

    LOG_FOLDER = Path("server/_data/logs/")

    # Posible events
    class Event(Enum):
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
        """Writes event to log file"""

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
        file_path = Log.LOG_FOLDER / "kryzbu.log"

        with open(file_path, "a") as f:
            f.write(log)
