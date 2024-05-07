from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ValidationError
from typing import Optional
from dotenv import load_dotenv
import pymysql
import os
import sys
import logging
import time

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root)

from connection_handling.DatabaseConnection import DatabaseConnection

app = FastAPI()
logging.basicConfig(filename='API_logs.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s') # allows outputs to be served to the log file if required - "ERROR" level is set to avoid excessive logging, can be changed to WARN or INFO


# Load environment variables (uses relative pathing) 
env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path=env_path)


# establishes base class template for `FirewallRule` transactional data. May need to be changed depending on format of packet sniffer data
class FirewallRule(BaseModel):
    ip: str = Field(..., alias='ip')
    allow_deny: str = Field(..., alias='allow_deny')
    protocol: str = Field(..., alias='protocol')
    weight: Optional[int] = Field(None, alias='weight')
    id: Optional[int] = Field(None, alias='id') 

    # Provides an example input on the /api/system/docs page - inputs for the ID field are ignored but included as currently unsure how data will be passed from the packet sniffer. 
    class Config:
        allow_population_by_field_name = True
        orm_mode = True
        schema_extra = {
            "example": {
                "ip": "10.11.12.13",
                "allow_deny": "Allow",
                "protocol": "ALL",
                "weight": 5,
                "id": 32
            }
        }
        

# Get database connection from the DatabaseConnection class
db_connection = DatabaseConnection()

# Displays already existing rules in the database
@app.get("/rules", response_model=list[FirewallRule])
def get_rules():
    db_conn = DatabaseConnection()
    conn = db_conn.connect_and_initialise()
    cursor = conn.cursor()
    cursor.execute("SELECT RuleID as 'id', IP as 'ip', AllowDeny as 'allow_deny', Protocol as 'protocol', Weighting as 'weight' FROM firewall_rules")
    rules = cursor.fetchall()
    conn.close()
    return rules 

# Adds a new rule to the database
@app.post("/rules", response_model=FirewallRule)
def add_rule(rule: FirewallRule):
    with db_connection.connect_and_initialise() as conn:
        cursor = conn.cursor()
        query = "INSERT INTO firewall_rules (IP, AllowDeny, Protocol, Weighting) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (rule.ip, rule.allow_deny, rule.protocol, rule.weight))
        conn.commit()
        rule_id = cursor.lastrowid
    return {**rule.dict(), "id": rule_id}

# Deletes a rule from the database
@app.delete("/rules/{rule_id}", response_model=FirewallRule)
def remove_rule(rule_id: int):
    db_conn = DatabaseConnection()
    conn = db_conn.connect_and_initialise()
    cursor = conn.cursor()
    cursor.execute("SELECT RuleID as 'id', IP as 'ip', AllowDeny as 'allow_deny', Protocol as 'protocol', Weighting as 'weight' FROM firewall_rules WHERE RuleID = %s", (rule_id,))
    rule = cursor.fetchone()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    cursor.execute("DELETE FROM firewall_rules WHERE RuleID = %s", (rule_id,))
    conn.commit()
    return rule

# Test instance for wider application use. Runs on 0.0.0.0 to listen to all open network interfaces
@app.get("/test-rule")
def test_rule():
    simulated_row = {'IP': '192.168.1.1', 'AllowDeny': 'Allow', 'Protocol': 'TCP', 'Weighting': 10}
    try:
        rule = FirewallRule(**simulated_row)
        return rule
    except ValidationError as exception:
        return {"error": str(exception), "data": simulated_row}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)