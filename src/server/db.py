from pathlib import Path
from .loglib import Log
import datetime
import sqlite3
import os


class User_db():
    """Database of users registered in Kryzbu server."""

    FOLDER = Path("server/_data")
    NAME = 'users.db'

    @staticmethod
    def init():
        """Initialize user database while server starting."""
        
        if not User_db.table_exists():
            con = sqlite3.connect(File_index.FOLDER / File_index.NAME)
            cur = con.cursor()
            cur.execute("CREATE TABLE users (username text, pass_hash text, pub_key text, secret text)")
            print("WARNING, User_db: No table found, empty one created")
            con.commit()
            con.close()

    
    @staticmethod
    def add(user_name: str, pass_hash: str, pub_key: str, secret: str):
        """Add new user to database."""

        con = sqlite3.connect(File_index.FOLDER / File_index.NAME)
        cur = con.cursor()
        cur.execute("INSERT INTO users VALUES (?,?,?,?)", (user_name, pass_hash, pub_key, secret))
        print(f"INFO, User_db: New user successfully added, name: {user_name}")
        User_db.show_all()
        con.commit()
        con.close()


    @staticmethod
    def show_all():
        """Print out all table."""

        con = sqlite3.connect(File_index.FOLDER / File_index.NAME)
        cur = con.cursor()
        for row in cur.execute("SELECT * FROM users"):
            print(row)
        con.close()


    @staticmethod
    def table_exists() -> bool:
        """Check if User already exists or not."""

        return Database.table_exists("users")


class File_index():
    """Database for indexing files saved in Kryzbu server storage. 
    Content of table: name, owner, date of upload, number of downloads.
    Table was created with: CREATE TABLE file_index (name text, owner text, uploaded date, downloads int)
    """

    FOLDER = Path("server/_data/")
    NAME = 'files.db'


    @staticmethod
    def init(storage_folder: Path):
        """Check if file index already exists, create empty one if not."""
        
        if not File_index.table_exists():
            con = sqlite3.connect(File_index.FOLDER / File_index.NAME)
            cur = con.cursor()
            cur.execute("CREATE TABLE file_index (name text, owner text, uploaded date, downloads int)")
            print(f"WARNING, File_index: No table found, empty one created")
            con.commit()
            con.close()

        # Check for changes in files and update idex respectively
        File_index.refresh(storage_folder)
   

    @staticmethod
    def add(file_name: str):
        """Add new file index to database."""

        con = sqlite3.connect(File_index.FOLDER / File_index.NAME)
        cur = con.cursor()
        cur.execute("INSERT INTO file_index VALUES (?,?,?,?)", (file_name, 'everyone', datetime.datetime.now().strftime("%m/%d/%Y"), 0))
        con.commit()
        con.close()


    @staticmethod
    def download(file_name: str):
        """Update download count for a file."""
        
        con = sqlite3.connect(File_index.FOLDER / File_index.NAME)
        cur = con.cursor()
        cur.execute("SELECT downloads FROM file_index WHERE name=:name", {"name": file_name})
        cur.execute("UPDATE file_index SET downloads=? WHERE name=?", (cur.fetchone()[0] + 1, file_name))
        con.commit()
        con.close()

    
    @staticmethod
    def delete(file_name: str):
        """Remove file record."""

        con = sqlite3.connect(File_index.FOLDER / File_index.NAME)
        cur = con.cursor()
        cur.execute("DELETE FROM file_index WHERE name=:name", {"name": file_name})
        con.commit()
        con.close()     

            
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

        con = sqlite3.connect(File_index.FOLDER / File_index.NAME)
        cur = con.cursor()
        for row in cur.execute("SELECT * FROM file_index"):
            print(row)
        con.close()

    
    @staticmethod
    def return_all() -> list:
        """Return all data."""

        list = []
        con = sqlite3.connect(File_index.FOLDER / File_index.NAME)
        cur = con.cursor()
        try:
            for row in cur.execute("SELECT * FROM file_index"):
                list.append(row)
            con.close()
        except:
            print('WARNING: File database empty!')
        return list


    @staticmethod
    def get_record(file_name: str):
        """Get info about file."""

        con = sqlite3.connect(File_index.FOLDER / File_index.NAME)
        cur = con.cursor()
        cur.execute("SELECT * FROM file_index WHERE name=:name", {"name": file_name})
        record = cur.fetchone()
        con.close()
        return record


    @staticmethod
    def table_exists() -> bool:
        """Check if File_index already exists or not."""

        return Database.table_exists("file_index")


class Database:
    """Functions implementacion that are shared between all databases."""

    @staticmethod
    def table_exists(table: str) -> bool:
        """Check if File_index already exists or not."""

        con = sqlite3.connect(File_index.FOLDER / File_index.NAME)
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=:name", {"name": table})
        if  cur.fetchone():
            con.close()
            return True
        else:
            con.close()
            return False
