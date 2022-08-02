"""
    Python 3
    coding: utf-8
"""
from operator import index
from socket import *
from threading import Thread
import sys, select

from os.path import exists
from datetime import datetime

from numpy import block

CREDENTIALS_FILE = "credentials.txt"
USERLOG_FILE = "userlog.txt"

# acquire server host and port from command line parameter
if len(sys.argv) != 3:
    print("\n===== Error usage, python3 TCPServer3.py SERVER_PORT ======\n")
    exit(0)
serverHost = "127.0.0.1"
serverPort = int(sys.argv[1])
allowedAttempts = int(sys.argv[2])
activeUsers = 0
userAttempts = []
blockedUsers = []
serverAddress = (serverHost, serverPort)

# define socket for the server side and bind address
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(serverAddress)

"""
    Define multi-thread class for client
    This class would be used to define the instance for each connection from each client
    For example, client-1 makes a connection request to the server, the server will call
    class (ClientThread) to define a thread for client-1, and when client-2 make a connection
    request to the server, the server will call class (ClientThread) again and create a thread
    for client-2. Each client will be runing in a separate therad, which is the multi-threading
"""
class ClientThread(Thread):
    def __init__(self, clientAddress, clientSocket):
        Thread.__init__(self)
        self.clientAddress = clientAddress
        self.clientSocket = clientSocket
        self.clientAlive = False
        self.active = False
        self.clientAlive = True
        
    def run(self):
        self.process_login()
        self.send_message("Enter one of the following commands (BCM, ATU, SRB, SRM, RDM, OUT): ")
        message = ''        

        while self.clientAlive:
            message = self.receive_message()
            
            # if the message from client is empty, the client would be off-line then set the client as offline (alive=Flase)
            if message == '':
                self.clientAlive = False
                print("===== the user disconnected - ", clientAddress)
                break
            
            # handle message from the client
            if message == 'BCM':
                print("[recv] New login request")
                self.process_login()
            elif message == 'ATU':
                print("[recv] Download request")
                message = 'download filename'
                print("[send] " + message)
                self.clientSocket.send(message.encode())
            elif message == 'SRB':
                print("hi")
            elif message == 'SRM':
                print("hi")
            elif message == 'RDM':
                print("hi")
            elif message == 'OUT':
                self.clientAlive = False
                break
            else:
                self.send_message("Invalid command. Enter one of the following commands (BCM, ATU, SRB, SRM, RDM, OUT): ")
    
    def send_message(self, message):
        self.clientSocket.send(message.encode())

    def receive_message(self):
        data = self.clientSocket.recv(1024)
        return data.decode()

    def check_blocked_users(self, username):
        if username in blockedUsers:
            for user in blockedUsers:
                if username is user:
                    if user[1] <= datetime.timestamp(datetime.now()):
                        blockedUsers.remove(user)
                        return False
                    else:
                        self.send_message("Your account is blocked due to multiple login failures. Please try again later")
                        return True

    def successful_login(self, username):
        self.active = True
        self.send_message("Welcome to TOOM!")
        activeUsers += 1
        timestamp = datetime.timestamp(datetime.now())
        dateTime = datetime.fromtimestamp(timestamp)
        dateTimeString = dateTime.strftime("%d %m %Y, %H:%M:%S")
        if exists(USERLOG_FILE):
            f = open(USERLOG_FILE, "a")
        else:
            f = open(USERLOG_FILE, "w")
        f.write(activeUsers + dateTimeString + username + self.clientAddress + self.clientSocket)

    def password_reattempt(self, username, credentials):
        if username not in userAttempts:
            userAttempts.append([username, 1])
            self.send_message("Invalid Password. Please try again")
        
            self.send_message("Password: ")
            password = self.receive_message()
            if password is credentials[index(username)+1]:
                self.successful_login(username)
            else:
                self.password_reattempt(self, username, credentials)
        else:
            for user in userAttempts:
                if username is user:
                    user[1] += 1
                    if user[1] == allowedAttempts:
                        self.send_message("Invalid Password. Your account has been blocked. Please try again later")    
                        timeoutStart = datetime.timestamp(datetime.now())
                        userAttempts.remove(user)
                        blockedUsers.append([username, timeoutStart + 10])
                    else:
                        self.send_message("Password: ")
                        password = self.receive_message()
                        if password is credentials[index(username)+1]:
                            self.successful_login(username)
                        else:
                            self.password_reattempt(self, username, credentials)

    def process_login(self):
        self.send_message("Username: ")
        username = self.receive_message()

        self.send_message("Password: ")
        password = self.receive_message()

        blocked = self.check_blocked_users(username)

        if not blocked:
            f = open(CREDENTIALS_FILE, "r")
            credentials = f.read().split()
            if username in credentials:
                if credentials.index(username) % 2 == 0:
                    if password is credentials[index(username)+1]:
                        self.successful_login(username)
                    else:
                        self.password_reattempt()
                else:
                    self.send_message("Invalid Username. Please try again")
            else:
                self.send_message("Invalid Username. Please try again")
            
        f.close()

print("\n===== Server is running =====")
print("===== Waiting for connection request from clients...=====")


while True:
    serverSocket.listen()
    clientSockt, clientAddress = serverSocket.accept()
    clientThread = ClientThread(clientAddress, clientSockt)
    clientThread.start()