import os
import sys
import ctypes
import pymysql
import subprocess
import asyncio
from dotenv import load_dotenv

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root)

from SQL_Integration.connection_handling.DatabaseConnection import DatabaseConnection


# Pulls the .env file from the absolute parent directory
load_dotenv('.env')

# Pulls from database credentials specified in main .env file - utilises the connect_database() function from DatabaseConnection.py to establish a connection
def connect_database():
    return pymysql.connect(
        host=os.getenv('SQLHost'),
        port=int(os.getenv('SQLPort')),
        user=os.getenv('SQLUser'),
        password=os.getenv('SQLPassword'),
        database=os.getenv('SQLDatabase'),
        cursorclass=pymysql.cursors.DictCursor
    )

# Clears all rules from the firewall group 'TSE-Demo' - general consistency protection upon each restart
def clear_rules():
    cmd = [
        "powershell",
        "Get-NetFirewallRule -Group 'TSE-Demo' | Remove-NetFirewallRule"
    ]
    subprocess.run(cmd, check=True)

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
        
# Adds the physical rule with the specified criteria from the database onto windows defender firewall
def add_rule(rule):
    name = f"TSE-Demo - Rule: {rule['RuleID']}"
    action = 'Allow' if rule['AllowDeny'] == 'Allow' else 'Block'
    
    # Check if a rule with the same name already exists
    existing_rules = ["powershell", "Get-NetFirewallRule", f"-DisplayName '{name}'"]
    try:
        existing_rules = subprocess.run(existing_rules, check=True, capture_output=True, text=True)
        if name in existing_rules.stdout:
            print(f"Rule '{name}' already exists. Skipping...")
            return
        
    # If the rule doesn't exist, pass the exception
    except subprocess.CalledProcessError:
        pass

    # Decides the protocol
    protocol = rule['Protocol']
    if protocol == "ALL": # sets the protocol_cmd to nothing which blocks all protocols
        protocol_cmd = ""
    else:
        protocol_cmd = f"-Protocol {protocol}" # sets the protocol_cmd variable to the actual protocol field
    
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
    
def setup_triggers():
    db = DatabaseConnection()
    connection = db.connect_and_initialise()
    db.create_triggers(connection)

def remove_rule_from_firewall(rule_id):
    name = f"TSE-Demo - Rule: {rule_id}"
    cmd = ["powershell", "Remove-NetFirewallRule", f"-DisplayName '{name}'"]
    subprocess.run(cmd, check=True)
    
async def check_new_rules():
    local_state = {}  # Stores index of already applied rules into main memory for comparison

    while True:
        with connect_database() as connection:
            with connection.cursor() as cursor:
                
                # Checks for any rules that have been deleted and iterates through to delete them from windows firewall
                cursor.execute("SELECT change_id, RuleID, change_type FROM rule_changes WHERE change_type='Deleted'")
                deletions = cursor.fetchall()
                for deletion in deletions:
                    rule_id = deletion['RuleID']
                    if rule_id in local_state:
                        remove_rule_from_firewall(rule_id)
                        print(f"RuleID {rule_id} deleted from firewall.")
                        local_state.pop(rule_id)
                    
                    # Deletes the record from rule_changes table after the rule has been removed from the firewall
                    cursor.execute("DELETE FROM rule_changes WHERE change_id=%s", (deletion['change_id'],))
                    connection.commit()

                # Fetch current rules from the database
                cursor.execute("SELECT * FROM firewall_rules ORDER BY weighting DESC")
                current_rules = {rule['RuleID']: rule for rule in cursor.fetchall()}

        # Check for additions or modifications
        for rule_id, rule_details in current_rules.items():
            if rule_id not in local_state or local_state[rule_id] != rule_details:
                if rule_id in local_state:
                    remove_rule_from_firewall(rule_id)
                    print(f"Existing rule ID {rule_id} updated.")
                add_rule(rule_details)
                local_state[rule_id] = rule_details

        FrequencyPollRate = int(os.getenv('FrequencyPollRate', '10'))  # Frequency of checks - set in .env file. Defaults to 10 seconds if not specified 
        await asyncio.sleep(FrequencyPollRate)

        print("Checking for rule changes...")
        
        
        
        

async def main():
    setup_triggers()  # Sets triggers to detect when new rules are added or removed
    request_admin_perms()  # Check if the script can run PowerShell as an admin
    clear_rules()  # Clear all rules from the firewall group 'TSE-Demo'
    
    await check_new_rules() # starts monitoring for rule changes

if __name__ == "__main__":
    asyncio.run(main())
