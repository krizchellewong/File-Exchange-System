# MP Server by S13 Group 9
# Names: Sayo, Trisha Alissandra
#        Wong, Krizchelle Danielle
#        Yung Cheng, Adrian


import socket
import time
import json
import os

# Message Buffer Size
BUFFER_SIZE = 1024

# Process Client Commands
def fromClients(entry):
    message = json.loads(entry.decode())
    command = message['command']
    
    # Join Server
    if command == "join":
        clients.update({address : None})
        print(f"Client {address} has connected")
        jsonData = {'command': 'success', 'message': "New user connected"}
        server_socket.sendto(json.dumps(jsonData).encode(), address)
           
    # Leave Server     
    elif command == "leave":
        print(f"Client {clients[address]}:{address} disconnected")
        if clients[address] == None:
            message = "Unregistered user disconnected"
        else:
            message = f"User {clients[address]} disconnected"
        jsonData = {'command': 'success', 'message': message}
        # Send to all Clients
        for client_address in clients:
            # Send to all except the sender
            if client_address != address:
                server_socket.sendto(json.dumps(jsonData).encode(), client_address)
    # Register Handle
    elif command == "register":
        handle = message['handle']
        # Client already has a handle, tries to register another
        if clients[address] != None:
            print(f"{address} ({clients[address]}) Attempted to register again")
            jsonData = {'command': 'error', 'message': "Error: Registration failed. You already have a username."}
        # Client has no handle, tries to register an already taken handle
        elif handle in clients.values():
            print(f"{address} handle registration failed")
            jsonData = {'command': 'error', 'message': "Error: Registration failed. Handle or alias already exists."}
        # Client has no handle and registers a new handle
        else:
            clients[address] = handle
            print(f"Username {handle} registered by {address}")
            jsonData = {'command': 'success', 'given' : 'register' , 'message': f"Welcome {handle}!"}
            # send back to client
            server_socket.sendto(json.dumps(jsonData).encode(), address)
    # Store File in Server        
    elif command == "store":
        # TODO: Add file to a list for the server to keep track of
        # Error Validation comes in the form of same filename and type, either ask user to overwrite, or rename file
        
        pass
    # Request File List from Server
    elif command == "dir":
        # TODO: Send file list to client
        pass
    # Retrieve File from Server
    elif command == "get":
        # TODO: send file requested to client
        # Error Validation comes in the form of if filename and type does not exist, return error message to client
        pass

# BONUS 1 - Broadcast to All Clients - Ping
def ping():
    # Checks All Users in Clients
    for user in clients:
        print(f"Pinging user {user} : ", end="")
        ping_req = {'command': 'ping', 'message' : "Server ping"}
        server_socket.sendto(json.dumps(ping_req).encode(), user)
        
        time.sleep(0.3)
        try:
            # Server waits for 3 seconds for response from client/s
            server_socket.settimeout(3)
            server_socket.recvfrom(BUFFER_SIZE)
            print("Online")
        except Exception as e:
            # No response, sets as offline
            print("Offline")
            disconnected.append(user)

# Client Address and Username in {address : username} format
clients = {}
# List of Disconnected Clients
disconnected = []

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)           
       
# Setup server      
while True:
    print("File Exchange UDP Server")
    try:
        ip = input("Enter IP Address: ")
        port = input("Enter Port Number: ")
        server_socket.bind((ip, int(port)))
        print(f"Server is running on {ip}:{port}")
        break
    except Exception as e:
        os.system('cls')
        print(f"Error: {str(e)}")
        print("Try again\n")
        
# Process incoming data
while True:
    try:
        entry, address = server_socket.recvfrom(BUFFER_SIZE)
        fromClients(entry)
        
    except ConnectionResetError as e:
        print(f"ConnectionResetError: {e}")
        ping()
        
    except Exception as e:
        print(f"Error: {str(e)}")
    
    finally:
        for user in disconnected:
            print(f"User {clients[user]} : {user} offline. Disconnecting")
            clients.pop(user)
        disconnected.clear()