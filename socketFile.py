import os
from socket import socket, AF_UNIX, SOCK_STREAM

# Set the socket file path
socket_file = os.path.join(os.path.curdir, "flaskServer.sock")

# Set the umask to 007
os.umask(0o007)

# Create the socket
sock = socket(AF_UNIX, SOCK_STREAM)

# Bind the socket to the file
try:
    sock.bind(socket_file)
except OSError as error:
    print(f"Error binding socket: {error}")
    raise
else:
    print(f"Socket successfully bound to: {socket_file}")

# ... (your application logic using the socket) ...