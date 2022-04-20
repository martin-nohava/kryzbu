import hashlib
from pathlib import Path
from typing import Tuple
from unicodedata import name
import uuid
from . import loglib
from enum import Enum
import datetime
import sqlite3
import os
from Crypto.Random import get_random_bytes


class User_db:
    """Database of users registered in Kryzbu server. For every user database holds his Username,
    salted SHA-256 hash of his password, AES-128 secret and salt. This database is used throughout
    whole server-side code."""

    FOLDER = Path("server/_data")
    TABLE_NAME = "users"
    NAME = "users.db"

    @staticmethod
    def init():
        """Initialize user database while server is starting."""

        if not User_db.table_exists():
            con = sqlite3.connect(User_db.FOLDER / User_db.NAME)
            cur = con.cursor()
            cur.execute(
                f"CREATE TABLE {User_db.TABLE_NAME} (name text, pass_hash text, aes_key text, salt text)"
            )
            print("WARNING, User_db: No table found, empty one created")
            con.commit()
            con.close()

    @staticmethod
    def add(user_name: str, password: str):
        """
        Add new user to user database with specified user name and password. Will create salted
        hash of specified password and generate AES-128 key for this user. And new :py:class:`REGISTER <server.loglib.Log.Event.REGISTER>` event
        is logged.

        :param user_name: User name of new user.
        :type user_name: str
        :param password: Password for new user.
        :type password: str

        """

        salt = uuid.uuid4().hex
        pass_hash = str(hashlib.sha256(salt.encode() + password.encode()).hexdigest())
        aes_key = get_random_bytes(16)

        if not User_db.name_exists(user_name):
            con = sqlite3.connect(User_db.FOLDER / User_db.NAME)
            cur = con.cursor()
            cur.execute(
                f"INSERT INTO {User_db.TABLE_NAME} VALUES (?,?,?,?)",
                (user_name, pass_hash, aes_key, salt),
            )
            print(f"INFO, User_db: New user successfully added, name: {user_name}")
            loglib.Log.event(loglib.Log.Event.REGISTER, 0, [user_name])
            con.commit()
            con.close()
        else:
            # User with same name already exists
            print(
                f"WARNING, User_db: Try add, but user with name: '{user_name}' already exists, New record was NOT added"
            )

    @staticmethod
    def delete(user_name: str):
        """
        Delete user from user database with all of his secrets.

        :param user_name: User name of user to be deleted.
        :type user_name: str

        """

        succ = Database.delete(Database.Table.USER_DB, user_name)
        if succ == 0:
            print(f"INFO, User_db: User successfully deleted, name: {user_name}")
            loglib.Log.event(loglib.Log.Event.UNREGISTER, 0, [user_name])
        elif succ == 1:
            print(f"INFO, User_db: User NOT exists, no action taken, name: {user_name}")
        else:
            print(
                f"ERROR, User_db.delete(): Database.delete() returned unexpected value, returned value: {succ}"
            )

    @staticmethod
    def get_record(user_name: str):
        """
        Get info about specified user.

        :param user_name: User name of requested user record.
        :type user_name: str

        """

        return Database.get_record(Database.Table.USER_DB, user_name)

    @staticmethod
    def return_all() -> list:
        """Return all user database with all of its records.

        :returns: All records in user database.
        :rtype: List
        """

        return Database.return_all(Database.Table.USER_DB)

    @staticmethod
    def show_all():
        """Print out all user database with all of its records."""

        Database.show_all(Database.Table.USER_DB)

    @staticmethod
    def table_exists() -> bool:
        """Check if user database already exists or not.

        :return: Return whether user database exists or not.
        :rtype: bool

        """

        return Database.table_exists(Database.Table.USER_DB)

    @staticmethod
    def name_exists(user_name: str) -> bool:
        """Check if username in registered in user database.

        :return: Return whether name exists or not.
        :rtype: bool

        """

        return Database.name_exists(Database.Table.USER_DB, user_name)


class File_index:
    """
    Database for indexing files saved in Kryzbu server storage. File index holds metadata about all files. Every file has its own record.
    Every record holds informations about the **name** and **owner** of a file, **date** of upload and **number of downloads**.
    """

    FOLDER = Path("server/_data/")
    TABLE_NAME = "file_index"
    NAME = "files.db"

    @staticmethod
    def init(storage_folder: Path):
        """
        Initialize file index while server is starting (called in :py:meth:`server.init() <server.server.Server.init>`
        with other inits functions). Check if file index already exists, create empty one if not.
        Also go refresh file index and check if listed files actually exists and update file index respectively.
        """

        if not File_index.table_exists():
            con = sqlite3.connect(File_index.FOLDER / File_index.NAME)
            cur = con.cursor()
            cur.execute(
                f"CREATE TABLE {File_index.TABLE_NAME} (name text, owner text, uploaded date, downloads int)"
            )
            print("WARNING, File_index: No table found, empty one created")
            con.commit()
            con.close()

        # Check for changes in files and update index respectively
        File_index.refresh(storage_folder)

    @staticmethod
    def add(file_name: str, user_name: str):
        """
        Add new file record into the file index. Store file name and owner user name from parameters.
        Date of upload set to current time and date and initiate number of downloads to 0. Called
        when a new file has been uploaded :py:meth:`Server.recieve_file() <server.server.Server.recieve_file()>`.

        :param file_name: File name of new file.
        :type file_name: str
        :param user_name: Owner of a file.
        :type user_name: str

        """

        if not File_index.file_exists(file_name):
            con = sqlite3.connect(File_index.FOLDER / File_index.NAME)
            cur = con.cursor()
            cur.execute(
                f"INSERT INTO {File_index.TABLE_NAME} VALUES (?,?,?,?)",
                (file_name, user_name, datetime.datetime.now().strftime("%m/%d/%Y"), 0),
            )
            con.commit()
            con.close()
        else:
            # File with same name already exists
            print(
                f"WARNING, File_index: Try add, but file '{file_name}' already exists. File was overwriten"
            )

    @staticmethod
    def download(file_name: str):
        """
        Just update (increment) download count of a file. Called when downdload of a file is requested :py:meth:`Server.serve_file() <server.server.Server.serve_file()>`.

        :param file_name: File name of requested file.
        :type file_name: str

        """

        con = sqlite3.connect(File_index.FOLDER / File_index.NAME)
        cur = con.cursor()
        cur.execute(
            f"SELECT downloads FROM {File_index.TABLE_NAME} WHERE name=:name",
            {"name": file_name},
        )
        cur.execute(
            "UPDATE file_index SET downloads=? WHERE name=?",
            (cur.fetchone()[0] + 1, file_name),
        )
        con.commit()
        con.close()

    @staticmethod
    def delete(file_name: str):
        """
        Remove file record from a file index with all of its data. Called when deletion of a file
        is requested :py:meth:`Server.remove_file() <server.server.Server.remove_file()>`.

        :param file_name: File name of deleted file.
        :type file_name: str

        """

        Database.delete(Database.Table.FILE_INDEX, file_name)

    @staticmethod
    def refresh(storage_folder: Path):
        """
        Check server filesystem integrity. Check for not indexed files in server storage and index them.
        Also check for indexed files but not existing in server storage and delete them. Called automatically
        when file index is been initialized :py:meth:`File_index.init() <server.db.File_index.init()>`.

        :param storage_folder: Path to server storage.
        :type storage_folder: Path

        """

        con = sqlite3.connect(File_index.FOLDER / File_index.NAME)
        cur = con.cursor()

        # Check for not indexed files
        for file in os.listdir(storage_folder):
            cur.execute(
                "SELECT * FROM file_index WHERE name=:name AND owner=:owner",
                {"name": file, "owner": os.path.basename(storage_folder)},
            )
            if not cur.fetchone():
                cur.execute(
                    "INSERT INTO file_index VALUES (?,?,?,?)",
                    (
                        file,
                        os.path.basename(storage_folder),
                        datetime.datetime.now().strftime("%m/%d/%Y"),
                        0,
                    ),
                )
                print(
                    f"WARNING, File_index: File '{file}' was not indexed, new record was added to file index and UPLOAD was logged"
                )
                loglib.Log.event(
                    loglib.Log.Event.UPLOAD, 0, [file, os.path.basename(storage_folder)]
                )

        # Check for indexed but not existing files
        for file in File_index.user_files(os.path.basename(storage_folder)):
            if not os.path.exists(
                storage_folder / file[0]
            ):  # file is a tuple, type not supported => need [0]
                cur.execute(
                    "DELETE FROM file_index WHERE name=:name AND owner=:owner",
                    {"name": file[0], "owner": os.path.basename(storage_folder)},
                )
                print(
                    f"WARNING, File_index: File '{file[0]}' was indexed but did NOT exist, record was deleted from file index and DELETE was logged"
                )
                loglib.Log.event(
                    loglib.Log.Event.DELETE,
                    0,
                    [file[0], os.path.basename(storage_folder)],
                )

        con.commit()
        con.close()

    @staticmethod
    def show_all():
        """Print out whole file index with all of its records."""

        Database.show_all(Database.Table.FILE_INDEX)

    @staticmethod
    def user_owns(user_name: str, file_name: str) -> bool:
        """
        Check if user owns specified file.

        :param user_name: Owner of a file.
        :type user_name: str
        :param file_name: File to be checked.
        :type file_name: str
        :returns: Ownership of a file
        :rtype: bool

        """

        # file record stucture: ("file_name", "user_name", "upload_date", n_downloads)
        record = Database.get_record(Database.Table.FILE_INDEX, file_name)

        return record[1] == user_name

    @staticmethod
    def user_files(user_name: str) -> list:
        """
        Return user's files. Look through whole file index and return all files owned by specified user.

        :param user_name: Owner of files.
        :type user_name: str

        """

        user_files: list = []
        records: Tuple = Database.return_all(Database.Table.FILE_INDEX)

        for record in records:
            if (
                record[1] == user_name
            ):  # record structure: ("file_name", "user_name", "upload_date", n_downloads)
                user_files.append(record)

        return user_files

    @staticmethod
    def return_all() -> list:
        """Return whole file index with all of its records.

        :returns: All records in file index.
        :rtype: List

        """

        return Database.return_all(Database.Table.FILE_INDEX)

    @staticmethod
    def get_record(file_name: str):
        """Get stored information about specified file.

        :param file_name: File name of requested file.
        :type file_name: str

        """

        return Database.get_record(Database.Table.FILE_INDEX, file_name)

    @staticmethod
    def table_exists() -> bool:
        """Check if file index already exists or not.

        :returns: Return whether file index exists or not.
        :rtype: bool

        """

        return Database.table_exists(Database.Table.FILE_INDEX)

    @staticmethod
    def file_exists(file_name: str) -> bool:
        """Check if file with specified name exists in file index.

        :param file_name: File name to check existance for.
        :type file_name: str
        :returns: Return whether file exists or not.
        :rtype: bool

        """

        return Database.name_exists(Database.Table.FILE_INDEX, file_name)


class Hmac_index:
    """Database for storing HMAC values of files (logs). Requires pair of file name and HMAC hash."""

    FOLDER = Path("server/_data/")
    TABLE_NAME = "hmac_index"
    NAME = "hmac.db"

    @staticmethod
    def init() -> None:
        """
        Check if *hmac.db* database already exists, creates empty one if not.

        """

        if not Hmac_index.table_exists():
            con = sqlite3.connect(Hmac_index.FOLDER / Hmac_index.NAME)
            cur = con.cursor()
            cur.execute(f"CREATE TABLE {Hmac_index.TABLE_NAME} (name text, hmac text)")
            print("WARNING, Hmac_index: No table found, empty one created")
            con.commit()
            con.close()

    @staticmethod
    def add(file_name: str, hmac: str):
        """
        Adds new entry to the database.

        :param file_name: Name of log file
        :type file_name: str
        :param hmac: Hex string of HMAC hash
        :type hmac: str

        """

        if not Hmac_index.file_exists(file_name):
            con = sqlite3.connect(Hmac_index.FOLDER / Hmac_index.NAME)
            cur = con.cursor()
            cur.execute(
                f"INSERT INTO {Hmac_index.TABLE_NAME} VALUES (?,?)", (file_name, hmac)
            )
            con.commit()
            con.close()
        else:
            # File with same name already exists
            Hmac_index.update(file_name, hmac)

    @staticmethod
    def update(file_name: str, hmac: str):
        """
        Only updates *hmac* value for an existing file entry

        :param file_name: Name of log file
        :type file_name: str
        :param hmac: Hex string of HMAC hash
        :type hmac: str
        
        """

        con = sqlite3.connect(Hmac_index.FOLDER / Hmac_index.NAME)
        cur = con.cursor()
        cur.execute(
            f"SELECT hmac FROM {Hmac_index.TABLE_NAME} WHERE name=:name",
            {"name": file_name},
        )
        cur.execute("UPDATE hmac_index SET hmac=? WHERE name=?", (hmac, file_name))
        con.commit()
        con.close()

    @staticmethod
    def get_record(file_name: str):
        """
        Returns specific database entry for a file

        :param file_name: Name of log file
        :type file_name: str
        :return: Specific row of *hmac.db* coresponding to file name
        :rtype: list

        """

        return Database.get_record(Database.Table.HMAC_INDEX, file_name)

    @staticmethod
    def table_exists() -> bool:
        """
        Check if *hmac.db* already exists or not.

        :return: True or False
        :rtype: bool

        """

        return Database.table_exists(Database.Table.HMAC_INDEX)

    @staticmethod
    def file_exists(file_name: str) -> bool:
        """
        Check if file with specified name exists in *hmac.db* index.

        :return: True or False
        :rtype: bool

        """

        return Database.name_exists(Database.Table.HMAC_INDEX, file_name)


class Database:
    """Functions implementacion that are shared between all databases."""

    class Table(Enum):
        USER_DB = User_db.TABLE_NAME
        FILE_INDEX = File_index.TABLE_NAME
        HMAC_INDEX = Hmac_index.TABLE_NAME

    @staticmethod
    def delete(table: Table, name: str) -> int:
        """Delete record from specified table.

        returns:\t 0 - Successfully deleted
        \t     1 - Record not in table"""

        if Database.name_exists(table, name):
            if table == Database.Table.FILE_INDEX:
                con = sqlite3.connect(File_index.FOLDER / File_index.NAME)
            elif table == Database.Table.USER_DB:
                con = sqlite3.connect(User_db.FOLDER / User_db.NAME)
            else:
                con = sqlite3.connect(User_db.FOLDER / Hmac_index.NAME)
            cur = con.cursor()
            cur.execute(f"DELETE FROM {table.value} WHERE name=:name", {"name": name})
            con.commit()
            con.close()
            return 0
        else:
            # Record not found
            return 1

    @staticmethod
    def get_record(table: Table, name):
        """Get record from specified table."""

        if table == Database.Table.FILE_INDEX:
            con = sqlite3.connect(File_index.FOLDER / File_index.NAME)
        elif table == Database.Table.USER_DB:
            con = sqlite3.connect(User_db.FOLDER / User_db.NAME)
        else:
            con = sqlite3.connect(User_db.FOLDER / Hmac_index.NAME)
        cur = con.cursor()
        cur.execute(
            f"SELECT * FROM {table.value} WHERE name=:name", {"name": name}
        )  # TODO: Posible sql injection
        record = cur.fetchone()
        con.close()
        return record

    @staticmethod
    def return_all(table: Table) -> list:
        """Return all data from specified table."""

        if table == Database.Table.FILE_INDEX:
            con = sqlite3.connect(File_index.FOLDER / File_index.NAME)
        elif table == Database.Table.USER_DB:
            con = sqlite3.connect(User_db.FOLDER / User_db.NAME)
        else:
            con = sqlite3.connect(User_db.FOLDER / Hmac_index.NAME)
        cur = con.cursor()

        list = []
        try:
            for row in cur.execute(
                f"SELECT * FROM {table.value}"
            ):  # TODO: Posible sql injection
                list.append(row)
            con.close()
        except:
            print("WARNING: File database empty!")
        return list

    @staticmethod
    def show_all(table: Table):
        """Print out whole table."""

        if table == Database.Table.FILE_INDEX:
            con = sqlite3.connect(File_index.FOLDER / File_index.NAME)
        elif table == Database.Table.USER_DB:
            con = sqlite3.connect(User_db.FOLDER / User_db.NAME)
        else:
            con = sqlite3.connect(User_db.FOLDER / Hmac_index.NAME)
        cur = con.cursor()

        for row in cur.execute(f"SELECT * FROM {table.value}"):
            print(row)
        con.close()

    @staticmethod
    def table_exists(table: Table) -> bool:
        """Check if table exists or not."""

        if table == Database.Table.FILE_INDEX:
            con = sqlite3.connect(File_index.FOLDER / File_index.NAME)
        elif table == Database.Table.USER_DB:
            con = sqlite3.connect(User_db.FOLDER / User_db.NAME)
        else:
            con = sqlite3.connect(User_db.FOLDER / Hmac_index.NAME)
        cur = con.cursor()
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=:name",
            {"name": table.value},
        )
        if cur.fetchone():
            con.close()
            return True
        else:
            con.close()
            return False

    @staticmethod
    def name_exists(table: Table, name: str) -> bool:
        """Check if specified name exists in specified table."""

        if table == Database.Table.FILE_INDEX:
            con = sqlite3.connect(File_index.FOLDER / File_index.NAME)
        elif table == Database.Table.USER_DB:
            con = sqlite3.connect(User_db.FOLDER / User_db.NAME)
        else:
            con = sqlite3.connect(User_db.FOLDER / Hmac_index.NAME)
        cur = con.cursor()
        cur.execute(f"SELECT name FROM {table.value} WHERE name=:name", {"name": name})
        if cur.fetchone():
            cur.close()
            return True
        else:
            cur.close()
            return False
