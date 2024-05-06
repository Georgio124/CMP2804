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

# Pulls the firewall rules from the table and loads them into main memory for quicker access.
# Orders the rules by Descending weight so rules with larger weighting are applied first (Windows will prioritise allow rules over block rules and then prioritise rules that were created first)        
def get_firewall_rules():
    with connect_database() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM firewall_rules ORDER BY weighting DESC")
            return cursor.fetchall()


def add_rule(rule):
    name = f"TSE-Demo - Rule: {rule['RuleID']}"
    action = 'Allow' if rule['AllowDeny'] == 'Allow' else 'Block'
 
    
    # Decides the protocol (Setting the protocol to nothing on Windows firewall automatically blocks each protocol)
    protocol = rule['Protocol']
    if protocol == "ALL": # sets the protocol_cmd to nothing (to be later removed) which blocks all protocols
        protocol_cmd = ""
        
    else:
        protocol_cmd = (f"-Protocol {protocol}") # sets the protocol_cmd variable to the actual protocol field
    
    cmd = [
        "powershell",
        "New-NetFirewallRule",
        f"-DisplayName '{name}'",
        f"-Direction Inbound",
        protocol_cmd,
        f"-Action {action}",
        f"-Group 'TSE-Demo'"
    ]

    # Filtering out empty strings from cmd list which are added if protocol is "ALL" before running it as admin on powershell
    cmd = list(filter(None, cmd))
    subprocess.run(cmd, check=True)


def main():
    request_admin_perms() # check if the script can run powershell as an admin
    rules = get_firewall_rules() # imports rules from database into main memory
    for rule in rules: # iterates through each rule and adds them to the firewall
        add_rule(rule)

if __name__ == "__main__":
    main()
