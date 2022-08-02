"""
    Python 3
    coding: utf-8
"""
from socket import *
import sys

def send_message(clientSocket):
    message = input()
    clientSocket.sendall(message.encode())

def receive_message(clientSocket):
    data = clientSocket.recv(1024)
    return data.decode()

#Server would be running on the same host as Client
if len(sys.argv) != 3:
    print("\n===== Error usage, python3 TCPClient3.py SERVER_IP SERVER_PORT ======\n")
    exit(0)
serverHost = sys.argv[1]
serverPort = int(sys.argv[2])
serverAddress = (serverHost, serverPort)

# define a socket for the client side, it would be used to communicate with the server
clientSocket = socket(AF_INET, SOCK_STREAM)

# build connection with the server and send message to it
clientSocket.connect(serverAddress)

receivedMessage = receive_message(clientSocket)
if receivedMessage == "Username: ":
    send_message(clientSocket)
if receivedMessage == "Password: ":
    send_message(clientSocket)

while True:
    receivedMessage = receive_message(clientSocket)

    if receivedMessage == "":
        print("[recv] Message from server is empty!")
    elif receivedMessage == "user credentials request":
        print("[recv] You need to provide username and password to login")
    elif receivedMessage == "download filename":
        print("[recv] You need to provide the file name you want to download")
    else:
        print("[recv] Message makes no sense")

# close the socket
clientSocket.close()