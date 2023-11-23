# MP Server by S13 Group 9
# Names: Sayo, Trisha Alissandra
#        Wong, Krizchelle Danielle
#        Yung Cheng, Adrian


import socket
import time
import json
import os
from datetime import datetime

# Message Buffer Size
BUFFER_SIZE = 1024

# Process Client Commands
def fromClients(entry):
    message = json.loads(entry.decode())
    command = message['command']
    
    # Join Server
    if command == "join":
        if address in clients:
            print(f"Client {address} has reconnected")
            jsonData = {'command': 'success', 'message': f"User {address} reconnected"}
            server_socket.sendto(json.dumps(jsonData).encode(), address)
        else:
            clients.update({address : None})
            print(f"Client {address} has connected")
            jsonData = {'command': 'success', 'message': "New user connected"}
            server_socket.sendto(json.dumps(jsonData).encode(), address)
        
        # Bonus 1 - Broadcast to All Clients that a User has Newly Connected/Reconnected
        for client_address in clients:
            # Send to all except the sender
            if client_address != address:
                jsonData = {'command': 'success', 'message': f"User {address} has connected"}
                server_socket.sendto(json.dumps(jsonData).encode(), client_address)
                
           
    # Leave Server     
    elif command == "leave":
        print(f"Client {clients[address]}:{address} disconnected")
        if clients[address] == None:
            message = "Unregistered user disconnected"
        else:
            message = f"User {clients[address]} disconnected"
        jsonData = {'command': 'success', 'message': message}
        
        # Bonus 2 - Broadcast to All Clients that a User has Disconnected
        for client_address in clients:
            # Send to all except the sender
            if client_address != address:
                server_socket.sendto(json.dumps(jsonData).encode(), client_address)
            else:
                server_socket.sendto(json.dumps(jsonData).encode(), address)
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
        
        # Bonus 3 - Broadcast to All Clients that a User has Registered a Handle    
        for client_address in clients:
            # Send to all except the sender
            if client_address != address:
                server_socket.sendto(json.dumps(jsonData).encode(), client_address)
            else:
                server_socket.sendto(json.dumps(jsonData).encode(), address)
    # Store File in Server        
    elif command == "store":
        # TODO: Add file to a list for the server to keep track of
        # Error Validation comes in the form of same filename and type, either ask user to overwrite, or rename file
        filename = message.get('filename')
        file_data = message.get('data')
        user = clients.get(address)  # Assuming `clients` is a dict mapping addresses to usernames

        try:
            # Save the file data received from the client
            with open(filename, 'wb') as file:
                file.write(file_data.encode('utf-8'))

            # Generate a timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file_list.append((filename, timestamp, user))
            response_message = f"{user}<{timestamp}>: Uploaded {filename}"
            response = json.dumps({'command': 'success', 'message': response_message})
        except Exception as e:
            # Handle exceptions during file write
            response = json.dumps({'command': 'error', 'message': str(e)})
        
        # Bonus 4 - Broadcast to All Clients that a User has Stored a File 
        for client_address in clients:
            # Send to all except the sender
            if client_address != address:
                server_socket.sendto(json.dumps(jsonData).encode(), client_address)
            else:
                server_socket.sendto(json.dumps(jsonData).encode(), address)
        
    # Request File List from Server
    elif command == "dir":
        try:
            # If Server does not contain any files
            # print("Command DIR")
            if len(file_list) == 0:
                print("Error: No files in server.")
                jsonData = {'command': 'error', 'message': "Error: No files in server."}
            # Server has files
            else:
                # print("Server has files")
                jsonData = {'command': 'dir', 'file_list': file_list}
            # Response to Client
            # print("Sending response")
            # print("Data being sent:", jsonData)
            server_socket.sendto(json.dumps(jsonData).encode(), address)
            # print("Sent successfully")
        except Exception as e:
            print("Error sending response to client:", e)
        
    # Retrieve File from Server
    elif command == "get":
        data, client_address = server_socket.recvfrom(BUFFER_SIZE)
        data = json.loads(data.decode())
        filename = data['filename']
        # print("Get")
        try:
            with open(filename, 'rb') as file:
                file_data = file.read()
                response = {"command": "get", "filename": filename, "data": file_data.decode('ISO-8859-1'), "message": "File sent successfully."}
                # print("Response found")
            print("File sent to client successfully.")
        except FileNotFoundError:
            response = {"command": "error", "message": f"File {filename} not found."}
            print("File Not Found.")
        except Exception as e:
            response = {"command": "error", "message": str(e)}
            print(f"Error: {str(e)}")
        server_socket.sendto(json.dumps(response).encode(), client_address)
        
    # BONUS 1 - Send Message to All Registered Handles
    elif command == "all":
        # If Sender has no Handle
        if clients[address] == None:
            print(f"Client {address} Attempted to /all without username")
            jsonData = {'command': 'error', 'message': "Error: You must register a handle first."}
            server_socket.sendto(json.dumps(jsonData).encode(), address)
            return
        # Default
        message = f"{clients[address]} : {message['message']}"
        print(f"{address} > {message}")
        message_jsonData = {'command': 'all', 'message': message}
        # Send Message to all Registered Handles
        for client_address, client_handle in clients.items():
            if client_handle != None:
                server_socket.sendto(json.dumps(message_jsonData).encode(), client_address)
       
    # BONUS 2 - Send Message to Specific Handle         
    elif command == "dm":
        handle = message['handle']
        message = message['message']
        sender = clients[address]
        
        # If Sender has no Handle
        if sender == None:
            print(f"Client {address} Attempted to /dm without username")
            jsonData = {'command': 'error', 'message': "Error: You must register a handle first."}
            server_socket.sendto(json.dumps(jsonData).encode(), address)
            return
        # If Sender send msg to Self
        elif sender == handle:
            print(f"Client {address} Attempted to /dm self")
            jsonData = {'command': 'error', 'message': "Error: You cannot DM yourself."}
            server_socket.sendto(json.dumps(jsonData).encode(), address)
            return
        
        for client_address, client_handle in clients.items():
            if client_handle == handle:
                message_jsonData = {'command': 'dm', 'handle' : sender, 'message': message}
                try:
                    server_socket.sendto(json.dumps(message_jsonData).encode(), client_address)
                    print(f"Message from {address} to {client_address}")
                    message = f"[To {handle} from {sender}] : {message}"
                    jsonData = {'command': 'success', 'given' : 'dm', 'message': message}
                except:
                    jsonData = {'command': 'error', 'message': "Error: Handle/alias does not exist."}
                
                server_socket.sendto(json.dumps(jsonData).encode(), address)
                return
            print(f"Direct Message by {address} to {handle} failed")
            jsonData = {'command': 'error', 'message': "Error: Handle/alias does not exist."}
            server_socket.sendto(json.dumps(jsonData).encode(), address)

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