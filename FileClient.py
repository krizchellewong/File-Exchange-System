# MP Client by S13 Group 9
# Names: Sayo, Trisha Alissandra
#        Wong, Krizchelle Danielle
#        Yung Cheng, Adrian

import socket
import threading
import json
import time
import os

# Message Buffer Size
BUFFER_SIZE = 1024
# Connection Status
isConnected = False
# Server Address Variable
server_address = None
# Command Variable
command = None
# Params Variable
params = None
# Current Client Handle
current_handle = None


# Command Processing
def toServer(entry):
    global isConnected
    global server_address
    global command
    global params
    
    # Invalid Command (does not start with "/")
    if not entry.startswith('/'):
        print("Error: That is not a command! Type /? for help.")
        return
    
    input_line = entry.split()
    command = input_line[0]
    params = input_line[1:]
    
    # Join Command
    if command == "/join":
        # Invalid Syntax/Parameters
        if len(params) != 2:
            print("Invalid command syntax!")
            print("Usage: /join <server_ip_add> <port>")
        # User is already connected to the server
        elif isConnected:
            print("Error: User is already connected to the server.")
        # No Errors
        else:
            try:
                socket.gethostbyname(params[0])

                server_address = (params[0], int(params[1]))

                # Send "Join" Command to Server
                client_socket.sendto(json.dumps({"command": "join"}).encode(), server_address)

                # Wait for "join_ack" Command from Server
                client_socket.settimeout(3)
                response = client_socket.recvfrom(BUFFER_SIZE)
                data = json.loads(response[0].decode())
                if data["command"] == "join_ack":
                    isConnected = True
                    print("Successfully connected to the server.")
                    client_socket.settimeout(None)
                else:
                    raise Exception("Did not receive 'join_ack' from server.")
            except socket.timeout:
                print("Error: Server is offline or not responding.")
                server_address = None
                return
            except Exception as e:
                print(f"Error: {str(e)}")
                server_address = None
                return
    # Leave Command
    elif command == "/leave":
        # Check if connected
        if isConnected:
            # No other parameters for command
            if len(params) > 0:
                print("Error: There should be no parameters for leave.")
                print("Usage: /leave")
            # Send "Leave" Command to Server
            else:
                client_socket.sendto(json.dumps({"command": "leave"}).encode(), server_address)
                time.sleep(0.1)
        # No Connection Established yet
        else:
            print("Error: Disconnection failed. Please connect to the server first.")
    # Register Command
    elif command == "/register":
        # Check if Client is Connected to the Server
        if isConnected:
            # Incorrect syntax/parameters
            if len(params) != 1:
                print("Error: Command parameters do not match or is not allowed.")
                print("Usage: /register <handle>")
            # Send "Register" Command to Server
            else:
                client_socket.sendto(json.dumps({"command": "register", "handle": params[0]}).encode(), server_address)
                time.sleep(0.1)
        # No Connection Established yet
        else:
            print("Error: Please connect to the server first.")
    # Store Command
    elif command == "/store":
        if isConnected:
            if len(params) < 1:
                print("Error: Invalid command syntax!")
                print("Usage: /store <filename>")
                
            elif current_handle == None:
                print("Error: Please register a handle first.")
            else:
                filename = params[0]
                try:
                    # Open the specified file in binary mode for reading
                    with open(filename, 'rb') as file:
                        file_data = file.read()
                        # Send file data to the server with the command and filename
                        client_socket.sendto(json.dumps({"command": "store", "filename": filename, "data": file_data.decode('ISO-8859-1')}).encode(), server_address)
                        time.sleep(0.1)
                except FileNotFoundError:
                    # Handle the case where the file does not exist
                    print(f"Error: File not found.")
                except Exception as e:
                    # General exception handling
                    print(f"Error: {str(e)}")
        else:
            print("Error: Please connect to the server first.")
        
    # DIR Command
    elif command == "/dir":
        # Request File List from Server
        if isConnected:
            if len(params) > 0:
                print("Error: There should be no parameters for dir.")
                print("Usage: /dir")
            
            elif current_handle == None:
                print("Error: Please register a handle first.")
                
            else:
                try:
                    client_socket.sendto(json.dumps({"command": "dir"}).encode(), server_address)
                    time.sleep(0.1)
                except Exception as e:
                    print("Error sending data:", e)            
        else:
            print("Error: Please connect to the server first.")

    # Get Command
    elif command == "/get":
        if isConnected:
            if len(params) < 1:
                print("Error: Invalid command syntax!")
                print("Usage: /get <filename>")
                
            elif current_handle == None:
                print("Error: Please register a handle first.")
            else:
                filename_str = params[0]
                try:
                    client_socket.sendto(json.dumps({"command": "get", "filename_str": filename_str}).encode(), server_address)
                    time.sleep(0.1)
                except Exception as e:
                    print("Error sending data:", e)
        else:
            print("Error: Please connect to the server first.")
            
    # Message All Command
    elif command == "/all":
        if isConnected:
            if len(params) == 0:
                print("Error: Command parameters do not match or is not allowed.")
                print("Usage: /all <message>")
            elif current_handle == None:
                print("Error: Please register a handle first.")
            else:
                message = ' '.join(params)
                client_socket.sendto(json.dumps({"command" : "all", "message" : message}).encode(), server_address)
        else:
            print('Error. Please connect to the server first.')
    
    # Direct Message Command
    elif command == "/dm":
        if isConnected:
            if len(params) < 2:
                print("Error: Command parameters do not match or is not allowed.")
                print("Usage: /dm <handle> <message>")
                
            elif current_handle == None:
                print("Error: Please register a handle first.")
            else:
                handle = params[0]
                message = ' '.join(params[1:])
                client_socket.sendto(json.dumps({"command" : "dm", "handle" : handle, "message" : message}).encode(), server_address)
        else:
            print('Error. Please connect to the server first.')
            
    elif command == "/cls":
        # Checking if the OS is Windows
        if os.name == "nt":  
             # Clear the screen for Windows            
            os.system('cls') 
        else:
            # Clear the screen for macOS/Linux
            os.system('clear')  

        if current_handle == None:
            print("File Exchange Client")
        else:
            print(f"File Exchange Client - {current_handle}")
        print("Enter a command. Type /? for help")


    # Help Command
    elif command == "/?":
        print("Connect to the server application:               /join <server_ip_add> <port>")
        print("Disconnect to the server application:            /leave")
        print("Register a unique handle or alias:               /register <handle>")
        print("Send file to server:                             /store <filename>")
        print("Request directory file list from server:         /dir")
        print("Fetch a file from a server:                      /get <filename>")
        print("Send a message to all registered Handles:        /all <message>")
        print("Send a direct message to one Handle:             /dm <handle> <message>")
        print("Request command help:                            /?")
        print("Clear Screen:                                    /cls")
    # Invalid Command (starts with / but not a command)
    else:
        print("Command not found. Type /? for help.")

# Server Message Response
def fromServer(data):
    global isConnected
    global server_address
    global command
    global current_handle

    # make sure the data is json
    if not(isinstance(data, str)):
        command = data['command']

        if 'message' in data:
            message = data['message']
        
        if command == "ping":
            ping_ack = {'command': 'ping'}
            client_socket.sendto(json.dumps(ping_ack).encode(), server_address)
            return
        
        # Server Join Response
        elif command == "join":
            message = data['message']
            print(f"{message}")
            
        # Server Leave Response
        elif command == "leave":
            print("Connection closed. Thank you!")
            isConnected = False
            server_address = None
        
        # Server Register Response
        elif command == "register":
            current_handle = data['handle']
            print(f"Handle Registration Successful! Your Handle is now {current_handle}.")
        
        # Server Store Response
        elif command == "store":
            filename_str = data['filename_str']
            print(f"File {filename_str} sent to server.")
        
        # Server Directory Response
        elif command == "dir":
            # Receive Response from Server
            if data['command'] == 'dir':
                print("File Server Directory:")
                file_list = data['file_list']
                timestamp_list = data['timestamp_list']
                uploader_list = data['uploader_list']
                for i in range(len(file_list)):
                    curr_filename = file_list[i]
                    curr_timestamp = timestamp_list[i]
                    curr_uploader = uploader_list[i]
                    print(f"{curr_filename} <{curr_timestamp}> : {curr_uploader}")
            return

        # Server Get Response
        elif command == "get":
            filename = data['filename']
            file_data = data['file_data'].encode('ISO-8859-1')
            try:
                with open(filename, 'wb') as file:
                    file.write(file_data)
                file.close()
                print(f"File received from server:  {filename}")
            except Exception as e:
                print(f"Error: {str(e)}")
                
        # Server All Response
        elif command == "all":
            sender = data['sender']
            message = f"[From {sender} to all]: {message}"
            print(f"{message}\n> ", end = "")
        
        # Server DM Response
        elif command == "dm":
            sender = data['sender']
            message = f"[From {sender} to you]: {message}"
            print(f"{message}\n> ", end = "")
            
        # Server Error Response
        elif command == 'error':
            if 'message' in data:
                print(f"{message}")

# Receive Response from Server  
def receive():
    global isConnected
    
    while True:
        
        # Lines only for when connected
        if command != "/join":
            if isConnected:
                try:   
                    response = client_socket.recvfrom(BUFFER_SIZE)

                    # check if data is string or json then read it accordingly
                    response_str = response[0].decode()
                    try:
                        data = json.loads(response_str)
                    except json.JSONDecodeError:
                        data = response_str

                    fromServer(data)
                except ConnectionResetError:
                    print("Error: Connection to the Server has been lost!")
                    isConnected = False
                except Exception as e:
                    print(f"Error314: {str(e)}")
                
   
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

thread = threading.Thread(target = receive)
thread.start()

print("File Exchange Client")
print("Enter a command. Type /? for help")
 
while True:
    entry = input("> ")
    toServer(entry)