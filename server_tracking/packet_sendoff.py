import requests
import os
from dotenv import load_dotenv
import time

env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(dotenv_path=env_path)


# URL of the FastAPI endpoint - pulls from the .env file in the root directory
fastapi_ip = os.getenv('FastAPI_IP')
fastapi_port = os.getenv('FastAPI_Port')

url = f"http://{fastapi_ip}:{fastapi_port}/api/system/rules"

# Sample data (you would need to adjust this to variable/a dynamic form of data)
data = {
    "ip": "10.11.12.13",
    "allow_deny": "Allow",
    "protocol": "ALL",
    "weight": 5,
    "id": 32 
}

# Sends the request to fastAPI and prints the response
response = requests.post(url, json=data)
print(response.status_code)
print(response.json())