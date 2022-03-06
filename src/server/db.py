from pathlib import Path
from unicodedata import name
from .loglib import Log
from enum import Enum
import datetime
import sqlite3
import os


class User_db():
    """Database of users registered in Kryzbu server.
    Content of table: username, SHA256(password || salt), public_key, secret"""

    FOLDER = Path("server/_data")
    TABLE_NAME = 'users'
    NAME = 'users.db'

    @staticmethod
    def init():
        """Initialize user database while server starting."""
        
        if not User_db.table_exists():
            con = sqlite3.connect(User_db.FOLDER / User_db.NAME)
            cur = con.cursor()
            cur.execute(f"CREATE TABLE {User_db.TABLE_NAME} (name text, pass_hash text, pub_key text, secret text)")
            print("WARNING, User_db: No table found, empty one created")
            con.commit()
            con.close()

    
    @staticmethod
    def add(user_name: str, pass_hash: str, pub_key: str, secret: str):
        """Add new user to database."""

        if not User_db.name_exists(user_name):
            con = sqlite3.connect(User_db.FOLDER / User_db.NAME)
            cur = con.cursor()
            cur.execute(f"INSERT INTO {User_db.TABLE_NAME} VALUES (?,?,?,?)", (user_name, pass_hash, pub_key, secret))
            print(f"INFO, User_db: New user successfully added, name: {user_name}")
            Log.event(Log.Event.REGISTER, 0, [user_name])
            con.commit()
            con.close()
        else:
            # User with same name already exists
            print(f"WARNING, User_db: Try add, but user with name: '{user_name}' already exists, New record was NOT added")


    @staticmethod
    def delete(user_name: str):
        """Delete user."""

        Database.delete(Database.Table.USER_DB, user_name)
        print(f"INFO, User_db: User successfully deleted, name: {user_name}")
        Log.event(Log.Event.UNREGISTER, 0, [user_name])

    
    @staticmethod
    def get_record(user_name: str):
        """Get info about specific username"""

        return Database.get_record(Database.Table.USER_DB, user_name)


    @staticmethod
    def return_all():
        """Return all user table"""

        return Database.return_all(Database.Table.USER_DB)


    @staticmethod
    def show_all():
        """Print out all table."""

        Database.show_all(Database.Table.USER_DB)


    @staticmethod
    def table_exists() -> bool:
        """Check if User already exists or not."""

        return Database.table_exists(Database.Table.USER_DB)


    @staticmethod
    def name_exists(user_name: str) -> bool:
        """Check if there is the specified username in user database."""

        return Database.name_exists(Database.Table.USER_DB, user_name)


class File_index():
    """Database for indexing files saved in Kryzbu server storage. 
    Content of table: name, owner, date of upload, number of downloads.
    """

    FOLDER = Path("server/_data/")
    TABLE_NAME = 'file_index'
    NAME = 'files.db'


    @staticmethod
    def init(storage_folder: Path):
        """Check if file index already exists, create empty one if not."""
        
        if not File_index.table_exists():
            con = sqlite3.connect(File_index.FOLDER / File_index.NAME)
            cur = con.cursor()
            cur.execute(f"CREATE TABLE {File_index.TABLE_NAME} (name text, owner text, uploaded date, downloads int)")
            print("WARNING, File_index: No table found, empty one created")
            con.commit()
            con.close()

        # Check for changes in files and update idex respectively
        File_index.refresh(storage_folder)
   

    @staticmethod
    def add(file_name: str, user_name: str):
        """Add new file index to database."""
        
        if not File_index.file_exists(file_name):
            con = sqlite3.connect(File_index.FOLDER / File_index.NAME)
            cur = con.cursor()
            cur.execute(f"INSERT INTO {File_index.TABLE_NAME} VALUES (?,?,?,?)", (file_name, user_name, datetime.datetime.now().strftime("%m/%d/%Y"), 0))
            con.commit()
            con.close()
        else:
            # File with same name already exists
            print(f"WARNING, File_index: Try add, but file '{file_name}' already exists. File was overwriten")


    @staticmethod
    def download(file_name: str):
        """Update download count for a file."""
        
        con = sqlite3.connect(File_index.FOLDER / File_index.NAME)
        cur = con.cursor()
        cur.execute(f"SELECT downloads FROM {File_index.TABLE_NAME} WHERE name=:name", {"name": file_name})
        cur.execute("UPDATE file_index SET downloads=? WHERE name=?", (cur.fetchone()[0] + 1, file_name))
        con.commit()
        con.close()

    
    @staticmethod
    def delete(file_name: str):
        """Remove file record."""

        Database.delete(Database.Table.FILE_INDEX, file_name)    

            
    @staticmethod
    def refresh(storage_folder: Path):
        "Check for not indexed files and index them and check for indexed but not existing files and delete them."

        con = sqlite3.connect(File_index.FOLDER / File_index.NAME)
        cur = con.cursor()
        
        # Check for not indexed files
        for file in os.listdir(storage_folder):
            cur.execute("SELECT * FROM file_index WHERE name=:name", {"name": file})
            if not cur.fetchone():
                cur.execute("INSERT INTO file_index VALUES (?,?,?,?)", (file, 'Local_Admin', datetime.datetime.now().strftime("%m/%d/%Y"), 0))
                print(f"WARNING, File_index: File '{file}' was not indexed, new record was added to file index and UPLOAD was logged")
                Log.event(Log.Event.UPLOAD, 0, [file, 'Local_Admin'])

        # Check for indexed but not existing files
        for file in File_index.return_all():
            if not os.path.exists(storage_folder / file[0]):    # file is a tuple, type not supported => need [0]
                cur.execute("DELETE FROM file_index WHERE name=:name", {"name": file[0]})
                print(f"WARNING, File_index: File '{file[0]}' was indexed but did NOT exist, record was deleted from file index and DELETE was logged")
                Log.event(Log.Event.DELETE, 0, [file[0], 'Local_Admin'])

        con.commit()
        con.close()
   
    
    @staticmethod
    def show_all():
        """Print out all table."""

        Database.show_all(Database.Table.FILE_INDEX)

    
    @staticmethod
    def return_all() -> list:
        """Return all data."""

        return Database.return_all(Database.Table.FILE_INDEX)


    @staticmethod
    def get_record(file_name: str):
        """Get info about file."""

        return Database.get_record(Database.Table.FILE_INDEX, file_name)        


    @staticmethod
    def table_exists() -> bool:
        """Check if file_index already exists or not."""

        return Database.table_exists(Database.Table.FILE_INDEX)

    @staticmethod
    def file_exists(file_name: str) -> bool:
        """Check if file with specified name exists in file index."""
        
        return Database.name_exists(Database.Table.FILE_INDEX, file_name)


class Database:
    """Functions implementacion that are shared between all databases."""

    class Table(Enum):
        USER_DB = User_db.TABLE_NAME
        FILE_INDEX = File_index.TABLE_NAME


    @staticmethod
    def delete(table: Table, name: str):
        """Delete record from specified table"""

        if table == Database.Table.FILE_INDEX:
            con = sqlite3.connect(File_index.FOLDER / File_index.NAME)
        else:
            con = sqlite3.connect(User_db.FOLDER / User_db.NAME)
        cur = con.cursor()
        cur.execute(f"DELETE FROM {table.value} WHERE name=:name", {"name": name})
        con.commit()
        con.close() 


    @staticmethod
    def get_record(table: Table, name):
        """Get record from specified table."""

        if table == Database.Table.FILE_INDEX:
            con = sqlite3.connect(File_index.FOLDER / File_index.NAME)
        else:
            con = sqlite3.connect(User_db.FOLDER / User_db.NAME)
        cur = con.cursor()
        cur.execute(f"SELECT * FROM {table.value} WHERE name=:name", {"name": name}) # TODO: Posible sql injection
        record = cur.fetchone()
        con.close()
        return record

    
    @staticmethod
    def return_all(table: Table) -> list:
        """Return all data from specified table."""

        if table == Database.Table.FILE_INDEX:
            con = sqlite3.connect(File_index.FOLDER / File_index.NAME)
        else:
            con = sqlite3.connect(User_db.FOLDER / User_db.NAME)
        cur = con.cursor()
        
        list = []
        try:
            for row in cur.execute(f"SELECT * FROM {table.value}"): # TODO: Posible sql injection
                list.append(row)
            con.close()
        except:
            print('WARNING: File database empty!')
        return list

    
    @staticmethod
    def show_all(table: Table):
        """Print out whole table."""

        if table == Database.Table.FILE_INDEX:
            con = sqlite3.connect(File_index.FOLDER / File_index.NAME)
        else:
            con = sqlite3.connect(User_db.FOLDER / User_db.NAME)
        cur = con.cursor()

        for row in cur.execute(f"SELECT * FROM {table.value}"):
            print(row)
        con.close()


    @staticmethod
    def table_exists(table: Table) -> bool:
        """Check if table exists or not."""

        if table == Database.Table.FILE_INDEX:
            con = sqlite3.connect(File_index.FOLDER / File_index.NAME)
        else:
            con = sqlite3.connect(User_db.FOLDER / User_db.NAME)
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=:name", {"name": table.value})
        if  cur.fetchone():
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
        else:
            con = sqlite3.connect(User_db.FOLDER / User_db.NAME)
        cur = con.cursor()
        cur.execute(f"SELECT name FROM {table.value} WHERE name=:name", {"name": name})
        if cur.fetchone():
            cur.close()
            return True
        else:
            cur.close()
            return False
