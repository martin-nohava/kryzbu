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
        # [1] – username, e.g. john_doe (NOT REQUIRED IN THIS VERSION)
        if type == Log.Event.UPLOAD:
            suc = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S") + " UPLOAD User john_doe uploaded file " + payload[0] + ".\n"
            err = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S") + " UPLOAD ERROR User john_doe failed to upload file " + payload[0] + " with error " + str(status) + ".\n"
            # SUCESS
            if status == 0: Log.write(suc)
            # ERROR
            else: Log.write(err)
                
        # DOWNLOAD: file was downloaded from the server
        # *********** payload ***********
        # [0] – filename, e.g. testfile.txt
        # [1] – username, e.g. john_doe (NOT REQUIRED IN THIS VERSION)
        elif type == Log.Event.DOWNLOAD:
            suc = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S") + " DOWNLOAD User john_doe downloaded file " + payload[0] + ".\n"
            err = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S") + " DOWNLOAD ERROR User john_doe failed to download file " + payload[0] + " with error " + str(status) + ".\n"
            # SUCESS
            if status == 0: Log.write(suc)
            # ERROR
            else: Log.write(err)

        # DELETE: file was deleted from the server
        # *********** payload ***********
        # [0] – filename, e.g. testfile.txt
        # [1] – username, e.g. john_doe (NOT REQUIRED IN THIS VERSION)
        elif type == Log.Event.DELETE:
            suc = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S") + " DELETE User john_doe deleted file " + payload[0] + ".\n"
            err = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S") + " DELETE ERROR User john_doe failed to delete file " + payload[0] + " with error " + str(status) + ".\n"
            # SUCESS
            if status == 0: Log.write(suc)
            # ERROR
            else: Log.write(err)

    @staticmethod
    # Function for appending lines to logfile
    def write(log: str) -> None:
        file_path = Log.LOG_FOLDER / "kryzbu.log"

        with open(file_path, "a") as f:
                f.write(log)
