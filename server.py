# server.py
# This is the central hub of our chat application.
# It wll listen for incoming connections from clients and broadcast messages to all connected clients.

import socket
import threading

# --- Constants ---
# We use '0.0.0.0' to allow connections from any IP address on the network.
# For local testing on one machine, you could also use '127.0.0.1' (localhost).
HOST = '0.0.0.0' 
PORT = 12345  # A port number that is unlikely to be in use.

# --- Server Setup ---
# Create a socket object.
# AF_INET specifies that we're using IPv4.
# SOCK_STREAM specifies that we're using TCP (a reliable connection-based protocol).
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the server to the specified host and port.
# This tells the OS that our server program will be listening on this address.
server.bind((HOST, PORT))

# Put the server into listening mode, ready to accept connections.
server.listen()
print(f"[*] Server listening on {HOST}:{PORT}")

# --- Client Management ---
# We need lists to keep track of connected clients and their chosen nicknames.
clients = []
nicknames = []

def broadcast(message, _client=None):
    """
    Sends a message to all connected clients, except the sender if specified.
    """
    for client in clients:
        # We can optionally exclude one client (the original sender)
        if client != _client:
            try:
                client.send(message)
            except:
                # If sending fails, the client has likely disconnected.
                # We'll handle their removal in the handle_client function.
                pass

def handle_client(client):
    """
    This function runs in a separate thread for each connected client.
    It handles receiving messages from a client and broadcasting them.
    """
    while True:
        try:
            # Receive a message from the client (up to 1024 bytes).
            message = client.recv(1024)
            if message:
                # If a message is received, broadcast it to other clients.
                print(f"[*] Broadcasting message: {message.decode('utf-8')}")
                broadcast(message, client)
            else:
                # If we receive no data, the client has disconnected.
                raise ConnectionResetError
        except (ConnectionResetError, ConnectionAbortedError):
            # This block executes if a client disconnects.
            if client in clients:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                nicknames.remove(nickname)
                
                # Announce that the client has left.
                disconnect_message = f"{nickname} has left the chat.".encode('utf-8')
                print(f"[*] {nickname} has disconnected.")
                broadcast(disconnect_message)
                break # Exit the loop for this client's thread.

def receive_connections():
    """
    The main server loop to accept new client connections.
    """
    while True:
        # accept() is a blocking call - it will wait here until a new client connects.
        # It returns the client's socket object and their address (IP, port).
        client, address = server.accept()
        print(f"[*] Accepted connection from {address[0]}:{address[1]}")

        # Ask the newly connected client for their nickname.
        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')

        # Add the new client and nickname to our lists.
        nicknames.append(nickname)
        clients.append(client)

        # Announce the new user to everyone in the chat.
        print(f"[*] Nickname of the client is {nickname}")
        broadcast(f"{nickname} has joined the chat!".encode('utf-8'), client)
        
        # Send a welcome message to the new client.
        client.send("Connected to the server!".encode('utf-8'))

        # Start a new thread to handle this client's messages.
        # This allows the server to handle multiple clients simultaneously.
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

# Start the main function to listen for connections.
receive_connections()

