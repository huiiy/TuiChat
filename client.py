# client.py
# This is the program that each user runs to connect to the chat server.

import socket
import threading
import time

def receive_messages(client_socket):
    """
    This function runs in a separate thread to listen for incoming messages from the server.
    """
    while True:
        try:
            # Receive message from the server.
            message = client_socket.recv(1024).decode('utf-8')
            
            if message == 'NICK':
                # The server is asking for our nickname.
                client_socket.send(nickname.encode('utf-8'))
            else:
                # Print the received message for the user to see.
                print(message)
        except:
            # An error occurred, likely the server has closed the connection.
            print("An error occurred! Disconnected from server.")
            client_socket.close()
            break

def send_messages(client_socket, nickname):
    """
    This function runs in the main thread, waiting for the user to type a message.
    """
    while True:
        # Wait for user input.
        message_text = input(f"{nickname}: ")
        
        # Format the message with the user's nickname.
        full_message = f"{nickname}: {message_text}"
        
        # Send the message to the server.
        try:
            client_socket.send(full_message.encode('utf-8'))
        except:
            print("Could not send message. Connection might be closed.")
            break

# --- Client Setup ---

# Ask the user for their desired nickname.
nickname = input("Choose your nickname: ")

# Ask for the server's IP address. For local testing, this will be '127.0.0.1'.
# If the server is on another computer on your network, use its local IP address.
server_ip = input("Enter server IP address (e.g., 127.0.0.1): ")
PORT = 12345

# Create a socket object.
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to the server.
    client.connect((server_ip, PORT))
except ConnectionRefusedError:
    print("Connection failed. Is the server running on that IP?")
    exit() # Exit the script if connection fails.


# --- Start Threads for Sending and Receiving ---

# Create and start a thread for receiving messages.
# This allows us to receive messages at the same time we are typing a new one.
receive_thread = threading.Thread(target=receive_messages, args=(client,))
receive_thread.start()

# Start the function for sending messages in the main thread.
time.sleep(0.1)
send_messages(client, nickname)

