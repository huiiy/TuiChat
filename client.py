# client.py
# This is the program that each user runs to connect to the chat server.

import socket
import threading
import sys # Import sys to use for flushing stdout

def receive_messages(client_socket):
    """
    This function runs in a separate thread to listen for incoming messages from the server.
    """
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            
            if message == 'NICK':
                client_socket.send(nickname.encode('utf-8'))
            else:
                # This is the magic part for a clean UI.
                # \r moves the cursor to the beginning of the line.
                # ANSI escape code \x1b[2K clears the entire line.
                # We then print the message, and then re-print the user's prompt.
                sys.stdout.write('\r\x1b[2K') # Clear the current line
                sys.stdout.write(f"{message}\n") # Print the received message
                sys.stdout.write(f"{nickname}: ") # Reprint the user's prompt
                sys.stdout.flush() # Force the output to display immediately

        except:
            print("\nAn error occurred! Disconnected from server.")
            client_socket.close()
            break

def send_messages(client_socket, nickname):
    """
    This function runs in the main thread, waiting for the user to type a message.
    """
    # The initial prompt is now handled by the receive_messages function
    # when the first message ("Connected to the server!") arrives.
    while True:
        try:
            message_text = input() # Input no longer needs a prompt string
            
            # Move cursor up one line and clear it, to remove the line the user typed on
            sys.stdout.write("\x1b[1A\x1b[2K")
            
            full_message = f"{nickname}: {message_text}"
            client_socket.send(full_message.encode('utf-8'))
        except (KeyboardInterrupt, EOFError):
            print("\nLeaving the chat.")
            client_socket.close()
            break
        except:
            print("Could not send message. Connection might be closed.")
            client_socket.close()
            break


# --- Client Setup ---

nickname = input("Choose your nickname: ")
server_ip = input("Enter server IP address (e.g., 127.0.0.1): ")
PORT = 12345

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect((server_ip, PORT))
except ConnectionRefusedError:
    print("Connection failed. Is the server running on that IP?")
    exit()
except socket.gaierror:
    print("Hostname could not be resolved. Check the IP address.")
    exit()


# --- Start Threads for Sending and Receiving ---

receive_thread = threading.Thread(target=receive_messages, args=(client,))
receive_thread.daemon = True # Allows main thread to exit even if this thread is running
receive_thread.start()

send_messages(client, nickname)
