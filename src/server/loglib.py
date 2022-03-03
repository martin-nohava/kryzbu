# Loglib is library for event loging in kryzbu programmes
#
# Source code available on: https://github.com/martin-nohava/kryzbu.

from pathlib import Path
import datetime

class Log:

    LOG_FOLDER = Path("server/_data/logs/")

    @staticmethod
    # Function params definition:
    # type – type of log message, e.g. UPLOAD, DOWNLOAD, etc.
    # status – status, if success 0, else pass error message e here
    # payload – list of required information to log
    def event(type: str, status, payload: list) -> None:
        """Writes event to log file"""
        
        # Switch for finding correct event type,
        # every event requires different data input

        # UPLOAD: file was uploaded to the server
        # *********** payload ***********
        # [0] – filename, e.g. testfile.txt
        # [1] – username, e.g. john_doe (NOT REQUIRED IN THIS VERSION)
        if type == "UPLOAD":
            suc = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S") + " " + type + " User john_doe uploaded file " + payload[0] + ".\n"
            err = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S") + " " + type + " ERROR User john_doe failed to upload file " + payload[0] + " with error " + str(status) + ".\n"
            # SUCESS
            if status == 0: Log.write(suc)
            # ERROR
            else: Log.write(err)
                
        # DOWNLOAD: file was downloaded from the server
        # *********** payload ***********
        # [0] – filename, e.g. testfile.txt
        # [1] – username, e.g. john_doe (NOT REQUIRED IN THIS VERSION)
        elif type == "DOWNLOAD":
            suc = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S") + " " + type + " User john_doe downloaded file " + payload[0] + ".\n"
            err = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S") + " " + type + " ERROR User john_doe failed to download file " + payload[0] + " with error " + str(status) + ".\n"
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
