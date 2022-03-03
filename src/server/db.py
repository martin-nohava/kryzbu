from pathlib import Path
import datetime
import sqlite3


class File_index():
    """Database for indexing files saved in Kryzbu server storage. 
    Content of table: name, owner, date of upload, number of downloads.
    Table was created with: CREATE TABLE file_index (name text, owner text, uploaded date, downloads int)
    """

    FOLDER = Path("server/_data/")
    NAME = 'files.db'
   

    @staticmethod
    def add(file_name: str):
        """Add new file index to database."""

        con = sqlite3.connect(File_index.FOLDER / File_index.NAME)
        cur = con.cursor()

        if not File_index.table_exists():   # Create table if it dosn't exist
            cur.execute("CREATE TABLE file_index (name text, owner text, uploaded date, downloads int)")

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

        con = sqlite3.connect(File_index.FOLDER / File_index.NAME)
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='file_index'")
        if  cur.fetchone():
            con.close()
            return True
        else:
            con.close()
            return False
