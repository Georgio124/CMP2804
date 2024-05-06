import subprocess

# built with windows in mind, would require .sh support for linux
def Run_process(path):
    cmd = (f"start cmd.exe /k python {path}")
    subprocess.run(cmd, shell=True)

# Add packet sniffer or other modules here later on if needed
scripts = [
    "SQL_Integration/main.py",
    "server_tracking/interface.py"
]

if __name__ == "__main__":
    for script in scripts:
        Run_process(script)
