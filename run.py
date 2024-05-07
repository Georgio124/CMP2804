import subprocess
import sys
import os
import time
from dotenv import load_dotenv

load_dotenv()

# This code automatically updates/installs the packages in the requirements.txt file. It can be enabled/disabled in the .env file.
if os.getenv('AutoUpdatePackages') == 'True':
    with open('requirements.txt', 'r') as file:
        packages = file.readlines()

    for package in packages:
        package = package.strip()
        result = subprocess.run(['pip', 'install', package], text=True, capture_output=True)
        if result.returncode != 0:
            print(f"Failed to install {package}")
        else:
            print(f"{package} is up to date.")

# built with windows in mind, would require .sh support for linux
def Run_process(path):
    cmd = (f"start cmd.exe /k python {path}")
    subprocess.run(cmd, shell=True)

# Add packet sniffer or other modules here later on if needed
scripts = [
    "SQL_Integration/main.py",
    #"server_tracking/interface.py",
    #"Windows_Interface/Windows_Firewall.py"
]

if __name__ == "__main__":
    for script in scripts:
        Run_process(script)
