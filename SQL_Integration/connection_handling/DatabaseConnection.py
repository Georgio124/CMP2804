import pymysql
from dotenv import load_dotenv
import os

class DatabaseConnection:
    
    # Pulls credentials from sql.env during class initialisation - will default to standard mysql credentials if not specified (windows/linux account username, port 3306, no password) 
    def __init__(self):
        self.host = os.getenv('SQLHost')
        self.port = int(os.getenv('SQLPort'))
        self.user = os.getenv('SQLUser')
        self.password = os.getenv('SQLPassword')
        self.database = os.getenv('SQLDatabase')

    # attempts to establish connection with database using the information provided in the class initialisation
    def connect(self):
        try:
            return pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database, port=self.port, charset='utf8mb4')
        
        # Exception is raised if a valid database isn't found on the database server. This will queue a new database to be made and a connection attempt to be made again
        except pymysql.err.OperationalError as exception:
            if exception.args[0] == 1049: # 1049 is the error code for unknown database
                connection = pymysql.connect(host=self.host, user=self.user, password=self.password, port=self.port, charset='utf8mb4')
                
                # Creates the database using the cursor thread (only runs if the database doesn't exist)
                with connection.cursor() as cursor:
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
                    connection.commit()
                    connection.close()

                # Reconnect to the newly created database
                return pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database, port=self.port, charset='utf8mb4')
            else:
                raise # generic exception handling

    def create_firewall_rules_table(self, connection):
        # SQL command to insert data (uses %s as a placeholder for the data to be inserted)
        sample_query = """INSERT INTO firewall_rules (IP, AllowDeny, Protocol, Weighting)
                          VALUES (%s, %s, %s, %s)"""
        
        # Inserts this sample entry into the table upon creation to verify write permissions work as expected and to raise any issues quickly
        test_samples = ('192.168.1.1', 'Allow', 'TCP', 10)

        # Attemptst to create the table (if it doesnt exist) and inserts the sample data - adheres to standardised data format 
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS firewall_rules (
                        RuleID INT AUTO_INCREMENT PRIMARY KEY,
                        IP VARCHAR(15),
                        AllowDeny ENUM('Allow', 'Deny') NOT NULL,
                        Protocol ENUM('TCP', 'UDP', 'ALL') NOT NULL,
                        Weighting INT
                    )
                """)
                connection.commit()

                # After table creation is committed and verified as successful, the sample data is inserted. Assuming that completes successfully, the connection is committed and the exception isn't raised
                cursor.execute(sample_query, test_samples)
                connection.commit()
        
        # Generic exception handling
        except pymysql.Error as exception:
            print("An error occurred: ", {exception})


    # Utilises iniation credentials to establish database connection and return the connection object
    def connect_and_initialise(self):
        return pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    
    # Adds triggers to the database if they dont already exist that can be used to detect when new rules are added or removed in Windows_Firewall.py
    def create_triggers(self, connection):
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS rule_changes")
            cursor.execute("""               
                CREATE TABLE rule_changes (
                    change_id INT AUTO_INCREMENT PRIMARY KEY,
                    RuleID INT,
                    change_type ENUM('Added', 'Deleted'),
                    change_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (RuleID) REFERENCES firewall_rules(RuleID)
                    ON DELETE CASCADE ON UPDATE CASCADE
                )
            """)

            cursor.execute("DROP TRIGGER AfterInsertRule")
            cursor.execute("""
                CREATE TRIGGER AfterInsertRule
                AFTER INSERT ON firewall_rules 
                FOR EACH ROW
                BEGIN
                    INSERT INTO rule_changes (rule_id, change_type, change_timestamp)
                    VALUES (NEW.RuleID, 'Added', NOW());
                END
            """)
            
            cursor.execute("DROP TRIGGER AfterDeleteRule")
            cursor.execute("""
                CREATE TRIGGER AfterDeleteRule
                AFTER DELETE ON firewall_rules 
                FOR EACH ROW
                BEGIN
                    INSERT INTO rule_changes (rule_id, change_type, change_timestamp)
                    VALUES (OLD.RuleID, 'Deleted', NOW());
                END
            """)
            connection.commit()

if __name__ == "__main__":
    db = DatabaseConnection()
    connection = db.connect_and_initialise()
    print("Database and table setup complete.")
