# External library imports
import asyncio
import uvicorn
import os
from dotenv import load_dotenv
from fastapi import FastAPI
import time

# External file imports
from interface_handling.System_API import app as system_api_app
from packet_logging.packet_logging import app as packet_logging_app
from connection_handling.DatabaseConnection import DatabaseConnection
from ModifyTable import ModifyTable
from interface_handling.User_CLI import UserCLI

app = FastAPI()

env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

# Async process to start to start both the FastAPI instances for Packet Logging and System API with uvicorn
async def start_uvicorn():
    host = os.getenv('FastAPI_IP')
    port = int(os.getenv('FastAPI_Port'))
    log_level = os.getenv('FastAPI_LogLevel')
    
    print(f"Starting FastAPI on {host}:{port} with log level {log_level}")

    config = uvicorn.Config(app=app, host=host, port=port, reload=True, log_level=log_level)
    server = uvicorn.Server(config)
    await server.serve()

# creates a new thread on startup that verifies database connectivity - will only run if uvicorn successfully starts
@app.on_event("startup")
async def startup_event():
    db_connection = await asyncio.to_thread(DatabaseConnection().connect_and_initialise)
    cli = UserCLI(db_connection)
    asyncio.create_task(run_cli(cli)) # dispatches a new process to run the user CLI

async def run_cli(cli):
    while True:
        await asyncio.to_thread(cli.run)

# Sets unique mountpoints for both FastAPI instances - can be changed if needed. /api/system/docs and /api/packet-logging/docs can be used for demonstration purposes
app.mount("/api/system", system_api_app)
app.mount("/api/packet-logging", packet_logging_app)

# Little east egg incase you happen to be reading this code :)
@app.get("/")
async def read_root():
    return {"Congratulations, you're found Ben's little easter egg! Have a coffee and rest here. You probably weren't expecting this - you may want to go to /api/system/docs or /api/packet-logging/docs :) "}

# Main process handler
if __name__ == "__main__":
    asyncio.run(start_uvicorn())
