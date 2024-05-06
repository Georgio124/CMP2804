import os
import sys
import ctypes
import pymysql
import subprocess
from dotenv import load_dotenv

# Pulls the .env file from the relative parent directory
load_dotenv('../.env')

# Pulls from database credentials specified in main .env file - encapsulated from DatabaseConnection.py to allow individual file testing
def connect_database():
    """ Connect to the SQL database using credentials from the .env file. """
    return pymysql.connect(
        host=os.getenv('SQLHost'),
        port=int(os.getenv('SQLPort')),
        user=os.getenv('SQLUser'),
        password=os.getenv('SQLPassword'),
        database=os.getenv('SQLDatabase'),
        cursorclass=pymysql.cursors.DictCursor
    )


# Check if script has admin perms, returns a False if not
def check_if_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
    
# If a False value is returned from check_if_admin(), a pop up asks for admin perms
def request_admin_perms():
    if not check_if_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()



def main():
    request_admin_perms()


if __name__ == "__main__":
    main()
