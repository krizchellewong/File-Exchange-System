# MP Server by S13 Group 9
# Names: Sayo, Trisha Alissandra
#        Wong, Krizchelle Danielle
#        Yung Cheng, Adrian


import socket
import time
import json
import os
import base64
from datetime import datetime

# Message Buffer Size
BUFFER_SIZE = 1024

# Process Client Commands
def fromClients(entry):
    message = json.loads(entry.decode())
    command = message['command']
    
    # Join Server
    if command == "join":
        # If Client has already connected to Server before
        if address in clients:
            print(f"Client {address} has reconnected")
            jsonData = {'command': 'join_ack', 'message': "Re-connection to the Server is successful!"}
        # If Client has not connected to Server before
        else:
            clients.update({address : None})
            print(f"Client {address} has connected")
            jsonData = {'command': 'join_ack', 'message': "Connection to the Server is successful!"}
        server_socket.sendto(json.dumps(jsonData).encode(), address)
                
           
    # Leave Server     
    elif command == "leave":
        print(f"Client {clients[address]}:{address} disconnected")
        # Client has never registered handle
        if clients[address] == None:
            message = "Unregistered user disconnected"
        # Client has registered a handle
        else:
            message = f"User {clients[address]} disconnected"
        jsonData = {'command': 'leave', 'message': message}
        server_socket.sendto(json.dumps(jsonData).encode(), address)

        # clients.pop(address)
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
            jsonData = {'command': 'register', 'given' : 'register' , 'handle' : handle, 'message': f"Welcome {handle}!"}
            # send back to client
        
        server_socket.sendto(json.dumps(jsonData).encode(), address)
    
    
    # Store File in Server        
    elif command == "store":
        
        filename = message.get('filename')
        file_data = base64.b64decode(message.get('data'))
        uploader = clients.get(address)  # Assuming `clients` is a dict mapping addresses to usernames

        try:
            # Save the file data received from the client
            with open(filename, 'wb') as file:
                file.write(file_data)

            # Generate a timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Check if Filename already exists in Server
            if filename not in file_list:
                print("New File Detected. Appending to Lists.")
                file_list.append(filename)
                file_data_list.append(file_data)
                timestamp_list.append(timestamp)
                uploader_list.append(uploader)
                response_message = f"{uploader} <{timestamp}>: Uploaded {filename}"
                print(response_message)
                response = {'command': 'store', 'uploader' : uploader, 'timestamp' : timestamp, 'filename': filename}
                server_socket.sendto(json.dumps(response).encode(), address)
            # Reject new file, filename already exists
            else:
                print("Existing File Detected")
                response_message = f"Error: File {filename} already exists."
                print(response_message)
                response = {'command': 'error', 'message': response_message}
                server_socket.sendto(json.dumps(response).encode(), address)
        except Exception as e:
            # Handle exceptions during file write
            response = json.dumps({'command': 'error', 'message': f"{str(e)}"})
            server_socket.sendto(json.dumps(response).encode(), address)
        
        
    # Request File List from Server
    elif command == "dir":
        try:
            # If Server does not contain any files
            if len(file_list) == 0:
                print("Error: No files in server.")
                jsonData = {'command': 'error', 'message': "Error: No files in server."}
            # Server has files
            else:
                jsonData = {'command': 'dir', 'file_list': file_list, 'timestamp_list': timestamp_list, 'uploader_list': uploader_list}
            # Response to Client
            server_socket.sendto(json.dumps(jsonData).encode(), address)
        except Exception as e:
            print("Error sending response to client: " + e)
    
    # Retrieve File from Server
    elif command == "get":
        filename = message['filename']
        
        try:
            # If Filename does not exist in Server
            if not filename in file_list:
                raise FileNotFoundError
            
            # If Filename exists in Server
            else:
                file_index = file_list.index(filename)
                file_data = file_data_list[file_index]
                encoded_file_data = base64.b64encode(file_data).decode()
                response = {"command": "get", "filename": filename, "file_data": encoded_file_data, "message": "File sent successfully."}
                    
            # Send Response to Client
            server_socket.sendto(json.dumps(response).encode(), address)
            print("File sent to client successfully.")
                
        except FileNotFoundError:
            response = {"command": "error", "message": f"Error: File {filename} not found."}
            print("File Not Found.")
            server_socket.sendto(json.dumps(response).encode(), address)
        except Exception as e:
            response = {"command": "error", "message": f"Error: {str(e)}"}
            print(f"Error: {str(e)}")
            server_socket.sendto(json.dumps(response).encode(), address)
        
    # BONUS 1 - Send Message to All Registered Handles
    elif command == "all":
        # If Sender has no Handle
        if clients[address] == None:
            print(f"Client {address} Attempted to /all without username")
            jsonData = {'command': 'error', 'message': "Error: You must register a handle first."}
            server_socket.sendto(json.dumps(jsonData).encode(), address)
            return
        # Default
        message = f"{message['message']}"
        print(f"{address} > {message}")
        message_jsonData = {'command': 'all', 'sender' : f'{clients[address]}', 'message': message}
        # Send Message to all Registered Handles
        for client_address, client_handle in clients.items():
            # Receivers must have a registered handle
            if client_handle != None:
                # All registered users except Sender
                if client_handle != clients[address]:
                    server_socket.sendto(json.dumps(message_jsonData).encode(), client_address)
       
    # BONUS 2 - Send Message to Specific Handle         
    elif command == "dm":
        handle = message['handle']
        message = message['message']
        sender = clients[address]
        
        # Print Validation
        print(f"{sender} to {handle} : {message}")
        
        # If Sender send msg to Self
        if sender == handle:
            print(f"Client {address} Attempted to /dm self")
            jsonData = {'command': 'error', 'message': "Error: You cannot DM yourself."}
            server_socket.sendto(json.dumps(jsonData).encode(), address)
            return
        
        # If Sender send msg to non-existent Handle
        elif handle not in clients.values():
            print(f"Client {address} Attempted to /dm non-existent handle")
            jsonData = {'command': 'error', 'message': "Error: Handle does not exist."}
            server_socket.sendto(json.dumps(jsonData).encode(), address)
            return
        
        # Default case, loop through all clients' addresses and handles
        for client_address, client_handle in clients.items():
            
            # if Receiver Handle is the same as Current Loop's Handle
            if client_handle == handle:
                # Contain message from sender
                message_jsonData = {'command': 'dm', 'sender' : sender, 'message': message}
                    
                # Send message to receiver
                server_socket.sendto(json.dumps(message_jsonData).encode(), client_address)
                print(f"Direct Message Sent from {sender} to {handle}")
                return

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
# Server File Directory List
file_list = []
# Server File Data List
file_data_list = []
# Server File Timestamp List
timestamp_list = []
# Server File Uploader List
uploader_list = []

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
        
# Server Data Processor from Clients
while True:
    try:
        entry, address = server_socket.recvfrom(BUFFER_SIZE)
        fromClients(entry)
        
    except ConnectionResetError as e:
        print(f"ConnectionResetError: {e}")
        ping()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print("default server exception tracker")
    
    finally:
        for user in disconnected:
            print(f"User {clients[user]} : {user} offline. Disconnecting")
            clients.pop(user)
        disconnected.clear()